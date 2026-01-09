# main.py
import argparse
from src.problem import generate_all_small_instances, generate_all_medium_instances, generate_all_large_instances
from src.algorithms import multi_start_solver, variable_neighborhood_search

def main():
    parser = argparse.ArgumentParser(description="Solucionador GCSP: Híbrido VNS + Tabu Search")
    
    # Solo necesitamos el tamaño
    parser.add_argument('--size', type=str, choices=['small', 'medium', 'large'], required=True,
                        help="Tamaño de la instancia.")
    
    # Parámetros del experimento
    parser.add_argument('--restarts', type=int, default=5, help="Intentos Multi-Start.")
    parser.add_argument('--iter', type=int, default=100, help="Iteraciones Tabú (Profundidad).")
    parser.add_argument('--tenure', type=int, default=8, help="Tabu Tenure.")
    parser.add_argument('--candidates', type=int, default=20, help="Vecinos por iteración.")
    parser.add_argument('--alpha', type=float, default=0.5, help="Alpha GRASP (0=Greedy, 1=Random).")

    args = parser.parse_args()
    
    # Generación de Instancias
    instances = []
    if args.size == 'small':
        instances = generate_all_small_instances()
    elif args.size == 'medium':
        instances = generate_all_medium_instances()
    elif args.size == 'large':
        instances = generate_all_large_instances()
    
    print(f"\n=== INICIANDO EXPERIMENTO ({args.size.upper()}) ===")
    print(f"Config: Restarts={args.restarts} | TabuIter={args.iter} | Tenure={args.tenure} | Cand={args.candidates} | Alpha={args.alpha}")

    for i, instance in enumerate(instances, 1):
        inst_name = getattr(instance, 'name', 'Instancia')
        print(f"\n>>> [{i}/{len(instances)}] {inst_name} (T:{len(instance.tasks)} G:{len(instance.cranes)})")

        # Configuración Unificada
        algo_params = {
            'grasp_alpha': args.alpha,
            'tabu_tenure': args.tenure,
            'max_iter': args.iter,
            'candidates_per_iter': args.candidates,
            'vns_loops': 10 # Tope de seguridad para el bucle VNS
        }
        
        # Llamada única al solver
        best_seq, best_val = multi_start_solver(
            instance=instance,
            algorithm_func=variable_neighborhood_search,
            n_restarts=args.restarts,
            **algo_params
        )

        print("-" * 30)
        print(f"RESULTADO FINAL: {best_val}")
        print(f"Secuencia: {best_seq}")
        print("-" * 30)

    print("\n=== FIN DEL LOTE ===")

if __name__ == "__main__":
    main()