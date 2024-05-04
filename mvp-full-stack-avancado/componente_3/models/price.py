from sqlalchemy import Column, String, Integer, DateTime, ForeignKey,Float,UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from  models import Base


class Price(Base):

    __tablename__ = 'prices'

    id = Column("pk_price", Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("asset.pk_asset"), nullable=False)
    date = Column(DateTime,nullable=False)
    #vertex = Column(Integer, primary_key=True)
    price = Column(Float,nullable=False)
    #pvalue = Column(Float,nullable=False)
    #volume = Column(Float, nullable=False)
    data_insercao = Column(DateTime, default=datetime.now())

    # Criando um requisito de unicidade envolvendo uma par de informações
    __table_args__ = (UniqueConstraint("asset_id", "date", name="port_composite_key"),)

    asset = relationship('Asset',back_populates='prices')

    def __init__(self,date:datetime,price:float,data_insercao:Union[DateTime, None] = None):
        """
        Cria um dado de rentabilidade projetada

        Arguments:
            asset: Ativo.
            date: Data base do dado.
            price: Valor do preço projetado.
            data_insercao: data de quando o retorno esperado foi inserido
                           na base.
        """
        self.date = date
        self.price = price
        if data_insercao:
            self.data_insercao = data_insercao
