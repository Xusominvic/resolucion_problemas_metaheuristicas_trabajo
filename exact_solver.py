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
    tasks = instance_data.tasks
    cranes = instance_data.cranes
    num_cranes = len(cranes)
    
    total_processing_time = sum(t.p_0 for t in tasks)
    max_processing_time = max(t.p_0 for t in tasks)
    BigM = total_processing_time

    prob = pulp.LpProblem("GCSP_Exact", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x", ((t.id, c.id) for t in tasks for c in cranes), cat='Binary')
    S = pulp.LpVariable.dicts("S", (t.id for t in tasks), lowBound=0, upBound=BigM, cat='Continuous')
    C = pulp.LpVariable.dicts("C", (t.id for t in tasks), lowBound=0, upBound=BigM, cat='Continuous')
    Cmax = pulp.LpVariable("Cmax", lowBound=0, upBound=BigM, cat='Continuous')
    
    pair_keys = [(t1.id, t2.id) for t1 in tasks for t2 in tasks if t1.id < t2.id]
    y = pulp.LpVariable.dicts("y", pair_keys, cat='Binary')

    prob += Cmax

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

    solver = pulp.PULP_CBC_CMD(msg=False)
    prob.solve(solver)
    
    status = pulp.LpStatus[prob.status]
    if status == 'Optimal' or status == 'Feasible':
        return_dict['makespan'] = pulp.value(Cmax)
        return_dict['status'] = 'OK'
    else:
        return_dict['makespan'] = None
        return_dict['status'] = 'FAIL'

# --- FUNCIÓN DE CONTROL CON TIMEOUT ---
def solve_exact_with_hard_timeout(instance, time_limit_sec):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=solve_process, args=(instance, return_dict))
    
    start_time = time.time()
    p.start()
    p.join(time_limit_sec)
    elapsed = time.time() - start_time
    
    if p.is_alive():
        p.terminate()
        time.sleep(0.1)
        if p.is_alive(): p.kill()
        p.join()
        return None, elapsed
    else:
        mk = return_dict.get('makespan')
        return mk, elapsed

if __name__ == "__main__":
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

    results_detailed = [] # Para guardar la traza completa
    results_agg = defaultdict(list)

    print(f"\n=== EJECUCIÓN EXACTO | SIZE: {args.size} | Timeout: {args.timeout}s ===")
    
    for filepath in files:
        inst = load_instance_from_json(filepath)
        mk, t = solve_exact_with_hard_timeout(inst, args.timeout)
        
        status_str = "TIMEOUT" if mk is None else "OK"
        mk_val = mk if mk is not None else -1.0
        
        # Guardar traza individual
        res_entry = {
            'name': inst.name,
            'n': len(inst.tasks),
            'm': len(inst.cranes),
            'makespan': mk_val,
            'time': t,
            'status': status_str
        }
        results_detailed.append(res_entry)
        results_agg[(res_entry['n'], res_entry['m'])].append(res_entry)
        
        print(f"Instancia: {inst.name:<20} | MK: {res_entry['makespan']:>8.1f} | T: {t:>7.2f}s | {status_str}")

    # --- ESCRIBIR ARCHIVO DE SALIDA ---
    with open(output_file, "w") as f:
        f.write(f"REPORTE DETALLADO - SOLVER EXACTO - {args.size.upper()}\n")
        f.write("="*90 + "\n\n")

        # 1. TRAZA COMPLETA (Instancia por instancia)
        f.write("1. TRAZA COMPLETA DE INSTANCIAS\n")
        f.write("-" * 90 + "\n")
        f.write(f"{'Instancia':<25} | {'Tamaño':<10} | {'Makespan':<12} | {'Tiempo (s)':<12} | {'Estado':<10}\n")
        f.write("-" * 90 + "\n")
        for r in results_detailed:
            mk_s = f"{r['makespan']:.1f}" if r['makespan'] > 0 else "TIMEOUT"
            f.write(f"{r['name']:<25} | {r['n']}x{r['m']:<7} | {mk_s:<12} | {r['time']:<12.2f} | {r['status']:<10}\n")
        
        # 2. RESUMEN POR GRUPOS (Medias)
        f.write("\n\n2. RESUMEN AGREGADO POR TAMAÑO\n")
        f.write("-" * 90 + "\n")
        f.write(f"{'Tamaño':<10} | {'Total':<6} | {'OK':<4} | {'Avg MK (OK)':<15} | {'Avg Time (OK)':<15} | {'Avg Time (All)':<15}\n")
        f.write("-" * 90 + "\n")
        
        for (n, m) in sorted(results_agg.keys()):
            group = results_agg[(n, m)]
            solved = [r for r in group if r['makespan'] > 0]
            
            avg_mk_ok = sum(r['makespan'] for r in solved) / len(solved) if solved else 0
            avg_t_ok = sum(r['time'] for r in solved) / len(solved) if solved else 0
            avg_t_all = sum(r['time'] for r in group) / len(group)
            
            f.write(f"{n}x{m:<7} | {len(group):<6} | {len(solved):<4} | {avg_mk_ok:<15.2f} | {avg_t_ok:<15.2f} | {avg_t_all:<15.2f}\n")

        # 3. DATOS BRUTOS PARA EXCEL (Formato CSV simple al final)
        f.write("\n\n3. DATOS BRUTOS (COPIAR A EXCEL)\n")
        f.write("Nombre;N;M;Makespan;Tiempo;Estado\n")
        for r in results_detailed:
            f.write(f"{r['name']};{r['n']};{r['m']};{r['makespan']};{r['time']};{r['status']}\n")

    print(f"\nProceso finalizado. Se han guardado todos los datos (incluida la traza) en: {output_file}")