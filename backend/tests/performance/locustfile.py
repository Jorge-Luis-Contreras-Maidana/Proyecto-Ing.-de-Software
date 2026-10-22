"""Pruebas de carga con Locust.

Simula el uso real en la hora de entrada: muchos docentes escaneando
credenciales a la vez y varias familias consultando la asistencia.

Uso:
    cd backend
    ..\venv\\Scripts\\locust -f tests/performance/locustfile.py --host http://localhost:5000

Para una prueba rápida y sin interfaz:
    ..\venv\\Scripts\\locust -f tests/performance/locustfile.py --headless \
        -u 20 -r 5 -t 60s --host http://localhost:5000
"""
import random

from locust import HttpUser, between, task

USUARIOS = [
    ("directora.mquispe", "Demo1234!"),
    ("prof.cmamani", "Demo1234!"),
    ("prof.rchoque", "Demo1234!"),
    ("tutor1", "Demo1234!"),
    ("estudiante1", "Demo1234!"),
]

ID_ESTUDIANTES = list(range(1, 33))


class UsuarioSESCO(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        usuario, contrasena = random.choice(USUARIOS)
        self.cliente.headers.update({"Content-Type": "application/json"})
        respuesta = self.client.post(
            "/api/auth/login", json={"nombre_usuario": usuario, "contrasena": contrasena}
        )
        if respuesta.status_code == 200:
            self.token = respuesta.json()["access_token"]
            self.cliente.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            self.token = None

    @task(3)
    def listar_estudiantes(self):
        """Las familias y los docentes buscan estudiantes en la lista."""
        self.client.get("/api/students", params={"per_page": 20})

    @task(3)
    def ver_historial(self):
        """Consulta del historial de asistencia de un estudiante."""
        self.client.get(f"/api/attendance/estudiante/{random.choice(ID_ESTUDIANTES)}")

    @task(2)
    def ver_sesiones_de_hoy(self):
        """El docente abre su lista de clases del día."""
        self.client.get("/api/attendance/hoy")

    @task(1)
    def ver_mi_credencial(self):
        """El estudiante abre su credencial QR."""
        self.client.get("/api/qr/me/code")

    @task(1)
    def ver_notificaciones(self):
        """Las familias revisan sus avisos."""
        self.client.get("/api/notifications")
