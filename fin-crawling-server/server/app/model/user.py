from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class LoginUser(BaseModel):
    email: str
    password: str


class User(BaseModel):
    username: str
    email: str
    hashedJwtPassword: Optional[str] = None
    disabled: Optional[bool] = None
    salt: Optional[str] = None


class JoinUser(BaseModel):
    username: str
    email: str
    hashedPassword: Optional[str] = None
    salt: Optional[str] = None


class Token(BaseModel):
    accessToken: str
    tokenType: str


class TokenData(BaseModel):
    userId: Optional[str] = None

