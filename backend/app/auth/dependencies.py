from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.connection import get_db
from app.database.models import User, StoreMember
from app.auth.security import decode_token

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates JWT Bearer token and returns authenticated User.
    In local development, if no header is present, provides the seeded Sharma Ji demo user.
    """
    if credentials and credentials.credentials:
        payload = decode_token(credentials.credentials)
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account inactive or not found",
            )
        return user

    # Local fallback for demo convenience if no token header provided
    demo_user = db.query(User).filter(User.email == "owner@sharmastore.com").first()
    if demo_user:
        return demo_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )

def require_store_access(
    store_id: str = "STORE_001",
    allowed_roles: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> StoreMember:
    """
    Verifies that the current user is a valid member of the store with authorized role.
    """
    membership = db.query(StoreMember).filter_by(user_id=current_user.id, store_id=store_id).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: User is not a member of store '{store_id}'",
        )

    if allowed_roles and membership.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions: Role '{membership.role}' lacks required authorization",
        )

    return membership
