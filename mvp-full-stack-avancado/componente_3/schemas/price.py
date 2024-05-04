from pydantic import BaseModel
from datetime import datetime,timedelta
from typing import Optional, List
from collections import defaultdict

class PriceSchema(BaseModel):
    """ Define como um preço a ser inserido deve ser representado.
    """
    asset_id: str = '1'
    price: float = 0.0
    date: datetime = datetime.today()
    
class PriceFormSchema(BaseModel):
    """ Define o input para a inserção de preços na base.
    """
    n: int = 10
    page:int = 1

class PriceQuerySchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita com base nos n ativos mais negociados ou uma lista.
    """
    n: int = 5
    assets:Optional[str] = None
    start_date:datetime = datetime.today() - timedelta(days=252)
    end_date :datetime = datetime.today()

class PriceAddSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma 
    requisição para inserir um dado
    """
    message: str
    n: int

class PriceViewSchema(BaseModel):
    """ Define como um preço a será exibido.
    """
    date:datetime = datetime.today()
    price: float = 0.0
   
class PriceListViewSchema(BaseModel):
    ticker: str = 'SQQQ'
    prices:List[PriceViewSchema]

class PriceDataViewSchema(BaseModel):
    prices_data:List[PriceListViewSchema]

class AssetViewSchema(BaseModel):
    asset: List[str]

class AssetQuerySchema(BaseModel):
    n:int

def apresenta_lista_precos(asset_prices):

    # Transformação para a segunda estrutura
    lista_transformada = [
        {
            "asset": asset.ticker,
            "prices":[{"date":p.date,"price":p.price} for p in asset.prices]
        }
        for asset in asset_prices
    ]

    return {"all_prices": lista_transformada}
