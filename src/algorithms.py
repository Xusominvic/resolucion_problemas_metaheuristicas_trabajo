# src/algorithms.py
import math
import random
import copy
import time

# =========================================================
# 0. CÁLCULO DE COTAS (NUEVO)
# =========================================================
def calculate_lower_bound(instance):
    """
    Calcula la Cota Inferior (Lower Bound) teórica.
    LB = max(Carga Promedio, Tarea Más Larga).
    Es imposible obtener un makespan menor que este valor.
    """
    # 1. Carga Promedio (Average Load)
    total_processing_time = sum(t.p_0 for t in instance.tasks)
    avg_load = total_processing_time / len(instance.cranes)
    
    # 2. Tarea más larga (Max Job)
    max_job = max(t.p_0 for t in instance.tasks)
    
    # El LB es el mayor de los dos (redondeado hacia arriba)
    return math.ceil(max(avg_load, max_job))

# =========================================================
# 1. EVALUADOR (Makespan)
# =========================================================

def calculate_makespan(instance, task_sequence_ids):
    """
    Calcula el makespan de una secuencia de tareas.
    """
    task_map_by_id = {t.id: t for t in instance.tasks}
    n = len(instance.tasks)
    m = len(instance.cranes)
    
    # Estado inicial
    cranes_pos = [0] + [c.location for c in instance.cranes] + [n + 1]
    cranes_avail_time = [float('inf')] + [0.0] * m + [float('inf')]
    tasks_completion_by_loc = [0.0] * (n + 2) 

    for task_id in task_sequence_ids:
        task = task_map_by_id[task_id]
        target_loc = task.location
        
        # Selección de grúa (Lógica Greedy por tiempo disponible)
        selected_crane_idx = -1
        for j in range(len(cranes_pos) - 1):
            if cranes_pos[j] <= target_loc <= cranes_pos[j+1]:
                if cranes_avail_time[j] < cranes_avail_time[j+1]:
                    selected_crane_idx = j
                elif cranes_avail_time[j] > cranes_avail_time[j+1]:
                    selected_crane_idx = j + 1
                else:
                    # Desempate por distancia
                    dist_j = abs(cranes_pos[j] - target_loc)
                    dist_j1 = abs(cranes_pos[j+1] - target_loc)
                    selected_crane_idx = j if dist_j <= dist_j1 else j + 1
                break
        
        # Corrección de seguridad
        if selected_crane_idx == 0: selected_crane_idx = 1
        if selected_crane_idx == m + 1: selected_crane_idx = m
        
        # Cálculo de tiempos
        k = selected_crane_idx
        current_loc = cranes_pos[k]
        
        min_path = min(current_loc, target_loc)
        max_path = max(current_loc, target_loc)
        
        # Bloqueo por interferencias en el trayecto
        max_block_time = 0.0
        for loc in range(min_path, max_path + 1):
            if tasks_completion_by_loc[loc] > max_block_time:
                max_block_time = tasks_completion_by_loc[loc]
        
        travel_time = abs(current_loc - target_loc) * instance.t_0
        start_time = max(max_block_time, cranes_avail_time[k])
        finish_time = start_time + task.p_0 + travel_time
        
        # Actualizar estado
        cranes_pos[k] = target_loc
        cranes_avail_time[k] = finish_time
        tasks_completion_by_loc[target_loc] = finish_time

    return max(tasks_completion_by_loc)


# =========================================================
# 2. OPERADORES DE MOVIMIENTO
# =========================================================

def apply_swap(sequence, i, j):
    new_seq = sequence[:]
    new_seq[i], new_seq[j] = new_seq[j], new_seq[i]
    return new_seq

def apply_insert(sequence, i, j):
    new_seq = sequence[:]
    val = new_seq.pop(j)
    new_seq.insert(i, val)
    return new_seq

def apply_invert(sequence, i, j):
    new_seq = sequence[:]
    start, end = min(i, j), max(i, j)
    new_seq[start:end+1] = new_seq[start:end+1][::-1]
    return new_seq

def get_random_neighbor_specific(sequence, move_type):
    """Genera un vecino específico para el VNS."""
    n = len(sequence)
    if n < 2: return sequence[:]
    idxs = random.sample(range(n), 2)
    i, j = min(idxs), max(idxs)
    
    if move_type == 'swap': return apply_swap(sequence, i, j)
    elif move_type == 'insert': return apply_insert(sequence, i, j)
    elif move_type == 'invert': return apply_invert(sequence, i, j)
    return sequence[:]

def get_neighbor(sequence, method="random"):
    """Genérico para Tabu Search (conservado por compatibilidad)."""
    if method == "random":
        r = random.random()
        method = "swap" if r < 0.33 else ("insert" if r < 0.66 else "invert")
    return get_random_neighbor_specific(sequence, method)


# =========================================================
# 3. CONSTRUCTOR GRASP Y RANDOM
# =========================================================

def construct_random_solution(instance):
    """
    Genera una solución inicial aleatoria (permutación simple).
    """
    seq = [t.id for t in instance.tasks]
    random.shuffle(seq)
    return seq

def construct_grasp_solution(instance, alpha=0.5):
    candidates = [t for t in instance.tasks]
    solution_seq = []
    crane_states = {c.id: {'loc': c.location, 'time': 0.0} for c in instance.cranes}

    while candidates:
        scored_candidates = []
        for task in candidates:
            best_finish = float('inf')
            best_crane = -1
            for c_id, state in crane_states.items():
                dist = abs(state['loc'] - task.location)
                arrival = state['time'] + dist
                finish = arrival + task.p_0
                if finish < best_finish:
                    best_finish = finish
                    best_crane = c_id
            scored_candidates.append({'task': task, 'cost': best_finish, 'crane': best_crane})

        costs = [x['cost'] for x in scored_candidates]
        min_c, max_c = min(costs), max(costs)
        threshold = min_c + alpha * (max_c - min_c)
        rcl = [x for x in scored_candidates if x['cost'] <= threshold]
        
        selection = random.choice(rcl)
        task = selection['task']
        solution_seq.append(task.id)
        candidates.remove(task)
        crane_states[selection['crane']]['loc'] = task.location
        crane_states[selection['crane']]['time'] = selection['cost']
        
    return solution_seq

# =========================================================
# 4. ALGORITMOS (Tabu & VNS)
# =========================================================

def tabu_search(instance, initial_sequence, tabu_tenure=8, max_iter=100, candidates_per_iter=20, **kwargs):
    """
    Búsqueda Tabú (Usada como Local Search dentro del VNS).
    """
    current_seq = initial_sequence[:]
    current_makespan = calculate_makespan(instance, current_seq)
    
    best_seq = current_seq[:]
    best_makespan = current_makespan
    
    tabu_list = []
    
    for _ in range(max_iter):
        best_candidate_seq = None
        best_candidate_makespan = float('inf')
        
        # Evaluar vecindario
        for _ in range(candidates_per_iter):
            neighbor = get_neighbor(current_seq, method="random")
            neighbor_makespan = calculate_makespan(instance, neighbor)
            
            # Criterios Tabú y Aspiración
            is_tabu = tuple(neighbor) in tabu_list
            is_aspiration = neighbor_makespan < best_makespan
            
            if (not is_tabu) or is_aspiration:
                if neighbor_makespan < best_candidate_makespan:
                    best_candidate_makespan = neighbor_makespan
                    best_candidate_seq = neighbor
        
        # Movimiento
        if best_candidate_seq:
            current_seq = best_candidate_seq
            current_makespan = best_candidate_makespan
            
            if current_makespan < best_makespan:
                best_makespan = current_makespan
                best_seq = current_seq[:]
            
            tabu_list.append(tuple(current_seq))
            if len(tabu_list) > tabu_tenure:
                tabu_list.pop(0)
                
    return best_seq, best_makespan, []


def variable_neighborhood_search(instance, initial_seq, **kwargs):
    """
    VNS Híbrido: Director (VNS) + Obrero (Tabu Search).
    """
    neighborhoods = ['swap', 'insert', 'invert']
    
    # 1. Punto de partida (Refinado una vez con Tabu)
    current_seq, current_makespan, _ = tabu_search(instance, initial_seq, **kwargs)
    
    best_seq = current_seq[:]
    best_makespan = current_makespan
    
    k = 0
    # Como VNS es costoso, limitamos las vueltas del bucle VNS si es necesario
    # O confiamos en que 'tabu_search' consume las iteraciones.
    max_vns_loops = kwargs.get('vns_loops', 5) # Evita bucles infinitos si no mejora
    loop_count = 0
    
    while k < len(neighborhoods) and loop_count < max_vns_loops:
        move_type = neighborhoods[k]
        
        # A. Shaking (Agitación)
        shaking_seq = get_random_neighbor_specific(current_seq, move_type)
        
        # B. Local Search (Intensificación con Tabu)
        improved_seq, improved_val, _ = tabu_search(instance, shaking_seq, **kwargs)
        
        # C. Cambio de Vecindario
        if improved_val < current_makespan:
            # Mejora -> Nos movemos y reiniciamos a Swap (k=0)
            current_makespan = improved_val
            current_seq = improved_seq[:]
            
            if current_makespan < best_makespan:
                best_makespan = current_makespan
                best_seq = current_seq[:]
            
            k = 0 
            loop_count = 0 # Reiniciamos contador de estancamiento
        else:
            # No mejora -> Siguiente vecindario más agresivo
            k += 1
            loop_count += 1
            
    return best_seq, best_makespan, []


# =========================================================
# 5. ESTRATEGIA MULTI-ARRANQUE
# =========================================================

def multi_start_solver(instance, algorithm_func, n_restarts=5, **kwargs):
    """
    Ejecuta el algoritmo 'n_restarts' veces.
    Soporta init_strategy: 
        - 'grasp': Construcción inteligente.
        - 'random': Genera 'pool_size' aleatorias y elige la mejor (Best of SN).
    """
    
    init_strategy = kwargs.get('init_strategy', 'grasp')
    alpha = kwargs.get('grasp_alpha', 0.5)
    pool_size = kwargs.get('pool_size', 1) # SN (Swarm Number) para Random

    results_makespan = []
    results_time = []
    
    best_global_makespan = float('inf')
    best_global_seq = []

    for i in range(n_restarts):
        start_t = time.time()
        
        # 1. Construcción
        if init_strategy == 'random':
            # ESTRATEGIA: Best of SN (Población Aleatoria)
            best_rand_sol = None
            best_rand_val = float('inf')
            
            # Generamos 'pool_size' soluciones y nos quedamos la mejor
            for _ in range(pool_size):
                cand = construct_random_solution(instance)
                val = calculate_makespan(instance, cand)
                if val < best_rand_val:
                    best_rand_val = val
                    best_rand_sol = cand[:]
            
            initial_sol = best_rand_sol
            
        else: 
            # ESTRATEGIA: GRASP
            current_alpha = alpha if isinstance(alpha, float) else random.uniform(0.1, 0.9)
            initial_sol = construct_grasp_solution(instance, alpha=current_alpha)
        
        # 2. Mejora (VNS + Tabu)
        sol, val, _ = algorithm_func(instance, initial_sol, **kwargs)
        
        end_t = time.time()
        elapsed = end_t - start_t
        
        results_makespan.append(val)
        results_time.append(elapsed)

        if val < best_global_makespan:
            best_global_makespan = val
            best_global_seq = sol[:]

    avg_makespan = sum(results_makespan) / len(results_makespan)
    avg_time = sum(results_time) / len(results_time)

    return best_global_seq, avg_makespan, avg_time