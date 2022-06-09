from typing import List
from uuid import UUID
from matplotlib import use
import pandas as pd
from app.repo.WalletLocalRepository import WalletLocalRepository
from app.repo.MarcapRepository import MarcapRepository
from app.model.wallet import Wallet, TotalCurrentStockBalance, CurrentStockBalance
import json
import luigi
from app.tasks.stockTasks import GetStockDayTask

class WalletService(object):
    walletLocalRepo: WalletLocalRepository
    def __init__(self) -> None:
        self.walletLocalRepo = WalletLocalRepository()
        self.marcapRepo = MarcapRepository()
    
    def calculateCurrentStockBalance(self, date: str, userId: str, walletId: UUID):
        total = 0
        currentStockBalanceDict = {}
        wallet: Wallet = self.getWallet(userId=userId, walletId=walletId)
        df = self.marcapRepo.getMarcapByDate(date)
        print(df)
        for code in wallet.stockBalance.keys():
            row = df[df["code"]==code]["close"]
            if len(row) == 1:
                current = float(row.iloc[0])
                currentStockBalance = CurrentStockBalance(code=code, number=wallet.stockBalance[code].number, \
                    total=wallet.stockBalance[code].number * current,
                    current=current)
                currentStockBalanceDict[code] = currentStockBalance
                total = total + currentStockBalance.total
            elif len(row) == 0:
                raise Exception("current not Exist")
            else:
                raise Exception("current multiple row")
        totalCurrentStockBalance = TotalCurrentStockBalance(total=total, currentStockBalance=currentStockBalanceDict)
        return totalCurrentStockBalance
        
    def getUsers(self) -> List:
        return self.walletLocalRepo.getUsers()
    
    def getWallet(self, userId: str, walletId: UUID) -> Wallet:
        return self.walletLocalRepo.getWallet(userId=userId, walletId=walletId)
    
    def deposit(self, userId: str, walletId: str, date: str, money: float):
        self.walletLocalRepo.deposit(userId=userId, walletId=walletId, date=date, money=money)

    def withdraw(self, userId: str, walletId: str, date: str, money: float):
        self.walletLocalRepo.withdraw(userId= userId, walletId=walletId, date=date, money=money)

    def transfer(self, toUserId: str, fromUserId:str, toWalletId: str, fromWalletId:str, date: str, money: float):
        self.walletLocalRepo.transfer( \
            toUserId=toUserId, \
            fromUserId=fromUserId, \
            toWalletId=toWalletId, \
            fromWalletId=fromWalletId, \
            date=date, money=money)
    

    def buyStock(self, userId: str, walletId: str, date: str, code: str, number: float, current: float):
        self.walletLocalRepo.buyStock(userId=userId, walletId=walletId, date=date, code=code, number=number)
    

    def sellStock(self, userId: str, walletId: str, date: str, code: str, number: float, current: float):
        self.walletLocalRepo.sellStock(userId=userId, walletId=walletId, date=date, code=code, number=number, current=current)
        