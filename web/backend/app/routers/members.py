"""
Members management router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..auth_enhanced import get_current_user

router = APIRouter()


@router.get("/", response_model=List[schemas.Member])
async def get_members(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members for the current user's system"""
    members = db.query(models.Member).filter(
        models.Member.user_id == current_user.id
    ).order_by(models.Member.name).all()
    return members


@router.get("/{member_id}", response_model=schemas.Member)
async def get_member(
    member_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific member"""
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.user_id == current_user.id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    return member


@router.post("/", response_model=schemas.Member, status_code=status.HTTP_201_CREATED)
async def create_member(
    member: schemas.MemberCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new member"""
    # Check for duplicate name
    existing = db.query(models.Member).filter(
        models.Member.user_id == current_user.id,
        models.Member.name == member.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member with this name already exists"
        )

    new_member = models.Member(
        user_id=current_user.id,
        **member.dict()
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member


@router.patch("/{member_id}", response_model=schemas.Member)
async def update_member(
    member_id: int,
    member_update: schemas.MemberUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a member"""
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.user_id == current_user.id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Update only provided fields
    update_data = member_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)

    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a member"""
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.user_id == current_user.id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    db.delete(member)
    db.commit()
    return None
