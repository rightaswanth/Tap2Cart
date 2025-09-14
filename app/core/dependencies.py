
# Dependency to get current user (you'll need to implement this)
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
security = HTTPBearer()



def get_current_user(token: str = Depends(security)):
    # Implement your JWT token validation here
    # This should return user info including user_id and is_admin flag
    # For now, returning a mock user
    return {
        "user_id": "mock_user_id",
        "is_admin": False,
        "email": "user@example.com"
    }

def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user
