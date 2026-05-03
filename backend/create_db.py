"""
Script to create the database if it doesn't exist.
Run this before running Alembic migrations.
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connection parameters
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ml_diabetes_tracker"

def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server (default 'postgres' database)
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"✓ Database '{DB_NAME}' created successfully!")
        else:
            print(f"✓ Database '{DB_NAME}' already exists.")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Creating database...")
    if create_database():
        print("\nYou can now run: python -m alembic upgrade head")
    else:
        print("\nFailed to create database. Please check your PostgreSQL connection.")
