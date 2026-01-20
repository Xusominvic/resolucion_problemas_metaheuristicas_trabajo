# main.py
import argparse
import random
import time
from src.problem import Task, Crane, GCSP_Instance, get_equidistant_positions
from src.algorithms import multi_start_solver, variable_neighborhood_search, calculate_lower_bound

# --- Generador al vuelo para el Benchmark (Flexible) ---
def generate_benchmark_instances(n_tasks, n_cranes, min_p, max_p, num_instances=6):
    """
    Genera un lote de instancias aleatorias con tiempos de procesamiento
    en el rango [min_p, max_p], tal como especifica el paper.
    """
    instances = []
    for i in range(num_instances):
        # Generar tareas con distribución uniforme correcta
        tasks = [Task(t_id, t_id, random.randint(min_p, max_p)) for t_id in range(1, n_tasks + 1)]
        
        # Posicionar grúas
        locs = get_equidistant_positions(n_tasks, n_cranes)
        cranes = [Crane(k, locs[k-1]) for k in range(1, n_cranes + 1)]
        
        # Crear objeto instancia
        inst = GCSP_Instance(tasks, cranes)
        inst.name = f"{n_tasks}x{n_cranes}_{i+1}"
        instances.append(inst)
    return instances

def main():
    parser = argparse.ArgumentParser(description="Benchmark Paper GCSP")
    
    parser.add_argument('--size', type=str, choices=['small', 'medium', 'large'], required=True, 
                        help="Conjunto de experimentos a ejecutar.")
    
    # Parámetros del algoritmo
    parser.add_argument('--restarts', type=int, default=5, help="Nº Intentos para hacer la media (Default: 5).")
    parser.add_argument('--iter', type=int, default=200, help="Iteraciones Tabú.")
    parser.add_argument('--tenure', type=int, default=8, help="Tabu Tenure.")
    parser.add_argument('--candidates', type=int, default=20, help="Vecinos por iteración.")
    parser.add_argument('--init', type=str, default='grasp', choices=['grasp', 'random'])

    args = parser.parse_args()

    # 1. Definir los tamaños (Pares N x M) y los rangos de tiempo
    benchmarks = []
    min_p, max_p = 30, 180 # Valor por defecto (Medium/Large)
    
    if args.size == 'small':
        # Instancias Pequeñas: Paper usa Uniforme[20, 150]
        min_p, max_p = 20, 150
        benchmarks = [
            (10, 2), (12, 2), (12, 3) 
            # Añade aquí más tamaños si el paper tiene otros 'small'
        ]
    elif args.size == 'medium':
        # Instancias Medianas: Paper usa Uniforme[30, 180]
        min_p, max_p = 30, 180
        benchmarks = [
            (15, 2), (15, 3), (20, 2), (20, 3)
        ]
    elif args.size == 'large':
        # Instancias Grandes: Paper usa Uniforme[30, 180]
        min_p, max_p = 30, 180
        tasks_list = [30, 40, 50, 60, 70]
        cranes_list = [3, 4, 5]
        benchmarks = [(t, c) for t in tasks_list for c in cranes_list]

    print(f"\n=== BENCHMARK: {args.size.upper()} | 6 Instancias x Tamaño | Media de {args.restarts} ejecuciones ===")
    print(f"Config: Init={args.init} | Iter={args.iter} | Tenure={args.tenure} | Cand={args.candidates}")
    print(f"Distribución Tiempos: Uniforme [{min_p}, {max_p}]")
    
    # Cabecera de la tabla comparativa
    print("-" * 95)
    print(f"{'Tamaño (NxM)':<15} | {'LB Promedio':<12} | {'Makespan Avg':<12} | {'GAP Avg (%)':<12} | {'Time Avg (s)':<12}")
    print("-" * 95)

    # Bucle Principal: Por cada tamaño
    for (n_tasks, n_cranes) in benchmarks:
        
        # Generar las 6 instancias con el rango CORRECTO
        instances_6 = generate_benchmark_instances(n_tasks, n_cranes, min_p, max_p, num_instances=6)
        
        sum_gap = 0
        sum_makespan = 0
        sum_lb = 0
        sum_time = 0
        
        # Ejecutar las 6 instancias
        for inst in instances_6:
            lb = calculate_lower_bound(inst)
            
            # Llamada al solver
            _, avg_mk, avg_t = multi_start_solver(
                instance=inst,
                algorithm_func=variable_neighborhood_search,
                n_restarts=args.restarts, 
                grasp_alpha=0.5,
                tabu_tenure=args.tenure,
                max_iter=args.iter,
                candidates_per_iter=args.candidates,
                vns_loops=10,
                init_strategy=args.init
            )
            
            # Cálculo del GAP para esta instancia
            # Cuidado: Si LB es 0 (caso raro), evitar división por cero
            if lb > 0:
                gap = ((avg_mk - lb) / lb) * 100
            else:
                gap = 0.0
            
            sum_lb += lb
            sum_makespan += avg_mk
            sum_gap += gap
            sum_time += avg_t

        # Calcular promedios finales
        final_lb = sum_lb / 6
        final_makespan = sum_makespan / 6
        final_gap = sum_gap / 6
        final_time = sum_time / 6
        
        # Imprimir fila
        size_str = f"{n_tasks} x {n_cranes}"
        print(f"{size_str:<15} | {final_lb:<12.1f} | {final_makespan:<12.1f} | {final_gap:<12.2f} | {final_time:<12.2f}")

    print("-" * 95)
    print("=== FIN DEL BENCHMARK ===")

if __name__ == "__main__":
    main()