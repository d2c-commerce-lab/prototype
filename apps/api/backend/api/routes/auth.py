from fastapi import APIRouter, status

from backend.schemas.auth import SignupRequest, SignupResponse
from backend.services.auth_service import create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest) -> SignupResponse:
    user = create_user(payload)
    return SignupResponse(**user)