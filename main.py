import argparse
import glob
from src.algorithms import multi_start_solver, variable_neighborhood_search, calculate_lower_bound
from src.io_handler import load_instance_from_json

def main():
    parser = argparse.ArgumentParser(description="Benchmark Paper GCSP")
    parser.add_argument('--size', type=str, choices=['small', 'medium', 'large'], required=True)
    # Parámetros del algoritmo
    parser.add_argument('--restarts', type=int, default=5)
    parser.add_argument('--iter', type=int, default=200) # Ignorado, se calcula dinamico
    parser.add_argument('--tenure', type=int, default=8)
    parser.add_argument('--candidates', type=int, default=20)
    parser.add_argument('--init', type=str, default='grasp', choices=['grasp', 'random'])
    
    args = parser.parse_args()

    # 1. Buscar archivos JSON generados previamente
    search_pattern = f"instances/{args.size}_*.json"
    files = sorted(glob.glob(search_pattern))
    
    if not files:
        print(f"ERROR: No se encontraron instancias en '{search_pattern}'.")
        print("Ejecuta primero: python generate_dataset.py")
        return

    print(f"\n=== BENCHMARK: {args.size.upper()} | {len(files)} Instancias (Desde archivo) ===")
    print(f"Config: Init={args.init} | Tenure={args.tenure} | Cand={args.candidates}")
    
    # Cabecera
    print("-" * 95)
    print(f"{'Instancia':<20} | {'LB':<8} | {'Makespan':<10} | {'GAP %':<10} | {'Time (s)':<10}")
    print("-" * 95)

    # Agrupar estadísticas
    total_gap = 0
    total_time = 0
    
    # Procesar cada archivo individualmente
    for filepath in files:
        inst = load_instance_from_json(filepath)
        
        # Parámetros dinámicos
        n_tasks = len(inst.tasks)
        n_cranes = len(inst.cranes)
        dynamic_iter = 6 * n_tasks * n_cranes
        sn_param = 3 * n_tasks
        
        lb = calculate_lower_bound(inst)
        
        # Ejecutar solver
        _, avg_mk, avg_t = multi_start_solver(
            instance=inst,
            algorithm_func=variable_neighborhood_search,
            n_restarts=args.restarts, 
            grasp_alpha=0.5,
            tabu_tenure=args.tenure,
            max_iter=dynamic_iter,
            candidates_per_iter=args.candidates,
            vns_loops=10,
            init_strategy=args.init,
            pool_size=sn_param
        )
        
        if lb > 0:
            gap = ((avg_mk - lb) / lb) * 100
        else:
            gap = 0.0
            
        print(f"{inst.name:<20} | {lb:<8.1f} | {avg_mk:<10.1f} | {gap:<10.2f} | {avg_t:<10.2f}")
        
        total_gap += gap
        total_time += avg_t

    # Promedios finales
    if len(files) > 0:
        print("-" * 95)
        print(f"{'PROMEDIO':<20} | {'-':<8} | {'-':<10} | {total_gap/len(files):<10.2f} | {total_time/len(files):<10.2f}")
    
    print("=== FIN ===")

if __name__ == "__main__":
    main()