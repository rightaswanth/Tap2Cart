from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SchemaBase(BaseModel):
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    class Config:
        from_attributes = True 