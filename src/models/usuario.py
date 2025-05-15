# src/models/usuario.py
from uuid import uuid4, UUID
from typing import List

class Usuario:
    def __init__(self, nombre: str, password_hash: str):
        """
        Inicializa un nuevo usuario.

        :param nombre: Nombre del usuario.
        :param password_hash: Hash de la contraseña del usuario.
        """
        if not nombre or not isinstance(nombre, str):
            raise ValueError("El nombre debe ser una cadena no vacía.")
        if not password_hash or not isinstance(password_hash, str):
            raise ValueError("El password_hash debe ser una cadena no vacía.")
        
        self.id: UUID = uuid4()
        self.nombre: str = nombre
        self.password_hash: str = password_hash
        self.tokens: List[UUID] = []

    def agregar_token(self, token_id: UUID) -> None:
        """
        Agrega un token NFT al usuario.

        :param token_id: UUID del token a agregar.
        """
        if not isinstance(token_id, UUID):
            raise ValueError("El token_id debe ser una instancia de UUID.")
        if token_id in self.tokens:
            raise ValueError("El token ya está asociado a este usuario.")
        self.tokens.append(token_id)

    def remover_token(self, token_id: UUID) -> None:
        """
        Elimina un token NFT del usuario.

        :param token_id: UUID del token a remover.
        :raises ValueError: si el token no pertenece al usuario.
        """
        if not isinstance(token_id, UUID):
            raise ValueError("El token_id debe ser una instancia de UUID.")
        try:
            self.tokens.remove(token_id)
        except ValueError:
            raise ValueError("El token no pertenece a este usuario.")

    def listar_tokens(self) -> List[UUID]:
        """
        Devuelve la lista de tokens asociados al usuario.

        :return: Lista de UUIDs de los tokens.
        """
        return self.tokens.copy()

    def __repr__(self) -> str:
        """
        Representación en cadena del usuario.

        :return: Una cadena representativa del usuario.
        """
        return f"Usuario(id={self.id}, nombre={self.nombre}, tokens={len(self.tokens)})"