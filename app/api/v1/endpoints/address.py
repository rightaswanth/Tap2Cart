from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.services.address import address_service
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse

router = APIRouter(tags=["address"])

@router.get("/", response_model=List[AddressResponse], summary="Get user addresses")
async def get_addresses(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all active addresses for a user."""
    return await address_service.get_multi_by_user(db, user_id=user_id)

@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED, summary="Add new address")
async def create_address(
    address_data: AddressCreate,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Add a new address for the user."""
    return await address_service.create(db, obj_in=address_data, user_id=user_id)

@router.put("/{address_id}", response_model=AddressResponse, summary="Update address")
async def update_address(
    address_id: str,
    address_data: AddressUpdate,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing address."""
    # First get the address to ensure ownership
    address = await address_service.get(db, id=address_id, user_id=user_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
        
    return await address_service.update(db, db_obj=address, obj_in=address_data)

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete address")
async def delete_address(
    address_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete (soft delete) an address."""
    result = await address_service.remove(db, id=address_id, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Address not found")
    return
