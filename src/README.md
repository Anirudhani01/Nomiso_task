# Minimalistic E-commerce Backend

A simple FastAPI-based e-commerce backend with user authentication and product management.

## Features

- **User Registration**: Create new user accounts
- **User Login**: Authenticate users and get JWT tokens
- **Product Management**: Add products (requires authentication)
- **Product Retrieval**: Get all products or specific products by ID

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python ecommerce_backend.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn ecommerce_backend:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API:**
   - API will be available at: `http://localhost:8000`
   - Interactive API docs: `http://localhost:8000/docs`
   - Alternative API docs: `http://localhost:8000/redoc`

## API Endpoints

### Public Endpoints

- `GET /` - API information and available endpoints
- `POST /register` - User registration
- `POST /login` - User login
- `GET /products` - Get all products
- `GET /products/{product_id}` - Get specific product

### Protected Endpoints

- `POST /products` - Add new product (requires authentication)

## Usage Examples

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john_doe",
       "email": "john@example.com",
       "password": "securepassword123"
     }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john_doe",
       "password": "securepassword123"
     }'
```

### 3. Add a Product (with authentication)
```bash
curl -X POST "http://localhost:8000/products" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "name": "Laptop",
       "description": "High-performance gaming laptop",
       "price": 1299.99,
       "category": "Electronics"
     }'
```

### 4. Get All Products
```bash
curl -X GET "http://localhost:8000/products"
```

## Data Models

### User
- `id`: Unique identifier
- `username`: Unique username
- `email`: Unique email address
- `password`: Hashed password (not returned in responses)

### Product
- `id`: Unique identifier
- `name`: Product name
- `description`: Product description
- `price`: Product price
- `category`: Product category
- `seller_id`: ID of the user who added the product

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Authentication**: Secure token-based authentication
- **Token Expiration**: Tokens expire after 30 minutes
- **Input Validation**: Pydantic models ensure data validation

## Notes

- This is a minimalistic implementation using in-memory storage
- Data will be lost when the server restarts
- For production use, replace in-memory storage with a proper database
- Change the `SECRET_KEY` in production
- Add proper error handling and logging for production use

## Testing the API

You can test the API using:
- The interactive Swagger UI at `/docs`
- cURL commands
- Postman or similar API testing tools
- Any HTTP client library in your preferred programming language
