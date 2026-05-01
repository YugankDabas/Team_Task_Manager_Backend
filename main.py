from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth, users, projects, tasks
import bcrypt
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Team Task Manager API",
    description="Full-stack Task Management with Role-Based Access Control",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Team Task Manager API"}

# Seed initial admin user if not exists
def seed_admin():
    db = SessionLocal()
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin_user:
        hashed_password = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        admin = User(
            name="Super Admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("Initial admin created: admin@example.com / admin123")
    db.close()

seed_admin()
