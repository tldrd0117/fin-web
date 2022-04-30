
from datetime import timedelta, datetime
import email
from typing import Optional

from aiohttp import WebSocketError
from app.model.user import User, LoginUser, TokenData, JoinUser
from fastapi import Depends, Form, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.datasource.UserDataSource import fake_users_db
from app.repo.UserRepository import UserRepository
from app.base.BaseComponent import BaseComponent
from app.module.logger import Logger
from jose import JWTError, jwt
from hashlib import pbkdf2_hmac


oauth2Scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserApiService(BaseComponent):
    userRepository: UserRepository
    def onComponentResisted(self) -> None:
        self.userRepository = self.get(UserRepository)
        self.logger = Logger("UserApiService")
        return super().onComponentResisted()
    
    def createAccessToken(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.userRepository.SECRET_KEY, algorithm=self.userRepository.ALGORITHM)
        return encoded_jwt
    
    def authenticateUser(self, email: str, password: str):
        user = self.userRepository.getUser(email)
        if not user:
            return False
        # pwd: bytes = pbkdf2_hmac("sha256", password.encode("utf-8"), user.salt.encode("utf-8"), iterations=1)
        if not self.userRepository.verifyPassword(password, user.hashedJwtPassword):
            return False
        return user
    
    async def getCurrentUser(self, token: str = Depends(oauth2Scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token,self.userRepository.SECRET_KEY, algorithms=[self.userRepository.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = self.userRepository.getUser(email)
        if user is None:
            raise credentials_exception
        return user

    async def getCurrentActiveUser(self, current_user: User = Depends(getCurrentUser)) -> User:
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user.dict()
    
    async def validateToken(self, token: str = Query(None)):
        credentials_exception = WebSocketError(1008, "token invalid")
        credentials_exception2 = WebSocketError(1008, "inactive User")
        try:
            payload = jwt.decode(token, self.userRepository.SECRET_KEY, algorithms=[self.userRepository.ALGORITHM])
            userNameOrEmail: str = payload.get("sub")
            if userNameOrEmail is None:
                raise credentials_exception
            tokenData = TokenData(userId= userNameOrEmail)
        except JWTError:
            raise credentials_exception
        user = self.userRepository.getUser(userNameOrEmail=tokenData.userId)
        if user is None:
            raise credentials_exception
        if user.disabled:
            raise credentials_exception2
        return user

    
    async def loginForAccessToken(self, form: OAuth2PasswordRequestForm):
        loginUser = LoginUser(**{
            "email": form.username,
            "password": self.userRepository.decryptRSA(form.password)
        })
        user = self.authenticateUser(loginUser.email, loginUser.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=self.userRepository.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.createAccessToken(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"accessToken": access_token, "tokenType": "bearer"}
    

    async def getPublicKey(self):
        return {"publicKey": self.userRepository.makePublicKey()}
    

    async def joinUser(self, joinUser: JoinUser):
        return self.userRepository.joinUser(joinUser)
    

    async def isDupUser(self, user: User):
        return self.userRepository.isDupUser(user)
    



    
