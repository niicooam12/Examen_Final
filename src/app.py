# app.py
from __future__ import print_function
import argparse
import sys
import os

# Agregar el directorio raíz del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.controllers.cli_controller import CLIController
from src.ui.gradio_app import GradioApp


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