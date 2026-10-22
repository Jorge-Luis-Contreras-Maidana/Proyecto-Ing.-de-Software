import time

import pyotp

# La ventana TOTP dura 20 segundos: el código se renueva en cada ventana.
INTERVALO = 20


class TOTPService:
    @staticmethod
    def generate_secret() -> str:
        return pyotp.random_base32()

    @staticmethod
    def current_window(now: float | None = None) -> int:
        """Identificador de la ventana TOTP actual. Sirve para impedir reutilizar un código."""
        momento = time.time() if now is None else now
        return int(momento // INTERVALO)

    @staticmethod
    def get_current_code_and_ttl(secret: str):
        totp = pyotp.TOTP(secret, interval=INTERVALO)
        code = totp.now()
        expires_in = INTERVALO - (int(time.time()) % INTERVALO)
        return code, expires_in

    @staticmethod
    def verify_code(secret: str, code: str, valid_window: int = 1) -> bool:
        totp = pyotp.TOTP(secret, interval=INTERVALO)
        return totp.verify(code, valid_window=valid_window)

    @staticmethod
    def ventana_del_codigo(secret: str, code: str) -> int | None:
        """Ventana TOTP a la que pertenece el código, o None si no corresponde a ninguna.

        Se aceptan la ventana actual y las inmediatamente vecinas (±20 s) para
        tolerar el desfase entre el momento en que el estudiante ve su código y
        el momento en que el docente lo escanea. Devolver la ventana del propio
        código (y no la del reloj) es lo que permite detectar la reutilización.
        """
        totp = pyotp.TOTP(secret, interval=INTERVALO)
        ahora = int(time.time())
        for desplazamiento in (0, -INTERVALO, INTERVALO):
            if totp.at(ahora + desplazamiento) == code:
                return (ahora + desplazamiento) // INTERVALO
        return None
