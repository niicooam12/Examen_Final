# src/patterns/strategy.py
from abc import ABC
from typing import Dict, Any
import json
import random
from src.models.encuesta import Encuesta

class DesempateStrategy(ABC):
    """
    Estrategia para resolver empates en una encuesta.
    """
    def resolver(self, encuesta: Encuesta) -> Any:
        """
        Resuelve el desempate y devuelve la opción ganadora o un resultado particular.
        """
        raise NotImplementedError("El método 'resolver' debe ser implementado por la subclase.")

class AlfabéticoStrategy(DesempateStrategy):
    """
    Selecciona la opción ganadora ordenando alfabéticamente y eligiendo la primera.
    """
    def resolver(self, encuesta: Encuesta) -> str:
        resultados = encuesta.obtener_resultados()
        max_votos = max(resultados.values())
        opciones_empate = [opt for opt, cnt in resultados.items() if cnt == max_votos]
        return sorted(opciones_empate)[0]

class AleatorioStrategy(DesempateStrategy):
    """
    Selecciona aleatoriamente entre las opciones empatadas.
    """
    def resolver(self, encuesta: Encuesta) -> str:
        resultados = encuesta.obtener_resultados()
        max_votos = max(resultados.values())
        opciones_empate = [opt for opt, cnt in resultados.items() if cnt == max_votos]
        return random.choice(opciones_empate)

class ProrrogaStrategy(DesempateStrategy):
    """
    Indica que la encuesta debe extenderse (prórroga) en caso de empate.
    """
    def resolver(self, encuesta: Encuesta) -> Dict[str, Any]:
        resultados = encuesta.obtener_resultados()
        max_votos = max(resultados.values())
        opciones_empate = [opt for opt, cnt in resultados.items() if cnt == max_votos]
        # Devolver datos para prórroga: opciones a repetir
        return {
            "accion": "prorroga",
            "opciones_empate": opciones_empate
        }

class PresentacionStrategy(ABC):
    """
    Estrategia para formatear resultados de la encuesta.
    """
    def presentar(self, resultados: Dict[str, int]) -> Any:
        """
        Recibe un diccionario opción->votos y devuelve la presentación formateada.
        """
        raise NotImplementedError("El método 'presentar' debe ser implementado por la subclase.")

class TextoStrategy(PresentacionStrategy):
    """
    Presenta los resultados en texto plano.
    """
    def presentar(self, resultados: Dict[str, int]) -> str:
        lineas = [f"{opt}: {cnt} voto(s)" for opt, cnt in resultados.items()]
        return "\n".join(lineas)

class ASCIIArtStrategy(PresentacionStrategy):
    """
    Presenta un gráfico ASCII simple de barras proporcionales.
    """
    def presentar(self, resultados: Dict[str, int]) -> str:
        max_votos = max(resultados.values()) or 1
        lineas = []
        for opt, cnt in resultados.items():
            longitud = int((cnt / max_votos) * 20)
            barra = '█' * longitud
            lineas.append(f"{opt}: {barra} ({cnt})")
        return "\n".join(lineas)

class JSONStrategy(PresentacionStrategy):
    """
    Presenta los resultados como JSON.
    """
    def presentar(self, resultados: Dict[str, int]) -> str:
        return json.dumps(resultados, ensure_ascii=False)
