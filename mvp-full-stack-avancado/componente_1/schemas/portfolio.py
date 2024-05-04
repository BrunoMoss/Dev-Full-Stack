from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PortfolioSchema(BaseModel):
    """ Define como portfolio de usuário deve ser representado
    """
    id: int = 1
    asset: str = 'VALE'
    weight: float = 0
    start_date: datetime = datetime.today()
    end_date: datetime 


