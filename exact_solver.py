import pulp
import time
import argparse
import glob
import sys
import os
import re
from src.io_handler import load_instance_from_json

# --- FUNCIÓN DE ORDENACIÓN ---
def get_sort_key(filepath):
    filename = os.path.basename(filepath)
    numbers = re.findall(r'\d+', filename)
    if len(numbers) >= 3:
        return int(numbers[0]), int(numbers[1]), int(numbers[2])
    return 0, 0, 0

# --- FUNCIÓN DE RESOLUCIÓN ---
def solve_exact(instance_data, time_limit_sec):
    tasks = instance_data.tasks
    cranes = instance_data.cranes
    num_cranes = len(cranes)
    
    total_processing_time = sum(t.p_0 for t in tasks)
    max_processing_time = max(t.p_0 for t in tasks)
    BigM = total_processing_time

    prob = pulp.LpProblem("GCSP_Exact", pulp.LpMinimize)

    # Variables
    x = pulp.LpVariable.dicts("x", ((t.id, c.id) for t in tasks for c in cranes), cat='Binary')
    S = pulp.LpVariable.dicts("S", (t.id for t in tasks), lowBound=0, upBound=BigM, cat='Continuous')
    C = pulp.LpVariable.dicts("C", (t.id for t in tasks), lowBound=0, upBound=BigM, cat='Continuous')
    Cmax = pulp.LpVariable("Cmax", lowBound=0, upBound=BigM, cat='Continuous')
    
    pair_keys = [(t1.id, t2.id) for t1 in tasks for t2 in tasks if t1.id < t2.id]
    y = pulp.LpVariable.dicts("y", pair_keys, cat='Binary')

    # Función Objetivo
    prob += Cmax

    # Restricciones
    prob += Cmax >= total_processing_time / num_cranes
    prob += Cmax >= max_processing_time
    for c in cranes:
        prob += pulp.lpSum(t.p_0 * x[t.id, c.id] for t in tasks) <= Cmax

    for t in tasks:
        prob += pulp.lpSum(x[t.id, c.id] for c in cranes) == 1
        prob += C[t.id] == S[t.id] + t.p_0
        prob += Cmax >= C[t.id]

    for c in cranes:
        for (t1_id, t2_id) in pair_keys:
            prob += S[t2_id] >= C[t1_id] - BigM * (3 - x[t1_id,c.id] - x[t2_id,c.id] - y[t1_id,t2_id])
            prob += S[t1_id] >= C[t2_id] - BigM * (2 - x[t1_id,c.id] - x[t2_id,c.id] + y[t1_id,t2_id])

    # Configuración del solver con límite de tiempo estricto
    # timeLimit es el parámetro que entiende el motor CBC
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit_sec)
    
    start_time = time.time()
    try:
        prob.solve(solver)
    except:
        # En caso de error inesperado o interrupción forzada
        pass
    elapsed = time.time() - start_time
    
    status = pulp.LpStatus[prob.status]
    
    # Verificamos si se obtuvo una solución válida
    # Si el tiempo transcurrido es mayor o igual al límite, o el estado no es óptimo/factible:
    if status in ['Optimal', 'Feasible'] and elapsed < (time_limit_sec + 2):
        return pulp.value(Cmax), elapsed, "OK"
    else:
        # Forzamos el MK a 0 si hay TIMEOUT o falla
        return 0.0, elapsed, "TIMEOUT"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=str, required=True, choices=['small', 'medium', 'large'])
    parser.add_argument('--timeout', type=int, default=600)
    args = parser.parse_args()

    files = glob.glob(f"instances/{args.size}_*.json")
    if not files:
        print("Error: No hay archivos JSON.")
        sys.exit()

    files.sort(key=get_sort_key)
    output_file = f"resultados_exactos_{args.size}.txt"

    print(f"\n=== EJECUCIÓN EXACTO | TAMAÑO: {args.size} | Límite: {args.timeout}s ===")
    
    with open(output_file, "w") as f:
        # Cabecera simple para Excel
        f.write(f"Instancia;N;M;Makespan;Tiempo;Estado\n")
        
        for filepath in files:
            inst = load_instance_from_json(filepath)
            mk, t, status_str = solve_exact(inst, args.timeout)
            
            n_tasks = len(inst.tasks)
            m_cranes = len(inst.cranes)
            
            # Resultado por consola
            print(f"Instancia: {inst.name:<20} | MK: {mk:>8.1f} | T: {t:>7.2f}s | {status_str}")
            
            # Guardar en archivo (sin medias, solo datos de la instancia)
            f.write(f"{inst.name};{n_tasks};{m_cranes};{mk:.1f};{t:.2f};{status_str}\n")

    print(f"\nProceso finalizado. Resultados guardados en: {output_file}")