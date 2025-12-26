import os
import hashlib
import hmac
from base64 import b64encode, b64decode

_ITERATIONS = 200_000
_ALGO = "sha256"
_SALT_BYTES = 16

def hash_password(password: str) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("Senha inválida.")
    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(_ALGO, password.encode("utf-8"), salt, _ITERATIONS)
    return f"pbkdf2:{_ALGO}:{_ITERATIONS}:{b64encode(salt).decode()}:{b64encode(dk).decode()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        parts = stored.split(":")
        if len(parts) != 5 or parts[0] != "pbkdf2":
            return False
        _, algo, iters, salt_b64, dk_b64 = parts
        iters = int(iters)
        salt = b64decode(salt_b64.encode())
        dk_expected = b64decode(dk_b64.encode())
        dk = hashlib.pbkdf2_hmac(algo, password.encode("utf-8"), salt, iters)
        return hmac.compare_digest(dk, dk_expected)
    except Exception:
        return False
