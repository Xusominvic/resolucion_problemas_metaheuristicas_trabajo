import argparse
import glob
import os
import re
import signal
from collections import defaultdict
from src.algorithms import multi_start_solver, variable_neighborhood_search, calculate_lower_bound
from src.io_handler import load_instance_from_json

# --- FUNCIÓN DE TIEMPO LÍMITE (TIMEOUT) ---
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException()

# --- FUNCIÓN DE ORDENACIÓN ---
def get_sort_key(filepath):
    filename = os.path.basename(filepath)
    numbers = re.findall(r'\d+', filename)
    if len(numbers) >= 3:
        return int(numbers[0]), int(numbers[1]), int(numbers[2])
    return 0, 0, 0

def main():
    parser = argparse.ArgumentParser(description="Metaheurística (VNS/Tabu) para GCSP")
    parser.add_argument('--size', type=str, choices=['small', 'medium', 'large'], required=True)
    parser.add_argument('--restarts', type=int, default=5, help="Nº de intentos por instancia")
    parser.add_argument('--tenure', type=int, default=8, help="Tabu Tenure")
    parser.add_argument('--candidates', type=int, default=20, help="Candidatos GRASP")
    parser.add_argument('--init', type=str, default='grasp', choices=['grasp', 'random'])
    
    args = parser.parse_args()

    search_pattern = f"instances/{args.size}_*.json"
    files = glob.glob(search_pattern)
    
    if not files:
        print(f"ERROR: No se encontraron instancias en '{search_pattern}'.")
        return

    files.sort(key=get_sort_key)
    output_file = f"resultados_simplificados_{args.size}.txt"

    print(f"\n=== METAHEURÍSTICA | SIZE: {args.size.upper()} | LIMIT: 600s ===")
    print("-" * 85)
    print(f"{'Instancia':<22} | {'Makespan':<10} | {'Tiempo(s)':<10} | {'LB':<8} | {'GAP %':<8}")
    print("-" * 85)

    # Configurar la señal de alarma (Solo funciona en Sistemas UNIX/Linux/Mac)
    # Si usas Windows, este método requiere una alternativa con Multiprocessing
    if os.name != 'nt':
        signal.signal(signal.SIGALRM, timeout_handler)

    with open(output_file, "w") as f:
        f.write(f"Instancia,Makespan,Tiempo,LB,GAP\n")

        for filepath in files:
            inst = load_instance_from_json(filepath)
            n_tasks = len(inst.tasks)
            n_cranes = len(inst.cranes)
            
            dynamic_iter = 6 * n_tasks * n_cranes
            sn_param = 3 * n_tasks
            lb = calculate_lower_bound(inst)
            
            # Variables para el resultado
            mk, t, gap = "TIMEOUT", "600.00", "N/A"

            # ACTIVAR EL LÍMITE DE TIEMPO REAL (600 SEGUNDOS)
            if os.name != 'nt':
                signal.alarm(600) 

            try:
                # Ejecutar algoritmo
                best_seq, avg_mk, avg_t = multi_start_solver(
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
                
                # Si termina antes del timeout:
                mk = f"{avg_mk:.1f}"
                t = f"{avg_t:.2f}"
                if lb > 0:
                    gap = f"{((avg_mk - lb) / lb) * 100:.2f}"
                else:
                    gap = "0.00"

            except TimeoutException:
                print(f"!!! {inst.name:<18} -> Límite de 600s alcanzado. Saltando...")
            finally:
                if os.name != 'nt':
                    signal.alarm(0) # Desactivar la alarma

            # Imprimir y Guardar
            result_line = f"{inst.name:<22} | {mk:<10} | {t:<10} | {lb:<8.1f} | {gap:<8}"
            print(result_line)
            f.write(f"{inst.name},{mk},{t},{lb},{gap}\n")

    print("\n" + "="*80)
    print(f"Proceso finalizado. Resultados en '{output_file}'")

if __name__ == "__main__":
    main()