from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from config import ACCESS_TOKEN_SECRET, REFRESH_TOKEN_SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme for token authentication
security = HTTPBearer()

# SQLAlchemy Base
Base = declarative_base()

# SQLAlchemy Admin model (use existing table name 'admin')
class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))

# Pydantic schemas for API requests/responses
class AdminCreate(BaseModel):
    name: str
    password: str

class AdminOut(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    name: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Security utilities
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str) -> str:
    """Create an access token with configurable expiry"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(to_encode, ACCESS_TOKEN_SECRET, algorithm=ALGORITHM)

def create_refresh_token(subject: str) -> str:
    """Create a refresh token with longer expiry"""
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    return jwt.encode(to_encode, REFRESH_TOKEN_SECRET, algorithm=ALGORITHM)

def create_tokens(subject: str) -> dict:
    """Create both access and refresh tokens"""
    access_token = create_access_token(subject)
    refresh_token = create_refresh_token(subject)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    }

def verify_token(token: str) -> str:
    """Verify and decode an access JWT token"""
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def verify_refresh_token(token: str) -> str:
    """Verify and decode a refresh JWT token"""
    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

# Database dependency for admin operations
def get_admin_by_name(db: Session, name: str) -> Optional[Admin]:
    """Get admin by name"""
    return db.query(Admin).filter(Admin.name == name).first()

def get_admin_by_id(db: Session, admin_id: int) -> Optional[Admin]:
    """Get admin by ID"""
    return db.query(Admin).filter(Admin.id == admin_id).first()

def create_admin(db: Session, admin_data: AdminCreate) -> Admin:
    """Create a new admin"""
    hashed_password = hash_password(admin_data.password)
    db_admin = Admin(name=admin_data.name, password_hash=hashed_password)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin
