#!/usr/bin/env python3
import uvicorn
import sys

try:
    print("Starting backend server (backend.main:app)...")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend"],
    )
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)
