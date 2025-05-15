# src/ui/gradio_app.py
import gradio as gr
from src.services.poll_service import PollService
from src.services.user_service import UserService
from src.services.nft_service import NFTService
from src.services.chatbot_service import ChatbotService

class GradioApp:
    def __init__(self):
        self.poll_service = PollService()
        self.user_service = UserService()
        self.nft_service = NFTService()
        self.chatbot_service = ChatbotService()

        self.usuario_actual = None
        self.token_sesion = None

    def login(self, username, password):
        if not username or not password:
            return "Usuario y contraseña son obligatorios."
        try:
            token = self.user_service.login(username, password)
            self.usuario_actual = username
            self.token_sesion = token
            return f"Bienvenido, {username}!"
        except ValueError as e:  # Ejemplo de excepción específica
            return str(e)
        except Exception:
            return "Error inesperado al iniciar sesión."

    def registrar_usuario(self, username, password):
        if not username or not password:
            return "Usuario y contraseña son obligatorios."
        try:
            self.user_service.register(username, password)
            return "Usuario registrado exitosamente."
        except ValueError as e:
            return str(e)
        except Exception:
            return "Error inesperado al registrar usuario."

    def votar(self, poll_id, opcion):
        if not self.usuario_actual:
            return "Debe iniciar sesión para votar."
        if not poll_id or not opcion:
            return "ID de encuesta y opción son obligatorios."
        try:
            self.poll_service.vote(poll_id, self.usuario_actual, opcion)
            return "Voto registrado correctamente."
        except ValueError as e:
            return str(e)
        except Exception:
            return "Error inesperado al registrar el voto."

    def ver_encuestas_activas(self):
        try:
            encuestas = self.poll_service.listar_encuestas_activas()
            if not encuestas:
                return "No hay encuestas activas en este momento."
            return "\n".join(
                [f"{e.id}: {e.pregunta} - Opciones: {', '.join(e.opciones)}" for e in encuestas]
            )
        except Exception:
            return "Error inesperado al obtener encuestas activas."

    def ver_mis_tokens(self):
        if not self.usuario_actual:
            return "Debe iniciar sesión para ver sus tokens."
        try:
            tokens = self.nft_service.obtener_tokens_usuario(self.usuario_actual)
            if not tokens:
                return "No tienes tokens disponibles."
            return "\n".join(
                [f"Token {t.token_id} - Encuesta {t.poll_id}, Opción: {t.option}" for t in tokens]
            )
        except Exception:
            return "Error inesperado al obtener los tokens."

    def transferir_token(self, token_id, nuevo_owner):
        if not self.usuario_actual:
            return "Debe iniciar sesión para transferir tokens."
        if not token_id or not nuevo_owner:
            return "ID del token y nuevo propietario son obligatorios."
        try:
            self.nft_service.transferir_token(token_id, self.usuario_actual, nuevo_owner)
            return "Token transferido correctamente."
        except ValueError as e:
            return str(e)
        except Exception:
            return "Error inesperado al transferir el token."

    def responder_chat(self, mensaje):
        if not self.usuario_actual:
            return "Debe iniciar sesión para usar el chatbot."
        if not mensaje:
            return "El mensaje no puede estar vacío."
        try:
            return self.chatbot_service.responder(self.usuario_actual, mensaje)
        except Exception:
            return "Error inesperado al procesar el mensaje del chatbot."

    def lanzar(self):
        with gr.Blocks() as demo:
            gr.Markdown("## Plataforma de Votaciones Interactivas para Streamers")

            with gr.Tab("Login / Registro"):
                user = gr.Textbox(label="Usuario")
                pwd = gr.Textbox(label="Contraseña", type="password")
                login_btn = gr.Button("Iniciar sesión")
                registro_btn = gr.Button("Registrarse")
                login_out = gr.TextArea(label="Estado")  # Cambiado a TextArea

                login_btn.click(fn=self.login, inputs=[user, pwd], outputs=login_out)
                registro_btn.click(fn=self.registrar_usuario, inputs=[user, pwd], outputs=login_out)

            with gr.Tab("Encuestas"):
                poll_id = gr.Textbox(label="ID de Encuesta")
                opcion = gr.Textbox(label="Opción a votar")
                votar_btn = gr.Button("Votar")
                votar_out = gr.TextArea(label="Resultado")  # Cambiado a TextArea
                votar_btn.click(fn=self.votar, inputs=[poll_id, opcion], outputs=votar_out)

                encuestas_btn = gr.Button("Ver encuestas activas")
                encuestas_out = gr.TextArea(label="Encuestas activas")  # Cambiado a TextArea
                encuestas_btn.click(fn=self.ver_encuestas_activas, inputs=[], outputs=encuestas_out)

            with gr.Tab("Tokens"):
                tokens_btn = gr.Button("Ver mis tokens")
                tokens_out = gr.TextArea(label="Tokens")  # Cambiado a TextArea
                tokens_btn.click(fn=self.ver_mis_tokens, inputs=[], outputs=tokens_out)

                transfer_id = gr.Textbox(label="ID del token")
                nuevo_owner = gr.Textbox(label="Nuevo propietario")
                transfer_btn = gr.Button("Transferir token")
                transfer_out = gr.TextArea(label="Estado transferencia")  # Cambiado a TextArea
                transfer_btn.click(fn=self.transferir_token, inputs=[transfer_id, nuevo_owner], outputs=transfer_out)

            with gr.Tab("Chatbot"):
                mensaje = gr.Textbox(label="Tu mensaje")
                respuesta = gr.TextArea(label="Respuesta del bot")  # Cambiado a TextArea
                chat_btn = gr.Button("Enviar")
                chat_btn.click(fn=self.responder_chat, inputs=mensaje, outputs=respuesta)

        demo.launch()
