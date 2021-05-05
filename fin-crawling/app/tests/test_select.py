from fin_crawling.data.StockMongoDataSource import StockMongoDataSource


def test() -> None:
    mongo = StockMongoDataSource(host="localhost", port="8082")
    print(mongo.selectCompleteTask())
