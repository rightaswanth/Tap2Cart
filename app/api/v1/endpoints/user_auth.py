from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from typing import Dict

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import OTPRequest, OTPVerify, Token
from app.core.security import create_access_token
from app.config import settings

router = APIRouter(tags=["auth"])

# In-memory OTP store for demonstration
# In production, use Redis with expiration
otp_store: Dict[str, str] = {}

@router.post("/send-otp", status_code=200, summary="Send OTP")
async def send_otp(request: OTPRequest):
    """
    Generate and send OTP to the given phone number.
    For development, the OTP is returned in the response.
    """
    # Mock OTP generation
    otp = "123456" 
    otp_store[request.phone_number] = otp
    
    # In real world: sms_service.send(request.phone_number, otp)
    
    return {"message": "OTP sent successfully", "otp": otp} # Remove 'otp' field in prod

@router.post("/login-otp", response_model=Token, summary="Login with OTP")
async def login_with_otp(
    verify_data: OTPVerify,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP and return JWT token.
    Creates user if phone number exists in DB? 
    Requirement says "normal user login". 
    If user doesn't exist, should we register them or fail?
    Usually OTP login implies auto-registration or matching existing.
    Guest checkout creates users. So user likely exists. 
    If not, let's create them to be safe/user-friendly.
    """
    stored_otp = otp_store.get(verify_data.phone_number)
    
    if not stored_otp or stored_otp != verify_data.otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Clear OTP after use
    del otp_store[verify_data.phone_number]
    
    # Find or Create User
    stmt = select(User).where(User.phone_number == verify_data.phone_number)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        # Auto-register
        user = User(
            phone_number=verify_data.phone_number,
            role="user",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Create Token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user.user_id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
