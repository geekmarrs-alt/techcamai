import os
from pathlib import Path
from cryptography.fernet import Fernet

# API and Worker share /data volume in production.
# In dev/test, this can be overridden or will use a local file.
KEY_FILE = Path(os.environ.get("TCAI_KEY_PATH", "/data/encryption.key"))

def _get_key() -> bytes:
    key = os.environ.get("TCAI_ENCRYPTION_KEY")
    if key:
        return key.encode()

    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()

    # Generate new key if not found.
    # Note: In a multi-replica setup, this would need a shared secret manager.
    # For TECHCAMAI on a Pi/Edge box, /data is persistent and shared.
    new_key = Fernet.generate_key()
    try:
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        KEY_FILE.write_bytes(new_key)
    except Exception:
        # If we cannot write (e.g. permissions), we return the generated key
        # but it won't persist across restarts unless provided via ENV.
        pass

    return new_key

_FERNET = Fernet(_get_key())

def encrypt_password(password: str | None) -> str | None:
    if password is None:
        return None
    if not password:
        return ""
    return _FERNET.encrypt(password.encode()).decode()

def decrypt_password(token: str | None) -> str | None:
    if token is None:
        return None
    if not token:
        return ""
    try:
        return _FERNET.decrypt(token.encode()).decode()
    except Exception:
        # If decryption fails, it might be plaintext (pre-migration) or a different key.
        return token

def is_encrypted(value: str | None) -> bool:
    if not value:
        return False
    # Fernet tokens start with gAAAA
    if not value.startswith("gAAAA"):
        return False
    try:
        _FERNET.decrypt(value.encode())
        return True
    except Exception:
        return False
