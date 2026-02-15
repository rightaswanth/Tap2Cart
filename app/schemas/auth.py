from pydantic import BaseModel, Field
from typing import Optional

class OTPRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number to send OTP to")

class OTPVerify(BaseModel):
    phone_number: str = Field(..., description="Phone number matching the OTP")
    otp: str = Field(..., description="The OTP received")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
