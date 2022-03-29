import asyncio
from typing import List
import pandas as pd
from pathlib import Path
import os.path
import sys
from app.base.BaseComponent import BaseComponent


class FactorFileDataSource:
    def __init__(self) -> None:
        super().__init__()

    async def loadFactorMerge(self) -> List:
        factor1 = await asyncio.create_task(self.loadFactor(2018))
        factor2 = await asyncio.create_task(self.loadFactor(2019))
        beforeFactor = factor1[factor1["년"] <= 2009]
        afterFactor = factor2[factor2["년"] > 2009]
        return pd.concat([beforeFactor, afterFactor]).sort_values(["년", "데이터명"]).to_dict("records")

    async def loadFactor(self, year: int) -> pd.DataFrame:
        upCodes = ['제조업']
        factors = ['당기순이익', '영업활동으로인한현금흐름', '투자활동으로인한현금흐름', '재무활동으로인한현금흐름', '당기순이익률', '영업이익률', '매출총이익률', '배당수익률', '매출액', '자산', '유동자산', '부채', '유동부채', '이익잉여금', 'roe', 'ebit', 'eps']
        # factors = ['per', 'pcr', 'pbr', 'roe', '당기순이익', '영업활동으로인한현금흐름', '투자활동으로인한현금흐름', '재무활동으로인한현금흐름', 'psr', 'roic', 'eps', 'ebit', 'ev_ebit', 'ev_sales', 'ev_ebitda', 
        # '당기순이익률', '영업이익률', '매출총이익률', '배당수익률', '매출액', '자산', '유동자산', '부채', '유동부채', '이익잉여금']
        factorDf: pd.DataFrame = pd.DataFrame()
        for upCode in upCodes:
            for factor in factors:
                df = await asyncio.create_task(self.loadFactorOneFile(year, upCode, factor))
                factorDf = factorDf.append(df)
        factorDf = factorDf.melt(id_vars=["종목코드", "종목명", "결산월", "단위", "데이터명"], var_name="년", value_name="데이터값")
        return factorDf
    
    async def loadFactorOneFile(self, year: int, upCode: str, factor: str) -> pd.DataFrame:
        if "pytest" in sys.modules:
            path = Path('../app/static/factors/'+str(year)+'/'+upCode+'_'+factor+'.xlsx')
        else:
            path = Path('app/static/factors/'+str(year)+'/'+upCode+'_'+factor+'.xlsx')
        print(path.resolve())
        print(os.path.dirname(__file__))
        name = path.resolve()
        # 'static/factors/'+str(year)+'/'+upCode+'_'+factor+'.xlsx'
        df = pd.read_excel(name, sheet_name='계정별 기업 비교 - 특정계정과목', skiprows=8)
        coli = list(df.iloc[0])
        print(coli)
        for i in range(len(coli)):
            if i >= 4:
                coli[i] = float(coli[i])
        df.columns = coli
        df = df.drop([0])
        df["데이터명"] = factor
        return df
    