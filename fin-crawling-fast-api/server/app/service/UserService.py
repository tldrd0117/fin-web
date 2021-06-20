
from app.model.user import User, UserInDB
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.datasource.UserDataSource import fake_users_db


class UserService:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    
    def __init__(self) -> None:
        pass

    def get_user(self, db: dict, username: str) -> UserInDB:
        if username in db:
            user_dict = db[username]
            return UserInDB(**user_dict)
        
    def fake_hash_password(self, password: str) -> str:
        return "fakehashed" + password

    def fake_decode_token(self, token: str) -> UserInDB:
        # This doesn't provide any security at all
        # Check the next version
        user = self.get_user(fake_users_db, token)
        return user
    
    def check_token(self, token: str) -> bool:
        return self.get_user(fake_users_db, token) != None

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserInDB:
        user = self.fake_decode_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def get_current_active_user(self, current_user: User = Depends(get_current_user)) -> UserInDB:
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user.dict()
