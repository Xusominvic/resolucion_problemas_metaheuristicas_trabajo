# algorithms.py
import math
from . import problem
import random

#################################
####### CALCULAR MAKESPAN #######
#################################

def calculate_makespan(instance, task_sequence_ids):
    """
    Decodificador basado en la Figura 4 del paper.
    Traduce una secuencia de IDs de tareas en un Makespan, respetando
    que las grúas no pueden saltar sobre tareas en proceso.
    """
    # Mapeo rápido de tareas por ID y por Ubicación
    task_map_by_id = {t.id: t for t in instance.tasks}
    # El paper asume que las tareas están indexadas por ubicación para chequear colisiones
    # task_time[loc] guardará cuándo se libera la ubicación 'loc'
    
    n = len(instance.tasks)
    m = len(instance.cranes)
    
    # --- Inicialización (según Fig. 4) ---
    # 1. Grúas: Posiciones actuales [Dummy, C1, C2, ..., Dummy]
    #    Dummy 0 en pos 0, Dummy m+1 en pos n+1
    cranes_pos = [0] + [c.location for c in instance.cranes] + [n + 1]
    
    # 2. Tiempos disponibles de grúas (crane_r)
    #    Dummies con infinito para que nunca sean seleccionados por tiempo
    false_cranes_time = 10000
    cranes_avail_time = [false_cranes_time] + [0.0] * m + [false_cranes_time]
    
    # 3. Tiempos de finalización de tareas por UBICACIÓN (task_time)
    #    Inicializado a 0. Indices 0..n+1 (usamos 1..n)
    #    Representa cuándo la vía en la posición 'i' queda libre.
    tasks_completion_by_loc = [0.0] * (n + 2) 

    # --- Bucle principal (Processing Sequence) ---
    for task_id in task_sequence_ids:
        task = task_map_by_id[task_id]
        target_loc = task.location
        
        selected_crane_idx = -1
        
        # A. Selección de Grúa (Lógica Voraz de Fig. 4)
        # Busamos el intervalo [j, j+1] donde cae la tarea
        for j in range(len(cranes_pos) - 1):
            if cranes_pos[j] <= target_loc <= cranes_pos[j+1]:
                
                # Reglas de decisión [cite: 351-363]
                r_j = cranes_avail_time[j]
                r_j1 = cranes_avail_time[j+1]
                
                if r_j < r_j1:
                    selected_crane_idx = j
                elif r_j > r_j1:
                    selected_crane_idx = j + 1
                else:
                    # Empate: decidir por distancia
                    dist_j = abs(cranes_pos[j] - target_loc)
                    dist_j1 = abs(cranes_pos[j+1] - target_loc)
                    if dist_j < dist_j1:
                        selected_crane_idx = j
                    elif dist_j > dist_j1:
                        selected_crane_idx = j + 1
                    else:
                        selected_crane_idx = j # Default izquierda
                break
        
        # Corrección de seguridad para no elegir dummies
        if selected_crane_idx == 0: selected_crane_idx = 1
        if selected_crane_idx == m + 1: selected_crane_idx = m
        
        # B. Cálculo de Tiempos (Ec. del paper )
        k = selected_crane_idx
        current_loc = cranes_pos[k]
        
        # Rango de movimiento: desde donde está la grúa hasta donde va la tarea
        min_num = min(current_loc, target_loc)
        max_num = max(current_loc, target_loc)
        
        # Interferencia: La grúa no puede completar la operación hasta que
        # TODAS las tareas en el trayecto [min_num, max_num] hayan terminado.
        # Esto modela "Non-crossing" implícito: no puedo pasar si hay alguien trabajando.
        max_task_time_in_path = 0.0
        
        # Iteramos por las ubicaciones físicas que atraviesa la grúa
        # Nota: range en python es [start, end), por eso max_num + 1
        for loc in range(min_num, max_num + 1):
            if tasks_completion_by_loc[loc] > max_task_time_in_path:
                max_task_time_in_path = tasks_completion_by_loc[loc]
        
        # Tiempo de viaje
        travel_time = abs(current_loc - target_loc) * instance.t_0
        
        # Actualización según formula Fig 4:
        # max{task_time(path)} + processing + travel
        # Nota: El paper suma travel AL FINAL, implicando que el viaje es parte del bloqueo
        new_completion_time = max(max_task_time_in_path, cranes_avail_time[k]) + task.p_0 + travel_time
        
        # C. Actualizar Estado
        cranes_pos[k] = target_loc
        cranes_avail_time[k] = new_completion_time
        tasks_completion_by_loc[target_loc] = new_completion_time

    # El makespan es el máximo tiempo de finalización registrado
    return max(tasks_completion_by_loc)



#################################
######### MOVIMIENTOS ###########
#################################

def get_neighbor(sequence, method="random"):
    """
    Genera una solución vecina aplicando un operador de movimiento.
    
    Args:
        sequence (list): La secuencia actual de IDs de tareas.
        method (str): 'swap', 'insert', 'invert' o 'random'.
    
    Returns:
        list: Una NUEVA lista con la modificación (no toca la original).
    """
    # 1. Copia eficiente (Slicing) - O(n)
    # Es crucial no modificar la lista 'sequence' original porque si la solución
    # vecina es mala, querremos descartarla y volver a la original.
    neighbor = sequence[:] 
    n = len(neighbor)
    
    # Si hay menos de 2 tareas, no se puede mover nada
    if n < 2: return neighbor
    
    # 2. Ruleta Probabilística (Selección Uniforme)
    if method == "random":
        r = random.random() # Devuelve float entre 0.0 y 1.0
        if r < 0.33:
            move_type = "swap"
        elif r < 0.66:
            move_type = "insert"
        else:
            move_type = "invert"
    else:
        move_type = method

    # 3. Selección de índices
    # random.sample garantiza que i != j y es muy rápido.
    # Usamos min/max para asegurar que i sea el índice menor (izquierda) y j el mayor (derecha).
    idxs = random.sample(range(n), 2)
    i, j = min(idxs), max(idxs)

    # --- Ejecución del Movimiento ---
    
    if move_type == "swap":
        # Intercambio simple
        # [1, 2, 3, 4] -> swap(0, 3) -> [4, 2, 3, 1]
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        
    elif move_type == "insert":
        # Extraer de j e insertar en i
        # [1, 2, 3, 4] -> insert(1, 3) -> Sacamos el 4 (idx 3) y lo ponemos en idx 1
        # Resultado: [1, 4, 2, 3]
        val = neighbor.pop(j)
        neighbor.insert(i, val)
        
    elif move_type == "invert":
        # Inversión de sub-ruta (2-opt)
        # [1, 2, 3, 4, 5] -> invert(1, 3) -> Invierte sublista [2, 3, 4]
        # Resultado: [1, 4, 3, 2, 5]
        # Python slicing [i:j+1] incluye el elemento j. [::-1] invierte esa slice.
        neighbor[i:j+1] = neighbor[i:j+1][::-1]
        
    return neighbor



#################################
####### RECOCIDO SIMULADO #######
#################################

def simulated_annealing(instance, initial_sequence, initial_temp=1000, cooling_rate=0.95, max_iter=1000):
    """
    Minimiza el Makespan usando Recocido Simulado.
    """
    # 1. Estado Inicial
    current_seq = initial_sequence[:]
    current_makespan = calculate_makespan(instance, current_seq)
    
    # Guardamos la mejor global encontrada
    best_seq = current_seq[:]
    best_makespan = current_makespan
    
    current_temp = initial_temp
    
    # Para monitorear progreso (opcional, retornamos historial)
    history = []
    
    for i in range(max_iter):
        # 2. Generar Vecino (Swap, Insert o Invert)
        neighbor_seq = get_neighbor(current_seq, method="random")
        neighbor_makespan = calculate_makespan(instance, neighbor_seq)
        
        # 3. Calcular Delta (Diferencia de costo)
        # Queremos MINIMIZAR. Delta negativo es bueno.
        delta = neighbor_makespan - current_makespan
        
        # 4. Criterio de Aceptación (Metropolis)
        accept = False
        
        if delta < 0:
            # Mejora: Aceptar siempre
            accept = True
            # Chequear si es record histórico
            if neighbor_makespan < best_makespan:
                best_makespan = neighbor_makespan
                best_seq = neighbor_seq[:]
        else:
            # Empeora: Aceptar con probabilidad probabilística
            # Evitamos overflow si T es muy baja
            if current_temp > 0.001:
                prob = math.exp(-delta / current_temp)
                if random.random() < prob:
                    accept = True
            else:
                accept = False
                
        # 5. Actualizar Estado Actual si aceptamos
        if accept:
            current_seq = neighbor_seq
            current_makespan = neighbor_makespan
            
        # 6. Enfriamiento
        current_temp *= cooling_rate
        
        # Guardar dato para gráfica o log
        history.append(best_makespan)
        
    return best_seq, best_makespan, history


#################################
######### BÚSQUEDA TABÚ #########
#################################

def tabu_search(instance, initial_sequence, tabu_tenure=10, max_iter=200, candidates_per_iter=20):
    """
    Minimiza el Makespan usando Búsqueda Tabú.
    
    Args:
        tabu_tenure (int): Cuántos turnos una solución permanece 'prohibida'.
        candidates_per_iter (int): Cuántos vecinos evaluamos en cada paso antes de movernos.
    """
    # 1. Estado Inicial
    current_seq = initial_sequence[:]
    current_makespan = calculate_makespan(instance, current_seq)
    
    # Mejor Global (Best So Far)
    best_seq = current_seq[:]
    best_makespan = current_makespan
    
    # Lista Tabú (Guardamos tuplas de secuencias porque las listas no son hashables)
    # Estructura: Lista de tuplas. Usamos una lista para mantener orden FIFO.
    tabu_list = [] 
    
    history = []
    
    for it in range(max_iter):
        
        # 2. Exploración de Vecindad (Generar candidatos)
        best_candidate_seq = None
        best_candidate_makespan = float('inf')
        
        # Generamos varios vecinos y buscamos el mejor movimiento posible
        for _ in range(candidates_per_iter):
            neighbor = get_neighbor(current_seq, method="random")
            neighbor_makespan = calculate_makespan(instance, neighbor)
            neighbor_tuple = tuple(neighbor)
            
            # 3. Clasificación del Candidato
            is_tabu = neighbor_tuple in tabu_list
            is_aspiration = neighbor_makespan < best_makespan # Criterio de Aspiración
            
            # Regla de Movimiento:
            # Aceptamos si NO es tabú O si cumple aspiración (es récord)
            if (not is_tabu) or is_aspiration:
                if neighbor_makespan < best_candidate_makespan:
                    best_candidate_makespan = neighbor_makespan
                    best_candidate_seq = neighbor
        
        # 4. Actualizar Estado Actual (Movimiento)
        # Si no encontramos ningún candidato válido (raro, pero posible si todo es tabú), seguimos
        if best_candidate_seq is not None:
            current_seq = best_candidate_seq
            current_makespan = best_candidate_makespan
            
            # Actualizar Mejor Global
            if current_makespan < best_makespan:
                best_makespan = current_makespan
                best_seq = current_seq[:]
            
            # 5. Gestión de Memoria Tabú
            tabu_list.append(tuple(current_seq))
            if len(tabu_list) > tabu_tenure:
                tabu_list.pop(0) # Olvidar el más viejo (FIFO)
        
        history.append(best_makespan)
        
    return best_seq, best_makespan, history


#################################
######### MULTI-ARRANQUE ########
#################################

def multi_start_solver(instance, algorithm_func, n_restarts=10, **kwargs):
    """
    Estrategia Multi-Arranque (Meta-algoritmo).
    Ejecuta 'n_restarts' veces el algoritmo dado desde puntos aleatorios distintos.
    
    Args:
        instance: La instancia del problema (GCSP).
        algorithm_func: La función del algoritmo a usar (simulated_annealing o tabu_search).
        n_restarts: Cuántas veces lanzamos el algoritmo.
        **kwargs: Argumentos extra para el algoritmo (temp, tenure, max_iter...).
        
    Returns:
        best_global_seq, best_global_makespan
    """
    # 1. Preparar variables para el Récord Mundial
    best_global_makespan = float('inf')
    best_global_seq = []
    
    # Lista base de IDs de tareas para barajar
    # Asumimos que los IDs son 1..N o están en instance.tasks
    base_ids = [t.id for t in instance.tasks]
    
    print(f"--- Iniciando Multi-Arranque ({n_restarts} intentos) ---")
    
    for i in range(n_restarts):
        # 2. Generar Semilla Aleatoria (El paracaidista salta en otro sitio)
        current_initial_sol = base_ids[:]
        random.shuffle(current_initial_sol)
        
        # 3. Ejecutar el Algoritmo Local
        # Pasamos **kwargs para que sirva tanto para SA como para Tabú
        sol, val, _ = algorithm_func(instance, current_initial_sol, **kwargs)
        
        # 4. Comprobar si es Récord
        if val < best_global_makespan:
            best_global_makespan = val
            best_global_seq = sol[:]
            print(f"  [Intento {i+1}] ¡Nuevo Récord! Makespan: {best_global_makespan}")
        else:
            # Opcional: imprimir progreso
            # print(f"  [Intento {i+1}] Makespan: {val} (No mejora)")
            pass

    return best_global_seq, best_global_makespan