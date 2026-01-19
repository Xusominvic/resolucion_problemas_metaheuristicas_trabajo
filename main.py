import argparse
import time # <--- IMPORTANTE: Importar librería de tiempo
from src.problem import generate_all_small_instances, generate_all_medium_instances, generate_all_large_instances
from src.algorithms import multi_start_solver, variable_neighborhood_search, calculate_lower_bound # <--- Importamos LB

def main():
    parser = argparse.ArgumentParser(description="Solucionador GCSP: Híbrido VNS + Tabu Search")
    
    # Argumentos
    parser.add_argument('--size', type=str, choices=['small', 'medium', 'large'], required=True, help="Tamaño de la instancia.")
    parser.add_argument('--restarts', type=int, default=5, help="Intentos Multi-Start.")
    parser.add_argument('--iter', type=int, default=100, help="Iteraciones Tabú.")
    parser.add_argument('--tenure', type=int, default=8, help="Tabu Tenure.")
    parser.add_argument('--candidates', type=int, default=20, help="Vecinos por iteración.")
    parser.add_argument('--alpha', type=float, default=0.5, help="Alpha GRASP.")

    args = parser.parse_args()
    
    # Selección de Instancias
    instances = []
    if args.size == 'small': instances = generate_all_small_instances()
    elif args.size == 'medium': instances = generate_all_medium_instances()
    elif args.size == 'large': instances = generate_all_large_instances()
     
    print(f"\n=== EXPERIMENTO ({args.size.upper()}) | Params: R={args.restarts} Iter={args.iter} T={args.tenure} C={args.candidates} ===")

    # Cabecera de la tabla de resultados (Añadimos Columna Tiempo)
    print(f"{'Instancia':<20} | {'LB (Teórico)':<12} | {'Makespan':<10} | {'Gap (%)':<10} | {'Tiempo (s)':<10} | {'Secuencia'}")
    print("-" * 115)

    total_gap = 0
    total_time = 0
    
    for i, instance in enumerate(instances, 1):
        # 1. Calcular el Lower Bound (Referencia perfecta)
        lb = calculate_lower_bound(instance)
        
        # 2. Configurar Algoritmo
        algo_params = {
            'grasp_alpha': args.alpha,
            'tabu_tenure': args.tenure,
            'max_iter': args.iter,
            'candidates_per_iter': args.candidates,
            'vns_loops': 10
        }
        
        # 3. Ejecutar y MEDIR TIEMPO
        start_time = time.time() # Iniciar cronómetro
        
        best_seq, best_val = multi_start_solver(
            instance=instance,
            algorithm_func=variable_neighborhood_search,
            n_restarts=args.restarts,
            **algo_params
        )
        
        elapsed_time = time.time() - start_time # Parar cronómetro
        
        # 4. Calcular Métricas
        # Gap: ((Valor Obtenido - Óptimo Teórico) / Óptimo Teórico) * 100
        gap = ((best_val - lb) / lb) * 100
        total_gap += gap
        total_time += elapsed_time

        # 5. Imprimir fila de la tabla
        inst_name = getattr(instance, 'name', f"Inst_{i}")
        seq_str = str(best_seq[:5]) + "..." if len(best_seq) > 5 else str(best_seq)
        
        print(f"{inst_name:<20} | {lb:<12.1f} | {best_val:<10.1f} | {gap:<10.2f} | {elapsed_time:<10.2f} | {seq_str}")

    # Resumen Final
    avg_gap = total_gap / len(instances)
    avg_time = total_time / len(instances)
    
    print("-" * 115)
    print(f"PROMEDIO GAP GLOBAL:   {avg_gap:.2f}%")
    print(f"TIEMPO MEDIO POR INST: {avg_time:.2f} s")
    print("=== FIN DEL EXPERIMENTO ===")

if __name__ == "__main__":
    main()