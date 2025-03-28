from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth
from ..auth import get_current_user

router = APIRouter(prefix="/markets", tags=["Markets"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", response_model=schemas.MarketOut)
def create_market(
    market: schemas.MarketCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    existing = db.query(models.Market).filter(models.Market.cnpj == market.cnpj).first()
    if existing:
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")

    new_market = models.Market(
        nome_fantasia=market.nome_fantasia,
        cnpj=market.cnpj,
        endereco=market.endereco,
        telefone=market.telefone,
        mercado_foto_url=market.mercado_foto_url,
        user_id=current_user.id
    )
    db.add(new_market)

    # 🔧 Atualiza o usuário manualmente via DB
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if user:
        user.role = "mercado"

    db.commit()
    db.refresh(new_market)
    return new_market


