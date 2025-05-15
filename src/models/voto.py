# src/models/voto.py
from uuid import uuid4, UUID
from datetime import datetime

class Voto:
    def __init__(self, encuesta_id, usuario, opcion, realizado_en=None, token_id=None, id=None):
        if not isinstance(encuesta_id, UUID):
            raise ValueError("El 'encuesta_id' debe ser un UUID válido.")
        if not isinstance(usuario, str) or not usuario.strip():
            raise ValueError("El 'usuario' debe ser una cadena no vacía.")
        if not isinstance(opcion, str) or not opcion.strip():
            raise ValueError("La 'opcion' debe ser una cadena no vacía.")

        self.encuesta_id = encuesta_id
        self.usuario = usuario.strip()
        self.opcion = opcion.strip()
        self.realizado_en = realizado_en or datetime.utcnow()
        self.token_id = token_id or uuid4()
        self.id = id or uuid4()

    def metadatos(self):
        """
        Devuelve los metadatos del voto.

        :return: Diccionario con detalles del voto.
        """
        return {
            "id_voto": str(self.id),
            "encuesta_id": str(self.encuesta_id),
            "usuario": self.usuario,
            "opcion": self.opcion,
            "realizado_en": self.realizado_en.isoformat(),
            "token_id": str(self.token_id)
        }