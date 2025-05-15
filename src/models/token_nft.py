# src/models/token_nft.py
from uuid import uuid4, UUID
from datetime import datetime

class TokenNFT:
    def __init__(self, encuesta_id: UUID, opcion: str, propietario: str):
        self.encuesta_id = encuesta_id
        self.opcion = opcion
        self.propietario = propietario
        self.emitido_en = datetime.utcnow()
        self.token_id = uuid4()

    def metadatos(self) -> dict:
        """
        Devuelve un diccionario con los metadatos del token.

        :return: Metadatos serializables del TokenNFT.
        """
        return {
            "token_id": str(self.token_id),
            "encuesta_id": str(self.encuesta_id),
            "opcion": self.opcion,
            "propietario": self.propietario,
            "emitido_en": self.emitido_en.isoformat()
        }

    def __repr__(self):
        return (
            f"TokenNFT(token_id={self.token_id}, encuesta_id={self.encuesta_id}, "
            f"opcion={self.opcion}, propietario={self.propietario}, emitido_en={self.emitido_en})"
        )
