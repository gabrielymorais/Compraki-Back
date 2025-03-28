from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .. import database, models, auth, schemas
from typing import List
import pandas as pd
from io import BytesIO

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/import-excel/")
def import_products_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    market = db.query(models.Market).filter(models.Market.user_id == current_user.id).first()
    if not market:
        raise HTTPException(status_code=403, detail="Usuário não é um mercado")

    contents = file.file.read()
    df = pd.read_excel(BytesIO(contents))

    required_columns = {"nome_produto", "marca", "preco", "em_estoque"}
    if not required_columns.issubset(set(map(str.lower, df.columns))):
        raise HTTPException(status_code=400, detail="Colunas inválidas no Excel")

    for _, row in df.iterrows():
        product = models.Product(
            nome_produto=row["nome_produto"],
            marca=row.get("marca", ""),
            preco=row["preco"],
            em_estoque=int(row["em_estoque"]),
            market_id=market.id
        )
        db.add(product)

    db.commit()
    return {"message": "Produtos importados com sucesso"}

@router.get("/me", response_model=List[schemas.ProductOut])
def get_my_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    market = db.query(models.Market).filter(models.Market.user_id == current_user.id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Mercado não encontrado para este usuário")
    
    products = db.query(models.Product).filter(models.Product.market_id == market.id).all()
    return products


@router.get("/export-excel/")
def export_products_excel(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    market = db.query(models.Market).filter(models.Market.user_id == current_user.id).first()
    if not market:
        raise HTTPException(status_code=403, detail="Usuário não é um mercado")

    products = db.query(models.Product).filter(models.Product.market_id == market.id).all()
    data = [{
        "nome_produto": p.nome_produto,
        "marca": p.marca,
        "preco": p.preco,
        "em_estoque": p.em_estoque
    } for p in products]

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)
    headers = {'Content-Disposition': 'attachment; filename=produtos.xlsx'}
    return StreamingResponse(output, headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
