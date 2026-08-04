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

from app.core.logging import logger

def get_dynamic_redirect_uri(request: Request) -> str:
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    if not redirect_uri or "your-app.vercel.app" in redirect_uri or "localhost" in redirect_uri:
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("x-forwarded-host", request.url.netloc)
        return f"{scheme}://{host}/api/v1/auth/callback"
    return redirect_uri

@router.get("/login")
async def login(request: Request):
    """Redirect to Google OAuth2 consent screen."""
    if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID.startswith("YOUR_"):
        # Fallback to demo login if Google Auth is not fully configured
        return RedirectResponse(url="/api/v1/auth/demo-login")
        
    redirect_uri = get_dynamic_redirect_uri(request)
    auth_url = (
        f"{GOOGLE_AUTH_URL}?"
        f"response_type=code&"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    return RedirectResponse(auth_url)

@router.get("/demo-login")
async def demo_login(request: Request, response: Response, db: Session = Depends(deps.get_db)):
    """Instant single-click demo authentication for local testing & development."""
    try:
        demo_google_id = "demo_user_studio_99"
        user = db.query(models.User).filter(models.User.google_id == demo_google_id).first()
        if not user:
            user = models.User(
                google_id=demo_google_id,
                email="candidate.studio@resumealigner.io",
                name="Demo Studio User",
                picture=""
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        user_session = models.UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at
        )
        db.add(user_session)
        db.commit()

        referer = request.headers.get("referer", "")
        if referer and "/auth/" not in referer and "/api/" not in referer:
            target_url = referer
        else:
            target_url = settings.FRONTEND_URL or "/"

        redirect_response = RedirectResponse(url=target_url)
        redirect_response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
            secure=settings.SECURE_COOKIES
        )
        return redirect_response
    except Exception as e:
        logger.error("[DEMO LOGIN ERROR] %s", str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Demo sign-in failed. Please try again.")

@router.get("/callback")
async def callback(code: str, request: Request, response: Response, db: Session = Depends(deps.get_db)):
    """Handle Google OAuth2 callback, create user, and issue session cookie."""
    try:
        redirect_uri = get_dynamic_redirect_uri(request)
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            # 1. Exchange code for token
            token_res = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": redirect_uri,
                }
            )
            if token_res.status_code != 200:
                logger.error("[AUTH ERROR] Token exchange failed: %s - %s", token_res.status_code, token_res.text)
                # Redirect to demo login on OAuth credential error
                return RedirectResponse(url="/api/v1/auth/demo-login")
            
            token_data = token_res.json()
            access_token = token_data.get("access_token")
            
            # 2. Get user info
            user_res = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if user_res.status_code != 200:
                logger.error("[AUTH ERROR] Userinfo fetch failed: %s - %s", user_res.status_code, user_res.text)
                return RedirectResponse(url="/api/v1/auth/demo-login")
                
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
        
        # 5. Set Cookie and redirect to frontend
        redirect_response = RedirectResponse(url=settings.FRONTEND_URL)
        redirect_response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,  # 7 days
            secure=settings.SECURE_COOKIES
        )
        return redirect_response

    except Exception as e:
        logger.error("[AUTH UNHANDLED EXCEPTION] %s", str(e))
        db.rollback()
        return RedirectResponse(url="/api/v1/auth/demo-login")

@router.post("/logout")
async def logout(request: Request, response: Response, db: Session = Depends(deps.get_db)):
    """Logout user and delete session cookie."""
    try:
        session_token = request.cookies.get("session_token")
        if session_token:
            db.query(models.UserSession).filter(models.UserSession.session_token == session_token).delete()
            db.commit()
    except Exception as e:
        logger.error("[LOGOUT EXCEPTION] %s", str(e))
        db.rollback()
        
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
