import argparse
import glob
import sys
import os
import re
from collections import defaultdict
from src.algorithms import multi_start_solver, variable_neighborhood_search, calculate_lower_bound
from src.io_handler import load_instance_from_json

# --- FUNCIÓN DE ORDENACIÓN (Idéntica al solver) ---
def get_sort_key(filepath):
    """
    Extrae los números del nombre del archivo para ordenar correctamente.
    Ejemplo: 'instances/small_6x2_1.json' -> (6, 2, 1)
    """
    filename = os.path.basename(filepath)
    numbers = re.findall(r'\d+', filename)
    if len(numbers) >= 3:
        return int(numbers[0]), int(numbers[1]), int(numbers[2])
    return 0, 0, 0

def main():
    parser = argparse.ArgumentParser(description="Metaheurística (VNS/Tabu) para GCSP")
    
    # Selección de tamaño (obligatorio)
    parser.add_argument('--size', type=str, choices=['small', 'medium', 'large'], required=True)
    
    # Parámetros del algoritmo
    parser.add_argument('--restarts', type=int, default=5, help="Nº de intentos por instancia (para hacer media)")
    parser.add_argument('--tenure', type=int, default=8, help="Tabu Tenure")
    parser.add_argument('--candidates', type=int, default=20, help="Candidatos GRASP")
    parser.add_argument('--init', type=str, default='grasp', choices=['grasp', 'random'])
    
    args = parser.parse_args()

    # 1. BUSCAR Y ORDENAR ARCHIVOS
    search_pattern = f"instances/{args.size}_*.json"
    files = glob.glob(search_pattern)
    
    if not files:
        print(f"ERROR: No se encontraron instancias en '{search_pattern}'.")
        print("Ejecuta primero: python generate_dataset.py")
        return

    files.sort(key=get_sort_key)

    # Nombre del archivo de salida
    output_file = f"resultados_heuristicas_{args.size}.txt"

    print(f"\n=== METAHEURÍSTICA (VNS) | SIZE: {args.size.upper()} | INSTANCIAS: {len(files)} ===")
    print(f"Config: Init={args.init} | Restarts={args.restarts}")
    print(f"Guardando resultados en: {output_file}")
    
    print("-" * 105)
    print(f"{'Instancia':<22} | {'LB':<8} | {'Avg MK':<10} | {'Avg GAP %':<12} | {'Avg Time':<10}")
    print("-" * 105)

    # Estructura para agrupar: results[(n_tasks, n_cranes)] = lista de diccionarios con metricas
    results_agg = defaultdict(list)
    processed_count = 0

    # 2. PROCESAR INSTANCIAS UNO A UNO
    for filepath in files:
        inst = load_instance_from_json(filepath)
        
        # Parámetros dinámicos basados en el paper
        n_tasks = len(inst.tasks)
        n_cranes = len(inst.cranes)
        
        # Iteraciones según complejidad (Paper Section 5)
        dynamic_iter = 6 * n_tasks * n_cranes
        # Tamaño de piscina para GRASP
        sn_param = 3 * n_tasks
        
        # Calcular Lower Bound (Cota Inferior)
        lb = calculate_lower_bound(inst)
        
        # EJECUTAR ALGORITMO (Hace la media de 'args.restarts' intentos internamente)
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
        
        # Calcular GAP
        if lb > 0:
            gap = ((avg_mk - lb) / lb) * 100
        else:
            gap = 0.0
            
        processed_count += 1
        
        # Imprimir progreso individual
        print(f"[{processed_count}/{len(files)}] {inst.name:<18} | {lb:<8.1f} | {avg_mk:<10.1f} | {gap:<12.2f} | {avg_t:<10.2f}")
        
        # Guardar métricas para el resumen final
        key = (n_tasks, n_cranes)
        results_agg[key].append({
            'lb': lb,
            'mk': avg_mk,
            'gap': gap,
            'time': avg_t
        })

    # 3. GENERAR INFORME FINAL (TXT y Consola)
    with open(output_file, "w") as f:
        header = f"RESUMEN RESULTADOS HEURÍSTICOS - {args.size.upper()}\n"
        separator = "=" * 100 + "\n"
        col_headers = f"{'Tamaño (NxM)':<15} | {'Muestras':<10} | {'Avg LB':<10} | {'Avg MK':<10} | {'Avg GAP %':<12} | {'Avg Time':<10}\n"
        dash_line = "-" * 100 + "\n"

        # Escribir cabecera en archivo
        f.write(separator)
        f.write(header)
        f.write(separator)
        f.write(col_headers)
        f.write(dash_line)

        # Imprimir cabecera en consola (Resumen)
        print("\n" + separator.strip())
        print(header.strip())
        print(col_headers.strip())
        print(dash_line.strip())

        # Ordenar grupos por tamaño
        sorted_keys = sorted(results_agg.keys(), key=lambda x: (x[0], x[1]))

        for (n_tasks, n_cranes) in sorted_keys:
            data_list = results_agg[(n_tasks, n_cranes)]
            num_samples = len(data_list)
            
            # Calcular promedios del grupo
            avg_lb_group = sum(d['lb'] for d in data_list) / num_samples
            avg_mk_group = sum(d['mk'] for d in data_list) / num_samples
            avg_gap_group = sum(d['gap'] for d in data_list) / num_samples
            avg_time_group = sum(d['time'] for d in data_list) / num_samples
            
            line = (f"{n_tasks} x {n_cranes:<11} | {num_samples:<10} | "
                    f"{avg_lb_group:<10.1f} | {avg_mk_group:<10.1f} | "
                    f"{avg_gap_group:<12.2f} | {avg_time_group:<10.2f}\n")
            
            f.write(line)
            print(line.strip())
        
        f.write(separator)

    print("\n" + "="*80)
    print(f"Proceso finalizado. Tabla guardada en '{output_file}'")

if __name__ == "__main__":
    main()