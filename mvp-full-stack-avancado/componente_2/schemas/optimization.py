from pydantic import BaseModel


class OptimizatonSchema(BaseModel):
    """ Define como portfolio de usuário deve ser representado
    """
    vol: str = 'BAIXA'
    n_assets: float = 10
    


