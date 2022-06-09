
from app.tasks.stockTasks import GetStockCodeFilteringByVarientRank, GetStockDayTask, GetMarcapCodes, GetStockCodeFilteringAltmanZScore
import luigi
import json
import pandas as pd
from app.service.TaskService import TaskService
from app.service.WalletService import WalletService
from app.utils.dateutils import getDateArr

# poetry run python -m pytest -s tests/test_taskService.py

def test_walletService() -> None:
    walletService = WalletService()
    walletService.walletLocalRepo.addUser("a")
    walletService.walletLocalRepo.addUser("b")

    user = walletService.getUsers()
    assert user is not None
    assert user[0] == "a"
    assert user[1] == "b"
    
    aWalletId = walletService.walletLocalRepo.addWallet("a", 200000.)
    bWalletId = walletService.walletLocalRepo.addWallet("b", 100000.)
    assert aWalletId is not None
    assert bWalletId is not None
    aWallet = walletService.getWallet("a", aWalletId)
    bWallet = walletService.getWallet("b", bWalletId)
    assert aWallet is not None
    assert aWallet.money == 200000.
    assert bWallet.money == 100000.

    walletService.walletLocalRepo.deposit("a", aWalletId, "20211123", 1000.)
    assert aWallet.money == 201000.
    walletService.walletLocalRepo.withdraw("b", bWalletId, "20111123", 1000.)
    assert bWallet.money == 99000.
    walletService.walletLocalRepo.buyStock("a", aWalletId, "20111231", "005930", 244., 10.)
    walletService.walletLocalRepo.buyStock("a", aWalletId, "20111231", "003490", 244., 10.)
    assert aWallet.stockBalance["005930"].code == "005930"
    assert aWallet.stockBalance["005930"].number == 244.
    walletService.walletLocalRepo.sellStock("a", aWalletId, "20111231", "005930", 144., 100.)
    assert aWallet.stockBalance["005930"].code == "005930"
    assert aWallet.stockBalance["005930"].number == 100.
    balance = walletService.calculateCurrentStockBalance("20151123", "a", aWalletId)
    print(balance)


# def test_taskService() -> None:
#     taskService = TaskService()
#     dateArr = getDateArr("20210101", "20220520")
#     taskService.simulate("20151123")
    



    
   
