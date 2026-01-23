import pulp
import time
import argparse
import glob
import sys
import os
import re
from collections import defaultdict
from src.io_handler import load_instance_from_json

# --- FUNCIÓN DE ORDENACIÓN ---
def get_sort_key(filepath):
    """
    Extrae los números del nombre del archivo para ordenar correctamente.
    Ejemplo: 'instances/small_6x2_1.json' -> (6, 2, 1)
    """
    filename = os.path.basename(filepath)
    # Busca todos los grupos de dígitos en el nombre
    numbers = re.findall(r'\d+', filename)
    if len(numbers) >= 3:
        # Retorna tupla (NumTareas, NumGruas, ID_Instancia)
        return int(numbers[0]), int(numbers[1]), int(numbers[2])
    return 0, 0, 0

def solve_exact_pulp(instance, time_limit_sec=1200):
    tasks = instance.tasks
    cranes = instance.cranes
    num_cranes = len(cranes)
    
    # Pre-cálculos para Cotas
    total_processing_time = sum(t.p_0 for t in tasks)
    max_processing_time = max(t.p_0 for t in tasks)
    
    # Big-M ajustado (Horizonte seguro)
    BigM = total_processing_time

    # 1. Definir Problema
    prob = pulp.LpProblem("GCSP_Exact", pulp.LpMinimize)

    # 2. Variables
    x = pulp.LpVariable.dicts("x", 
                              ((t.id, c.id) for t in tasks for c in cranes), 
                              cat='Binary')
    
    S = pulp.LpVariable.dicts("S", (t.id for t in tasks), lowBound=0, upBound=BigM, cat='Continuous')
    C = pulp.LpVariable.dicts("C", (t.id for t in tasks), lowBound=0, upBound=BigM, cat='Continuous')
    Cmax = pulp.LpVariable("Cmax", lowBound=0, upBound=BigM, cat='Continuous')
    
    # Variables de ordenamiento (solo para pares i < j)
    pair_keys = [(t1.id, t2.id) for t1 in tasks for t2 in tasks if t1.id < t2.id]
    y = pulp.LpVariable.dicts("y", pair_keys, cat='Binary')

    # 3. Función Objetivo
    prob += Cmax

    # --- 4. OPTIMIZACIÓN (CORTES) ---
    # Cota de Capacidad
    prob += Cmax >= total_processing_time / num_cranes
    # Cota de Tarea Máxima
    prob += Cmax >= max_processing_time
    # Cota Suma Asignada
    for c in cranes:
        prob += pulp.lpSum(t.p_0 * x[t.id, c.id] for t in tasks) <= Cmax

    # 5. Restricciones Estructurales
    # R1: Cada tarea asignada a una grúa
    for t in tasks:
        prob += pulp.lpSum(x[t.id, c.id] for c in cranes) == 1

    # R2: Definición de Tiempos
    for t in tasks:
        prob += C[t.id] == S[t.id] + t.p_0
        prob += Cmax >= C[t.id]

    # R3: Secuenciación (Big-M)
    for c in cranes:
        for (t1_id, t2_id) in pair_keys:
            # Caso y=1 (t1 antes t2)
            prob += S[t2_id] >= C[t1_id] - BigM * (3 - x[t1_id,c.id] - x[t2_id,c.id] - y[t1_id,t2_id])
            # Caso y=0 (t2 antes t1)
            prob += S[t1_id] >= C[t2_id] - BigM * (2 - x[t1_id,c.id] - x[t2_id,c.id] + y[t1_id,t2_id])

    # 6. Resolución
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit_sec)
    
    start_time = time.time()
    try:
        prob.solve(solver)
    except Exception as e:
        return None, 0

    elapsed = time.time() - start_time
    status = pulp.LpStatus[prob.status]
    
    if status == 'Optimal' or (status == 'Feasible' and elapsed < time_limit_sec):
        return pulp.value(Cmax), elapsed
    else:
        return None, elapsed

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=str, required=True, choices=['small', 'medium', 'large'])
    parser.add_argument('--timeout', type=int, default=1200)
    args = parser.parse_args()

    # 1. Buscar archivos
    search_pattern = f"instances/{args.size}_*.json"
    files = glob.glob(search_pattern)
    
    if not files:
        print(f"Error: No se encontraron archivos con el patrón '{search_pattern}'.")
        print("Asegúrate de haber ejecutado 'generate_dataset.py' primero.")
        sys.exit()

    # 2. ORDENAR CORRECTAMENTE (Numérico)
    files.sort(key=get_sort_key)

    output_file = f"resultados_exactos_{args.size}.txt"
    
    print(f"\n=== MÉTODO EXACTO (PuLP) | SIZE: {args.size} | Total Archivos: {len(files)} ===")
    print(f"Guardando resultados en: {output_file}")
    print("-" * 65)
    print(f"{'Instancia':<25} | {'Makespan':<10} | {'Time (s)':<10} | {'Status':<10}")
    print("-" * 65)
    
    # Estructura para agrupar resultados: results[(n_tasks, n_cranes)] = list of (mk, time)
    results_agg = defaultdict(list)
    processed_count = 0

    # 3. Procesar Instancias
    for filepath in files:
        inst = load_instance_from_json(filepath)
        
        # Resolver
        mk, t = solve_exact_pulp(inst, args.timeout)
        
        processed_count += 1
        
        status_str = "OK" if mk is not None else "TIMEOUT"
        mk_str = f"{mk:.1f}" if mk is not None else "-"
        
        # Imprimir progreso en consola
        print(f"[{processed_count}/{len(files)}] {inst.name:<22} | {mk_str:<10} | {t:<10.2f} | {status_str}")
        
        # Guardar datos
        key = (len(inst.tasks), len(inst.cranes))
        results_agg[key].append((mk, t))

    # --- GENERAR INFORME FINAL (TXT) ---
    with open(output_file, "w") as f:
        header = f"RESUMEN RESULTADOS EXACTOS - {args.size.upper()}\n"
        f.write("=" * 80 + "\n")
        f.write(header)
        f.write("=" * 80 + "\n")
        f.write(f"{'Tamaño (NxM)':<15} | {'Muestras':<10} | {'AVG Makespan':<15} | {'AVG Time (s)':<15}\n")
        f.write("-" * 80 + "\n")

        # Ordenar claves para el TXT
        sorted_keys = sorted(results_agg.keys(), key=lambda x: (x[0], x[1]))

        for (n_tasks, n_cranes) in sorted_keys:
            data = results_agg[(n_tasks, n_cranes)]
            
            # Filtrar solo resueltas para el Makespan
            solved_data = [d for d in data if d[0] is not None]
            num_total = len(data)
            num_solved = len(solved_data)
            
            if num_solved > 0:
                avg_mk = sum(d[0] for d in solved_data) / num_solved
                avg_time = sum(d[1] for d in solved_data) / num_solved
                line = f"{n_tasks} x {n_cranes:<11} | {num_total:<10} | {avg_mk:<15.2f} | {avg_time:<15.2f}\n"
            else:
                line = f"{n_tasks} x {n_cranes:<11} | {num_total:<10} | {'TIMEOUT':<15} | {'> LIMIT':<15}\n"
            
            f.write(line)
            # Imprimir también en consola el resumen final
            print(line.strip())

    print("\n" + "="*65)
    print(f"Proceso finalizado. Resultados guardados en '{output_file}'")