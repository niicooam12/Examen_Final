# app.py
from __future__ import print_function
import argparse
import sys
import os

# Agregar el directorio raíz del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformers import pipeline

class ChatbotService:
    def __init__(self):
        self.chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")

    def responder(self, usuario, mensaje):
        # Simular una conversación sin usar la clase Conversation
        respuesta = self.chatbot(mensaje)
        return respuesta[0]["generated_text"]
    
from src.controllers.cli_controller import CLIController
try:
    from src.ui.gradio_app import GradioApp
except ModuleNotFoundError:
    print("Error: No se pudo encontrar el módulo 'src.ui.gradio_app'. Verifique la estructura del proyecto.")
    sys.exit(1)
except ImportError as e:
    print(f"Error de importación: {e}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Aplicación de votaciones interactivas para streamers.")
    parser.add_argument("--ui", action="store_true", help="Iniciar interfaz web con Gradio")
    args = parser.parse_args()

    if args.ui:
        print("Iniciando interfaz web en paralelo...")
        gradio_app = GradioApp()
        gradio_app.lanzar()
    else:
        print("Iniciando modo línea de comandos...")
        cli = CLIController()
        cli.iniciar()


if __name__ == "__main__":
    main()