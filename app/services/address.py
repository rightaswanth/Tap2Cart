from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user import Address
from app.schemas.address import AddressCreate, AddressUpdate
from typing import List, Optional
import datetime

class AddressService:
    
    @staticmethod
    async def get_user_addresses(db: AsyncSession, user_id: str) -> List[Address]:
        """Get all active addresses for a user."""
        query = select(Address).where(
            Address.user_id == user_id,
            Address.is_active == True
        ).order_by(Address.is_default.desc(), Address.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_address_by_id(db: AsyncSession, address_id: str, user_id: str) -> Optional[Address]:
        """Get a specific address."""
        query = select(Address).where(
            Address.address_id == address_id,
            Address.user_id == user_id,
            Address.is_active == True
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_address(db: AsyncSession, user_id: str, address_data: AddressCreate) -> Address:
        """Create a new address."""
        # If this is set as default, unset other defaults
        if address_data.is_default:
            await AddressService._unset_defaults(db, user_id)
            
        address = Address(
            user_id=user_id,
            street_address=address_data.street_address,
            city=address_data.city,
            state=address_data.state,
            postal_code=address_data.postal_code,
            country=address_data.country,
            is_default=address_data.is_default
        )
        
        db.add(address)
        await db.commit()
        await db.refresh(address)
        return address
    
    @staticmethod
    async def update_address(
        db: AsyncSession, 
        address_id: str, 
        user_id: str, 
        address_data: AddressUpdate
    ) -> Optional[Address]:
        """Update an existing address."""
        address = await AddressService.get_address_by_id(db, address_id, user_id)
        if not address:
            return None
        
        # If setting as default, unset other defaults
        if address_data.is_default:
            await AddressService._unset_defaults(db, user_id)
        
        update_data = address_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(address, field, value)
            
        address.updated_at = datetime.datetime.utcnow()
        
        await db.commit()
        await db.refresh(address)
        return address
    
    @staticmethod
    async def delete_address(db: AsyncSession, address_id: str, user_id: str) -> bool:
        """Soft delete an address."""
        address = await AddressService.get_address_by_id(db, address_id, user_id)
        if not address:
            return False
        
        address.is_active = False
        address.updated_at = datetime.datetime.utcnow()
        
        await db.commit()
        return True
        
    @staticmethod
    async def _unset_defaults(db: AsyncSession, user_id: str):
        """Unset is_default for all user addresses."""
        stmt = update(Address).where(
            Address.user_id == user_id
        ).values(is_default=False)
        await db.execute(stmt)
