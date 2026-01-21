# main.py
import argparse
import random
import time
from src.problem import Task, Crane, GCSP_Instance, get_equidistant_positions
from src.algorithms import multi_start_solver, variable_neighborhood_search, calculate_lower_bound

# ... [MANTENER generate_benchmark_instances IGUAL] ...
def generate_benchmark_instances(n_tasks, n_cranes, min_p, max_p, num_instances=6):
    instances = []
    for i in range(num_instances):
        tasks = [Task(t_id, t_id, random.randint(min_p, max_p)) for t_id in range(1, n_tasks + 1)]
        locs = get_equidistant_positions(n_tasks, n_cranes)
        cranes = [Crane(k, locs[k-1]) for k in range(1, n_cranes + 1)]
        inst = GCSP_Instance(tasks, cranes)
        inst.name = f"{n_tasks}x{n_cranes}_{i+1}"
        instances.append(inst)
    return instances

def main():
    parser = argparse.ArgumentParser(description="Benchmark Paper GCSP")
    
    parser.add_argument('--size', type=str, choices=['small', 'medium', 'large'], required=True, 
                        help="Conjunto de experimentos a ejecutar.")
    
    parser.add_argument('--restarts', type=int, default=5, help="Nº Intentos para hacer la media.")
    parser.add_argument('--iter', type=int, default=200, help="(IGNORADO) Iteraciones Tabú.") 
    parser.add_argument('--tenure', type=int, default=8, help="Tabu Tenure.")
    parser.add_argument('--candidates', type=int, default=20, help="Vecinos por iteración.")
    parser.add_argument('--init', type=str, default='grasp', choices=['grasp', 'random'])

    args = parser.parse_args()

    benchmarks = []
    min_p, max_p = 30, 180 
    
    if args.size == 'small':
        min_p, max_p = 20, 150
        tasks_list = [6, 7, 8, 9, 10, 11]
        cranes_list = [2, 3]
        benchmarks = [(t, c) for t in tasks_list for c in cranes_list]
    elif args.size == 'medium':
        min_p, max_p = 30, 180
        tasks_list = [15, 16, 17, 18, 19, 20]
        cranes_list = [2, 3, 4]
        benchmarks = [(t, c) for t in tasks_list for c in cranes_list]
    elif args.size == 'large':
        min_p, max_p = 30, 180
        tasks_list = [30, 40, 50, 60, 70]
        cranes_list = [3, 4, 5]
        benchmarks = [(t, c) for t in tasks_list for c in cranes_list]

    print(f"\n=== BENCHMARK: {args.size.upper()} | 6 Instancias x Tamaño | Media de {args.restarts} ejecuciones ===")
    print(f"Config: Init={args.init} | Tenure={args.tenure} | Cand={args.candidates}")
    print(f"Iteraciones Dinámicas: 6 x N x M")
    if args.init == 'random':
        print(f"Población Inicial Random (SN): 3 x N")
    print(f"Distribución Tiempos: Uniforme [{min_p}, {max_p}]")
    
    print("-" * 110)
    print(f"{'Tamaño':<10} | {'Iter':<6} | {'LB Avg':<10} | {'Makespan':<10} | {'GAP %':<10} | {'Time (s)':<10}")
    print("-" * 110)

    for (n_tasks, n_cranes) in benchmarks:
        
        # 1. Calcular iteraciones dinámicas: 6 * n * m
        dynamic_iter = 6 * n_tasks * n_cranes
        
        # 2. Calcular SN (Swarm Number) para Random: 3 * n
        sn_param = 3 * n_tasks
        
        instances_6 = generate_benchmark_instances(n_tasks, n_cranes, min_p, max_p, num_instances=6)
        
        sum_gap = 0
        sum_makespan = 0
        sum_lb = 0
        sum_time = 0
        
        for inst in instances_6:
            lb = calculate_lower_bound(inst)
            
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
                pool_size=sn_param # <--- Pasamos el SN calculado
            )
            
            if lb > 0:
                gap = ((avg_mk - lb) / lb) * 100
            else:
                gap = 0.0
            
            sum_lb += lb
            sum_makespan += avg_mk
            sum_gap += gap
            sum_time += avg_t

        final_lb = sum_lb / 6
        final_makespan = sum_makespan / 6
        final_gap = sum_gap / 6
        final_time = sum_time / 6
        
        size_str = f"{n_tasks}x{n_cranes}"
        print(f"{size_str:<10} | {dynamic_iter:<6} | {final_lb:<10.1f} | {final_makespan:<10.1f} | {final_gap:<10.2f} | {final_time:<10.2f}")

    print("-" * 110)
    print("=== FIN DEL BENCHMARK ===")

if __name__ == "__main__":
    main()