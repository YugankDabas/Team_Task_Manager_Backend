from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.project import Project, ProjectMember
from models.user import User
from schemas.user import UserOut
from schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, AddMemberRequest, ProjectMemberOut, AddMemberByEmailRequest
from auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectOut])
def get_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Both admins and members only see projects they are a part of
    member_projects = db.query(ProjectMember).filter(ProjectMember.user_id == current_user.id).all()
    project_ids = [mp.project_id for mp in member_projects]
    return db.query(Project).filter(Project.id.in_(project_ids)).all()


@router.post("/", response_model=ProjectOut)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    new_project = Project(
        name=project.name,
        description=project.description,
        created_by=current_user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Add creator as admin member to the project
    member = ProjectMember(user_id=current_user.id, project_id=new_project.id, role="admin")
    db.add(member)
    db.commit()
    
    # Reload with relationships
    db.refresh(new_project)
    return new_project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_update.name is not None:
        project.name = project_update.name
    if project_update.description is not None:
        project.description = project_update.description

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"detail": "Project deleted successfully"}


@router.post("/{project_id}/members", response_model=ProjectMemberOut)
def add_project_member(
    project_id: int,
    member_req: AddMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user = db.query(User).filter(User.id == member_req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member_req.user_id
    ).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this project")

    new_member = ProjectMember(
        user_id=member_req.user_id,
        project_id=project_id,
        role=member_req.role
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member


@router.post("/{project_id}/add-member", response_model=ProjectMemberOut)
def add_project_member_by_email(
    project_id: int,
    member_req: AddMemberByEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user = db.query(User).filter(User.email == member_req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found with this email")

    existing_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id
    ).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this project")

    new_member = ProjectMember(
        user_id=user.id,
        project_id=project_id,
        role=member_req.role
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member


@router.get("/{project_id}/members", response_model=List[UserOut])
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Optional: ensure current_user is a member or admin
    if current_user.role != "admin":
        is_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        ).first()
        if not is_member:
            raise HTTPException(status_code=403, detail="Not a member of this project")

    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    users = [m.user for m in members if m.user]
    return users


@router.delete("/{project_id}/members/{user_id}")
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found in project")

    db.delete(member)
    db.commit()
    return {"detail": "Member removed successfully"}
