from sqlalchemy import Column, String, Integer, DateTime, ForeignKey,Float
from sqlalchemy.orm import relationship
from sqlalchemy.schema import PrimaryKeyConstraint
from datetime import datetime
from typing import Union

from  models import Base, User


class Portfolio(Base):

    __tablename__ = 'portfolio'

    id = Column(Integer, primary_key=True)
    asset = Column(String(50),primary_key=True)
    weight = Column(Float,nullable=False)
    start_date = Column(DateTime,nullable=False)
    end_date = Column(DateTime)
    data_insercao = Column(DateTime, default=datetime.now())

    # Definição do relacionamento entre o portfolio e um usuário.
    user_id = Column(Integer, ForeignKey("users.pk_user"), nullable=False)
    

    # Criando um requisito de unicidade envolvendo uma par de informações
    __table_args__ = (PrimaryKeyConstraint("id", "asset", name="port_composite_key"),)

    user = relationship('User',back_populates='portfolios')

    def __init__(self, asset:str,weight:float,start_date:datetime,end_date:datetime, data_insercao:Union[DateTime, None] = None):
        """
        Cria um Portfolio

        Arguments:
            asset: Ativo pertencente ao portfolio.
            weight: Peso do ativo no portfolio.
            start_date: Data inicial do portfolio.
            end_date: Data final do portfolio.
            data_insercao: data de quando o portfolio foi feito ou inserido
                           à base
        """
        self.asset = asset
        self.weight = weight
        self.start_date = start_date
        self.end_date = end_date
        if data_insercao:
            self.data_insercao = data_insercao

    def to_dict(self):
        """
        Retorna a representação em dicionário do Objeto Portfolio.
        """
        return{
            "portfolio_id":self.id,
            "asset": self.asset,
            "weight": self.weight,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "data_insercao": self.data_insercao 
        }