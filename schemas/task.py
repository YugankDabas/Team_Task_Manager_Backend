from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from schemas.user import UserOut


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    due_date: Optional[date] = None
    assigned_to: Optional[int] = None
    project_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[int] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    due_date: Optional[date] = None
    assigned_to: Optional[int] = None
    project_id: int
    created_at: Optional[datetime] = None
    assignee: Optional[UserOut] = None

    class Config:
        from_attributes = True
