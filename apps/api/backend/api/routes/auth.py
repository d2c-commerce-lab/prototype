from fastapi import APIRouter, status

from backend.schemas.auth import (
    LoginRequest,
    LoginResponse,
    SignupRequest, 
    SignupResponse
)
from backend.services.auth_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest) -> SignupResponse:
    user = create_user(payload)
    return SignupResponse(**user)

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest) -> LoginResponse:
    user = authenticate_user(payload)
    return LoginResponse(**user)