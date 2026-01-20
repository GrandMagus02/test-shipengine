.PHONY: migration-create migration-apply

# Generate a new migration
migration-create:
	POSTGRES_SERVER=localhost uv run alembic revision --autogenerate

# Apply migrations to the database
migration-apply:
	POSTGRES_SERVER=localhost uv run alembic upgrade head
