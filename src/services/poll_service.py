# src/services/poll_service.py
from uuid import UUID
from datetime import datetime
from typing import List, Dict, Optional

from src.models.encuesta import Encuesta
from src.models.voto import Voto
from src.repositories.encuesta_repo import EncuestaRepository
from src.patterns.observer import SujetoObservable
from src.patterns.factory import PollFactory
from src.patterns.strategy import DesempateStrategy, TextoStrategy
from src.services.nft_service import NFTService


class PollService(SujetoObservable):
    """
    Servicio para gestionar encuestas: creación, votación, cierre y resultados.
    """

    def __init__(self,
                desempate_strategy: Optional[DesempateStrategy] = None,
                presentacion_strategy: Optional[TextoStrategy] = None):
        super().__init__()
        self.repo = EncuestaRepository()
        self.nft_service = NFTService()
        self.desempate_strategy = desempate_strategy or DesempateStrategy()
        self.presentacion_strategy = presentacion_strategy or TextoStrategy()

    def now(self) -> datetime:
        """Devuelve la hora actual en UTC."""
        return datetime.utcnow()

    def create_poll(self, pregunta: str, opciones: List[str],
                    duracion_segundos: int, tipo: str = 'simple') -> Encuesta:
        """
        Crea una nueva encuesta y la persiste.
        """
        if not pregunta or not opciones or duracion_segundos <= 0:
            raise ValueError("Parámetros inválidos para crear la encuesta.")
        encuesta = PollFactory.create_poll(pregunta, opciones, duracion_segundos, tipo)
        self.repo.agregar(encuesta)
        return encuesta

    def list_polls(self, active_only: bool = False) -> List[Encuesta]:
        """
        Lista encuestas, activas o todas.
        """
        return self.repo.listar(activas_solo=active_only)

    def vote(self, poll_id: UUID, username: str, options: List[str]) -> Voto:
        """
        Registra un voto en la encuesta y genera un token NFT.
        """
        if not options or len(options) != 1:
            raise ValueError("Debe seleccionar exactamente una opción para votar.")
        encuesta = self.repo.obtener_por_id(poll_id)
        if not encuesta:
            raise ValueError(f"Encuesta no encontrada: {poll_id}")
        encuesta.comprobar_expiracion()
        voto = Voto(encuesta_id=poll_id, usuario=username, opcion=options[0])
        encuesta.agregar_voto(voto)
        self.repo.actualizar(encuesta)
        token = self.nft_service.mint_token(poll_id, options[0], username)
        voto.token_id = token.token_id
        self.notificar_observadores('voto_emitido', {'encuesta_id': str(poll_id), 'usuario': username, 'opcion': options[0]})
        return voto

    def close_poll(self, poll_id: UUID) -> bool:
        """
        Cierra manualmente una encuesta.
        """
        encuesta = self.repo.obtener_por_id(poll_id)
        if not encuesta:
            raise ValueError(f"Encuesta no encontrada: {poll_id}")
        if not encuesta.activa:
            return False
        encuesta.activa = False
        self.repo.actualizar(encuesta)
        self.notificar_observadores('encuesta_cerrada', {'encuesta_id': str(poll_id)})
        return True

    def get_partial_results(self, poll_id: UUID) -> Dict[str, int]:
        """
        Devuelve conteo parcial de votos.
        """
        encuesta = self.repo.obtener_por_id(poll_id)
        if not encuesta:
            raise ValueError(f"Encuesta no encontrada: {poll_id}")
        return encuesta.obtener_resultados()

    def get_final_results(self, poll_id: UUID) -> str:
        """
        Devuelve presentación formateada de resultados finales, aplicando desempate si necesario.
        """
        encuesta = self.repo.obtener_por_id(poll_id)
        if not encuesta:
            raise ValueError(f"Encuesta no encontrada: {poll_id}")
        resultados = encuesta.obtener_resultados()
        max_votos = max(resultados.values(), default=0)
        opciones_empate = [opt for opt, cnt in resultados.items() if cnt == max_votos]
        if len(opciones_empate) > 1:
            ganador = self.desempate_strategy.resolver(encuesta)
            return f"Empate entre {opciones_empate}. Ganador por desempate: {ganador}\n" + \
                self.presentacion_strategy.presentar(resultados)
        return self.presentacion_strategy.presentar(resultados)
