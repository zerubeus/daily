from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.security import HTTPBasicCredentials

from app.schemas.user import UserCreate, UserActivate, UserResponse, ActivationResponse
from app.services.user_service import create_user, activate_user, get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register_user(request: Request, user: UserCreate):
    try:
        db_user = create_user(request, user.email, user.password)
        return UserResponse(
            id=db_user["id"], email=db_user["email"], is_active=db_user["is_active"]
        )
    except HTTPException as e:
        raise e


@router.post("/activate", response_model=ActivationResponse)
def activate_user_route(
    request: Request,
    user: UserActivate,
    credentials: HTTPBasicCredentials = Depends(get_current_user),
):
    try:
        if activate_user(request, user.user_id, user.code):
            return ActivationResponse(message="User activated successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired code",
            )
    except HTTPException as e:
        raise e
