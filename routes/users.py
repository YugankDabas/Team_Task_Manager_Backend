from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import User
from schemas.user import UserOut
from auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/search")
def search_users(
    email: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if not email:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Email parameter is required")

    print(f"DEBUG: Incoming search query for email: '{email}'")

    if len(email) < 2:
        return []
    
    # Use ILIKE for case-insensitive partial match
    users = db.query(User).filter(User.email.ilike(f"%{email}%")).limit(10).all()
    
    print(f"DEBUG: Found {len(users)} users matching query '{email}'")
    
    # Return clean response with only required fields
    return [
        {"id": u.id, "name": u.name, "email": u.email}
        for u in users
    ]
