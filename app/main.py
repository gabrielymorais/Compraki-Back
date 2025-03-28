from fastapi import FastAPI
from . import models, database
from .routers import user, market, product
app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

app.include_router(user.router)
app.include_router(market.router)
app.include_router(product.router)