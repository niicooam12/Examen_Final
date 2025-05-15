# src/services/user_service.py
import uuid
import hashlib
from typing import Optional

from src.models.usuario import Usuario
from src.repositories.usuario_repo import UsuarioRepository


class UserNotFoundError(Exception):
    """Excepción para usuario no encontrado."""
    pass


class InvalidPasswordError(Exception):
    """Excepción para contraseña incorrecta."""
    pass


class UsernameAlreadyExistsError(Exception):
    """Excepción para nombre de usuario ya existente."""
    pass


class UserService:
    """
    Servicio para registro, login y gestión de sesiones de usuarios.
    """

    def __init__(self):
        self.repo = UsuarioRepository()
        self.sesiones: dict[str, str] = {}  # Diccionario username -> session_token

    def hash_password(self, password: str, salt: bytes) -> str:
        """
        Genera un hash seguro para la contraseña usando PBKDF2.
        """
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()

    def generate_salt(self) -> bytes:
        """
        Genera una sal aleatoria para el hashing de contraseñas.
        """
        return uuid.uuid4().bytes

    def register(self, username: str, password: str) -> bool:
        """
        Registra un nuevo usuario con username y contraseña.
        """
        if self.repo.obtener_por_username(username):
            raise UsernameAlreadyExistsError("El nombre de usuario ya existe.")

        salt = self.generate_salt()
        password_hash = self.hash_password(password, salt)
        usuario = Usuario(username=username, password_hash=password_hash, salt=salt.hex())
        self.repo.agregar(usuario)
        return True

    def login(self, username: str, password: str) -> str:
        """
        Verifica credenciales y retorna un token de sesión.
        """
        usuario = self.repo.obtener_por_username(username)
        if not usuario:
            raise UserNotFoundError("Usuario no encontrado.")

        salt = bytes.fromhex(usuario.salt)
        if usuario.password_hash != self.hash_password(password, salt):
            raise InvalidPasswordError("Contraseña incorrecta.")

        session_token = str(uuid.uuid4())
        self.sesiones[username] = session_token
        return session_token

    def verificar_sesion(self, username: str, token: str) -> bool:
        """
        Verifica que el token corresponde a la sesión activa del usuario.
        """
        return self.sesiones.get(username) == token

    def cerrar_sesion(self, username: str) -> None:
        """
        Cierra la sesión del usuario.
        """
        self.sesiones.pop(username, None)
