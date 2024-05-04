from sqlalchemy import Column, String, DateTime, ForeignKey,Float,Integer
from datetime import datetime
from typing import Union
from sqlalchemy.orm import relationship

from  models import Base


class User(Base):
    __tablename__ = 'users'
    id = Column('pk_user',Integer, primary_key=True)
    name = Column(String(100),nullable=False)
    email = Column(String(50), unique=True, nullable=False) 
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    dt_insert = Column(DateTime, default=datetime.now())

    portfolios = relationship('Portfolio',back_populates='user')

    def __init__(self, name:str,email:str,username:str,password:str,dt_insert:Union[DateTime, None] = None):
        """
        Cadastra uma usuário

        Arguments:
            name: Nome do usuário
            email: Email de cadastro do usuário
            username: Nome do usuário
            password: Senha do usuário
            dt_insert: data de quando o usuário foi inserido na base
        """
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        # se não for informada, será o data exata da inserção no banco
        if dt_insert:
            self.dt_insert = dt_insert