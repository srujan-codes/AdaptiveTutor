"""
Auth Service — JWT creation, verification, and password hashing.
Implementation: TICKET-004
"""

# TODO: [TICKET-004] Implement auth service
# - hash_password(plain: str) → str (bcrypt)
# - verify_password(plain: str, hashed: str) → bool
# - create_access_token(user_id: str) → str (HS256, 24h, sub claim)
# - verify_token(token: str) → str (returns user_id or raises)
# - get_current_user dependency for FastAPI
