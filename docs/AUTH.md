# Backend Authentication and Authorization

WO-10: JWT token validation, Cognito integration, RBAC.

## Overview

- **JWT extraction**: Bearer token from `Authorization` header
- **Cognito validation**: RS256 signature, issuer, audience, expiration
- **Mock tokens**: `mock-jwt-*` for local dev (no Cognito)
- **User sync**: First Cognito auth creates/updates User in PostgreSQL
- **RBAC**: Roles `admin`, `researcher`, `viewer` from `cognito:groups`

## Dependencies

### Optional auth: `get_current_user`

Returns `CurrentUser | None`. Use when the endpoint works with or without a user.

```python
@router.get("/public")
async def public(user: CurrentUser | None = Depends(get_current_user)):
    if user:
        return {"greeting": f"Hello, {user.email}"}
    return {"greeting": "Hello, guest"}
```

### Required auth: `get_current_user_required`

Raises `401 Unauthorized` when no valid token. Syncs Cognito user to DB on first auth.

```python
@router.get("/api/me")
async def get_me(user: CurrentUser = Depends(get_current_user_required)):
    return {"id": user.id, "email": user.email, "role": user.role}
```

### Role check: `require_role(*roles)`

Requires one of the given roles. Raises `403 Forbidden` otherwise.

```python
@router.delete("/admin/users/{id}")
async def delete_user(
    _: None = Depends(require_role("admin")),
):
    ...
```

### Resource ownership: `check_resource_ownership`

Call in route body after fetching the resource. Raises `403` if the user does not own it. Admins bypass by default.

```python
@router.delete("/theories/{theory_id}")
async def delete_theory(
    theory_id: str,
    user: CurrentUser = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_db),
):
    theory = await get_theory_or_404(session, theory_id)
    check_resource_ownership(theory, user, owner_attr="author_id")
    await theory_repo.delete(theory_id)
```

Use `allow_admin=False` to enforce ownership even for admins.

## CurrentUser

| Field        | Description                                  |
|-------------|----------------------------------------------|
| `id`        | DB User.id (UUID) or `"mock-dev"` for mock   |
| `email`     | User email                                  |
| `cognito_sub` | Cognito sub claim                         |
| `name`      | Display name (may be None)                  |
| `role`      | `admin` \| `researcher` \| `viewer`         |

## Configuration

| Env var                 | Purpose                            |
|-------------------------|------------------------------------|
| `COGNITO_USER_POOL_ID`  | Cognito User Pool ID               |
| `COGNITO_CLIENT_ID`     | App client ID (audience)            |
| `COGNITO_JWKS_URL`      | JWKS endpoint for key fetch        |
| `COGNITO_REGION`        | AWS region (default: us-east-1)    |

Without Cognito: use mock tokens (`mock-jwt-*`) for local dev.

## Errors

| Status | Cause                                           |
|--------|--------------------------------------------------|
| 401    | No token, invalid token, expired, wrong config   |
| 403    | Valid token but insufficient role or ownership   |
