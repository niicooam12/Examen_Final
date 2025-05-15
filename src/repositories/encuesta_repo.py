# src/repositories/encuesta_repo.py
import json
import os
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.models.encuesta import Encuesta


class EncuestaRepository:
    """
    Repositorio para persistir encuestas y votos en un archivo JSON.
    """
    def __init__(self, file_path: str = 'data/encuestas.json'):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({'encuestas': []}, f, ensure_ascii=False, indent=2)

    def _load(self) -> dict:
        """Carga los datos del archivo JSON."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'encuestas': []}

    def _save(self, data: dict) -> None:
        """Guarda los datos en el archivo JSON."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise RuntimeError(f"Error al guardar los datos: {e}")

    def agregar(self, encuesta: Encuesta) -> None:
        """Agrega una nueva encuesta al repositorio."""
        data = self._load()
        data['encuestas'].append(self._serialize_encuesta(encuesta))
        self._save(data)

    def obtener_por_id(self, encuesta_id: UUID) -> Optional[Encuesta]:
        """Recupera una encuesta por su ID."""
        data = self._load()
        for enc in data['encuestas']:
            if enc['id'] == str(encuesta_id):
                return self._deserialize_encuesta(enc)
        return None

    def listar(self, activas_solo: bool = False) -> List[Encuesta]:
        """Lista todas las encuestas, opcionalmente solo las activas."""
        data = self._load()
        encuestas = [self._deserialize_encuesta(enc) for enc in data['encuestas']]
        if activas_solo:
            return [e for e in encuestas if e.activa]
        return encuestas

    def actualizar(self, encuesta: Encuesta) -> None:
        """Actualiza una encuesta existente en el repositorio."""
        data = self._load()
        for i, enc in enumerate(data['encuestas']):
            if enc['id'] == str(encuesta.id):
                data['encuestas'][i] = self._serialize_encuesta(encuesta)
                self._save(data)
                return
        raise KeyError(f"Encuesta no encontrada: {encuesta.id}")

    def _serialize_encuesta(self, encuesta: Encuesta) -> dict:
        """Convierte una Encuesta a un dict serializable."""
        return {
            'id': str(encuesta.id),
            'pregunta': encuesta.pregunta,
            'opciones': encuesta.opciones,
            'duracion_segundos': encuesta.duracion_segundos,
            'tipo': encuesta.tipo,
            'creado_en': encuesta.creado_en.isoformat(),
            'expira_en': encuesta.expira_en.isoformat(),
            'activa': encuesta.activa,
        }

    def _deserialize_encuesta(self, data: dict) -> Encuesta:
        """Convierte un dict a una instancia de Encuesta."""
        try:
            encuesta = Encuesta(
                pregunta=data['pregunta'],
                opciones=data['opciones'],
                duracion_segundos=data['duracion_segundos'],
                tipo=data.get('tipo', 'simple')
            )
            encuesta.id = UUID(data['id'])
            encuesta.creado_en = datetime.fromisoformat(data['creado_en'])
            encuesta.expira_en = datetime.fromisoformat(data['expira_en'])
            encuesta.activa = data['activa']
            return encuesta
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error al deserializar la encuesta: {e}")
