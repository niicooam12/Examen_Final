# src/patterns/observer.py
from abc import ABC

class Observador(ABC):
    """
    Interfaz para observadores que reaccionan a eventos de la encuesta.
    """
    def actualizar(self, evento: str, datos: dict) -> None:
        pass

class SujetoObservable:
    """
    Clase base para objetos que pueden ser observados.
    """
    def __init__(self):
        self._observadores: list[Observador] = []
