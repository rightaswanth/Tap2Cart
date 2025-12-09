from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.services.address import AddressService
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse

router = APIRouter(tags=["address"])

@router.get("/", response_model=List[AddressResponse], summary="Get user addresses")
async def get_addresses(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all active addresses for a user."""
    return await AddressService.get_user_addresses(db, user_id)

@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED, summary="Add new address")
async def create_address(
    address_data: AddressCreate,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Add a new address for the user."""
    return await AddressService.create_address(db, user_id, address_data)

@router.put("/{address_id}", response_model=AddressResponse, summary="Update address")
async def update_address(
    address_id: str,
    address_data: AddressUpdate,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing address."""
    address = await AddressService.update_address(db, address_id, user_id, address_data)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete address")
async def delete_address(
    address_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete (soft delete) an address."""
    success = await AddressService.delete_address(db, address_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")
    return
