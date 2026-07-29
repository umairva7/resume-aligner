from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
import secrets
from datetime import datetime, timedelta

from app.api import deps
from app.core.config import settings
from app.db import models

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

@router.get("/login")
async def login():
    """Redirect to Google OAuth2 consent screen."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Auth is not configured")
        
    auth_url = (
        f"{GOOGLE_AUTH_URL}?"
        f"response_type=code&"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline"
    )
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(code: str, response: Response, db: Session = Depends(deps.get_db)):
    """Handle Google OAuth2 callback, create user, and issue session cookie."""
    async with httpx.AsyncClient() as client:
        # 1. Exchange code for token
        token_res = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            }
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to retrieve token from Google")
        
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        
        # 2. Get user info
        user_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to retrieve user info from Google")
            
        user_info = user_res.json()
    
    # 3. Create or update user in DB
    google_id = user_info.get("id")
    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")
    
    user = db.query(models.User).filter(models.User.google_id == google_id).first()
    if not user:
        user = models.User(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update details in case they changed
        user.email = email
        user.name = name
        user.picture = picture
        db.commit()
        db.refresh(user)
        
    # 4. Create Session
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    user_session = models.UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at
    )
    db.add(user_session)
    db.commit()
    
    # 5. Set Cookie and redirect
    response = RedirectResponse(url=settings.FRONTEND_URL)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        secure=False  # Set to True in production with HTTPS
    )
    return response

@router.post("/logout")
async def logout(request: Request, response: Response, db: Session = Depends(deps.get_db)):
    """Logout user and delete session cookie."""
    session_token = request.cookies.get("session_token")
    if session_token:
        # Delete from DB
        db.query(models.UserSession).filter(models.UserSession.session_token == session_token).delete()
        db.commit()
        
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_me(current_user: models.User = Depends(deps.get_current_user)):
    """Get current logged in user details."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture
    }
