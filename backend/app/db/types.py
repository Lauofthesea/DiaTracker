"""
Database type compatibility utilities.

Provides cross-database type support for PostgreSQL and SQLite.
"""

from sqlalchemy import JSON, TypeDecorator, Text
from sqlalchemy.dialects.postgresql import JSONB as PostgreSQL_JSONB, UUID as PostgreSQL_UUID, ARRAY as PostgreSQL_ARRAY
from sqlalchemy.types import String
import uuid
import json as json_module


class JSONB(TypeDecorator):
    """
    Cross-database JSON type that uses JSONB for PostgreSQL and JSON for SQLite.
    """
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgreSQL_JSONB())
        else:
            return dialect.type_descriptor(JSON())


class UUID(TypeDecorator):
    """
    Cross-database UUID type that uses UUID for PostgreSQL and String for SQLite.
    """
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgreSQL_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, str):
                return uuid.UUID(value)
            return value


class ARRAY(TypeDecorator):
    """
    Cross-database ARRAY type that uses ARRAY for PostgreSQL and JSON for SQLite.
    """
    impl = Text
    cache_ok = True

    def __init__(self, item_type=None):
        self.item_type = item_type
        super().__init__()

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgreSQL_ARRAY(self.item_type or Text))
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            # Store as JSON string for SQLite
            return json_module.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            # Parse JSON string for SQLite
            if isinstance(value, str):
                return json_module.loads(value)
            return value
