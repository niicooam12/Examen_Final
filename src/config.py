import json
import builtins

class Config:
    def __init__(self, ruta_config="config.json"):
        self.ruta = ruta_config
        self.parametros = {}
        self.cargar_configuracion()

    def cargar_configuracion(self):
        try:
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                self.parametros = json.load(archivo)
        except FileNotFoundError:
            print(f"Archivo de configuración '{self.ruta}' no encontrado. Se usarán valores por defecto.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo de configuración. Verifica el formato JSON.")

    def obtener(self, clave, por_defecto=None):
        return self.parametros.get(clave, por_defecto)
