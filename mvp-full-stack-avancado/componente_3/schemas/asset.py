from pydantic import BaseModel
from datetime import datetime,timedelta
from typing import Optional, List
from collections import defaultdict

class AssetSchema(BaseModel):
    """ Define como um ativo a ser inserido deve ser representado.
    """
    id : int = 1
    ticker :str = 'SQQQ'
    asset_name : str = 'ProShares UltraPro Short QQQ'
    avg_volume :float = 1000000.00
    insert_date : datetime = datetime.today()

class AssetAddSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma 
    requisição para inserir um dado
    """
    message: str
    n: int

class AssetFormSchema(BaseModel):
    """ Define o input para a inserção de ativos na base.
    """
    n: int = 10