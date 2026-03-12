from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict
from jose import jwt
from typing import Annotated
from fastapi import Depends

from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    nombre: str


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    return jwt.encode(to_encode, settings.auth_secret_key, algorithm="HS256")


@router.post("/login", response_model=LoginResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authenticate the application and return a JWT token.
    Accepts application/x-www-form-urlencoded with username and password.
    """
    if (
        form_data.username != settings.auth_username
        or form_data.password != settings.auth_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(data={"sub": form_data.username})
    return LoginResponse(
        access_token=access_token,
        user_id=999,
        nombre="Admin Base Datos",
    )
