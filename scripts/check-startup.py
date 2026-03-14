#!/usr/bin/env python3
"""Diagnose application startup - run from project root."""
import sys
import os

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.chdir(os.path.join(os.path.dirname(__file__), "..", "backend"))

print("1. Testing imports...")
try:
    from app.core.config import settings
    print("   config OK")
except Exception as e:
    print(f"   config FAIL: {e}")
    sys.exit(1)

try:
    from app.core.database import init_db
    print("   database OK")
except Exception as e:
    print(f"   database FAIL: {e}")
    sys.exit(1)

try:
    from app.routers import observations
    print("   observations router OK")
except Exception as e:
    print(f"   observations router FAIL: {e}")
    sys.exit(1)

try:
    from app.api_v1_app import api_v1_app
    print("   api_v1_app OK")
except Exception as e:
    print(f"   api_v1_app FAIL: {e}")
    sys.exit(1)

try:
    from app.main import app
    print("   main app OK")
except Exception as e:
    print(f"   main app FAIL: {e}")
    sys.exit(1)

print("2. All imports OK - app should start")
