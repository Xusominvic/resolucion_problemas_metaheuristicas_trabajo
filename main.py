import argparse
import sys
from src.problem import generate_all_small_instances, generate_all_medium_instances, generate_all_large_instances
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
    
    args = parser.parse_args()
    
    # ---------------------------------------------------------
    # 2. GENERACIÓN DE LA LISTA DE INSTANCIAS (FUERA DEL BUCLE)
    # ---------------------------------------------------------
    # <--- CAMBIO: Generamos TODAS las instancias antes de empezar

    instances_to_run = []

    if args.size == 'small':
        instances_to_run = generate_all_small_instances()
        print(f"-> Generadas {len(instances_to_run)} instancias SMALL (exhaustivo).")

    elif args.size == 'medium':
        instances_to_run = generate_all_medium_instances()
        print(f"-> Generadas {len(instances_to_run)} instancias MEDIUM (exhaustivo).")

    elif args.size == 'large':
        instances_to_run = generate_all_large_instances()
        print(f"-> Generadas {len(instances_to_run)} instancias LARGE (exhaustivo).")

    total_instances = len(instances_to_run)
    print(f"--- INICIANDO LOTE DE {total_instances} EXPERIMENTOS ({args.size.upper()} - {args.algo.upper()}) ---")

    # ---------------------------------------------------------
    # --- BUCLE PRINCIPAL (Se repite 'instance_count' veces) ---
    for i, instance in enumerate(instances_to_run, 1):
        
        print(f"\n>>> EJECUCIÓN {i} DE {total_instances} <<<")
        # Mostramos el nombre generado en problem.py (si lo pusiste) o datos genéricos
        inst_name = getattr(instance, 'name', 'Sin Nombre')
        print(f"Instancia: {inst_name} | Tareas: {len(instance.tasks)}, Grúas: {len(instance.cranes)}")


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