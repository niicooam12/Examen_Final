import gradio as gr
from src.services.user_service import UserService
from src.services.poll_service import PollService
from src.services.nft_service import NFTService
from src.services.chatbot_service import ChatbotService


class UIController:
    def __init__(self):
        self.user_service = UserService()
        self.poll_service = PollService()
        self.nft_service = NFTService()
        self.chatbot_service = ChatbotService()

    def vote_fn(self, poll_full_id, options, username, password):
        if not poll_full_id or not options:
            return "Error: Debes seleccionar una encuesta y al menos una opción.", None
        if not username or not password:
            return "Error: Usuario y contraseña son obligatorios.", None

        token = self.user_service.login(username, password)
        if not token:
            return "Error: Credenciales inválidas.", None
        try:
            poll_id = poll_full_id.split(' - ')[0]
            vote = self.poll_service.vote(
                poll_id=poll_id,
                username=username,
                options=options
            )
            token_obj = self.nft_service.get_token(vote.token_id)
            return "Voto registrado.", token_obj.metadata()
        except Exception as e:
            return f"Error al votar: {e}", None

    def get_active_polls(self):
        try:
            polls = self.poll_service.list_polls(active_only=True)
            return [{"id": p.id, "question": p.question, "options": p.options} for p in polls]
        except Exception:
            return []

    def chatbot_fn(self, username, message):
        if not username or not message:
            return "Error: Usuario y mensaje son obligatorios."
        try:
            return self.chatbot_service.ask(username, message)
        except Exception as e:
            return f"Error en chatbot: {e}"

    def list_tokens_fn(self, username, password):
        if not username or not password:
            return []
        token = self.user_service.login(username, password)
        if not token:
            return []
        try:
            tokens = self.nft_service.list_tokens(username)
            return [{"token_id": t.token_id, "poll_id": t.poll_id, "option": t.option, "issued_at": str(t.issued_at)} for t in tokens]
        except Exception:
            return []

    def transfer_fn(self, token_id, current_owner, password, new_owner):
        if not token_id or not current_owner or not password or not new_owner:
            return "Error: Todos los campos son obligatorios."
        token = self.user_service.login(current_owner, password)
        if not token:
            return "Error: Credenciales inválidas."
        try:
            self.nft_service.transfer_token(token_id=token_id, current_owner=current_owner, new_owner=new_owner)
            return "Transferencia completada."
        except Exception as e:
            return f"Error en transferencia: {e}"

    def build_ui(self):
        with gr.Blocks(title="Streamer Votes UI") as demo:
            gr.Markdown("## 🗳️ Votaciones en vivo")

            with gr.Row():
                polls = gr.Dropdown(choices=[], label="Encuesta activa", interactive=True)
                options = gr.CheckboxGroup(choices=[], label="Opciones")

            with gr.Row():
                username = gr.Textbox(label="Usuario")
                password = gr.Textbox(label="Contraseña", type="password")

            with gr.Row():
                vote_btn = gr.Button("Votar")
                vote_output = gr.Textbox(label="Estado de voto")
                token_info = gr.JSON(label="Token NFT generado")

            def update_poll_choices():
                data = self.get_active_polls()
                return gr.update(choices=[f"{p['id']} - {p['question']}" for p in data])

            def update_poll_options(poll_selection):
                if not poll_selection:
                    return gr.update(choices=[])
                poll_id = poll_selection.split(' - ')[0]
                data = self.get_active_polls()
                selected_poll = next((p for p in data if str(p['id']) == poll_id), None)
                return gr.update(choices=selected_poll['options']) if selected_poll else gr.update(choices=[])

            polls.change(fn=update_poll_choices, inputs=[], outputs=[polls])
            polls.change(fn=update_poll_options, inputs=[polls], outputs=[options])

            vote_btn.click(
                fn=self.vote_fn,
                inputs=[polls, options, username, password],
                outputs=[vote_output, token_info]
            )

            gr.Markdown("## 🤖 Chatbot IA")
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="Mensaje")
            send_btn = gr.Button("Enviar mensaje")
            send_btn.click(
                fn=self.chatbot_fn,
                inputs=[username, msg],
                outputs=[chatbot]
            )

            gr.Markdown("## 🎟️ Mis Tokens NFT")
            tokens_table = gr.Dataframe(headers=["token_id", "poll_id", "option", "issued_at"],
                                        datatype=["str", "str", "str", "str"],
                                        interactive=False)
            load_btn = gr.Button("Cargar mis tokens")
            load_btn.click(
                fn=self.list_tokens_fn,
                inputs=[username, password],
                outputs=[tokens_table]
            )

            gr.Markdown("## 🔁 Transferencia de Token")
            with gr.Row():
                transfer_token_id = gr.Textbox(label="ID del Token")
                new_owner = gr.Textbox(label="Nuevo dueño")
            transfer_pass = gr.Textbox(label="Contraseña", type="password")
            transfer_btn = gr.Button("Transferir token")
            transfer_output = gr.Textbox(label="Resultado")
            transfer_btn.click(
                fn=self.transfer_fn,
                inputs=[transfer_token_id, username, transfer_pass, new_owner],
                outputs=[transfer_output]
            )

        return demo


if __name__ == "__main__":
    controller = UIController()
    ui = controller.build_ui()
    ui.launch()
