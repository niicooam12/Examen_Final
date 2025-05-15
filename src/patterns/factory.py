from uuid import uuid4
from src.models.encuesta import Encuesta
from src.models.voto import Voto
from src.models.token_nft import TokenNFT

class PollFactory:
    """
    Fábrica para crear encuestas de distintos tipos.
    Tipos soportados: 'simple', 'multiple'.
    """
    def create_poll(self, pregunta: str, opciones: list, duracion_segundos: int, tipo: str = 'simple') -> Encuesta:
        if tipo not in ('simple', 'multiple'):
            raise ValueError(f"Tipo de encuesta inválido: {tipo}")
        encuesta = Encuesta(
            pregunta=pregunta,
            opciones=opciones,
            duracion_segundos=duracion_segundos,
            tipo=tipo
        )
        return encuesta

class TokenFactory:
    """
    Fábrica para crear tokens NFT estándar o edición limitada.
    """
    def create_token(self, encuesta_id, opcion, propietario, limitado: bool = False) -> TokenNFT:
        metadata = {
            'encuesta_id': encuesta_id,
            'opcion': opcion,
            'propietario': propietario
        }
        if limitado:
            # Por ejemplo, prefijo especial o campos extra
            metadata['edicion'] = 'limitada'
        token = TokenNFT(
            encuesta_id=encuesta_id,
            opcion=opcion,
            propietario=propietario
        )
        # Podríamos envolver lógica adicional según 'limitado'
        return token
