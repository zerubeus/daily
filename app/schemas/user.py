from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserActivate(BaseModel):
    user_id: int
    code: constr(min_length=4, max_length=4)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool


class ActivationResponse(BaseModel):
    message: str
