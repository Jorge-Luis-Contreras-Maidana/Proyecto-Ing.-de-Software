import time
import pyotp


class TOTPService:
    @staticmethod
    def generate_secret() -> str:
        return pyotp.random_base32()

    @staticmethod
    def get_current_code_and_ttl(secret: str):
        totp = pyotp.TOTP(secret, interval=20)  # Renovación cada 20 segundos
        code = totp.now()
        expires_in = 20 - (int(time.time()) % 20)
        return code, expires_in

    @staticmethod
    def verify_code(secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret, interval=20)
        return totp.verify(code, valid_window=1)