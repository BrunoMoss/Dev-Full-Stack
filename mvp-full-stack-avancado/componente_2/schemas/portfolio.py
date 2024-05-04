from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class AssetSchema(BaseModel):
    """ Define como portfolio de usuário deve ser representado
    """
    asset: str = 'VALE'
    weight: float = 0
    start_date: datetime = datetime.today()

class PortfolioSchema(BaseModel):
    portfolio:List[AssetSchema]