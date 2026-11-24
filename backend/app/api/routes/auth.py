import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database.connection import get_db
from app.database.models import User, Store, StoreMember
from app.database.repository import BusinessRepository
from app.auth.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.auth.dependencies import get_current_user, require_store_access
from app.api.schemas.auth_schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse,
    RefreshTokenRequest, StoreCreateRequest, AddMemberRequest,
    UserInfo, StoreInfo
)

router = APIRouter(prefix="/auth", tags=["Authentication & Multi-Tenant Workspaces"])

@router.post("/register", response_model=TokenResponse)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    repo = BusinessRepository(db)
    existing_user = repo.get_user_by_email(req.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Create new user
    pwd_hash = hash_password(req.password)
    user = repo.create_user(email=req.email, password_hash=pwd_hash, full_name=req.full_name)

    # Create primary store workspace for the user
    new_store_id = f"STORE_{uuid.uuid4().hex[:8].upper()}"
    store = repo.create_store(
        store_id=new_store_id,
        name=req.store_name or "My Kirana Store",
        location=req.store_location or "Ranchi, Jharkhand",
        owner_name=req.full_name
    )

    # Assign OWNER role
    repo.add_store_member(user_id=user.id, store_id=new_store_id, role="OWNER")

    # Generate JWT tokens
    token_data = {"sub": user.email, "user_id": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    stores = repo.get_user_stores(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active
        },
        "stores": stores
    }

@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    repo = BusinessRepository(db)
    user = repo.get_user_by_email(req.email)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact system administrator."
        )

    token_data = {"sub": user.email, "user_id": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    stores = repo.get_user_stores(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active
        },
        "stores": stores
    }

@router.get("/me")
def get_current_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = BusinessRepository(db)
    stores = repo.get_user_stores(current_user.id)
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active
        },
        "stores": stores
    }

@router.post("/refresh")
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    email = payload.get("sub")
    repo = BusinessRepository(db)
    user = repo.get_user_by_email(email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive."
        )

    token_data = {"sub": user.email, "user_id": user.id}
    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "Bearer"
    }

@router.post("/logout")
def logout():
    return {"status": "SUCCESS", "message": "Successfully logged out."}

@router.get("/stores")
def get_my_stores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = BusinessRepository(db)
    return repo.get_user_stores(current_user.id)

@router.post("/stores")
def create_new_store(
    req: StoreCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = BusinessRepository(db)
    new_store_id = f"STORE_{uuid.uuid4().hex[:8].upper()}"
    store = repo.create_store(
        store_id=new_store_id,
        name=req.name,
        location=req.location or "Ranchi, Jharkhand",
        owner_name=current_user.full_name
    )
    repo.add_store_member(user_id=current_user.id, store_id=new_store_id, role="OWNER")
    return {
        "status": "SUCCESS",
        "message": f"Store workspace '{req.name}' created successfully.",
        "store": {
            "store_id": store.store_id,
            "name": store.name,
            "location": store.location,
            "role": "OWNER"
        }
    }

@router.get("/stores/{store_id}/members")
def get_store_members(
    store_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure current user has access to store
    require_store_access(store_id=store_id, current_user=current_user, db=db)
    repo = BusinessRepository(db)
    return repo.get_store_members(store_id)

@router.post("/stores/{store_id}/members")
def add_store_member(
    store_id: str,
    req: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only OWNER or MANAGER can add members
    require_store_access(store_id=store_id, allowed_roles=["OWNER", "MANAGER"], current_user=current_user, db=db)
    repo = BusinessRepository(db)
    target_user = repo.get_user_by_email(req.email)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{req.email}' not found. They must register first."
        )

    member = repo.add_store_member(user_id=target_user.id, store_id=store_id, role=req.role)
    return {
        "status": "SUCCESS",
        "message": f"Assigned role '{req.role}' to {req.email} for store '{store_id}'."
    }
