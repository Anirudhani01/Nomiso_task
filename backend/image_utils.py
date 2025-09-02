#!/usr/bin/env python3
import os
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
from fastapi import HTTPException, UploadFile
from config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
import io

def create_upload_directory():
    """Create upload directory if it doesn't exist"""
    upload_path = Path(UPLOAD_DIR)
    upload_path.mkdir(exist_ok=True)
    return upload_path

def validate_image_file(file: UploadFile) -> Tuple[bool, str]:
    """Validate uploaded image file"""
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return False, f"File size exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit"
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed"
    
    # Check content type
    if not file.content_type or not file.content_type.startswith('image/'):
        return False, "File must be an image"
    
    return True, ""

def compute_image_hash(file_content: bytes) -> str:
    """Compute SHA-256 hash of image content"""
    return hashlib.sha256(file_content).hexdigest()

def save_image_with_deduplication(
    file_content: bytes, 
    emp_id: int, 
    image_hash: str
) -> str:
    """
    Save image with deduplication:
    - Save canonical file as {hash}.png
    - Create alias {emp_id}.png (hardlink if possible, else copy)
    - Return the alias path
    """
    upload_path = create_upload_directory()
    
    # Canonical file path (by hash)
    canonical_path = upload_path / f"{image_hash}.png"
    
    # Alias file path (by employee ID)
    alias_path = upload_path / f"{emp_id}.png"
    
    # Save canonical file if it doesn't exist
    if not canonical_path.exists():
        try:
            # Open image and convert to PNG
            image = Image.open(io.BytesIO(file_content))
            # Convert to RGB if necessary (PNG doesn't support RGBA for some cases)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            image.save(canonical_path, 'PNG', optimize=True)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    # Create alias (hardlink if possible, else copy)
    try:
        if not alias_path.exists():
            # Try to create hardlink first
            try:
                os.link(canonical_path, alias_path)
            except OSError:
                # If hardlink fails, copy the file
                shutil.copy2(canonical_path, alias_path)
        else:
            # If alias exists, update it
            alias_path.unlink()  # Remove existing alias
            try:
                os.link(canonical_path, alias_path)
            except OSError:
                shutil.copy2(canonical_path, alias_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create image alias: {str(e)}")
    
    return str(alias_path)

def get_image_path(emp_id: int) -> Optional[str]:
    """Get image path for employee ID"""
    upload_path = create_upload_directory()
    alias_path = upload_path / f"{emp_id}.png"
    
    if alias_path.exists():
        return str(alias_path)
    return None

def delete_employee_image(emp_id: int) -> bool:
    """Delete employee image alias (keep canonical file)"""
    upload_path = create_upload_directory()
    alias_path = upload_path / f"{emp_id}.png"
    
    if alias_path.exists():
        try:
            alias_path.unlink()
            return True
        except Exception:
            return False
    return False

def cleanup_orphaned_canonical_files():
    """Clean up canonical files that are no longer referenced by any employee"""
    # This is a utility function for maintenance
    # In a production system, you might want to run this periodically
    pass
