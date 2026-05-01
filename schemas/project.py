from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from schemas.user import UserOut


class ProjectMemberOut(BaseModel):
    user_id: int
    project_id: int
    role: str
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_by: int
    created_at: Optional[datetime] = None
    members: List[ProjectMemberOut] = []
    creator: Optional[UserOut] = None

    class Config:
        from_attributes = True


class AddMemberRequest(BaseModel):
    user_id: int
    role: Optional[str] = "member"

class AddMemberByEmailRequest(BaseModel):
    email: str
    role: Optional[str] = "member"
