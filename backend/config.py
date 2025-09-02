import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://anirudh:password123@localhost/employee_db")

# JWT Configuration
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", "your-super-secret-access-token-key-change-this-in-production")
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET", "your-super-secret-refresh-token-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "2"))  # 2 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "5"))  # 5 minutes

# Image Upload Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
