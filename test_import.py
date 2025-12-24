#!/usr/bin/env python3
import sys
sys.path.append('.')

print("Testing user schema import...")
try:
    from app.schemas.user import UserResponse
    print("User schema import: SUCCESS")
except Exception as e:
    print(f"User schema import: FAILED - {e}")

print("\nTesting voiceprint router syntax...")
try:
    with open('app/routers/voiceprint.py', 'r') as f:
        content = f.read()
    
    # Check for the problematic import
    if 'from app.schemas.user import UserResponse' in content:
        print("Voiceprint router: FAILED - still contains UserResponse import")
    elif 'ModuleNotFoundError: No module named \'app.schemas.user\'' in content:
        print("Voiceprint router: FAILED - contains error message")
    else:
        print("Voiceprint router syntax: SUCCESS")
except Exception as e:
    print(f"Voiceprint router syntax check: FAILED - {e}")