from app.module.logger import Logger
from app.datasource.MongoDataSource import MongoDataSource
from app.model.user import User
import traceback
from app.util.DateUtils import getNow

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "tester": {
        "username": "tester",
        "full_name": "test er",
        "email": "tester@example.com",
        "hashed_password": "fakehashedtester00",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

class UserDataSource(MongoDataSource):
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logger("UserDataSource")
    

    def getUser(self, email: str):
        try:
            cursor = self.user.find({"email":email})
            return list(cursor)
        except:
            self.logger.error("getUser", traceback.format_exc())
    
    def getUserFromUsername(self, email: str):
        try:
            cursor = self.user.find({"username":email})
            return list(cursor)
        except:
            self.logger.error("getUser", traceback.format_exc())

    
    def isDupUser(self, user: User):
        result = self.user.find_one({"email": user.email})
        return result is not None


    def updateUser(self, user: User):
        try:
            userDict = user.dict()
            userDict["updatedAt"] =  getNow()
            result = self.user.update_one({
                "username": user.username,
                "email": user.email
            }, {
                "$set": userDict,
                "$setOnInsert": {"createdAt": getNow()}
            }, upsert=True)
            return str(result.upserted_id)
        except Exception:
            self.logger.error("updateUser", traceback.format_exc())
