#!/usr/bin/env python3
"""
Database initialization script.
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base


def create_database():
    """Create the database if it doesn't exist."""
    # Extract database name from URL
    db_url_parts = settings.DATABASE_URL.split('/')
    db_name = db_url_parts[-1]
    base_url = '/'.join(db_url_parts[:-1])
    
    # Connect to postgres database to create our database
    engine = create_engine(f"{base_url}/postgres")
    
    with engine.connect() as conn:
        # Set autocommit mode
        conn.execute(text("COMMIT"))
        
        # Check if database exists
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
            {"db_name": db_name}
        )
        
        if not result.fetchone():
            print(f"Creating database: {db_name}")
            conn.execute(text(f"CREATE DATABASE {db_name}"))
        else:
            print(f"Database {db_name} already exists")


def init_database():
    """Initialize database with tables."""
    print("Initializing database...")
    
    # Create database if it doesn't exist
    create_database()
    
    # Create engine for our database
    engine = create_engine(settings.DATABASE_URL)
    
    # Enable extensions
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\""))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialization complete!")


if __name__ == "__main__":
    init_database()