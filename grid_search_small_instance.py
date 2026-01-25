import argparse
import sys
# Importamos las funciones desde tu archivo original
from src.problem import (
    generate_all_small_instances, 
    generate_all_medium_instances, 
    generate_all_large_instances
)

def ejecutar():
    parser = argparse.ArgumentParser(description="Controlador dinámico de búsqueda de rejilla.")
    
    # Definimos el argumento --size
    parser.add_argument(
        '--size', 
        choices=['small', 'medium', 'large'], 
        required=True,
        help="Determina qué generador de instancias ejecutar."
    )

    args = parser.parse_args()

    # Diccionario de mapeo para evitar muchos 'if/else'
    mapeo_funciones = {
        'small': generate_all_small_instances,
        'medium': generate_all_medium_instances,
        'large': generate_all_large_instances
    }

    # Llamada dinámica
    print(f"--- Iniciando proceso para tamaño: {args.size.upper()} ---")
    
    try:
        funcion_a_ejecutar = mapeo_funciones[args.size]
        funcion_a_ejecutar() 
        print(f"--- Proceso {args.size} finalizado con éxito ---")
    except Exception as e:
        print(f"Error al ejecutar la instancia {args.size}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar()