from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth.create_access_token(data={"sub": db_user.email, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}
