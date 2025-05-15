# src/models/encuesta.py
from __future__ import annotations
from typing import List, Dict, Union
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from src.models.voto import Voto


class Encuesta:
    def __init__(self, pregunta: str, opciones: List[str], duracion_segundos: int, tipo: str = 'simple'):
        """
        Inicializa una nueva encuesta.

        :param pregunta: Pregunta de la encuesta.
        :param opciones: Lista de opciones disponibles.
        :param duracion_segundos: Duración de la encuesta en segundos.
        :param tipo: Tipo de encuesta ('simple' o 'multiple').
        """
        self.id: UUID = uuid4()
        self.pregunta: str = pregunta
        self.opciones: List[str] = opciones
        self.duracion_segundos: int = duracion_segundos
        self.tipo: str = tipo  # 'simple' o 'multiple'
        self.creado_en: datetime = datetime.utcnow()
        self.expira_en: datetime = self.creado_en + timedelta(seconds=duracion_segundos)
        self.activa: bool = True
        self.votos: Dict[str, Union[Voto, List[Voto]]] = {}

    def agregar_voto(self, voto: Voto) -> Union[None, str]:
        """
        Agrega un voto a la encuesta.

        :param voto: Instancia de Voto a registrar.
        :return: Mensaje de error si no se puede agregar el voto, None si se agrega correctamente.
        """
        if not self.activa:
            return "Encuesta cerrada"
        
        if voto.opcion not in self.opciones:
            return "Opción no válida"
        
        votos_usuario = self.votos.get(voto.usuario)
        if self.tipo == 'simple':
            if votos_usuario is not None:
                return "El usuario ya votó"
            self.votos[voto.usuario] = voto
        else:  # Encuesta de tipo 'multiple'
            if votos_usuario is None:
                self.votos[voto.usuario] = []
            self.votos[voto.usuario].append(voto)

    def comprobar_expiracion(self) -> bool:
        """
        Verifica si la encuesta ha expirado y la marca como cerrada si es el caso.

        :return: True si la encuesta ya no está activa.
        """
        if self.activa and datetime.utcnow() >= self.expira_en:
            self.activa = False
        return not self.activa

    def obtener_resultados(self) -> Dict[str, int]:
        """
        Calcula el conteo de votos por opción.

        :return: Diccionario opción -> número de votos.
        """
        conteo: Dict[str, int] = {opt: 0 for opt in self.opciones}
        lista_votos = []
        for v in self.votos.values():
            if isinstance(v, list):
                lista_votos.extend(v)
            else:
                lista_votos.append(v)
        for voto in lista_votos:
            conteo[voto.opcion] += 1
        return conteo
