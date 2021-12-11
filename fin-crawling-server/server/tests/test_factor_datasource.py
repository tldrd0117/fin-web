from app.datasource.FactorFileDataSource import FactorFileDataSource
import asyncio


async def getFactorsInFile():
    factorFileDataSource = FactorFileDataSource()
    data = await asyncio.create_task(factorFileDataSource.loadFactorMerge())
    print(data)


# pytest -s test_factor_datasource.py
def test():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(getFactorsInFile())
    loop.close()

