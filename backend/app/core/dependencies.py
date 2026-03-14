"""FastAPI dependency injection - database session, current user.
WO-10: Backend JWT Authentication and Authorization
"""

from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    CurrentUser,
    extract_bearer_token,
    resolve_user_from_api_key,
    resolve_user_from_token,
)
from app.core.database import async_session_factory
from app.core.exceptions import ForbiddenError, UnauthorizedError


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield database session for request scope."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CurrentUser | None:
    """Optional auth: validate JWT or API key if present, return CurrentUser or None."""
    token = extract_bearer_token(request)
    if not token:
        return None
    from app.services.api_key_service import is_api_key_format

    if is_api_key_format(token):
        user = await resolve_user_from_api_key(token, session)
        if user:
            request.state.api_key_id = user.id  # for rate limit and usage logging
        return user
    try:
        return resolve_user_from_token(token)
    except UnauthorizedError:
        return None


async def get_current_user_required(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[CurrentUser | None, Depends(get_current_user)],
) -> CurrentUser:
    """Required auth: raise 401 when no valid token. Syncs Cognito user to DB on first auth."""
    if user is None:
        raise UnauthorizedError("Authentication required")
    if user.cognito_sub == "mock-sub":
        return user
    from app.repositories.user import UserRepository

    repo = UserRepository(session)
    db_user = await repo.upsert_by_cognito(
        cognito_sub=user.cognito_sub,
        email=user.email,
        name=user.name,
        role=user.role,
    )
    return CurrentUser(
        id=str(db_user.id),
        email=db_user.email,
        cognito_sub=db_user.cognito_sub,
        name=db_user.name,
        role=db_user.role,
    )


def check_resource_ownership(
    resource: Any,
    user: CurrentUser,
    owner_attr: str = "author_id",
    allow_admin: bool = True,
) -> None:
    """Raise ForbiddenError if user does not own the resource. Admins bypass if allow_admin."""
    if allow_admin and user.role == "admin":
        return
    owner_id = getattr(resource, owner_attr, None)
    if owner_id is None:
        raise ForbiddenError("Resource has no owner")
    if str(owner_id) != str(user.id):
        raise ForbiddenError("You do not own this resource")


def require_role(*allowed_roles: str):
    """Dependency factory: require user to have one of the given roles."""

    async def _check(
        user: Annotated[CurrentUser, Depends(get_current_user_required)],
    ) -> CurrentUser:
        if user.role not in allowed_roles:
            raise ForbiddenError(f"Requires one of: {', '.join(allowed_roles)}")
        return user

    return _check


# Repository dependencies
def get_theory_repository(session: AsyncSession):
    """Yield TheoryRepository for request scope."""
    from app.repositories.theory import TheoryRepository
    return TheoryRepository(session)


def get_user_repository(session: AsyncSession):
    """Yield UserRepository for request scope."""
    from app.repositories.user import UserRepository
    return UserRepository(session)
