
from typing_extensions import Final
from pymitter import EventEmitter
from app.module.logger import Logger
from app.model.dto import FactorRunCrawling
import pandas as pd
from pathlib import Path
import os.path

EVENT_FACTOR_CRAWLING_ON_RESULT_OF_FACTOR: Final = "factorCrawler/onResultOfFactor"


class FactorCrawler(object):
    def __init__(self) -> None:
        self.ee = EventEmitter()
        # self.logger = Logger("MarcapCrawler")
    
    def crawling(self, dto: FactorRunCrawling) -> None:
        year = dto.year
        upCodes = ['제조업']
        factors = ['당기순이익', '영업활동으로인한현금흐름', '투자활동으로인한현금흐름', '재무활동으로인한현금흐름', '당기순이익률', '영업이익률', '매출총이익률', '배당수익률', '매출액', '자산', '유동자산', '부채', '유동부채', '이익잉여금', 'roe', 'ebit', 'eps']
        # factors = ['per', 'pcr', 'pbr', 'roe', '당기순이익', '영업활동으로인한현금흐름', '투자활동으로인한현금흐름', '재무활동으로인한현금흐름', 'psr', 'roic', 'eps', 'ebit', 'ev_ebit', 'ev_sales', 'ev_ebitda', '당기순이익률', '영업이익률', '매출총이익률', '배당수익률', '매출액', '자산', '유동자산', '부채', '유동부채', '이익잉여금']
        factorDf = pd.DataFrame()
        for upCode in upCodes:
            for factor in factors:
                path = Path('../app/static/factors/'+str(year)+'/'+upCode+'_'+factor+'.xlsx')
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
                df["factor"] = factor
                factorDf = factorDf.append(df)
                # df = df.set_index("종목코드")
                
                # if factor not in dfs:
                    # dfs[factor] = pd.DataFrame()
                # factorDf.loc[factor] = df
                # dfs[factor] = pd.concat([dfs[factor], df])
        factorDf = factorDf.melt(id_vars=["종목코드", "종목명", "결산월", "단위", "데이터명"],
                    var_name="year", value_name="데이터값")
        self.ee.emit(EVENT_FACTOR_CRAWLING_ON_RESULT_OF_FACTOR, factorDf.to_dict("records"))