import gradio as gr
from src.services.user_service import UserService
from src.services.poll_service import PollService
from src.services.nft_service import NFTService
from src.services.chatbot_service import ChatbotService

class UIController:
    def __init__(self):
        # Inicializar servicios
        self.user_service = UserService()
        self.poll_service = PollService()
        self.nft_service = NFTService()
        self.chatbot_service = ChatbotService()

    def vote_fn(self, poll_id, options, username, password):
        # Login temporal para la UI
        token = self.user_service.login(username, password)
        if not token:
            return "Error: credenciales inválidas.", None
        try:
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
        polls = self.poll_service.list_polls(active_only=True)
        return [{"id": p.id, "question": p.question, "options": p.options} for p in polls]

    def chatbot_fn(self, username, message):
        # Asumir usuario autenticado previamente en UI
        response = self.chatbot_service.ask(username, message)
        return response

    def list_tokens_fn(self, username, password):
        token = self.user_service.login(username, password)
        if not token:
            return []
        tokens = self.nft_service.list_tokens(username)
        return [{"token_id": t.token_id, "poll_id": t.poll_id, "option": t.option, "issued_at": str(t.issued_at)} for t in tokens]

    def transfer_fn(self, token_id, current_owner, password, new_owner):
        token = self.user_service.login(current_owner, password)
        if not token:
            return "Error: credenciales inválidas."
        try:
            self.nft_service.transfer_token(token_id=token_id, current_owner=current_owner, new_owner=new_owner)
            return "Transferencia completada."
        except Exception as e:
            return f"Error en transferencia: {e}"

    def build_ui(self):
        with gr.Blocks(title="Streamer Votes UI") as demo:
            gr.Markdown("## Votaciones en vivo")
            polls = gr.Dropdown(choices=[], label="Selecciona encuesta", interactive=True)
            options = gr.CheckboxGroup(choices=[], label="Opciones")
            username = gr.Textbox(label="Usuario")
            password = gr.Textbox(label="Password", type="password")
            vote_btn = gr.Button("Votar")
            vote_output = gr.Textbox(label="Estado")
            token_info = gr.JSON(label="Token Generado")

            def update_polls():
                data = self.get_active_polls()
                polls_choices = [f"{p['id']} - {p['question']}" for p in data]
                return gr.update(choices=polls_choices)

            polls.change(lambda _: update_polls(), inputs=[polls], outputs=[polls])
            vote_btn.click(
                fn=lambda poll_selection, opts, u, p: self.vote_fn(poll_selection.split(' - ')[0], opts, u, p),
                inputs=[polls, options, username, password],
                outputs=[vote_output, token_info]
            )

            gr.Markdown("## Chatbot IA")
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="Mensaje")
            send_btn = gr.Button("Enviar")
            send_btn.click(
                fn=self.chatbot_fn,
                inputs=[username, msg],
                outputs=[chatbot]
            )

            gr.Markdown("## Mis Tokens NFT")
            tokens_table = gr.Dataframe(headers=["token_id", "poll_id", "option", "issued_at"], datatype=["str", "str", "str", "str"], interactive=False)
            load_btn = gr.Button("Cargar tokens")
            load_btn.click(
                fn=self.list_tokens_fn,
                inputs=[username, password],
                outputs=[tokens_table]
            )

            gr.Markdown("## Transferir Token")
            transfer_token_id = gr.Textbox(label="Token ID")
            new_owner = gr.Textbox(label="Nuevo owner")
            transfer_pass = gr.Textbox(label="Password", type="password")
            transfer_btn = gr.Button("Transferir")
            transfer_output = gr.Textbox(label="Estado")
            transfer_btn.click(
                fn=lambda tid, u, pw, no: self.transfer_fn(tid, u, pw, no),
                inputs=[transfer_token_id, username, transfer_pass, new_owner],
                outputs=[transfer_output]
            )

        return demo

if __name__ == "__main__":
    controller = UIController()
    ui = controller.build_ui()
    ui.launch()
