import argparse
import sys
from src.problem import generate_small_instance, generate_medium_instance, generate_large_instance
from src.algorithms import tabu_search, simulated_annealing, multi_start_solver

def main():
    # 1. Configurar los argumentos que acepta el programa
    parser = argparse.ArgumentParser(description="Solucionador GCSP: Tabu Search & Simulated Annealing")
    
    # Argumento: Tamaño de la instancia
    parser.add_argument('--size', type=str, choices=['small', 'medium', 'large'], required=True,
                        help="Tamaño de la instancia a generar.")
    
    # Argumento: Algoritmo
    parser.add_argument('--algo', type=str, choices=['tabu', 'sa'], required=True,
                        help="Algoritmo a utilizar: 'tabu' o 'sa' (Simulated Annealing).")
    
    # Argumentos Opcionales
    parser.add_argument('--restarts', type=int, default=5, help="Número de reinicios para Multi-Arranque (Default: 5).")
    parser.add_argument('--iter', type=int, default=100, help="Iteraciones máximas por arranque (Default: 100).")
    
    # NUEVO ARGUMENTO: Cantidad de instancias a ejecutar
    parser.add_argument('--instance_count', type=int, default=1, help="Cuántas instancias distintas resolver secuencialmente (Default: 1).")
    
    args = parser.parse_args()

    print(f"--- INICIANDO LOTE DE {args.instance_count} EXPERIMENTOS ({args.size.upper()} - {args.algo.upper()}) ---")
    # --- BUCLE PRINCIPAL (Se repite 'instance_count' veces) ---
    for i in range(1, args.instance_count + 1):
        
        print(f"\n>>> EJECUCIÓN {i} DE {args.instance_count} <<<")

        # 2. Selección del Generador de Instancia (Se genera una NUEVA en cada vuelta)
        if args.size == 'small':
            instance = generate_small_instance()
        elif args.size == 'medium':
            instance = generate_medium_instance()
        elif args.size == 'large':
            instance = generate_large_instance()
        
        print(f"Instancia generada: {len(instance.tasks)} tareas, {len(instance.cranes)} grúas.")

        # 3. Selección del Algoritmo
        if args.algo == 'tabu':
            algo_func = tabu_search
            # Parámetros específicos de Tabú
            algo_params = {'tabu_tenure': 8, 'max_iter': args.iter, 'candidates_per_iter': 20}
        
        elif args.algo == 'sa':
            algo_func = simulated_annealing
            # Parámetros específicos de SA
            algo_params = {'initial_temp': 500, 'cooling_rate': 0.98, 'max_iter': args.iter}

        # 4. Ejecución (Usando siempre Multi-Start)
        print(f"Ejecutando {args.restarts} arranques de {args.iter} iteraciones...")
        
        best_seq, best_val = multi_start_solver(
            instance=instance,
            algorithm_func=algo_func,
            n_restarts=args.restarts,
            **algo_params
        )

        # 5. Reporte de esta instancia
        print("-" * 40)
        print(f"RESULTADO INSTANCIA {i}:")
        print(f"Makespan: {best_val}")
        print(f"Secuencia: {best_seq}")
        print("-" * 40)

    print("\n=== LOTE DE EXPERIMENTOS FINALIZADO ===")

if __name__ == "__main__":
    main()