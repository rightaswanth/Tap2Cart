from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user import Address
from app.schemas.address import AddressCreate, AddressUpdate
from typing import List, Optional
import datetime


class AddressService:
    def __init__(self):
        self.model = Address

    async def get_multi_by_user(
        self, 
        db: AsyncSession, 
        user_id: str
    ) -> List[Address]:
        """Get all active addresses for a user."""
        query = select(Address).where(
            Address.user_id == user_id,
            Address.is_active == True
        ).order_by(Address.is_default.desc(), Address.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get(
        self, 
        db: AsyncSession, 
        id: str, 
        user_id: Optional[str] = None
    ) -> Optional[Address]:
        """Get a specific address."""
        query = select(Address).where(
            Address.address_id == id,
            Address.is_active == True
        )
        if user_id:
            query = query.where(Address.user_id == user_id)
            
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: AddressCreate, 
        user_id: str
    ) -> Address:
        """Create a new address."""
        # If this is set as default, unset other defaults
        if obj_in.is_default:
            await self._unset_defaults(db, user_id)
            
        # We need to manually inject user_id since it's not in AddressCreate usually?
        # AddressCreate in schema usually has street, city etc. user_id is from token.
        # CRUDBase.create takes obj_in. We can convert to dict and add user_id.
        
        db_obj = Address(
            user_id=user_id,
            **obj_in.model_dump()
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Address, 
        obj_in: AddressUpdate | dict
    ) -> Address:
         # Check default flag in update
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        if update_data.get("is_default"):
            await self._unset_defaults(db, db_obj.user_id)
            
        # Inline logic from CRUDBase.update
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(
        self, 
        db: AsyncSession, 
        *, 
        id: str,
        user_id: Optional[str] = None
    ) -> Optional[Address]:
        # Soft delete
        obj = await self.get(db, id=id, user_id=user_id)
        if not obj:
            return None
        
        obj.is_active = False
        obj.updated_at = datetime.datetime.utcnow()
        await db.commit()
        return obj

    async def _unset_defaults(self, db: AsyncSession, user_id: str):
        """Unset is_default for all user addresses."""
        stmt = update(Address).where(
            Address.user_id == user_id
        ).values(is_default=False)
        await db.execute(stmt)

address_service = AddressService()
