from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.user import User, Organization, RefreshSession, UserRole
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse, UserCreate
from app.api.deps import get_current_user
from app.services.audit_service import log_audit_event
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    org_name = user_in.organization_name or "Default Organization"
    org = db.query(Organization).filter(Organization.name == org_name).first()
    if not org:
        org = Organization(name=org_name)
        db.add(org)
        db.commit()
        db.refresh(org)

    hashed_pw = get_password_hash(user_in.password)
    user = User(
        organization_id=org.id,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pw,
        role=user_in.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_audit_event(
        db=db,
        action="USER_REGISTERED",
        entity_type="USER",
        organization_id=user.organization_id,
        user_id=user.id,
        entity_id=user.id,
        details={"email": user.email, "role": user.role.value}
    )

    return user

@router.post("/login", response_model=TokenResponse)
def login(
    login_in: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        log_audit_event(
            db=db,
            action="LOGIN_FAILED",
            entity_type="USER",
            details={"email": login_in.email},
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Update last login timestamp
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        organization_id=user.organization_id
    )
    refresh_token = create_refresh_token(subject=user.id)

    # Store refresh session in database
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_session = RefreshSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=expires_at
    )
    db.add(refresh_session)
    db.commit()

    # Set HttpOnly refresh cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False, # Set True in HTTPS production
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    )

    log_audit_event(
        db=db,
        action="LOGIN_SUCCESS",
        entity_type="USER",
        organization_id=user.organization_id,
        user_id=user.id,
        entity_id=user.id,
        ip_address=request.client.host if request.client else None
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("refresh_token")
    if not token:
        body = request.headers.get("Authorization")
        if body and body.startswith("Bearer "):
            token = body.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    session = db.query(RefreshSession).filter(
        RefreshSession.refresh_token == token,
        RefreshSession.revoked == False
    ).first()

    if not session or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or revoked"
        )

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User invalid or inactive"
        )

    new_access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        organization_id=user.organization_id
    )

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(RefreshSession).filter(
        RefreshSession.user_id == current_user.id
    ).update({"revoked": True})
    db.commit()

    response.delete_cookie("refresh_token")

    log_audit_event(
        db=db,
        action="LOGOUT",
        entity_type="USER",
        organization_id=current_user.organization_id,
        user_id=current_user.id
    )

    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
