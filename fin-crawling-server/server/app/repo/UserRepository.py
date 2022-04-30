
from datetime import timedelta, datetime
from tkinter import Label
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.base.BaseComponent import BaseComponent
from app.datasource.UserDataSource import UserDataSource
from app.model.user import User, TokenData, Token, JoinUser
from dotenv import dotenv_values
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

config = dotenv_values('.env')

class UserRepository(BaseComponent):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    pwdContext: CryptContext
    PRIVATE_KEY: rsa.RSAPrivateKey


    def onComponentResisted(self) -> None:
        self.SECRET_KEY = config["SECRET_KEY"]
        self.ALGORITHM = config["ALGORITHM"]
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(config["ACCESS_TOKEN_EXPIRE_MINUTES"])
        self.pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.userd = self.get(UserDataSource)
        self.makePrivateKey()
        return super().onComponentResisted()
    

    def makePrivateKey(self):
        self.PRIVATE_KEY = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        print(self.PRIVATE_KEY.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode("utf-8"))
    
    def makePublicKey(self) -> str:
        publicKey =  self.PRIVATE_KEY.public_key()
        pem = publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        print(pem.decode("utf-8"))
        return pem.decode("utf-8")
    

    def decryptRSA(self, chipertext: str):
        chiperBytes = base64.b64decode(chipertext)
        return self.PRIVATE_KEY.decrypt(chiperBytes,
        padding=padding.PKCS1v15())

    
    def verifyPassword(self, plainPassword, hashedPassword):
        return self.pwdContext.verify(plainPassword, hashedPassword)
    
    def getPasswordHash(self, password):
        return self.pwdContext.hash(password)
    
    def getUser(self, userNameOrEmail):
        user = self.userd.getUser(userNameOrEmail)
        if user is None or len(user)<=0:
            user = self.userd.getUserFromUsername(userNameOrEmail)
        if user is not None and len(user)>0:
            user = user[0]
            return User(**{
                "username": user["username"],
                "email": user["email"],
                "hashedJwtPassword": user["hashedJwtPassword"],
                "disabled": user["disabled"],
                "salt": user["salt"], 
                "updatedAt": user["updatedAt"],
                "createdAt": user["createdAt"]
            })
    

    def isDupUser(self, user: User) -> bool:
        return self.userd.isDupUser(user)

    
    def joinUser(self, joinUser: JoinUser) -> str:
        user = User(**{
            "username": joinUser.username,
            "email": joinUser.email,
            "hashedJwtPassword": self.getPasswordHash(joinUser.hashedPassword),
            "disabled": False,
            "salt": joinUser.salt
        })
        print(user)
        return self.userd.updateUser(user)
    