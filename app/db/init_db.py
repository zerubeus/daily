from app.core.logging import logger
from app.db.connection import get_db


def create_tables(conn=None):
    if not conn:
        conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT FALSE
        );
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

        CREATE TABLE IF NOT EXISTS activation_codes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            code VARCHAR(4) NOT NULL,
            is_used BOOLEAN DEFAULT FALSE,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        CREATE INDEX IF NOT EXISTS idx_activation_codes_user_id ON activation_codes(user_id);
        CREATE INDEX IF NOT EXISTS idx_activation_codes_code ON activation_codes(code);
        """
        )
        conn.commit()
        logger.info("Tables created successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating tables: {e}")
        raise
    finally:
        cur.close()
        conn.close()
