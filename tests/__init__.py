import unittest
from unittest.mock import patch
from src.controllers.cli_controller import CLIController
from src.services.user_service import UserService
from src.services.poll_service import PollService

class TestCLIController(unittest.TestCase):

    def setUp(self):
        # Crear instancias reales o simuladas de los servicios
        self.user_service = UserService()
        self.poll_service = PollService()
        self.cli = CLIController(user_service=self.user_service, poll_service=self.poll_service)

    def test_registrar_usuario(self):
        # Simular el comportamiento del registro de usuario
        with patch.object(self.user_service, 'register', return_value=True):
            with patch('sys.argv', ['streamer-votes', 'register', 'testuser', 'password']):
                with patch('builtins.print') as mock_print:
                    self.cli.run()
                    mock_print.assert_called_with("Registro exitoso.")

    def test_iniciar_sesion_usuario(self):
        # Simular el comportamiento del inicio de sesión
        with patch.object(self.user_service, 'login', return_value="mock_token"):
            with patch('sys.argv', ['streamer-votes', 'login', 'testuser', 'password']):
                with patch('builtins.print') as mock_print:
                    self.cli.run()
                    mock_print.assert_called_with("Login exitoso. Token de sesión: mock_token")

    def test_crear_encuesta(self):
        # Simular el comportamiento de la creación de encuestas
        with patch.object(self.poll_service, 'create_poll', return_value=type('Poll', (object,), {'id': 1})()):
            with patch('sys.argv', ['streamer-votes', 'create_poll', '¿Te gusta el stream?', 'Sí', 'No', '60', 'simple']):
                with patch('builtins.print') as mock_print:
                    self.cli.run()
                    mock_print.assert_called_with("Encuesta creada con ID: 1")

if __name__ == '__main__':
    unittest.main()