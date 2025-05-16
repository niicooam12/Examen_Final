import unittest
from unittest.mock import MagicMock, patch
from src.controllers.ui_controller import UIController

class TestUIController(unittest.TestCase):

    def setUp(self):
        self.ui = UIController()

    def test_vote_fn(self):
        self.ui.user_service.login = MagicMock(return_value="mock_token")
        self.ui.poll_service.vote = MagicMock(return_value=MagicMock(token_id="mock_token_id"))
        self.ui.nft_service.get_token = MagicMock(return_value=MagicMock(metadata=lambda: {"key": "value"}))

        result, metadata = self.ui.vote_fn("poll_id", ["option1"], "username", "password")
        self.assertEqual(result, "Voto registrado.")
        self.assertEqual(metadata, {"key": "value"})

    def test_get_active_polls(self):
        self.ui.poll_service.list_polls = MagicMock(return_value=[
            MagicMock(id="poll1", question="Question 1", options=["Option 1", "Option 2"]),
            MagicMock(id="poll2", question="Question 2", options=["Option A", "Option B"]),
        ])

        polls = self.ui.get_active_polls()
        self.assertEqual(len(polls), 2)
        self.assertEqual(polls[0]["id"], "poll1")
        self.assertEqual(polls[1]["question"], "Question 2")

    def test_chatbot_fn(self):
        self.ui.chatbot_service.ask = MagicMock(return_value="Mock response")

        response = self.ui.chatbot_fn("username", "message")
        self.assertEqual(response, "Mock response")

    def test_list_tokens_fn(self):
        self.ui.user_service.login = MagicMock(return_value="mock_token")
        self.ui.nft_service.list_tokens = MagicMock(return_value=[
            MagicMock(token_id="token1", poll_id="poll1", option="option1", issued_at="2025-05-16T00:00:00"),
            MagicMock(token_id="token2", poll_id="poll2", option="option2", issued_at="2025-05-16T01:00:00"),
        ])

        tokens = self.ui.list_tokens_fn("username", "password")
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0]["token_id"], "token1")

    def test_transfer_fn(self):
        self.ui.user_service.login = MagicMock(return_value="mock_token")
        self.ui.nft_service.transfer_token = MagicMock()

        result = self.ui.transfer_fn("token_id", "current_owner", "password", "new_owner")
        self.assertEqual(result, "Transferencia completada.")

if __name__ == "__main__":
    unittest.main()