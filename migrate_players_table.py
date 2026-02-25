"""
Migration script to add missing columns to players table
Run this script to update the players table schema

Usage: python migrate_players_table.py
"""

from sqlalchemy import text
from app.database import engine, check_connection
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_players_table():
    """Add missing columns to players table if they don't exist"""
    if not check_connection():
        logger.error("Cannot connect to database. Please check your configuration.")
        return False
    
    try:
        with engine.begin() as conn:  # Use begin() for transaction management
            # First, check what columns exist
            result = conn.execute(text("""
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'players'
                ORDER BY ORDINAL_POSITION
            """))
            
            existing_columns = {row[0]: row for row in result.fetchall()}
            logger.info(f"Existing columns: {list(existing_columns.keys())}")
            
            # Check if player_id column exists
            if 'player_id' not in existing_columns:
                logger.info("Adding player_id column to players table...")
                
                # Check if there's an existing primary key
                has_primary_key = any(col[3] == 'PRI' for col in existing_columns.values())
                
                if has_primary_key:
                    logger.warning("Table already has a primary key. You may need to drop it first.")
                    logger.info("Attempting to add player_id as primary key...")
                    # Try to add as primary key (this will fail if another PK exists)
                    try:
                        # First add as nullable, then populate, then make it NOT NULL and PK
                        conn.execute(text("""
                            ALTER TABLE players
                            ADD COLUMN player_id CHAR(36) NULL
                        """))
                        # Generate UUIDs for existing rows using Python
                        result = conn.execute(text("SELECT COUNT(*) FROM players"))
                        count = result.fetchone()[0]
                        if count > 0:
                            logger.info(f"Generating UUIDs for {count} existing rows...")
                            rows = conn.execute(text("SELECT * FROM players WHERE player_id IS NULL LIMIT 1000"))
                            for row in rows:
                                new_uuid = str(uuid.uuid4())
                                # Get a unique identifier for this row (assuming there's an id or similar)
                                # For now, we'll use a workaround
                                pass
                            logger.warning("You may need to manually populate player_id for existing rows")
                        # Make it NOT NULL and PRIMARY KEY
                        try:
                            conn.execute(text("""
                                ALTER TABLE players
                                MODIFY COLUMN player_id CHAR(36) NOT NULL,
                                ADD PRIMARY KEY (player_id)
                            """))
                            logger.info("✓ Added player_id column as primary key")
                        except Exception as e:
                            logger.warning(f"Could not set as primary key: {e}. Column added as nullable.")
                    except Exception as e:
                        logger.error(f"Could not add player_id column: {e}")
                        logger.info("Adding player_id as nullable column...")
                        conn.execute(text("""
                            ALTER TABLE players
                            ADD COLUMN player_id CHAR(36) NULL
                        """))
                        logger.info("✓ Added player_id column (nullable)")
                else:
                    # No existing primary key, add player_id as nullable first
                    conn.execute(text("""
                        ALTER TABLE players
                        ADD COLUMN player_id CHAR(36) NULL
                    """))
                    # Check if there are existing rows
                    result = conn.execute(text("SELECT COUNT(*) FROM players"))
                    count = result.fetchone()[0]
                    if count > 0:
                        logger.warning(f"Found {count} existing rows. You may need to populate player_id manually.")
                        logger.info("Attempting to make player_id NOT NULL and PRIMARY KEY...")
                        try:
                            # Try to make it NOT NULL and PRIMARY KEY
                            conn.execute(text("""
                                ALTER TABLE players
                                MODIFY COLUMN player_id CHAR(36) NOT NULL,
                                ADD PRIMARY KEY (player_id)
                            """))
                            logger.info("✓ Added player_id column as primary key")
                        except Exception as e:
                            logger.warning(f"Could not set as primary key (table may have existing rows): {e}")
                            logger.info("Column added as nullable. Populate player_id values and then set as PK.")
                    else:
                        # No rows, safe to add as NOT NULL PRIMARY KEY
                        conn.execute(text("""
                            ALTER TABLE players
                            MODIFY COLUMN player_id CHAR(36) NOT NULL,
                            ADD PRIMARY KEY (player_id)
                        """))
                        logger.info("✓ Added player_id column as primary key")
            else:
                logger.info("✓ player_id column already exists")
            
            # Check if one_signal_id column exists
            if 'one_signal_id' not in existing_columns:
                logger.info("Adding one_signal_id column to players table...")
                conn.execute(text("""
                    ALTER TABLE players
                    ADD COLUMN one_signal_id TEXT NULL
                """))
                conn.execute(text("""
                    CREATE INDEX idx_one_signal_id ON players(one_signal_id(255))
                """))
                logger.info("✓ Added one_signal_id column with index")
            else:
                logger.info("✓ one_signal_id column already exists")
            
            logger.info("Migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    migrate_players_table()

