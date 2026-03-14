# Security Best Practices

WO-11: Security Middleware and Rate Limiting

## Overview

- **CORS**: Configured via `cors_origins`; allow credentials for auth
- **Rate limiting**: Per-IP; Redis when available, in-memory fallback
- **Security headers**: X-Frame-Options, X-Content-Type-Options, HSTS, CSP, Referrer-Policy
- **Request ID**: `X-Request-ID` for tracing across requests

## Rate Limiting

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Max requests per minute |
| `X-RateLimit-Remaining` | Remaining requests in current window |
| `X-RateLimit-Reset` | Unix timestamp when window resets |
| `Retry-After` | Seconds until retry (on 429) |

- **Storage**: Redis (`REDIS_URL`) when available; in-memory otherwise
- **Key**: Client IP (X-Forwarded-For when behind proxy)
- **Window**: 1 minute sliding (Redis) or per-minute bucket (memory)

## Input Validation

- Use Pydantic models for all request payloads
- Add `Field(..., max_length=N)` for string length limits
- Use `Field(..., ge=0, le=1)` for numeric ranges
- Validate `equation_spec` and physics parameters with custom validators

## Security Headers

| Header | Value |
|--------|-------|
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| X-XSS-Protection | 1; mode=block |
| Strict-Transport-Security | max-age=31536000; includeSubDomains |
| Referrer-Policy | strict-origin-when-cross-origin |
| Content-Security-Policy | default-src 'self'; script-src 'self' 'unsafe-inline' |

## Authentication

- JWT validation via Cognito (WO-10)
- Use `get_current_user_required` for protected routes
- Use `check_resource_ownership` for resource-level auth

## AWS WAF (Production)

When deploying to AWS, configure WAF rules for:

- DDoS protection (rate limits at edge)
- SQL injection blocking
- XSS prevention
- Managed rule groups (AWSManagedRulesCommonRuleSet)

## Developer Checklist

- [ ] Validate all request bodies with Pydantic
- [ ] Use parameterized queries (SQLModel/ORM) — never raw SQL with user input
- [ ] Sanitize user-generated content before storage/display
- [ ] Protect sensitive routes with `get_current_user_required`
- [ ] Check resource ownership with `check_resource_ownership` before mutations
- [ ] Use HTTPS in production
- [ ] Rotate secrets (Cognito, Redis, DB) via env vars; never commit
