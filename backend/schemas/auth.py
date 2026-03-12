from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = {
        "from_attributes": True
    }
