import json

from pandas import DataFrame


def toJson(df: DataFrame) -> str:
    return json.dumps(df.to_dict())