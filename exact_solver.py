import pulp
import time
import argparse
import glob
import sys
import math
from collections import defaultdict
from src.io_handler import load_instance_from_json

def solve_exact_pulp(instance, time_limit_sec=1200):
    tasks = instance.tasks
    cranes = instance.cranes
    num_cranes = len(cranes)
    
    # Pre-cálculos para Cotas
    total_processing_time = sum(t.p_0 for t in tasks)
    max_processing_time = max(t.p_0 for t in tasks)
    
    # Big-M: Usamos la suma total como horizonte seguro
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

    # --- 4. OPTIMIZACIÓN: COTAS INFERIORES (Cortes) ---
    # Esto ayuda al solver a descartar soluciones imposibles rápido
    
    # A. Cota de Capacidad: Cmax >= (Suma total) / num_gruas
    prob += Cmax >= total_processing_time / num_cranes
    
    # B. Cota de Tarea Máxima: Cmax >= Tarea más larga
    prob += Cmax >= max_processing_time

    # C. Cota Suma Asignada (Cut local): La suma de lo asignado a UNA grúa <= Cmax
    for c in cranes:
        prob += pulp.lpSum(t.p_0 * x[t.id, c.id] for t in tasks) <= Cmax

    # 5. Restricciones Estructurales
    
    # R1: Cada tarea asignada a EXACTAMENTE una grúa
    for t in tasks:
        prob += pulp.lpSum(x[t.id, c.id] for c in cranes) == 1

    # R2: Definición de Tiempos
    for t in tasks:
        prob += C[t.id] == S[t.id] + t.p_0
        prob += Cmax >= C[t.id]

    # R3: Secuenciación en la misma grúa (Disyuntiva Big-M)
    for c in cranes:
        for (t1_id, t2_id) in pair_keys:
            # Si x1=1 y x2=1 en la misma grúa, activar restricción de orden
            
            # Caso y=1 (t1 antes t2): S[t2] >= C[t1]
            prob += S[t2_id] >= C[t1_id] - BigM * (3 - x[t1_id,c.id] - x[t2_id,c.id] - y[t1_id,t2_id])

            # Caso y=0 (t2 antes t1): S[t1] >= C[t2]
            prob += S[t1_id] >= C[t2_id] - BigM * (2 - x[t1_id,c.id] - x[t2_id,c.id] + y[t1_id,t2_id])

    # 6. Resolución
    # msg=False reduce el ruido en consola, ponlo True si quieres ver el log
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

    files = sorted(glob.glob(f"instances/{args.size}_*.json"))
    if not files:
        print("Error: No hay archivos JSON. Ejecuta generate_dataset.py")
        sys.exit()

    print(f"\n=== EJECUTANDO MÉTODO EXACTO (AGREGADO) | SIZE: {args.size} ===")
    print(f"Progreso en tiempo real (Paciencia para instancias densas como 10x3)...")
    print("-" * 60)
    print(f"{'Instancia':<20} | {'MK':<10} | {'Time (s)':<10}")
    print("-" * 60)
    
    # Estructura para agrupar resultados: results[(n_tasks, n_cranes)] = [list of (mk, time)]
    results_agg = defaultdict(list)
    
    # Contadores globales
    total_instances = len(files)
    processed = 0

    for filepath in files:
        inst = load_instance_from_json(filepath)
        
        # Resolver
        mk, t = solve_exact_pulp(inst, args.timeout)
        
        processed += 1
        
        # Mostrar progreso individual (para que sepas que no se ha colgado)
        mk_str = f"{mk:.1f}" if mk is not None else "TIMEOUT"
        print(f"[{processed}/{total_instances}] {inst.name:<20} | {mk_str:<10} | {t:<10.2f}")
        
        # Guardar para la media (solo si se resolvió)
        key = (len(inst.tasks), len(inst.cranes))
        
        if mk is not None:
            results_agg[key].append((mk, t))
        else:
            # Si hace timeout, decidimos si guardarlo como None o penalizar
            # Para la tabla, lo marcamos como no resuelto
            results_agg[key].append((None, t))

    # --- TABLA FINAL DE MEDIAS ---
    print("\n" + "="*80)
    print(f"RESUMEN FINAL (MEDIAS) - COPIAR AL PAPER")
    print("="*80)
    print(f"{'Tamaño (NxM)':<15} | {'Instancias':<10} | {'Avg Makespan':<15} | {'Avg Time (s)':<15} | {'Resueltas':<10}")
    print("-" * 80)

    # Ordenar por número de tareas y luego grúas
    sorted_keys = sorted(results_agg.keys(), key=lambda x: (x[0], x[1]))

    for (n_tasks, n_cranes) in sorted_keys:
        data = results_agg[(n_tasks, n_cranes)]
        
        # Filtrar solo las resueltas para el promedio de MK
        solved_data = [d for d in data if d[0] is not None]
        num_total = len(data)
        num_solved = len(solved_data)
        
        if num_solved > 0:
            avg_mk = sum(d[0] for d in solved_data) / num_solved
            # El tiempo promedio solemos quererlo de TODAS (incluso las que gastaron 1200s y fallaron)
            # O solo de las resueltas. Normalmente: promedio de las resueltas.
            avg_time = sum(d[1] for d in solved_data) / num_solved
            
            print(f"{n_tasks} x {n_cranes:<11} | {num_total:<10} | {avg_mk:<15.2f} | {avg_time:<15.2f} | {num_solved}/{num_total}")
        else:
            # Caso donde fallaron todas (TIMEOUT)
            print(f"{n_tasks} x {n_cranes:<11} | {num_total:<10} | {'-':<15} | {'> 1200':<15} | 0/{num_total}")
            
    print("="*80)