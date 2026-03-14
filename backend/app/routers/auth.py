"""Auth endpoints - current user, token validation.
WO-10: Backend JWT Authentication and Authorization
"""

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser
from app.core.dependencies import get_current_user_required

router = APIRouter(prefix="/api", tags=["auth"])


@router.get("/me")
async def get_me(user: CurrentUser = Depends(get_current_user_required)):
    """Return the authenticated user. Requires valid Bearer token."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
    }
