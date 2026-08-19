from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.logger import logger

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# Bearer token scheme — auto_error=False allows anonymous access
security_scheme = HTTPBearer(auto_error=False)

# Demo token for frontend testing without real auth
DEMO_TOKENS = {
    "demo-token-xyz",
    "demo_token",
    "test-token",
}

def hash_password(password: str) -> str:
    """Hash a password securely."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(
            minutes=getattr(settings, 'JWT_EXPIRE_MINUTES', 10080)
        )
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    return jwt.encode(
        to_encode,
        getattr(settings, 'JWT_SECRET', 'edumind-secret-key-2024'),
        algorithm=getattr(settings, 'JWT_ALGORITHM', 'HS256')
    )

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token."""
    # Allow demo tokens in development
    if token in DEMO_TOKENS:
        logger.debug("Demo token accepted")
        return {
            "sub":   "demo-user-001",
            "email": "demo@edumind.ai",
            "role":  "admin",
            "exp":   None
        }

    try:
        payload = jwt.decode(
            token,
            getattr(settings, 'JWT_SECRET', 'edumind-secret-key-2024'),
            algorithms=[
                getattr(settings, 'JWT_ALGORITHM', 'HS256')
            ]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Token decode failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        security_scheme
    )
) -> Dict[str, Any]:
    """Get current authenticated user from token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return {
        "user_id": user_id,
        "email":   payload.get("email"),
        "role":    payload.get("role", "student"),
        "exp":     payload.get("exp")
    }

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        security_scheme
    )
) -> Dict[str, Any]:
    """
    Get current user if authenticated.
    Returns anonymous user dict if no token provided.
    Never raises — always returns a valid dict.
    """
    if not credentials:
        return {
            "user_id": "anonymous",
            "email":   "anonymous@edumind.ai",
            "role":    "user",
            "exp":     None
        }

    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub", "anonymous")
        return {
            "user_id": user_id,
            "email":   payload.get("email", ""),
            "role":    payload.get("role", "user"),
            "exp":     payload.get("exp")
        }
    except HTTPException:
        # Token invalid — return anonymous instead of error
        return {
            "user_id": "anonymous",
            "email":   "anonymous@edumind.ai",
            "role":    "user",
            "exp":     None
        }
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return {
            "user_id": "anonymous",
            "email":   "anonymous@edumind.ai",
            "role":    "user",
            "exp":     None
        }

def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require admin role."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_role(role: str):
    """Require specific role — factory function."""
    async def _require_role(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        if current_user.get("role") != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        return current_user
    return _require_role
