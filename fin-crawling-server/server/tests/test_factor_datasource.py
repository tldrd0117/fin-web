from app.datasource.FactorFileDataSource import FactorFileDataSource


# pytest -s test_factor_datasource.py
def test():
    factorFileDataSource = FactorFileDataSource()
    print(factorFileDataSource.loadFactorMerge())
    # factorFileDataSource.loadFactorMerge()

