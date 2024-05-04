from sqlalchemy import Column, String, Integer, DateTime, ForeignKey,Float
from sqlalchemy.orm import relationship
from sqlalchemy.schema import PrimaryKeyConstraint
from datetime import datetime
from typing import Union
from  models import Base,Price


class Asset(Base):

    __tablename__ = 'asset'

    id = Column('pk_asset',Integer, primary_key=True)
    ticker = Column(String(10),unique=True)
    asset_name =  Column(String(200),nullable=False)
    avg_volume = Column(Float)
    data_insercao = Column(DateTime, default=datetime.now())

    # Criando um requisito de unicidade envolvendo uma par de informações
    #__table_args__ = (PrimaryKeyConstraint("asset", "id", name="port_composite_key"),)

    prices = relationship('Price',back_populates='asset')

    def __init__(self, ticker:str,asset_name:str,avg_volume:float,data_insercao:Union[DateTime, None] = None):
        """
        Cria um dado de ativo

        Arguments:
            ticker: código do ativo.
            name: nome do ativo.
            avg_volume: volume médio negociado
            data_insercao: data de quando o ativo foi inserido
                           na base.
        """
        self.ticker = ticker
        self.asset_name = asset_name
        self.avg_volume = avg_volume
        if data_insercao:
            self.data_insercao = data_insercao

    def add_price(self, price:Price):
        """ Adiciona um novo preço ao Produto
        """
        self.prices.append(price)