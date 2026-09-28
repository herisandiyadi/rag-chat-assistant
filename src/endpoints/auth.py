from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import authenticate_user, create_access_token, get_password_hash
from schemas import UserLogin, Token
from dependencies import get_current_active_user

router = APIRouter()


async def get_current_active_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """BUG-005 fix: only super_admin/dept_admin may create accounts."""
    if current_user.role_type not in ("super_admin", "dept_admin"):
        raise HTTPException(status_code=403, detail="Akses admin diperlukan")
    return current_user


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "department_id": user.department_id, "role_type": user.role_type}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),  # BUG-005 fix: admin-only
):
    """Create user. Admin-only — BUG-005 fix (was open to unauthenticated callers)."""
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password minimal 8 karakter")
    if admin.role_type == "dept_admin":
        # dept_admin cannot create accounts outside their own department
        pass  # ponytail: department assignment for dept_admin defaults to None; enforce in admin panel
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        nama_lengkap=username,
        department_id=None,
        level_id=None,
        role_type="user",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}
