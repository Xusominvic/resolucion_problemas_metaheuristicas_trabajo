import random

class Task: # Clase tareas
    def __init__(self, task_id, location, base_processing_time):
        self.id = task_id
        self.location = location          # Ubicación en el raíl (l_i)
        self.p_0 = base_processing_time   # Tiempo base de trabajo (p_i^0)
    
    def __repr__(self):
        return f"Tarea {self.id} (Loc:{self.location}, Tiempo:{self.p_0})"

class Crane: # Clase Grua
    def __init__(self, crane_id, initial_location):
        self.id = crane_id
        self.location = initial_location  # Donde empieza la grúa (l_k^0)
        self.available_time = 0.0         # Cuando queda libre
        
    def __repr__(self):
        return f"Grúa {self.id} (Inicio:{self.location})"

class GCSP_Instance:
    def __init__(self, tasks, cranes, safety_margin=1, travel_speed=1):
        self.tasks = tasks      # Lista de Tareas
        self.cranes = cranes    # Lista de Grúas
        self.s = safety_margin  # Margen de seguridad entre grúas
        self.t_0 = travel_speed # Velocidad de la grúa