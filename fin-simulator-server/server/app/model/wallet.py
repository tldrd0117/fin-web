from typing import Dict, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import IntEnum

#

class TrType(IntEnum):
    DEPOSIT = 1
    WITHDRAW = 2
    TRANSFER = 3
    STOCK_BUY = 3
    STOCK_SELL = 4

class TransactionRecord(BaseModel):
    transactionId: UUID = Field(default_factory=uuid4)
    date: str

class DepositRecord(TransactionRecord):
    walletId: UUID
    trType: int = Field(default=TrType.DEPOSIT)
    money: float


class WithdrawRecord(TransactionRecord):
    walletId: UUID
    trType: int = Field(default=TrType.WITHDRAW)
    money: float


class TransferRecord(TransactionRecord):
    trType: int = Field(default=TrType.TRANSFER)
    toWalletId: UUID
    fromWalletId: UUID
    money: float


class StockBuyRecord(TransactionRecord):
    walletId: UUID
    trType: int = Field(default=TrType.STOCK_BUY)
    code: str
    number: float
    current: float


class StockSellRecord(TransactionRecord):
    walletId: UUID
    trType: int = Field(default=TrType.STOCK_SELL)
    code: str
    number: float
    current: float


class StockBalance(BaseModel):
    code: str
    number: float

class CurrentStockBalance(StockBalance):
    total: float
    current: float

class TotalCurrentStockBalance(BaseModel):
    total: float
    currentStockBalance: Dict[str, CurrentStockBalance] = Field(default={})

class Wallet(BaseModel):
    walletId: UUID = Field(default_factory=uuid4)
    userId: str 
    money: float = 0
    stockBalance: Dict[str, StockBalance] = Field(default={})
    transactionRecordIds: List[str] = []

class User(BaseModel):
    userId: str
    wallets: Dict[str, Wallet] = Field(default={})

class Transactions(BaseModel):
    records: Dict[str, Dict] = Field(default={})