# src/services/chatbot_service.py
from transformers import pipeline, Conversation
from typing import Dict, List
from src.services.poll_service import PollService
from datetime import datetime

class ChatbotService:
    """
    Servicio de chatbot que responde preguntas de los usuarios,
    integrando lógica de encuestas y modelo conversacional.
    """
    def __init__(self):
        # Inicializa pipeline de conversación
        self.chatbot = pipeline("conversational", model="facebook/blenderbot-400M-distill")
        self.poll_service = PollService()
        # Historial de conversaciones por usuario
        self.historial: Dict[str, List[Conversation]] = {}

    def ask(self, usuario: str, mensaje: str) -> str:
        """
        Procesa un mensaje del usuario y devuelve la respuesta.

        Si el mensaje menciona encuestas, actúa según comandos; sino, usa el pipeline.
        """
        texto = mensaje.lower()
        # Palabras clave para encuestas
        if any(kw in texto for kw in ["quién va ganando", "quien va ganando", "cuánto falta", "cuanto falta"]):
            return self._respuesta_encuestas(texto)

        # Lógica conversacional general
        conv = Conversation(mensaje)
        if usuario not in self.historial:
            self.historial[usuario] = []
        # Añadir contexto previo
        for prev in self.historial[usuario]:
            conv.add_user_input(prev.inputs[-1])
            conv.append_response(prev.generated_responses[-1])
        respuesta = self.chatbot(conv)
        # Guardar en historial
        self.historial[usuario].append(conv)
        return respuesta.generated_responses[-1]

    def _respuesta_encuestas(self, texto: str) -> str:
        """
        Procesa preguntas relacionadas con encuestas y devuelve la respuesta.
        """
        # Obtener la encuesta activa más reciente
        encuestas = self.poll_service.list_polls(active_only=True)
        if not encuestas:
            return "No hay encuestas activas en este momento."
        
        poll = encuestas[0]
        resultados = self.poll_service.get_partial_results(poll.id)
        
        if "quién va ganando" in texto or "quien va ganando" in texto:
            # Determinar la opción con más votos
            if not resultados:
                return "Aún no hay votos registrados en la encuesta."
            ganador = max(resultados, key=resultados.get)
            return f"La opción que va ganando es '{ganador}' con {resultados[ganador]} voto(s)."
        
        if "cuánto falta" in texto or "cuanto falta" in texto:
            ahora = self.poll_service.now()
            if poll.expira_en <= ahora:
                return "La encuesta ya ha cerrado."
            faltan = (poll.expira_en - ahora).total_seconds()
            minutos = int(faltan // 60)
            segundos = int(faltan % 60)
            return f"Faltan {minutos} minuto(s) y {segundos} segundo(s) para que cierre la encuesta."
        
        # Fallback
        return "No entendí tu pregunta sobre las encuestas."

