from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    usuario_foto_url: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class MarketBase(BaseModel):
    nome_fantasia: str
    cnpj: str
    endereco: str
    telefone: Optional[str] = None

class MarketCreate(MarketBase):
    mercado_foto_url: Optional[str] = None

class MarketOut(MarketBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    nome_produto: str
    marca: Optional[str] = None
    preco: float
    em_estoque: int

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    market_id: int

    class Config:
        from_attributes = True
