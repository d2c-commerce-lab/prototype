from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    user_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    marketing_opt_in_yn: bool = False


class SignupResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    user_name: str
    user_status: str
    marketing_opt_in_yn: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class LoginResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    user_name: str
    user_status: str
    message: str