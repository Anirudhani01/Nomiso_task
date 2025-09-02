# Employee Management API with JWT Authentication

A FastAPI application for managing employee data with secure JWT authentication system.

## Features (Updated)

- Employee Management: Full CRUD operations for employee data (requires authentication)
- JWT Authentication: Secure login with access and refresh tokens
- Admin Management: Admin registration system
- Password Security: Bcrypt password hashing
- Token Management: 60-minute access tokens, refresh tokens
- Image Upload: Employee photo upload with deduplication and hash-based storage
- CORS: Configured for frontend integration
- Error Handling: Robust error responses for all endpoints
- Pagination: Efficient employee listing
- Search & Filtering: Multi-criteria employee search
- Statistics: Employee dashboard metrics

## Endpoints (Updated)

### Public Endpoints
- POST /auth/login: Login and get JWT tokens
- POST /admin/register: Register a new admin
- GET /: Health check

### Protected Endpoints (JWT required)
- GET /me: Get current admin info
- GET /employees/: List employees (pagination)
- GET /employees/{emp_id}: Get employee by ID
- POST /employees/: Create new employee
- PUT /employees/{emp_id}: Update employee
- DELETE /employees/{emp_id}: Delete employee
- GET /employees/search/: Search employees
- POST /employees/{emp_id}/image: Upload employee image
- GET /employees/{emp_id}/image: Get employee image info
- DELETE /employees/{emp_id}/image: Delete employee image
- PUT /employees/{emp_id}/image: Update employee image

## Technical Changes (Summary)
- Moved all backend code to backend/ folder
- Consolidated CRUD logic into main.py
- Added JWT authentication with HTTPBearer
- Added password hashing with bcrypt (passlib)
- Added image upload and deduplication (Pillow)
- Added CORS middleware for frontend integration
- Added robust error handling and validation
- Added pagination, search, and statistics endpoints
- Added database population and admin bootstrap scripts
- Updated for Python 3.12 compatibility

## Business Logic

- **Public Endpoints**: Login and admin registration only
- **Protected Endpoints**: All employee CRUD operations require authentication
- **Simple Token System**: Single access token with 60-minute expiry (no refresh tokens)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Configuration

The application uses MySQL. Make sure your database is running and accessible with the credentials:
- Username: `anirudh`
- Password: `password123`
- Database: `employee_db`

### 3. Environment Variables (Optional)

Create a `.env` file in the backend directory for custom configuration:

```env
DATABASE_URL=mysql+mysqlconnector://anirudh:password123@localhost/employee_db
ACCESS_TOKEN_SECRET=your-super-secret-access-token-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Bootstrap Initial Admin

Run the bootstrap script to create the first admin user:

```bash
python bootstrap_admin.py
```

This creates an admin with:
- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANT**: Change the default password after first login!

### 5. Run the Application

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

### Public Endpoints (No Authentication Required)

#### 1. Login
```http
POST /auth/login
Content-Type: application/json

{
  "name": "admin",
  "password": "admin123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### 2. Register Admin
```http
POST /admin/register
Content-Type: application/json

{
  "name": "newadmin",
  "password": "securepassword123"
}
```

### Protected Endpoints (Require Authentication)

All employee endpoints require a valid Bearer token in the Authorization header.

#### 1. Get Current Admin Info
```http
GET /me
Authorization: Bearer <access_token>
```

#### 2. Employee Endpoints (All require authentication)

- `GET /employees/` - Get all employees
- `GET /employees/{emp_id}` - Get employee by ID
- `POST /employees/` - Create new employee
- `PUT /employees/{emp_id}` - Update employee
- `DELETE /employees/{emp_id}` - Delete employee
- `GET /employees/search/` - Search employees

Example with authentication:
```http
GET /employees/
Authorization: Bearer <access_token>
```

## Usage Examples

### 1. Login and Get Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "admin",
       "password": "admin123"
     }'
```

### 2. Use Access Token for Employee Operations

```bash
# Store the access token
ACCESS_TOKEN="your_access_token_here"

# Get all employees
curl -X GET "http://localhost:8000/employees/" \
     -H "Authorization: Bearer $ACCESS_TOKEN"

# Create new employee
curl -X POST "http://localhost:8000/employees/" \
     -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "Name": "John Doe",
       "Email": "john.doe@example.com",
       "Education": "Bachelors",
       "JoiningYear": 2023,
       "City": "Mumbai",
       "PaymentTier": 2,
       "Age": 30,
       "Gender": "Male",
       "EverBenched": "No",
       "ExperienceInCurrentDomain": 2,
       "LeaveOrNot": 0
     }'

# Get current admin info
curl -X GET "http://localhost:8000/me" \
     -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 3. Test Without Authentication (Should Fail)

```bash
# This should return 401 Unauthorized
curl "http://localhost:8000/employees/"
```

## Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **JWT Tokens**: Secure token-based authentication
- **Token Expiry**: Access tokens expire in 60 minutes
- **Protected Endpoints**: All employee operations require authentication
- **Unique Admin Names**: Prevents duplicate admin registrations

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## Project Structure

```
backend/
├── main.py              # Main FastAPI application
├── auth_models.py       # Authentication models and utilities
├── config.py           # Configuration and environment variables
├── bootstrap_admin.py  # Script to create initial admin
├── test_auth.py        # Test script for authentication
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Testing

Run the test script to verify the authentication system:

```bash
python test_auth.py
```

## Notes

- **All employee endpoints require authentication** - this is the correct business logic
- Only login and admin registration are public endpoints
- Simple token system with 60-minute expiry (no refresh tokens needed)
- The first admin must be created using the bootstrap script
- Change default passwords in production environments
- Store JWT secrets securely in production
