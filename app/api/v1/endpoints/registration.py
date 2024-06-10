from app.services.user_service import create_user, activate_user
from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/register")
def register_user(user: UserCreate):
    db_user = create_user(user.email, user.password)
    return db_user


@router.post("/activate")
def activate_user_route(user_id: int, code: str):
    if activate_user(user_id, code):
        return {"message": "User activated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code"
        )
