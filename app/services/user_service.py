import random
from datetime import datetime, timedelta

from fastapi import HTTPException, Request, Depends, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from psycopg2.errors import UniqueViolation

from app.core.logging import logger
from app.core.redis import redis_client
from app.core.security import hash_password, verify_password
from app.db.connection import get_db
from app.services.smtp_client_service import send_email

security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, email, hashed_password FROM users WHERE email = %s",
            (credentials.username,),
        )
        user = cur.fetchone()
        if user is None or not verify_password(
            credentials.password, user["hashed_password"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    finally:
        cur.close()


def create_user(request: Request, email: str, password: str):
    hashed_password = hash_password(password)
    conn = request.state.db
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (email, hashed_password) VALUES (%s, %s) RETURNING id, email, is_active",
            (email, hashed_password),
        )
        user = cur.fetchone()
        conn.commit()
        logger.info(f"User created with email: {email}")
        send_activation_code(request, user["id"], email)
        return user
    except UniqueViolation as e:
        conn.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        cur.close()


def send_activation_code(request: Request, user_id: int, email: str):
    code = f"{random.randint(1000, 9999)}"
    expires_at = datetime.utcnow() + timedelta(minutes=1)
    conn = request.state.db
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO activation_codes (user_id, code, is_used, expires_at) VALUES (%s, %s, %s, %s)",
            (user_id, code, False, expires_at),
        )
        conn.commit()
        redis_client.setex(f"activation_code:{user_id}", timedelta(minutes=1), code)
        send_email(email, code)
        logger.info(f"Activation code sent to user_id: {user_id}, email: {email}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error sending activation code: {e}")
        raise
    finally:
        cur.close()


def activate_user(request: Request, user_id: int, code: str):
    stored_code = redis_client.get(f"activation_code:{user_id}")
    if stored_code and stored_code.decode("utf-8") == code:
        conn = request.state.db
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT expires_at FROM activation_codes WHERE user_id = %s AND code = %s AND is_used = FALSE",
                (user_id, code),
            )
            result = cur.fetchone()

            if result and datetime.utcnow() <= result["expires_at"]:
                cur.execute(
                    "UPDATE users SET is_active = TRUE WHERE id = %s", (user_id,)
                )
                cur.execute(
                    "UPDATE activation_codes SET is_used = TRUE WHERE user_id = %s AND code = %s",
                    (user_id, code),
                )
                conn.commit()
                redis_client.delete(f"activation_code:{user_id}")
                logger.info(f"User activated with user_id: {user_id}")
                return True
            else:
                logger.warning(
                    f"Activation code expired or invalid for user_id: {user_id}"
                )
                return False
        except Exception as e:
            conn.rollback()
            logger.error(f"Error activating user: {e}")
            raise
        finally:
            cur.close()
    logger.warning(f"Invalid activation code for user_id: {user_id}")
    return False
