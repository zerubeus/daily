from fastapi import Request, Response, FastAPI

from app.api.v1.endpoints import registration
from app.core.logging import logger
from app.db.connection import get_db, close_db_connection
from app.db.init_db import create_tables
from app.exceptions.custom_exceptions import DatabaseConnectionError

app = FastAPI()


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = get_db()
        response = await call_next(request)
    except DatabaseConnectionError as e:
        response = Response(f"Database connection failed: {e}", status_code=500)
    finally:
        close_db_connection(request.state.db)
    return response


app.include_router(registration.router, prefix="/api/v1", tags=["registration"])


@app.on_event("startup")
def on_startup():
    create_tables()
    logger.info("Application startup: tables created")
