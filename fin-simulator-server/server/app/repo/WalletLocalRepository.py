from typing import Dict, List
from uuid import UUID
from app.model.wallet import Wallet, DepositRecord, WithdrawRecord, User, StockBalance, \
    Transactions, TransactionRecord, TransferRecord, StockBuyRecord, StockSellRecord


class WalletLocalRepository():
    users: Dict[str, User] = {}
    transactions: Dict[str, Transactions] = {}
    def __init__(self) -> None:
        pass

    def getUsers(self) -> List:
        return list(self.users.keys())

    def addUser(self, userId: str):
        if userId in self.users:
            raise Exception("duplicate User")
        user: User = User(userId=userId)
        self.users[userId] = user


    def addWallet(self, userId: str, money: float = 0, stockBalance: Dict[str, StockBalance] = {}):
        if userId not in self.users:
            raise Exception("user not exist")
        wallet = Wallet(userId=userId, money=money, stockBalance=stockBalance)
        self.users[userId].wallets[str(wallet.walletId)] = wallet
        return wallet.walletId
    

    def getWallet(self, userId: str, walletId: UUID) -> Wallet:
        return self.users[userId].wallets[str(walletId)]
    

    def applyAddMoney(self, userId: str, walletId: UUID, money: float, trId: str):
        walletId = str(walletId)
        print(self.users[userId].wallets)
        if walletId not in self.users[userId].wallets:
            raise Exception("wallet not exist")
        wallet: Wallet = self.users[userId].wallets[walletId]
        if wallet.money + money < 0:
            raise Exception("not enough money")
        wallet.money = wallet.money + money
        wallet.transactionRecordIds.append(trId)
        self.users[userId].wallets[walletId] = wallet
    

    def applyAddStock(self, userId: str, walletId: UUID, code: str, number: float):
        walletId = str(walletId)
        if walletId not in self.users[userId].wallets:
            raise Exception("wallet not exist")
        wallet: Wallet = self.users[userId].wallets[walletId]
        if code not in wallet.stockBalance:
            wallet.stockBalance[code] = StockBalance(code=code, number=number)
        else:
            resultNumber = wallet.stockBalance[code].number + number
            if resultNumber < 0:
                raise Exception("not enough stock")
            wallet.stockBalance[code].number = wallet.stockBalance[code].number + number

    def applyAddTransaction(self, transaction: TransactionRecord, walletId: UUID):
        walletId = str(walletId)
        if walletId not in self.transactions:
            self.transactions[walletId] = Transactions()
        self.transactions[walletId].records[str(transaction.transactionId)] = transaction
    
    
    def deposit(self, userId: str, walletId: UUID, date: str, money: float):
        if userId not in self.users:
            raise Exception("user not exist")
        trRecord = DepositRecord(date=date, money=money, walletId=walletId)
        self.applyAddMoney(userId, walletId, money, trRecord.transactionId)
        self.applyAddTransaction(trRecord, walletId)
    

    def withdraw(self, userId: str, walletId: str, date: str, money: float):
        if userId not in self.users:
            raise Exception("user not exist")
        trRecord = WithdrawRecord(date=date, money=money, walletId=walletId)
        self.applyAddMoney(userId, walletId, -money, trRecord.transactionId)
        self.applyAddTransaction(trRecord, walletId)

    def transfer(self, toUserId: str, fromUserId:str, toWalletId: str, fromWalletId:str, date: str, money: float):
        if toUserId not in self.users:
            raise Exception("toUserId not exist")
        if fromUserId not in self.users:
            raise Exception("fromUserId not exist")
        trRecord = TransferRecord(date=date, toWalletId=toWalletId, fromWalletId=fromWalletId, money=money)
        self.applyAddMoney(toUserId, toWalletId, -money, trRecord.transactionId)
        self.applyAddMoney(fromUserId, fromWalletId, money, trRecord.transactionId)
        self.applyAddTransaction(trRecord, toWalletId)
        self.applyAddTransaction(trRecord, fromWalletId)
    

    def buyStock(self, userId: str, walletId: str, date: str, code: str, number: float, current: float):
        if userId not in self.users:
            raise Exception("user not exist")
        trRecord = StockBuyRecord(date=date, walletId=walletId, code=code, number=number, current=current)
        self.applyAddMoney(userId=userId, walletId=walletId, money=-number*current, trId=trRecord.transactionId)
        self.applyAddStock(userId=userId, walletId=walletId, code=code, number=number)
        self.applyAddTransaction(trRecord, walletId)
    

    def sellStock(self, userId: str, walletId: str, date: str, code: str, number: float, current: float):
        if userId not in self.users:
            raise Exception("user not exist")
        trRecord = StockSellRecord(date=date, walletId=walletId, code=code, number=number, current=current)
        self.applyAddMoney(userId=userId, walletId=walletId, money=number*current, trId=trRecord.transactionId)
        self.applyAddStock(userId=userId, walletId=walletId, code=code, number=-number)
        self.applyAddTransaction(trRecord, walletId)


