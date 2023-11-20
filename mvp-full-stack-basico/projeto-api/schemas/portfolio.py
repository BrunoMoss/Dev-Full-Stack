from unicodedata import category
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BuscaPortfolioSchema(BaseModel):
    cnpj: str  = None
    data_inicial: datetime = None
    data_final: datetime = None


class PortfolioViewSchema(BaseModel):
    cnpj: str = "01.496.940/0001-86"
    dt_comptc: datetime = datetime(2023,1,1)
    cd_ativo: str = "PETR4"
    qtd_negociada:  float = 0.0
    vl_negociado: float = 0.0
    qt_pos_final: float = 0.0
    vl_merc_pos_final: float = 0.0

def apresenta_portfolio(portfolio):
     
    return {
        "cnpj": portfolio.cnpj,
        "dt_comptc": portfolio.dt_comptc,
        "vl_cota": portfolio.vl_cota,
        "captc_dia": portfolio.captc_dia,
        "resg_dia": portfolio.resg_dia,
        "nr_cotst": portfolio.nr_cotst
    }


class PortfolioListaViewSchema(BaseModel):
    cotas: List[CotaViewSchema]


def apresenta_lista_portfolio(portfolios):
    result = []
    for portfolio in portfolios:
        result.append(apresenta_portfolio(portfolio))
    return {"portfolios": result}
