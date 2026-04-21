# from passlib.context import CryptContext  # plus besoin
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from core.config import settings
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models.Admin import Admin

# plus de CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- MOT DE PASSE EN CLAIR ----
def hash_password(password: str) -> str:
    # ne rien hasher
    return password

def verify_password(password: str, hashed: str):
    # comparaison directe
    return password == hashed

# ---- JWT ----
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

def decode_refresh_token(token: str):
    return jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=["HS256"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
    except:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    admin = db.query(Admin).filter(Admin.id == payload["sub"]).first()

    if not admin:
        raise HTTPException(status_code=401, detail="Admin introuvable")

    return admin
