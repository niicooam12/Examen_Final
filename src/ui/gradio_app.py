# src/ui/gradio_app.py
import gradio as gr
from src.services.poll_service import PollService
from src.services.chatbot_service import ChatbotService
from src.services.nft_service import NFTService
from src.services.user_service import UserService

class GradioApp:
    def __init__(self):
        self.poll_service = PollService()
        self.chatbot_service = ChatbotService()
        self.nft_service = NFTService()
        self.user_service = UserService()

    def mostrar_encuestas(self):
        try:
            encuestas = self.poll_service.listar_encuestas_activas()
            if not encuestas:
                return "No hay encuestas activas."
            return "\n".join([f"{e.id}: {e.pregunta}" for e in encuestas])
        except Exception as e:
            return f"Error al obtener encuestas: {str(e)}"

    def votar(self, poll_id, username, opcion):
        try:
            self.poll_service.verificar_encuestas_activas()
            self.poll_service.votar(poll_id, username, opcion)
            return f"Voto registrado por {username} en la encuesta {poll_id}."
        except Exception as e:
            return f"Error al registrar el voto: {str(e)}"

    def responder_chatbot(self, mensaje, username):
        try:
            return self.chatbot_service.responder(username, mensaje)
        except Exception as e:
            return f"Error en el chatbot: {str(e)}"

    def ver_tokens(self, username):
        try:
            tokens = self.nft_service.obtener_tokens_usuario(username)
            if not tokens:
                return "No tienes tokens."
            return "\n".join(
                [f"Token {t.token_id} - Encuesta {t.poll_id}, Opción:
            with gr.Tab("Encuestas"):
                gr.Markdown("### Encuestas Activas")
                encuestas_output = gr.Textbox(label="Encuestas")
                refresh_btn = gr.Button("Refrescar")
                refresh_btn.click(fn=self.mostrar_encuestas, outputs=encuestas_output)

                poll_id = gr.Textbox(label="ID de Encuesta")
                username = gr.Textbox(label="Usuario")
                opcion = gr.Textbox(label="Opción")
                votar_btn = gr.Button("Votar")
                voto_output = gr.Textbox(label="Resultado del Voto")
                votar_btn.click(fn=self.votar, inputs=[poll_id, username, opcion], outputs=voto_output)

            with gr.Tab("Chatbot"):
                gr.Markdown("### Asistente IA")
                chat_username = gr.Textbox(label="Usuario")
                chat_input = gr.Textbox(label="Mensaje")
                chat_output = gr.Textbox(label="Respuesta")
                chat_btn = gr.Button("Enviar")
                chat_btn.click(fn=self.responder_chatbot, inputs=[chat_input, chat_username], outputs=chat_output)

            with gr.Tab("Tokens"):
                gr.Markdown("### Mis Tokens")
                token_user = gr.Textbox(label="Usuario")
                ver_tokens_btn = gr.Button("Ver Tokens")
                tokens_output = gr.Textbox(label="Tokens")
                ver_tokens_btn.click(fn=self.ver_tokens, inputs=token_user, outputs=tokens_output)

                token_id = gr.Textbox(label="ID del Token")
                nuevo_owner = gr.Textbox(label="Nuevo Propietario")
                actual_owner = gr.Textbox(label="Propietario Actual")
                transfer_btn = gr.Button("Transferir")
                transfer_output = gr.Textbox(label="Resultado Transferencia")
                transfer_btn.click(fn=self.transferir_token, inputs=[token_id, nuevo_owner, actual_owner], outputs=transfer_output)

        interfaz.launch()
