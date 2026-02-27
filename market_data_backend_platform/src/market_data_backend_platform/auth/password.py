"""Password hashing utilities.

Uses the bcrypt library directly (not passlib, which is incompatible
with bcrypt >= 4.x) to hash and verify passwords stored as bcrypt strings.
"""

import bcrypt


def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt.

    Args:
        plain: Plain-text password to hash.

    Returns:
        Bcrypt hash string.
    """
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
    return str(hashed.decode("utf-8"))


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash.

    Args:
        plain: Plain-text password to check.
        hashed: Stored bcrypt hash.

    Returns:
        True if password matches, False otherwise.
    """
    return bool(bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8")))
