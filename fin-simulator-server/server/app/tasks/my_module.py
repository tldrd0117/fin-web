
import luigi


# poetry run python -m luigi --module my_module MyTask --x 123 --y 456 --local-scheduler
class GetStockData(luigi.Task):
    startDate = luigi.IntParameter()
    endDate = luigi.IntParameter()

    def run(self) -> None:
        print(self.x + self.y)