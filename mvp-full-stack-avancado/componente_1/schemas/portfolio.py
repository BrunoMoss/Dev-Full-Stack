from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from collections import defaultdict

class PortfolioSchema(BaseModel):
    """ Define como portfolio de usuário deve ser representado
    """
    id_pk: int = 1
    id: int = 1
    asset: str = 'VALE'
    weight: float = 0
    start_date: datetime = datetime.today()
    end_date: datetime 

class QueryPortfolio(BaseModel):
    """ Define os como a consulta a um portfolio é feita. 
    """
    id_portfolio:Optional[int] = 1
    start_date:Optional[datetime] = None
    end_date: Optional[datetime] = None

class PortfolioBodySchema(BaseModel):
    """ Define os dados a serem inseridos na criação de um portfolio simples
    """
    asset: str = 'VALE'
    weight: float = 0
   

class PortfolioBodyJsonSchema(BaseModel):
    """ Define os dados a serem inseridos na criação de um portfolio complexo
    """
    portifolio:List[PortfolioBodySchema]

class PortfolioDeleteSchema(BaseModel):
    """ Deleção de portfolio de um usuário por id.
    """
    id_portfolio:int =1


class PortfolioUpdateSchema(BaseModel):
    """ Define será a estrutura de busca por ID
    """
    close:bool = False
    portfolios:List[PortfolioSchema]

class PortfolioViewSchema(BaseModel):
    """ Define será a estrutura de visualização do portfolio
    """
    portfolios:List[PortfolioSchema]


class OptimizatonSchema(BaseModel):
    """ Define os parêmetros da otimização
    """
    opt_parameter: str = 'SQQQ,SPY,FXI'

def apresenta_lista_portfolios(portfolios):

    # Dicionário temporário para agrupar por CNPJ e dt_comptc
    temp_dict = defaultdict(list)

    # Agrupamento dos itens no dicionário temporário
    for item in portfolios:
        key = (item.id)
        temp_dict[key].append({
            "asset": item.asset,
            "weight":item.weight,
            "start_date":item.start_date,
            "end_date":item.end_date
        })

    # Transformação para a segunda estrutura
    lista_transformada = [
        {
            "id":id,
            "portifolio":portfolio
        }
        for (id), portfolio in temp_dict.items()
    ]

    return {"portfolios": lista_transformada}
