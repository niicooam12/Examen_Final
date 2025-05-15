# src/repositories/nft_repo.py
import json
import os
from typing import List, Optional
from uuid import UUID
from src.models.token_nft import TokenNFT
from datetime import datetime


class NFTRepository:
    """
    Repositorio para persistir tokens NFT en un archivo JSON.
    """

    def __init__(self, file_path: str = 'data/nfts.json'):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({'tokens': []}, f, ensure_ascii=False, indent=2)

    def _load(self) -> dict:
        """Carga los datos desde el archivo JSON."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Error al cargar el archivo: {e}")

    def _save(self, data: dict) -> None:
        """Guarda los datos en el archivo JSON."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise RuntimeError(f"Error al guardar el archivo: {e}")

    def agregar(self, token: TokenNFT) -> None:
        """Agrega un nuevo token NFT al repositorio."""
        if not isinstance(token, TokenNFT):
            raise ValueError("El objeto proporcionado no es una instancia de TokenNFT.")
        data = self._load()
        data['tokens'].append(self._serialize_token(token))
        self._save(data)

    def obtener_por_id(self, token_id: UUID) -> Optional[TokenNFT]:
        """Recupera un token por su ID."""
        if not isinstance(token_id, UUID):
            raise ValueError("El token_id debe ser una instancia de UUID.")
        data = self._load()
        for t in data['tokens']:
            if t['token_id'] == str(token_id):
                return self._deserialize_token(t)
        return None

    def listar_por_usuario(self, usuario: str) -> List[TokenNFT]:
        """Lista todos los tokens de un usuario."""
        if not isinstance(usuario, str):
            raise ValueError("El usuario debe ser una cadena de texto.")
        data = self._load()
        tokens = [
            self._deserialize_token(t) for t in data['tokens'] if t['propietario'] == usuario
        ]
        return tokens

    def transferir(self, token_id: UUID, nuevo_propietario: str) -> None:
        """Transfiere la propiedad de un token."""
        if not isinstance(token_id, UUID):
            raise ValueError("El token_id debe ser una instancia de UUID.")
        if not isinstance(nuevo_propietario, str):
            raise ValueError("El nuevo propietario debe ser una cadena de texto.")
        data = self._load()
        for i, t in enumerate(data['tokens']):
            if t['token_id'] == str(token_id):
                data['tokens'][i]['propietario'] = nuevo_propietario
                self._save(data)
                return
        raise KeyError(f"Token no encontrado: {token_id}")

    def _serialize_token(self, token: TokenNFT) -> dict:
        """Convierte un TokenNFT a dict serializable."""
        return {
            'token_id': str(token.token_id),
            'encuesta_id': str(token.encuesta_id),
            'opcion': token.opcion,
            'propietario': token.propietario,
            'emitido_en': token.emitido_en.isoformat()
        }

    def _deserialize_token(self, data: dict) -> TokenNFT:
        """Convierte un dict a instancia TokenNFT."""
        try:
            token = TokenNFT(
                encuesta_id=UUID(data['encuesta_id']),
                opcion=data['opcion'],
                propietario=data['propietario']
            )
            token.token_id = UUID(data['token_id'])
            token.emitido_en = datetime.fromisoformat(data['emitido_en'])
            return token
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error al deserializar el token: {e}")
