# src/services/nft_service.py
from typing import List, Optional
from uuid import UUID
from src.models.token_nft import TokenNFT
from src.repositories.nft_repo import NFTRepository
from src.repositories.usuario_repo import UsuarioRepository

class NFTService:
    """
    Servicio para generar, listar y transferir tokens NFT simulados.
    """
    def __init__(self):
        self.nft_repo = NFTRepository()
        self.usuario_repo = UsuarioRepository()

    def mint_token(self, encuesta_id: UUID, opcion: str, propietario: str) -> TokenNFT:
        """
        Genera un nuevo TokenNFT tras un voto y lo persiste.

        :param encuesta_id: ID de la encuesta votada.
        :param opcion: opción votada.
        :param propietario: nombre de usuario que recibe el token.
        :return: instancia de TokenNFT creada.
        :raises ValueError: si el usuario no existe.
        """
        # Verificar que el usuario existe
        usuario = self.usuario_repo.obtener_por_nombre(propietario)
        if usuario is None:
            raise ValueError(f"Usuario no encontrado: {propietario}")
        
        # Crear token
        token = TokenNFT(encuesta_id=encuesta_id, opcion=opcion, propietario=propietario)
        
        # Persistir token
        self.nft_repo.agregar(token)
        
        # Asociar token al usuario
        usuario.tokens.append(token.token_id)
        self.usuario_repo.actualizar(usuario)
        
        return token

    def list_tokens(self, propietario: str) -> List[TokenNFT]:
        """
        Recupera todos los tokens de un usuario.

        :param propietario: nombre de usuario.
        :return: lista de TokenNFT.
        :raises ValueError: si el usuario no existe.
        """
        # Verificar que el usuario existe
        usuario = self.usuario_repo.obtener_por_nombre(propietario)
        if usuario is None:
            raise ValueError(f"Usuario no encontrado: {propietario}")
        
        return self.nft_repo.listar_por_usuario(propietario)

    def transfer_token(self, token_id: UUID, current_owner: str, new_owner: str) -> None:
        """
        Transfiere un token NFT de un usuario a otro.

        :param token_id: ID del token a transferir.
        :param current_owner: propietario actual.
        :param new_owner: futuro propietario.
        :raises ValueError: si el token no pertenece al current_owner o si algún usuario no existe.
        """
        # Verificar propietarios
        usuario_actual = self.usuario_repo.obtener_por_nombre(current_owner)
        if usuario_actual is None:
            raise ValueError(f"Usuario no encontrado: {current_owner}")
        
        if token_id not in usuario_actual.tokens:
            raise ValueError("El token no pertenece al usuario actual.")
        
        usuario_destino = self.usuario_repo.obtener_por_nombre(new_owner)
        if usuario_destino is None:
            raise ValueError(f"Usuario destinatario no encontrado: {new_owner}")
        
        # Actualizar repositorios
        usuario_actual.tokens.remove(token_id)
        self.usuario_repo.actualizar(usuario_actual)
        
        usuario_destino.tokens.append(token_id)
        self.usuario_repo.actualizar(usuario_destino)
        
        self.nft_repo.transferir(token_id, new_owner)

    def get_token(self, token_id: UUID) -> Optional[TokenNFT]:
        """
        Obtiene un token por su ID.

        :param token_id: ID del token.
        :return: TokenNFT o None si no existe.
        """
        return self.nft_repo.obtener_por_id(token_id)
