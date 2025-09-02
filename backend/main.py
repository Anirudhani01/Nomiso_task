from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional
from auth_models import (
    Admin, AdminCreate, AdminOut, LoginRequest, TokenResponse, RefreshTokenRequest,
    get_admin_by_name, get_admin_by_id, create_admin, verify_password,
    create_tokens, verify_token, verify_refresh_token, security, Base
)
from config import DATABASE_URL, UPLOAD_DIR
from image_utils import (
    validate_image_file, compute_image_hash, save_image_with_deduplication,
    get_image_path, delete_employee_image, create_upload_directory
)

# Database configuration
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy Model (existing - unchanged)
class Employee(Base):
    __tablename__ = "employees"
    emp_id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(255), nullable=False)
    Email = Column(String(255), unique=True, nullable=False)
    Education = Column(String(100))
    JoiningYear = Column(Integer)
    City = Column(String(100))
    PaymentTier = Column(Integer)
    Age = Column(Integer)
    Gender = Column(String(10))
    EverBenched = Column(String(10))
    ExperienceInCurrentDomain = Column(Integer)
    LeaveOrNot = Column(Integer)
    # NEW IMAGE FIELDS
    image_path = Column(String(500), nullable=True)
    image_hash = Column(String(64), nullable=True)  # SHA-256 hash

# Pydantic Schemas (existing - unchanged)
class EmployeeBase(BaseModel):
    Name: str
    Email: str
    Education: Optional[str] = None
    JoiningYear: Optional[int] = None
    City: Optional[str] = None
    PaymentTier: Optional[int] = None
    Age: Optional[int] = None
    Gender: Optional[str] = None
    EverBenched: Optional[str] = None
    ExperienceInCurrentDomain: Optional[int] = None
    LeaveOrNot: Optional[int] = None
    # NEW IMAGE FIELDS
    image_path: Optional[str] = None
    image_hash: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    Name: Optional[str] = None
    Email: Optional[str] = None
    Education: Optional[str] = None
    JoiningYear: Optional[int] = None
    City: Optional[str] = None
    PaymentTier: Optional[int] = None
    Age: Optional[int] = None
    Gender: Optional[str] = None
    EverBenched: Optional[str] = None
    ExperienceInCurrentDomain: Optional[int] = None
    LeaveOrNot: Optional[int] = None

class EmployeeResponse(EmployeeBase):
    emp_id: int
    
    class Config:
        from_attributes = True
        orm_mode = True

# Explicitly import Admin model to ensure registration before creating tables
from auth_models import Admin
# Base.metadata.create_all(bind=engine)  # Commented out to prevent table recreation

# Database dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_sync():
    """Synchronous database session for testing"""
    return SessionLocal()

# Authentication dependency
async def get_current_admin(token=Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated admin"""
    admin_id = verify_token(token.credentials)
    admin = get_admin_by_id(db, int(admin_id))
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid token")
    return admin

# FastAPI App
app = FastAPI(
    title="Employee Management API with JWT Auth",
    description="A FastAPI application for managing employee data with secure JWT authentication",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory and mount static files
create_upload_directory()
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Public endpoints (no authentication required)
@app.get("/")
def read_root():
    return {"message": "Welcome to Employee Management API with JWT Authentication"}

@app.get("/debug/admin")
def debug_admin():
    """Debug endpoint to check admin user"""
    try:
        db = SessionLocal()
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        admin_count = db.query(Admin).count()
        admin = db.query(Admin).first()
        
        return {
            "tables": tables,
            "admin_count": admin_count,
            "admin_exists": admin is not None,
            "admin_name": admin.name if admin else None,
            "admin_id": admin.id if admin else None,
            "database_url": DATABASE_URL
        }
    except Exception as e:
        return {"error": str(e), "database_url": DATABASE_URL}
    finally:
        if 'db' in locals():
            db.close()

@app.post("/auth/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    """Login endpoint to get access token"""
    print(f"Login attempt for user: {login_data.name}")
    
    # Use direct database connection
    db = SessionLocal()
    try:
        admin = get_admin_by_name(db, login_data.name)
        print(f"Admin found: {admin is not None}")
        
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        password_valid = verify_password(login_data.password, admin.password_hash)
        print(f"Password valid: {password_valid}")
        
        if not password_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        tokens = create_tokens(str(admin.id))
        print(f"Tokens created for admin ID: {admin.id}")
        
        return TokenResponse(**tokens)
    finally:
        db.close()

@app.post("/auth/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    print(f"Token refresh attempt")
    
    try:
        admin_id = verify_refresh_token(refresh_data.refresh_token)
        print(f"Refresh token valid for admin ID: {admin_id}")
        
        # Create new tokens
        tokens = create_tokens(admin_id)
        print(f"New tokens created for admin ID: {admin_id}")
        
        return TokenResponse(**tokens)
    except HTTPException as e:
        print(f"Refresh token error: {e.detail}")
        raise e

@app.post("/admin/register", response_model=AdminOut)
def register_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    """Register a new admin (public endpoint for initial setup)"""
    # Check if admin name already exists
    existing_admin = get_admin_by_name(db, admin_data.name)
    if existing_admin:
        raise HTTPException(status_code=409, detail="Admin name already registered")
    
    new_admin = create_admin(db, admin_data)
    return AdminOut(id=new_admin.id, name=new_admin.name)

# Protected endpoints (require authentication)
@app.get("/me", response_model=AdminOut)
def get_current_admin_info(current_admin: Admin = Depends(get_current_admin)):
    """Get current admin information"""
    return AdminOut(id=current_admin.id, name=current_admin.name)

@app.get("/employees/", response_model=List[EmployeeResponse])
def get_employees(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)  # Require authentication
):
    """Get all employees with pagination (requires authentication)"""
    employees = db.query(Employee).offset(skip).limit(limit).all()
    return employees

@app.get("/employees/{emp_id}", response_model=EmployeeResponse)
def get_employee(
    emp_id: int, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)  # Require authentication
):
    """Get employee by ID (requires authentication)"""
    employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.post("/employees/", response_model=EmployeeResponse)
def create_employee(
    employee: EmployeeCreate, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)  # Require authentication
):
    """Create a new employee (requires authentication)"""
    existing_employee = db.query(Employee).filter(Employee.Email == employee.Email).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Get the next available emp_id
    max_emp_id = db.query(func.max(Employee.emp_id)).scalar() or 0
    next_emp_id = max_emp_id + 1
    
    # Create employee with the generated emp_id
    employee_data = employee.dict()
    employee_data['emp_id'] = next_emp_id
    db_employee = Employee(**employee_data)
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.put("/employees/{emp_id}", response_model=EmployeeResponse)
def update_employee(
    emp_id: int, 
    employee: EmployeeUpdate, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)  # Require authentication
):
    """Update an existing employee (requires authentication)"""
    db_employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    if employee.Email and employee.Email != db_employee.Email:
        existing_employee = db.query(Employee).filter(Employee.Email == employee.Email).first()
        if existing_employee:
            raise HTTPException(status_code=400, detail="Email already registered")
    update_data = employee.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.put("/employees/{emp_id}/image", response_model=EmployeeResponse)
def update_employee_with_image(
    emp_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update employee image (reuse upload logic)"""
    # This endpoint reuses the upload logic for updating images
    return upload_employee_image(emp_id, file, db, current_admin)

@app.delete("/employees/{emp_id}")
def delete_employee(
    emp_id: int, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)  # Require authentication
):
    """Delete an employee (requires authentication)"""
    db_employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Delete associated image if it exists
    if db_employee.image_path:
        delete_employee_image(emp_id)
    
    db.delete(db_employee)
    db.commit()
    return {"message": "Employee deleted successfully"}

@app.get("/employees/search/", response_model=List[EmployeeResponse])
def search_employees(
    name: Optional[str] = Query(None, description="Search by name (partial match)"),
    city: Optional[str] = Query(None, description="Search by city (partial match)"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    payment_tier: Optional[int] = Query(None, description="Filter by payment tier"),
    education: Optional[str] = Query(None, description="Filter by education"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)  # Require authentication
):
    """Search employees by various criteria (requires authentication)"""
    query = db.query(Employee)
    if name:
        query = query.filter(Employee.Name.ilike(f"%{name}%"))
    if city:
        query = query.filter(Employee.City.ilike(f"%{city}%"))
    if gender:
        query = query.filter(Employee.Gender == gender)
    if payment_tier is not None:
        query = query.filter(Employee.PaymentTier == payment_tier)
    if education:
        query = query.filter(Employee.Education == education)
    employees = query.all()
    return employees

# Debug: list all registered routes
@app.get("/debug/routes")
def list_routes():
    try:
        return {"routes": [getattr(r, 'path', str(r)) for r in app.routes]}
    except Exception as e:
        return {"error": str(e)}

# Image Upload/Download Endpoints
@app.post("/employees/{emp_id}/image")
def upload_employee_image(
    emp_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Upload image for an employee (requires authentication)"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Validate image file
    is_valid, error_message = validate_image_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    try:
        # Read file content
        file_content = file.file.read()
        
        # Compute image hash
        image_hash = compute_image_hash(file_content)
        
        # Save image with deduplication
        image_path = save_image_with_deduplication(file_content, emp_id, image_hash)
        
        # Update employee record
        employee.image_path = f"/uploads/{emp_id}.png"
        employee.image_hash = image_hash
        db.commit()
        
        return {
            "message": "Image uploaded successfully",
            "image_path": employee.image_path,
            "image_hash": image_hash
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@app.get("/employees/{emp_id}/image")
def get_employee_image(
    emp_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get employee image (requires authentication)"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if employee has an image
    if not employee.image_path:
        raise HTTPException(status_code=404, detail="Employee has no image")
    
    # Return image path
    return {
        "image_path": employee.image_path,
        "image_hash": employee.image_hash
    }

@app.delete("/employees/{emp_id}/image")
def delete_employee_image_endpoint(
    emp_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete employee image (requires authentication)"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Delete image file
    success = delete_employee_image(emp_id)
    
    # Update employee record
    employee.image_path = None
    employee.image_hash = None
    db.commit()
    
    return {"message": "Image deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
