import random
from src.problem import Task, Crane, GCSP_Instance, get_equidistant_positions
from src.io_handler import save_instance_to_json

def generate_batch(size_label, tasks_list, cranes_list, min_p, max_p, num_instances=5):
    print(f"--- Generando dataset: {size_label} ---")
    
    # Combinatoria de tareas y grúas
    benchmarks = [(t, c) for t in tasks_list for c in cranes_list]
    
    for (n_tasks, n_cranes) in benchmarks:
        for i in range(num_instances):
            # Generar Tareas
            tasks = [Task(t_id, t_id, random.randint(min_p, max_p)) for t_id in range(1, n_tasks + 1)]
            
            # Generar Grúas
            locs = get_equidistant_positions(n_tasks, n_cranes)
            cranes = [Crane(k, locs[k-1]) for k in range(1, n_cranes + 1)]
            
            inst = GCSP_Instance(tasks, cranes)
            # Nombre: size_NxM_id (ej: small_10x2_1)
            inst.name = f"{size_label}_{n_tasks}x{n_cranes}_{i+1}"
            
            save_instance_to_json(inst, folder="instances")
            
    print(f"-> Completado {size_label}")

if __name__ == "__main__":
    # 1. SMALL
    tasks_s = [6, 7, 8, 9, 10, 11, 12]
    cranes_s = [2, 3]
    generate_batch('small', tasks_s, cranes_s, 20, 150)

    # 2. MEDIUM
    tasks_m = [15, 16, 17, 18, 19, 20]
    cranes_m = [2, 3, 4]
    generate_batch('medium', tasks_m, cranes_m, 30, 180)

    # 3. LARGE
    tasks_l = [30, 40, 50, 60, 70]
    cranes_l = [3, 4, 5]
    generate_batch('large', tasks_l, cranes_l, 30, 180)