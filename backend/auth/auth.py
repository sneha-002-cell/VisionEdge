from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.database.models import User

from backend.auth.schemas import (
    UserRegister,
    UserLogin,
)

from backend.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.get("/")
def home():
    return {"message": "Authentication API Ready"}


# ---------------------------
# User Registration
# ---------------------------
@router.post("/register")
def register(user: UserRegister):

    db: Session = SessionLocal()

    # Check if email already exists
    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.close()

    return {
        "message": "User registered successfully"
    }


# ---------------------------
# User Login
# ---------------------------
@router.post("/login")
def login(user: UserLogin):

    db: Session = SessionLocal()

    # Find user by email
    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing:
        db.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        user.password,
        existing.password
    ):
        db.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = create_access_token(
        {
            "sub": existing.email
        }
    )

    db.close()

    return {
        "access_token": token,
        "token_type": "bearer"
    }