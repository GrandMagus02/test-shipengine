from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.app.api.v1.shipments import update_shipment_tracking
from src.app.core.exceptions.http_exceptions import BadRequestException, NotFoundException, ServiceUnavailableException
from src.app.core.worker.functions import update_shipment_tracking_status
from src.app.schemas.shipment import (
    Shipment,
    ShipmentStatus,
    TrackingUpdateStatusType,
)


class TestUpdateShipmentTrackingAPI:
    @pytest.mark.asyncio
    async def test_update_shipment_tracking_success(self, mock_db):
        shipment_id = 1
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.PENDING,
        )

        with patch("src.app.api.v1.shipments.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)

            with patch("src.app.api.v1.shipments.queue") as mock_queue:
                mock_pool = Mock()
                mock_pool.enqueue_job = AsyncMock(return_value="job_id_123")
                mock_queue.pool = mock_pool

                await update_shipment_tracking(shipment_id, mock_db)

                mock_crud.get.assert_called_once_with(
                    db=mock_db,
                    id=shipment_id,
                    schema_to_select=Shipment,
                )
                mock_pool.enqueue_job.assert_called_once_with("update_shipment_tracking_status", shipment_id)

    @pytest.mark.asyncio
    async def test_update_shipment_tracking_not_found(self, mock_db):
        shipment_id = 999

        with patch("src.app.api.v1.shipments.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Shipment not found"):
                await update_shipment_tracking(shipment_id, mock_db)

    @pytest.mark.asyncio
    async def test_update_shipment_tracking_no_tracking_number(self, mock_db):
        shipment_id = 1
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number=None,
            status=ShipmentStatus.PENDING,
        )

        with patch("src.app.api.v1.shipments.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)

            with pytest.raises(BadRequestException, match="Shipment has no tracking number"):
                await update_shipment_tracking(shipment_id, mock_db)

    @pytest.mark.asyncio
    async def test_update_shipment_tracking_queue_unavailable(self, mock_db):
        shipment_id = 1
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.PENDING,
        )

        with patch("src.app.api.v1.shipments.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)

            with patch("src.app.api.v1.shipments.queue") as mock_queue:
                mock_queue.pool = None

                with pytest.raises(ServiceUnavailableException, match="Queue pool not available"):
                    await update_shipment_tracking(shipment_id, mock_db)


class TestUpdateShipmentTrackingStatusWorker:
    @pytest.mark.asyncio
    async def test_status_progression_pending_to_processing(self, mock_db):
        """Test status progression from PENDING to PROCESSING."""
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.PENDING,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)
            mock_crud.update = AsyncMock(return_value=None)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                with patch("src.app.core.worker.functions.queue") as mock_queue:
                    mock_pool = Mock()
                    mock_pool.enqueue_job = AsyncMock()
                    mock_queue.pool = mock_pool

                    result = await update_shipment_tracking_status(ctx, shipment_id)

                    assert result.status == TrackingUpdateStatusType.UPDATED
                    assert result.shipment_id == shipment_id
                    assert result.old_status == ShipmentStatus.PENDING.value
                    assert result.new_status == ShipmentStatus.PROCESSING.value
                    mock_crud.update.assert_called_once()
                    # Should schedule next update since PROCESSING is not terminal
                    mock_pool.enqueue_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_status_progression_processing_to_shipped(self, mock_db):
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.PROCESSING,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)
            mock_crud.update = AsyncMock(return_value=None)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                with patch("src.app.core.worker.functions.queue") as mock_queue:
                    mock_pool = Mock()
                    mock_pool.enqueue_job = AsyncMock()
                    mock_queue.pool = mock_pool

                    result = await update_shipment_tracking_status(ctx, shipment_id)

                    assert result.status == TrackingUpdateStatusType.UPDATED
                    assert result.old_status == ShipmentStatus.PROCESSING.value
                    assert result.new_status == ShipmentStatus.SHIPPED.value
                    mock_pool.enqueue_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_status_progression_shipped_to_in_transit(self, mock_db):
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.SHIPPED,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)
            mock_crud.update = AsyncMock(return_value=None)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                with patch("src.app.core.worker.functions.queue") as mock_queue:
                    mock_pool = Mock()
                    mock_pool.enqueue_job = AsyncMock()
                    mock_queue.pool = mock_pool

                    result = await update_shipment_tracking_status(ctx, shipment_id)

                    assert result.status == TrackingUpdateStatusType.UPDATED
                    assert result.old_status == ShipmentStatus.SHIPPED.value
                    assert result.new_status == ShipmentStatus.IN_TRANSIT.value
                    mock_pool.enqueue_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_status_progression_in_transit_to_delivered(self, mock_db):
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.IN_TRANSIT,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)
            mock_crud.update = AsyncMock(return_value=None)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                with patch("src.app.core.worker.functions.queue") as mock_queue:
                    mock_pool = Mock()
                    mock_pool.enqueue_job = AsyncMock()
                    mock_queue.pool = mock_pool

                    result = await update_shipment_tracking_status(ctx, shipment_id)

                    assert result.status == TrackingUpdateStatusType.UPDATED
                    assert result.old_status == ShipmentStatus.IN_TRANSIT.value
                    assert result.new_status == ShipmentStatus.DELIVERED.value
                    # Should NOT schedule next update since DELIVERED is terminal
                    mock_pool.enqueue_job.assert_not_called()

    @pytest.mark.asyncio
    async def test_status_terminal_delivered(self, mock_db):
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.DELIVERED,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                with patch("src.app.core.worker.functions.queue") as mock_queue:
                    mock_pool = Mock()
                    mock_pool.enqueue_job = AsyncMock()
                    mock_queue.pool = mock_pool

                    result = await update_shipment_tracking_status(ctx, shipment_id)

                    assert result.status == TrackingUpdateStatusType.TERMINAL
                    assert result.shipment_id == shipment_id
                    assert result.current_status == ShipmentStatus.DELIVERED.value
                    mock_crud.update.assert_not_called()
                    mock_pool.enqueue_job.assert_not_called()

    @pytest.mark.asyncio
    async def test_status_terminal_cancelled(self, mock_db):
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.CANCELLED,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                result = await update_shipment_tracking_status(ctx, shipment_id)

                assert result.status == TrackingUpdateStatusType.TERMINAL
                assert result.current_status == ShipmentStatus.CANCELLED.value
                mock_crud.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_status_terminal_failed(self, mock_db):
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.FAILED,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                result = await update_shipment_tracking_status(ctx, shipment_id)

                assert result.status == TrackingUpdateStatusType.TERMINAL
                assert result.current_status == ShipmentStatus.FAILED.value
                mock_crud.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_shipment_not_found(self, mock_db):
        shipment_id = 999
        ctx = {"job_id": "test_job_123"}

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                result = await update_shipment_tracking_status(ctx, shipment_id)

                assert result.status == TrackingUpdateStatusType.NOT_FOUND
                assert result.shipment_id == shipment_id

    @pytest.mark.asyncio
    async def test_no_tracking_number(self, mock_db):
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number=None,
            status=ShipmentStatus.PENDING,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                result = await update_shipment_tracking_status(ctx, shipment_id)

                assert result.status == TrackingUpdateStatusType.NO_TRACKING
                assert result.shipment_id == shipment_id
                mock_crud.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_status_none_defaults_to_pending(self, mock_db):
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=None,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)
            mock_crud.update = AsyncMock(return_value=None)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                with patch("src.app.core.worker.functions.queue") as mock_queue:
                    mock_pool = Mock()
                    mock_pool.enqueue_job = AsyncMock()
                    mock_queue.pool = mock_pool

                    result = await update_shipment_tracking_status(ctx, shipment_id)

                    assert result.status == TrackingUpdateStatusType.UPDATED
                    assert result.new_status == ShipmentStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db):
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.PENDING,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)
            mock_crud.update = AsyncMock(side_effect=Exception("Database error"))

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                result = await update_shipment_tracking_status(ctx, shipment_id)

                assert result.status == TrackingUpdateStatusType.ERROR
                assert result.shipment_id == shipment_id
                assert result.error == "Database error"

    @pytest.mark.asyncio
    async def test_queue_pool_none_no_scheduling(self, mock_db):
        shipment_id = 1
        ctx = {"job_id": "test_job_123"}
        mock_shipment = Shipment(
            id=shipment_id,
            warehouse_id=1,
            ship_to_id=1,
            ship_from_id=2,
            tracking_number="TRACK123",
            status=ShipmentStatus.PROCESSING,
        )

        with patch("src.app.core.worker.functions.crud_shipments") as mock_crud:
            mock_crud.get = AsyncMock(return_value=mock_shipment)
            mock_crud.update = AsyncMock(return_value=None)

            with patch("src.app.core.worker.functions.local_session") as mock_session:
                mock_session.return_value.__aenter__.return_value = mock_db
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

                with patch("src.app.core.worker.functions.queue") as mock_queue:
                    mock_queue.pool = None

                    result = await update_shipment_tracking_status(ctx, shipment_id)

                    assert result.status == TrackingUpdateStatusType.UPDATED
                    mock_crud.update.assert_called_once()
