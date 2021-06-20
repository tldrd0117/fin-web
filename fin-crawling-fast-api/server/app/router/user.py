from typing import Dict
from fastapi import APIRouter

from app.model.user import User, UserInDB
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.datasource.UserDataSource import fake_users_db
from app.module.locator import Locator

from app.service.UserService import UserService


router = APIRouter(prefix="/user")
userService: UserService = Locator.getInstance().get(UserService)


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict:
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = userService.fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@router.get("/me")
async def read_users_me(current_user: User = Depends(userService.get_current_active_user)) -> UserInDB:
    return current_user
