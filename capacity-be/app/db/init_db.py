"""
Database initialization module
Handles automatic database schema creation and migration on startup
"""

import logging
from typing import Optional
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.core.config import settings
from app.db.base import engine

logger = logging.getLogger(__name__)


def check_database_exists() -> bool:
    """Check if the database exists and is accessible"""
    try:
        with engine.connect() as connection:
            # Try a simple query to verify database connection
            connection.execute(sa.text("SELECT 1"))
            return True
    except (OperationalError, ProgrammingError) as e:
        logger.warning(f"Database connection failed: {e}")
        return False


def check_tables_exist() -> bool:
    """Check if required tables exist in the database"""
    try:
        from app.db.base import Base

        # Check if at least the alembic_version table exists
        inspector = sa.inspect(engine)
        existing_tables = inspector.get_table_names()

        if 'alembic_version' not in existing_tables:
            logger.info("Alembic version table not found - database appears to be uninitialized")
            return False

        # Check if our main tables exist
        required_tables = ['members', 'sprints', 'pto', 'holidays']
        missing_tables = [table for table in required_tables if table not in existing_tables]

        if missing_tables:
            logger.info(f"Missing tables detected: {missing_tables}")
            return False

        logger.info("All required tables found in database")
        return True

    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        return False


def run_alembic_upgrade() -> bool:
    """Run Alembic upgrade to head"""
    try:
        # Get the alembic.ini path
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to capacity-be directory where alembic.ini is located
        alembic_ini_path = os.path.join(current_dir, '..', '..', 'alembic.ini')

        if not os.path.exists(alembic_ini_path):
            logger.error(f"Alembic config file not found at: {alembic_ini_path}")
            return False

        # Create alembic config
        alembic_cfg = Config(alembic_ini_path)

        # Override the sqlalchemy.url with our current setting
        alembic_cfg.set_main_option("sqlalchemy.url", settings.MYSQL_URL)

        # Run the upgrade
        logger.info("Running Alembic upgrade to head...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic upgrade completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error running Alembic upgrade: {e}")
        return False


def init_database() -> bool:
    """
    Initialize the database by running migrations if needed
    Returns True if initialization was successful, False otherwise
    """
    logger.info("Starting database initialization...")

    # Check if database is accessible
    if not check_database_exists():
        logger.error("Cannot connect to database - initialization failed")
        return False

    # Check if tables exist
    if check_tables_exist():
        logger.info("Database tables already exist - skipping initialization")
        return True

    # Run migrations
    logger.info("Database tables missing - running Alembic migrations...")
    if run_alembic_upgrade():
        logger.info("Database initialization completed successfully")
        return True
    else:
        logger.error("Database initialization failed")
        return False


def ensure_database_ready() -> None:
    """
    Ensure database is ready for use
    This function should be called during application startup
    """
    logger.info("Ensuring database is ready...")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            if init_database():
                logger.info("Database is ready for use")
                return
            else:
                logger.warning(f"Database initialization attempt {attempt + 1} failed")

        except Exception as e:
            logger.error(f"Database initialization attempt {attempt + 1} failed with error: {e}")

        if attempt < max_retries - 1:
            import time
            logger.info(f"Retrying in 2 seconds... (attempt {attempt + 2}/{max_retries})")
            time.sleep(2)

    logger.error("Failed to initialize database after all attempts")
    raise RuntimeError("Database initialization failed - cannot start application")
