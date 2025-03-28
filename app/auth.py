from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError  # type: ignore
from fastapi import Depends, HTTPException, status
from .database import SessionLocal
from . import models
from sqlalchemy.orm import Session
import os
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  

def hash_password(password: str) -> str: 
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool: 
    return pwd_context.verify(plain_password, hashed_password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
