import pulp
import time
import argparse
import glob
import sys
import os
import re
import multiprocessing
from collections import defaultdict
from src.io_handler import load_instance_from_json

# --- FUNCIÓN DE ORDENACIÓN ---
def get_sort_key(filepath):
    filename = os.path.basename(filepath)
    numbers = re.findall(r'\d+', filename)
    if len(numbers) >= 3:
        return int(numbers[0]), int(numbers[1]), int(numbers[2])
    return 0, 0, 0

# --- FUNCIÓN WORKER (PROCESO HIJO) ---
def solve_process(instance_data, return_dict):
    """
    Esta función se ejecuta en un proceso aislado.
    Recibe los datos crudos para reconstruir el modelo y resolverlo.
    """
    # Reconstruir datos (multiprocessing no pasa bien los objetos complejos, mejor pasar dicts o primitivos)
    # Sin embargo, en este script simple, podemos intentar pasar la instancia si es pickleable.
    # Si da error, pasamos solo las rutas.
    
    # IMPORTANTE: Re-importar dentro del proceso si fuera necesario, pero aquí hereda contexto.
    tasks = instance_data.tasks
    cranes = instance_data.cranes
    num_cranes = len(cranes)
    
    total_processing_time = sum(t.p_0 for t in tasks)
    max_processing_time = max(t.p_0 for t in tasks)
    BigM = total_processing_time

    # Definir Problema
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

    # Restricciones y Cortes
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

    # Resolver (sin límite de tiempo interno, lo controla el padre)
    # Usamos msg=False para que no ensucie la consola
    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)
    
    # Guardar resultado en el diccionario compartido
    status = pulp.LpStatus[prob.status]
    if status == 'Optimal' or status == 'Feasible':
        return_dict['makespan'] = pulp.value(Cmax)
        return_dict['status'] = 'OK'
    else:
        return_dict['makespan'] = None
        return_dict['status'] = 'FAIL'

# --- FUNCIÓN PRINCIPAL DE CONTROL ---
def solve_exact_with_hard_timeout(instance, time_limit_sec):
    """
    Lanza el solver en un proceso separado y lo mata si excede el tiempo.
    """
    # Gestor de memoria compartida
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    
    # Crear el proceso
    p = multiprocessing.Process(target=solve_process, args=(instance, return_dict))
    
    start_time = time.time()
    p.start()
    
    # Esperar el tiempo límite (join con timeout)
    p.join(time_limit_sec)
    
    elapsed = time.time() - start_time
    
    # Verificamos si sigue vivo
    if p.is_alive():
        # ¡TIMEOUT REAL!
        p.terminate() # Intentar cerrar amablemente
        time.sleep(0.1)
        if p.is_alive():
            p.kill() # Matar forzosamente (SIGKILL)
        p.join() # Limpiar proceso zombie
        
        return None, time_limit_sec # Devolvemos el límite exacto (o elapsed)
    else:
        # Terminó a tiempo
        mk = return_dict.get('makespan')
        return mk, elapsed

if __name__ == "__main__":
    # Fix para Windows (necesario para multiprocessing)
    multiprocessing.freeze_support()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=str, required=True, choices=['small', 'medium', 'large'])
    parser.add_argument('--timeout', type=int, default=650)
    args = parser.parse_args()

    files = glob.glob(f"instances/{args.size}_*.json")
    if not files:
        print("Error: No hay archivos JSON.")
        sys.exit()

    files.sort(key=get_sort_key)
    output_file = f"resultados_exactos_{args.size}.txt"

    print(f"\n=== EXACTO (HARD TIMEOUT) | SIZE: {args.size} | Limit: {args.timeout}s ===")
    print("-" * 65)
    print(f"{'Instancia':<25} | {'Makespan':<10} | {'Time (s)':<10} | {'Status':<10}")
    print("-" * 65)
    
    results_agg = defaultdict(list)
    processed_count = 0

    for filepath in files:
        inst = load_instance_from_json(filepath)
        
        # LLAMADA A LA NUEVA FUNCIÓN BLINDADA
        mk, t = solve_exact_with_hard_timeout(inst, args.timeout)
        
        processed_count += 1
        
        # Ajuste visual: Si t >= timeout, forzamos que se vea como timeout
        is_timeout = mk is None or t >= args.timeout
        status_str = "TIMEOUT" if is_timeout else "OK"
        mk_str = f"{mk:.1f}" if mk is not None else "-"
        
        print(f"[{processed_count}/{len(files)}] {inst.name:<22} | {mk_str:<10} | {t:<10.2f} | {status_str}")
        
        # Guardar (Si es timeout, guardamos None en makespan)
        key = (len(inst.tasks), len(inst.cranes))
        results_agg[key].append((mk, t))

    # --- GENERAR INFORME (Igual que antes) ---
    with open(output_file, "w") as f:
        header = f"RESULTADOS EXACTOS (HARD TIMEOUT) - {args.size.upper()}\n"
        f.write("=" * 80 + "\n" + header + "=" * 80 + "\n")
        f.write(f"{'Tamaño':<15} | {'Muestras':<10} | {'Avg MK':<15} | {'Avg Time':<15}\n")
        f.write("-" * 80 + "\n")

        for (n_tasks, n_cranes) in sorted(results_agg.keys()):
            data = results_agg[(n_tasks, n_cranes)]
            solved = [d for d in data if d[0] is not None]
            
            if solved:
                avg_mk = sum(d[0] for d in solved) / len(solved)
                avg_time = sum(d[1] for d in solved) / len(solved) # Tiempo de las resueltas
                # Opcional: avg_time global incluyendo los 600s de los fallos
                
                line = f"{n_tasks} x {n_cranes:<11} | {len(data):<10} | {avg_mk:<15.2f} | {avg_time:<15.2f}\n"
            else:
                line = f"{n_tasks} x {n_cranes:<11} | {len(data):<10} | {'TIMEOUT':<15} | {'> LIMIT':<15}\n"
            
            f.write(line)
            print(line.strip())

    print("\n" + "="*65)
    print(f"Completado. Guardado en '{output_file}'")