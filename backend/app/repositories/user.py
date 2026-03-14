"""User repository."""

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entities."""

    def __init__(self, session) -> None:
        super().__init__(session, User)

    async def get_by_cognito_sub(self, cognito_sub: str) -> User | None:
        """Get user by Cognito sub claim."""
        from sqlalchemy import select

        result = await self.session.execute(
            select(User).where(User.cognito_sub == cognito_sub)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        from sqlalchemy import select

        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def upsert_by_cognito(
        self,
        cognito_sub: str,
        email: str,
        name: str | None = None,
        role: str = "researcher",
    ) -> User:
        """Create or update User by cognito_sub. Returns User with DB id."""
        existing = await self.get_by_cognito_sub(cognito_sub)
        if existing:
            existing.email = email
            existing.name = name or existing.name
            existing.role = role
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        return await self.create(
            cognito_sub=cognito_sub,
            email=email,
            name=name,
            role=role,
        )
