import json
import os
from src.problem import Task, Crane, GCSP_Instance

def save_instance_to_json(instance, folder="instances"):
    """Guarda una instancia GCSP en un archivo JSON."""
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    data = {
        "name": instance.name,
        "num_tasks": len(instance.tasks),
        "num_cranes": len(instance.cranes),
        "tasks": [
            {"id": t.id, "location": t.location, "p_0": t.p_0} 
            for t in instance.tasks
        ],
        "cranes": [
            {"id": c.id, "location": c.location} 
            for c in instance.cranes
        ]
    }
    
    filepath = os.path.join(folder, f"{instance.name}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    return filepath

def load_instance_from_json(filepath):
    """Carga una instancia desde un JSON y reconstruye los objetos."""
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    tasks = [Task(t['id'], t['location'], t['p_0']) for t in data['tasks']]
    cranes = [Crane(c['id'], c['location']) for c in data['cranes']]
    
    inst = GCSP_Instance(tasks, cranes)
    inst.name = data['name']
    return inst