from unicodedata import category
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BuscaCotaSchema(BaseModel):
    cnpj: str  = None
    data_inicial: datetime = None
    data_final: datetime = None


class CotaViewSchema(BaseModel):
    cnpj: str = "01.496.940/0001-86"
    dt_comptc: datetime = datetime(2023,1,1)
    vl_cota:  float = 0.0
    captc_dia:  float = 0.0
    resg_dia: float = 0.0
    nr_cotst: int = 0

def apresenta_cota(cota):
     
    return {
        "cnpj": cota.cnpj,
        "dt_comptc": cota.dt_comptc,
        "vl_cota": cota.vl_cota,
        "captc_dia": cota.captc_dia,
        "resg_dia": cota.resg_dia,
        "nr_cotst": cota.nr_cotst
    }


class CotaListaViewSchema(BaseModel):
    cotas: List[CotaViewSchema]


def apresenta_lista_cotas(cotas):
    result = []
    for cota in cotas:
        result.append(apresenta_cota(cota))
    return {"cotas": result}
