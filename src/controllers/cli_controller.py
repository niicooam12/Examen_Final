import argparse
from src.services.user_service import UserService
from src.services.poll_service import PollService
from src.services.nft_service import NFTService


class CLIController:
    POLL_TYPES = ['simple', 'multiple']

    def __init__(self):
        self.user_service = UserService()
        self.poll_service = PollService()
        self.nft_service = NFTService()
        self.parser = self._setup_parser()

    def _setup_parser(self):
        parser = argparse.ArgumentParser(
            prog="streamer-votes",
            description="CLI para administrar encuestas y tokens NFT de tu canal"
        )
        subparsers = parser.add_subparsers(dest="command", required=True)

        # Registro y login
        self._add_register_parser(subparsers)
        self._add_login_parser(subparsers)

        # Encuestas
        self._add_poll_parsers(subparsers)

        # Votos y tokens
        self._add_vote_parsers(subparsers)

        return parser

    def _add_register_parser(self, subparsers):
        parser = subparsers.add_parser("register", help="Registrar un nuevo usuario")
        parser.add_argument("username", type=str, help="Nombre de usuario")
        parser.add_argument("password", type=str, help="Contraseña")
        parser.set_defaults(func=self.register)

    def _add_login_parser(self, subparsers):
        parser = subparsers.add_parser("login", help="Login de un usuario")
        parser.add_argument("username", type=str, help="Nombre de usuario")
        parser.add_argument("password", type=str, help="Contraseña")
        parser.set_defaults(func=self.login)

    def _add_poll_parsers(self, subparsers):
        parser_create = subparsers.add_parser("create_poll", help="Crear una nueva encuesta")
        parser_create.add_argument("question", type=str, help="Texto de la pregunta")
        parser_create.add_argument("options", nargs='+', help="Opciones disponibles (mínimo 2)")
        parser_create.add_argument("duration", type=int, help="Duración en segundos (debe ser mayor a 0)")
        parser_create.add_argument("type", choices=self.POLL_TYPES, default='simple', help="Tipo de encuesta")
        parser_create.set_defaults(func=self.create_poll)

        parser_list = subparsers.add_parser("list_polls", help="Listar encuestas (activas y cerradas)")
        parser_list.set_defaults(func=self.list_polls)

        parser_close = subparsers.add_parser("close_poll", help="Cerrar una encuesta manualmente")
        parser_close.add_argument("poll_id", type=str, help="ID de la encuesta a cerrar")
        parser_close.set_defaults(func=self.close_poll)

        parser_results = subparsers.add_parser("view_results", help="Ver resultados de una encuesta")
        parser_results.add_argument("poll_id", type=str, help="ID de la encuesta")
        parser_results.set_defaults(func=self.view_results)

    def _add_vote_parsers(self, subparsers):
        parser_vote = subparsers.add_parser("vote", help="Votar en una encuesta")
        parser_vote.add_argument("poll_id", type=str, help="ID de la encuesta")
        parser_vote.add_argument("options", nargs='+', help="Opción(es) a votar")
        parser_vote.set_defaults(func=self.vote)

        parser_tokens = subparsers.add_parser("mis_tokens", help="Listar tokens NFT del usuario logueado")
        parser_tokens.set_defaults(func=self.list_tokens)

        parser_transfer = subparsers.add_parser("transfer_token", help="Transferir un token a otro usuario")
        parser_transfer.add_argument("token_id", type=str, help="ID del token a transferir")
        parser_transfer.add_argument("new_owner", type=str, help="Username del nuevo propietario")
        parser_transfer.set_defaults(func=self.transfer_token)

    def run(self, args=None):
        args = self.parser.parse_args(args)
        try:
            args.func(args)
        except AttributeError:
            print("Error: comando no válido.")
        except ValueError as e:
            print(f"Error de validación: {e}")
        except Exception as e:
            print(f"Error inesperado al ejecutar comando '{args.command}': {e}")

    # Command handlers
    def register(self, args):
        success = self.user_service.register(args.username, args.password)
        print("Registro exitoso." if success else "Error: usuario ya existe.")

    def login(self, args):
        token = self.user_service.login(args.username, args.password)
        print(f"Login exitoso. Token de sesión: {token}" if token else "Error: credenciales inválidas.")

    def create_poll(self, args):
        if len(args.options) < 2:
            raise ValueError("Debe proporcionar al menos dos opciones para la encuesta.")
        if args.duration <= 0:
            raise ValueError("La duración debe ser mayor a 0 segundos.")

        poll = self.poll_service.create_poll(
            question=args.question,
            options=args.options,
            duration_seconds=args.duration,
            poll_type=args.type
        )
        print(f"Encuesta creada con ID: {poll.id}")

    def list_polls(self, args):
        polls = self.poll_service.list_polls()
        self._print_polls(polls)

    def close_poll(self, args):
        closed = self.poll_service.close_poll(args.poll_id)
        print("Encuesta cerrada." if closed else "Error: no se pudo cerrar encuesta.")

    def view_results(self, args):
        results = self.poll_service.get_results(args.poll_id)
        self._print_results(results)

    def vote(self, args):
        vote = self.poll_service.vote(
            poll_id=args.poll_id,
            username=self.user_service.current_user,
            options=args.options
        )
        print("Voto registrado. Token NFT generado con ID:", vote.token_id)

    def list_tokens(self, args):
        tokens = self.nft_service.list_tokens(self.user_service.current_user)
        self._print_tokens(tokens)

    def transfer_token(self, args):
        self.nft_service.transfer_token(
            token_id=args.token_id,
            current_owner=self.user_service.current_user,
            new_owner=args.new_owner
        )
        print("Transferencia completada.")

    # Helper methods
    def _print_polls(self, polls):
        for p in polls:
            status = 'ACTIVA' if p.is_active else 'CERRADA'
            print(f"{p.id}\t{p.question}\t{status}")

    def _print_results(self, results):
        for opt, count in results.items():
            print(f"{opt}: {count} voto(s)")

    def _print_tokens(self, tokens):
        for t in tokens:
            print(f"{t.token_id}\tEncuesta: {t.poll_id}\tOpción: {t.option}\tEmitido: {t.issued_at}")


if __name__ == "__main__":
    CLIController().run()
