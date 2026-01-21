import pulp
import time
import argparse
import glob
import os
from src.io_handler import load_instance_from_json

def solve_exact_pulp(instance, time_limit_sec=1200):
    """
    Resuelve la instancia usando programación lineal entera (CBC Solver).
    Retorna (Makespan, Tiempo_Transcurrido).
    Si falla o excede el tiempo, retorna (None, Tiempo_Transcurrido).
    """
    tasks = instance.tasks
    cranes = instance.cranes
    
    # Big-M: Valor suficientemente grande para relajar restricciones
    # (Suma de tiempos * 2 suele ser seguro)
    BigM = sum(t.p_0 for t in tasks) * 2

    print(f"  -> Construyendo modelo para {instance.name} (T={len(tasks)}, G={len(cranes)})...")

    # --- 1. MODELO ---
    prob = pulp.LpProblem("GCSP_Exact", pulp.LpMinimize)

    # Variables
    # x[i,k] = 1 si tarea i la hace grúa k
    x = pulp.LpVariable.dicts("x", 
                                ((t.id, c.id) for t in tasks for c in cranes), 
                                cat='Binary')
    
    # S[i] = Tiempo inicio tarea i
    S = pulp.LpVariable.dicts("S", (t.id for t in tasks), lowBound=0, cat='Continuous')
    
    # C[i] = Tiempo fin tarea i
    C = pulp.LpVariable.dicts("C", (t.id for t in tasks), lowBound=0, cat='Continuous')
    
    # Cmax = Makespan
    Cmax = pulp.LpVariable("Cmax", lowBound=0, cat='Continuous')
    
    # Ordenamiento y[i,j] = 1 si i precede a j.
    # Optimizacion: Solo crear variables para pares i < j que podrían chocar
    y = pulp.LpVariable.dicts("y", 
                                ((t1.id, t2.id) for t1 in tasks for t2 in tasks if t1.id < t2.id),
                                cat='Binary')

    # --- 2. FUNCIÓN OBJETIVO ---
    prob += Cmax

    # --- 3. RESTRICCIONES ---
    
    # R1: Asignación Única
    for t in tasks:
        prob += pulp.lpSum(x[t.id, c.id] for c in cranes) == 1

    # R2: Definición de Tiempos (C = S + p) y Cmax
    for t in tasks:
        prob += C[t.id] == S[t.id] + t.p_0
        prob += Cmax >= C[t.id]

    # R3: No solapamiento en la misma grúa (Disyuntiva Big-M)
    for c in cranes:
        for t1 in tasks:
            for t2 in tasks:
                if t1.id >= t2.id: continue # Solo procesar i < j una vez
                
                # RESTRICCIÓN CLAVE:
                # Si ambas tareas (t1 y t2) las hace la grúa 'c', no pueden solaparse.
                # Se usa Big-M para que la restricción solo aplique si x[t1,c]=1 Y x[t2,c]=1
                
                # Caso A (y=1 -> t1 antes que t2): S[t2] >= C[t1]
                # Activado solo si x[t1,c] + x[t2,c] = 2. Si no, el término (3 - ...) se hace grande y lo anula.
                prob += S[t2.id] >= C[t1.id] - BigM * (3 - x[t1.id,c.id] - x[t2.id,c.id] - y[t1.id,t2.id])
                
                # Caso B (y=0 -> t2 antes que t1): S[t1] >= C[t2]
                prob += S[t1.id] >= C[t2.id] - BigM * (2 - x[t1.id,c.id] - x[t2.id,c.id] + y[t1.id,t2.id])

    # --- 4. RESOLUCIÓN ---
    # msg=False para no ensuciar la salida, timeLimit define el corte
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit_sec)
    
    start_time = time.time()
    try:
        prob.solve(solver)
    except Exception as e:
        print(f"  Error Solver: {e}")
        elapsed = time.time() - start_time
        return None, elapsed

    elapsed = time.time() - start_time
    status = pulp.LpStatus[prob.status]
    
    # Verificar éxito
    if status == 'Optimal' or (status == 'Feasible' and elapsed < time_limit_sec):
        return pulp.value(Cmax), elapsed
    else:
        # Timeout o Infeasible
        return None, elapsed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solver Exacto (PuLP/CBC) para GCSP")
    
    parser.add_argument('--size', type=str, choices=['small', 'medium', 'large'], required=True, 
                        help="Conjunto de instancias a resolver.")
    
    parser.add_argument('--timeout', type=int, default=1200, 
                        help="Tiempo límite en segundos (Default: 1200s = 20min).")

    args = parser.parse_args()

    # 1. Buscar archivos JSON
    search_pattern = f"instances/{args.size}_*.json"
    files = sorted(glob.glob(search_pattern))
    
    if not files:
        print(f"ERROR: No se encontraron instancias en '{search_pattern}'.")
        print("Ejecuta primero: python generate_dataset.py")
        exit()

    print(f"\n=== SOLVER EXACTO (PuLP) | SIZE: {args.size.upper()} | Timeout: {args.timeout}s ===")
    print("-" * 90)
    print(f"{'Instancia':<25} | {'Makespan':<12} | {'Tiempo (s)':<12} | {'Estado':<15}")
    print("-" * 90)
    
    total_solved = 0
    
    # 2. Recorrer TODOS los archivos
    for filepath in files:
        inst = load_instance_from_json(filepath)
        
        # Llamar al solver con el timeout
        mk, elapsed = solve_exact_pulp(inst, time_limit_sec=args.timeout)
        
        # Preparar datos para imprimir
        if mk is not None:
            mk_str = f"{mk:.1f}"
            status_str = "Optimal"
            total_solved += 1
        else:
            mk_str = "-"
            status_str = "TIMEOUT (>20m)"
            
        print(f"{inst.name:<25} | {mk_str:<12} | {elapsed:<12.2f} | {status_str:<15}")

    print("-" * 90)
    print(f"Resueltas: {total_solved}/{len(files)}")
    print("=== FIN DEL PROCESO EXACTO ===")