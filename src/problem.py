import random

# Clase tarea
class Task:
    def __init__(self, task_id, location, base_processing_time):
        self.id = task_id
        self.location = location  # l_i en el paper
        self.p_0 = base_processing_time  # p_i^0 en el paper (sin penalización por dwelling)
        
    def __repr__(self):
        return f"T{self.id}(Loc:{self.location}, Time:{self.p_0})"

# Clase grua
class Crane: 
    def __init__(self, crane_id, initial_location):
        self.id = crane_id
        self.location = initial_location # l_k^0 en el paper
        self.available_time = 0.0 # r_k, se actualizará en la Fase 2
        
    def __repr__(self):
        return f"C{self.id}(StartLoc:{self.location})"

# Clase instancia
class GCSP_Instance:
    def __init__(self, tasks, cranes, safety_margin=1, travel_speed=1):
        self.tasks = tasks     # Lista de objetos Task
        self.cranes = cranes   # Lista de objetos Crane
        self.s = safety_margin # s en el paper
        self.t_0 = travel_speed # t^0 en el paper


# --- Función Auxiliar para posicionar grúas equidistantes ---
def get_equidistant_positions(n_tasks, m_cranes):
    """
    Calcula posiciones distribuidas uniformemente entre 1 y n_tasks.
    Ejemplo: n=10, m=3 -> [1, 5, 10]
    Ejemplo: n=20, m=4 -> [1, 7, 13, 20]
    """
    if m_cranes < 2: return [1]
    if m_cranes == 2: return [1, n_tasks]
    
    positions = []
    # Fórmula de interpolación lineal: Pos_i = 1 + (i * (n-1) / (m-1))
    for i in range(m_cranes):
        pos = 1 + i * (n_tasks - 1) / (m_cranes - 1)
        positions.append(int(round(pos)))
        
    # Aseguramos que la última siempre sea n (por errores de redondeo)
    positions[-1] = n_tasks
    
    # Aseguramos que no haya posiciones repetidas (si m es muy grande para n pequeño)
    # Aunque con tus parámetros (n>=15, m<=5) esto nunca pasará.
    return sorted(list(set(positions)))


# --- Generador Tamaño Pequeño (Small) ---
# Tareas: 6-12 | Grúas: 2-3 | Total: 14 instancias
def generate_all_small_instances():
    instances_list = []
    # random.seed(42) # Descomenta si quieres que los tiempos sean idénticos siempre
    
    for num_tasks in range(6, 13): # 6 a 12
        for num_cranes in range(2, 4): # 2 a 3
            tasks = [Task(i, i, random.randint(20, 150)) for i in range(1, num_tasks+1)]
            locs = get_equidistant_positions(num_tasks, num_cranes)
            cranes = [Crane(k, locs[k-1]) for k in range(1, num_cranes+1)]
            
            inst = GCSP_Instance(tasks, cranes)
            inst.name = f"Small_T{num_tasks}_C{num_cranes}" # Etiqueta útil para el reporte
            instances_list.append(inst)
    return instances_list

# --- Generador Tamaño Mediano (Medium) ---
# Tareas: 13-20 | Grúas: 3-4 | Total: 16 instancias
def generate_all_medium_instances():
    instances_list = []

    # Rango propuesto: 15 a 20 tareas
    for num_tasks in range(15, 21): 
        # Rango propuesto: 2 a 3 grúas
        for num_cranes in range(2, 5): 
            
            tasks = [Task(i, i, random.randint(30, 180)) for i in range(1, num_tasks+1)]
            locs = get_equidistant_positions(num_tasks, num_cranes)
            cranes = [Crane(k, locs[k-1]) for k in range(1, num_cranes+1)]
            
            inst = GCSP_Instance(tasks, cranes)
            inst.name = f"Medium_T{num_tasks}_C{num_cranes}"
            instances_list.append(inst)
    return instances_list

# --- Generador Tamaño Grande (Large) ---
# Tareas: 21-30 | Grúas: 4-6 | Total: 30 instancias
def generate_all_large_instances():
    instances_list = []
    
    # Rango propuesto: 21 a 30 tareas
    for num_tasks in range(21, 31): 
        # Rango propuesto: 4 a 6 grúas (4, 5 y 6)
        for num_cranes in range(4, 7): 
            
            tasks = [Task(i, i, random.randint(30, 180)) for i in range(1, num_tasks+1)]
            locs = get_equidistant_positions(num_tasks, num_cranes)
            cranes = [Crane(k, locs[k-1]) for k in range(1, num_cranes+1)]
            
            inst = GCSP_Instance(tasks, cranes)
            inst.name = f"Large_T{num_tasks}_C{num_cranes}"
            instances_list.append(inst)
    return instances_list