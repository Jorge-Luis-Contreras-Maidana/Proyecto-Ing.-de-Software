"""Hash de contraseñas con Argon2. Nunca se guarda texto plano. RNF-02.2."""
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()
_DUMMY_HASH = _hasher.hash("contrasena-de-relleno")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(stored_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def burn_verification_time(password: str) -> None:
    """Verifica contra un hash falso para que 'usuario inexistente' tarde lo mismo que 'contraseña incorrecta'."""
    verify_password(_DUMMY_HASH, password)
