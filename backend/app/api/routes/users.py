from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from app.services.supabase_client import supabase
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer()

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str

@router.get("/me")
async def get_current_user():
    """Get current user info"""
    return {"message": "User endpoint working"}

@router.get("/")
async def get_users():
    """Get all users (admin only)"""
    return {"message": "Users list endpoint"}