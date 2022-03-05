from typing import Any
from pandas import DataFrame


def intersectCode(df1: Any, df2: DataFrame) -> DataFrame:
    if(isinstance(df1, list)):
        return df2[df2["code"].isin(df1)]
    elif(isinstance(df1, DataFrame)):
        return df1[df1["code"].isin(df2["code"])]
    return None


def op(df1: DataFrame, df2: DataFrame, op: str, name: str) -> str:
    df1 = intersectCode(df1, df2).reset_index(drop=True)
    df2 = intersectCode(df2, df1).reset_index(drop=True)
    if df1["code"].equals(df2["code"]):
        newDf = df1.copy()
        newDf["dataName"] = name
        if op == "+":
            newDf["dataValue"] = df1["dataValue"] + df2["dataValue"]
        elif op == "-":
            newDf["dataValue"] = df1["dataValue"] - df2["dataValue"]
        elif op == "*":
            newDf["dataValue"] = df1["dataValue"] * df2["dataValue"]
        elif op == "/":
            newDf["dataValue"] = df1["dataValue"] / df2["dataValue"]
        else:
            return DataFrame.empty
        return newDf
    else:
        return DataFrame.empty
