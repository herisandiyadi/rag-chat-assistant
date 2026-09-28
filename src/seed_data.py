"""Seed data for RAG Chat Assistant - Super Admin, Departments, Levels, Users"""
from datetime import datetime
from sqlalchemy.orm import Session
from models import Department, Level, User
from auth import get_password_hash


def seed_data(db: Session):
    """Create seed data: departments, levels, and test users"""
    
    # Create departments
    departments = [
        Department(kode="hr", nama="Human Resources"),
        Department(kode="finance", nama="Finance"),
        Department(kode="legal", nama="Legal"),
        Department(kode="it", nama="Information Technology"),
    ]
    for dept in departments:
        if not db.query(Department).filter(Department.kode == dept.kode).first():
            db.add(dept)
    db.commit()
    
    # Create levels
    levels = [
        Level(angka=1, nama_jabatan="Staff"),
        Level(angka=2, nama_jabatan="Supervisor"),
        Level(angka=3, nama_jabatan="Manager"),
    ]
    for level in levels:
        if not db.query(Level).filter(Level.angka == level.angka).first():
            db.add(level)
    db.commit()
    
    # Get department and level IDs
    dept_hr = db.query(Department).filter(Department.kode == "hr").first()
    dept_finance = db.query(Department).filter(Department.kode == "finance").first()
    level_staff = db.query(Level).filter(Level.angka == 1).first()
    level_manager = db.query(Level).filter(Level.angka == 3).first()
    
    # Hash password for all users
    hashed_password = get_password_hash("admin123")
    
    # Create test users
    users = [
        # Super Admin
        User(
            username="super_admin",
            email="super_admin@company.com",
            password_hash=hashed_password,
            nama_lengkap="Super Administrator",
            department_id=None,
            level_id=None,
            role_type="super_admin",
            is_active=True
        ),
        # Admin HR
        User(
            username="admin_hr",
            email="admin_hr@company.com",
            password_hash=hashed_password,
            nama_lengkap="HR Administrator",
            department_id=dept_hr.id,
            level_id=level_manager.id,
            role_type="dept_admin",
            is_active=True
        ),
        # Manager HR
        User(
            username="manager_hr",
            email="manager_hr@company.com",
            password_hash=hashed_password,
            nama_lengkap="HR Manager",
            department_id=dept_hr.id,
            level_id=level_manager.id,
            role_type="user",
            is_active=True
        ),
        # Staff HR
        User(
            username="staff_hr",
            email="staff_hr@company.com",
            password_hash=hashed_password,
            nama_lengkap="HR Staff",
            department_id=dept_hr.id,
            level_id=level_staff.id,
            role_type="user",
            is_active=True
        ),
        # Manager Finance
        User(
            username="manager_finance",
            email="manager_finance@company.com",
            password_hash=hashed_password,
            nama_lengkap="Finance Manager",
            department_id=dept_finance.id,
            level_id=level_manager.id,
            role_type="user",
            is_active=True
        ),
    ]
    
    for user in users:
        if not db.query(User).filter(User.username == user.username).first():
            db.add(user)
    
    db.commit()
    print("Seed data created successfully!")
    return True
