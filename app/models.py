from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship 
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # cliente, mercado, admin
    usuario_foto_url = Column(String, nullable=True)



class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    nome_fantasia = Column(String, nullable=False)
    cnpj = Column(String, nullable=False, unique=True)
    endereco = Column(String, nullable=False)
    telefone = Column(String, nullable=True)
    mercado_foto_url = Column(String, nullable=True)

    user = relationship("User")
    produtos = relationship("Product", back_populates="market", cascade="all, delete")


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    nome_produto = Column(String, nullable=False)
    marca = Column(String, nullable=True)
    preco = Column(Float, nullable=False)
    em_estoque = Column(Integer, default=0)
    market_id = Column(Integer, ForeignKey("markets.id"))

    market = relationship("Market", back_populates="produtos")
    