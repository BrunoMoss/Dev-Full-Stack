from pydantic import BaseModel
from typing import Optional, List
from models.user import User
from collections import defaultdict
from schemas.portfolio import PortfolioSchema


class UserSchema(BaseModel):
    """ Define como um novo usuário a ser inserido deve ser representado
    """
    name: str = "Bruno"
    email: str = "bruno@gmail.com"
    username: str = "bmoss"
    password: str = "123456"


class UserViewSchema(BaseModel):
    """ Define como um novo usuário a ser inserido deve ser representado
    """
    name: str = "Bruno"
    email: str = "bruno@gmail.com"
    username: str = "bmoss"
    password: str = "123456"
    portfolios:List[PortfolioSchema]

class UserPathSchema(BaseModel):
    """Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no username do usuário.
    """
    username:str = "bmoss"

class UserLoginSchema(BaseModel):
    """Define como deve ser a estrutura que representa o login. 
    """
    username:str = "bmoss"
    password:str = "123456"

def lista_usuario(user: User):
    """ Retorna uma representação do usuario seguindo o schema definido em
        UsuarioViewSchema.
    """
    
    portfolio_por_data = defaultdict(list)

    # Agrupar os objetos por data
    for obj in user.portfolios:
        portfolio_por_data[obj.id].append(obj)

    # Converter o dicionário em uma lista de JSON
    json_portfolio =[]
    for data, objs in portfolio_por_data.items():
        json_portfolio.append({"portfolio_id": data, "portfolio": [p.to_dict() for p in objs]})

    return {
        "user_id": user.id,
        "usename": user.username,
        "email": user.email,
        "data_criacao": user.dt_insert,
        "total_portfolios": len(json_portfolio),
        "portfolio": json_portfolio
    }
