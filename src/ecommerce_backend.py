from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from jose import jwt
import datetime
import uuid
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI(title="Minimalistic E-commerce Backend", version="1.0.0")

# Security configurations
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token bearer
security = HTTPBearer()

# In-memory storage (replace with database in production)
users_db = {}
products_db = {}

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
    email: str

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    seller_id: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Endpoints
@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """Register a new user"""
    # Check if username already exists
    if user.username in [u["username"] for u in users_db.values()]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if user.email in [u["email"] for u in users_db.values()]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    
    users_db[user_id] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password
    }
    
    return User(
        id=user_id,
        username=user.username,
        email=user.email
    )

@app.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Login user and return access token"""
    # Find user by username
    user = None
    for u in users_db.values():
        if u["username"] == user_credentials.username:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["username"]})
    
    return Token(access_token=access_token, token_type="bearer")

@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def add_product(product: ProductCreate, current_user: str = Depends(verify_token)):
    """Add a new product (requires authentication)"""
    # Find user by username
    user = None
    for u in users_db.values():
        if u["username"] == current_user:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new product
    product_id = str(uuid.uuid4())
    
    products_db[product_id] = {
        "id": product_id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category": product.category,
        "seller_id": user["id"]
    }
    
    return Product(
        id=product_id,
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category,
        seller_id=user["id"]
    )

@app.get("/products", response_model=List[Product])
async def get_products():
    """Get all products"""
    return [
        Product(
            id=product["id"],
            name=product["name"],
            description=product["description"],
            price=product["price"],
            category=product["category"],
            seller_id=product["seller_id"]
        )
        for product in products_db.values()
    ]

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    if product_id not in products_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product = products_db[product_id]
    return Product(
        id=product["id"],
        name=product["name"],
        description=product["description"],
        price=product["price"],
        category=product["category"],
        seller_id=product["seller_id"]
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Minimalistic E-commerce Backend",
        "endpoints": {
            "register": "/register",
            "login": "/login",
            "add_product": "/products",
            "get_products": "/products",
            "get_product": "/products/{product_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
