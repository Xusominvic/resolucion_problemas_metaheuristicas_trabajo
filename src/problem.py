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
def generate_small_instance():
    num_tasks = random.randint(6, 12)
    num_cranes = random.randint(2, 3)
    
    tasks = [Task(i, i, random.randint(20, 150)) for i in range(1, num_tasks+1)]
    
    locs = get_equidistant_positions(num_tasks, num_cranes)
    cranes = [Crane(k, locs[k-1]) for k in range(1, num_cranes+1)]
    
    return GCSP_Instance(tasks, cranes)

# --- Generador Tamaño Medio (Medium) ---
def generate_medium_instance():
    # n = 15, 16, ..., 20
    num_tasks = random.randint(15, 20) 
    # m = 2, 3, 4
    num_cranes = random.randint(2, 4)  
    
    # Tiempos: U(30, 180)
    tasks = [Task(i, i, random.randint(30, 180)) for i in range(1, num_tasks+1)]
    
    # Posicionamiento: 1 a n distribuido
    locs = get_equidistant_positions(num_tasks, num_cranes)
    cranes = [Crane(k, locs[k-1]) for k in range(1, num_cranes+1)]
    
    return GCSP_Instance(tasks, cranes)

# --- Generador Tamaño Grande (Large) ---
def generate_large_instance():
    # n = 30, 40, 50, 60, 70 (Valores discretos específicos)
    num_tasks = random.choice([30, 40, 50, 60, 70])
    # m = 3, 4, 5
    num_cranes = random.randint(3, 5)
    
    # Tiempos: U(30, 180)
    tasks = [Task(i, i, random.randint(30, 180)) for i in range(1, num_tasks+1)]
    
    # Posicionamiento: 1 a n distribuido
    locs = get_equidistant_positions(num_tasks, num_cranes)
    cranes = [Crane(k, locs[k-1]) for k in range(1, num_cranes+1)]
    
    return GCSP_Instance(tasks, cranes)