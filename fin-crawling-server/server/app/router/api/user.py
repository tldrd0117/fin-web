from typing import Dict
from fastapi import APIRouter

from app.model.user import User, Token, JoinUser
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.datasource.UserDataSource import fake_users_db
from app.module.locator import Locator

from app.service.api.UserApiService import UserApiService
from app.module.logger import Logger


router = APIRouter(prefix="/user")
userService: UserApiService = Locator.getInstance().get(UserApiService)
logger = Logger("UserRouter")


@router.post("/publicKey")
async def getPublicKey():
    return await userService.getPublicKey()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await userService.loginForAccessToken(form_data)


@router.post("/join")
async def join(user: JoinUser):
    logger.info("join", user.dict())
    return await userService.joinUser(user)


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(userService.getCurrentActiveUser)):
    return current_user
