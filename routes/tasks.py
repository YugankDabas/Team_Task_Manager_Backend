from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from database import get_db
from models.task import Task
from models.project import Project, ProjectMember
from models.user import User
from schemas.task import TaskCreate, TaskUpdate, TaskOut
from auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskOut])
def get_all_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all tasks for projects the user is a member of, or tasks explicitly assigned to them"""
    member_projects = db.query(ProjectMember).filter(ProjectMember.user_id == current_user.id).all()
    project_ids = [mp.project_id for mp in member_projects]
    
    return db.query(Task).filter(
        or_(
            Task.project_id.in_(project_ids),
            Task.assigned_to == current_user.id
        )
    ).all()


@router.get("/project/{project_id}", response_model=List[TaskOut])
def get_project_tasks(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all tasks for a specific project"""
    # Check if user is admin or member of the project
    if current_user.role != "admin":
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(status_code=403, detail="Not a member of this project")

    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return tasks


@router.post("/", response_model=TaskOut)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        due_date=task.due_date,
        assigned_to=task.assigned_to,
        project_id=task.project_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only admin can update title/description/assignment/due_date
    # Member can only update status if they are assigned to it
    if current_user.role != "admin":
        if task.assigned_to != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned to this task")
        
        # Non-admin assigned member can only update status
        if task_update.status is not None:
            task.status = task_update.status
    else:
        # Admin can update everything
        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.status is not None:
            task.status = task_update.status
        if task_update.due_date is not None:
            task.due_date = task_update.due_date
        if task_update.assigned_to is not None:
            # Verify user exists if assigning
            user = db.query(User).filter(User.id == task_update.assigned_to).first()
            if not user:
                raise HTTPException(status_code=404, detail="Assigned user not found")
            task.assigned_to = task_update.assigned_to

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}
