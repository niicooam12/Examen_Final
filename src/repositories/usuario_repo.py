# src/repositories/usuario_repo.py
import json
import os
from typing import Optional, List  # Ensure 'Optional' and 'List' are imported for type hints
from uuid import UUID
from src.models.usuario import Usuario
# Removed unused import 'datetime'

class UsuarioRepository:
    """
    Repositorio para persistir usuarios en un archivo JSON.
    """
    def __init__(self, file_path: str = 'data/usuarios.json'):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({'usuarios': []}, f, ensure_ascii=False, indent=2)

    def _load(self) -> dict:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save(self, data: dict) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def agregar(self, usuario: Usuario) -> None:
        """Agrega un nuevo usuario al repositorio."""
        data = self._load()
        data['usuarios'].append(self._serialize_usuario(usuario))
        self._save(data)

    def obtener_por_nombre(self, nombre: str) -> Optional[Usuario]:
        """Recupera un usuario por su nombre."""
        data = self._load()
        for u in data['usuarios']:
            if u['nombre'] == nombre:
                return self._deserialize_usuario(u)
        return None

    def listar(self) -> List[Usuario]:
        """Lista todos los usuarios registrados."""
        data = self._load()
        return [self._deserialize_usuario(u) for u in data['usuarios']]

    def actualizar(self, usuario: Usuario) -> None:
        """Actualiza los datos de un usuario existente."""
        data = self._load()
        for i, u in enumerate(data['usuarios']):
            if u['nombre'] == usuario.nombre:
                data['usuarios'][i] = self._serialize_usuario(usuario)
                self._save(data)
                return
        raise KeyError(f"Usuario no encontrado: {usuario.nombre}")

    def _serialize_usuario(self, usuario: Usuario) -> dict:
        """Convierte un Usuario a diccionario serializable."""
        return {
            'nombre': usuario.nombre,
            'password_hash': usuario.password_hash,
            'id': str(usuario.id),
            'tokens': [str(t) for t in usuario.tokens]
        }

    def _deserialize_usuario(self, data: dict) -> Usuario:
        """Convierte un diccionario en instancia de Usuario."""
        usuario = Usuario(
            nombre=data['nombre'],
            password_hash=data['password_hash']
        )
        usuario.id = UUID(data['id'])
        usuario.tokens = [UUID(t) for t in data.get('tokens', [])]
        return usuario