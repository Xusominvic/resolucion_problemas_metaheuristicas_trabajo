"""
Solver Exacto CP-SAT para GCSP - Versión con Timeout Riguroso.
- Usa multiprocessing para garantizar el límite de tiempo por instancia.
- Reduce la explosión combinatoria comprobando solo grúas adyacentes.
"""

import argparse
import glob
import os
import re
import time
import multiprocessing
from ortools.sat.python import cp_model
from src.io_handler import load_instance_from_json


class GCSP_CP_SAT_Solver:
    def __init__(self, instance, time_limit=7200):
        self.instance = instance
        self.time_limit = time_limit
        self.model = cp_model.CpModel()
        
        self.tasks = instance.tasks
        self.cranes = instance.cranes
        self.num_tasks = len(self.tasks)
        self.num_cranes = len(self.cranes)
        self.t0 = instance.t_0
        self.s = instance.s
        
        # Mapeos
        self.all_tasks = range(self.num_tasks)
        self.all_cranes = range(self.num_cranes)
        self.depot_start = self.num_tasks
        
        # Horizonte Temporal
        total_p = sum(t.p_0 for t in self.tasks)
        max_dist = self.num_tasks * 20
        max_travel = self.num_tasks * max_dist * self.t0
        self.horizon = int(total_p + max_travel + 600)

        # Variables
        self.starts = {}      
        self.ends = {}        
        self.presence = {}
        self.makespan = None
        
        # Estado
        self.solver = None
        self.status = None
        self.solve_time = 0

    def build_model(self):
        print(f"   [Construyendo modelo... {self.num_tasks} Tareas, {self.num_cranes} Grúas]")
        start_build = time.time()

        # 1. Variables de Tiempo
        for i in self.all_tasks:
            self.starts[i] = self.model.NewIntVar(0, self.horizon, f's{i}')
            self.ends[i] = self.model.NewIntVar(0, self.horizon, f'e{i}')
            self.model.Add(self.ends[i] == self.starts[i] + self.tasks[i].p_0)

        self.makespan = self.model.NewIntVar(0, self.horizon, 'mk')

        locations = [t.location for t in self.tasks] + [c.location for c in self.cranes]

        # 2. Routing (Circuit)
        for k in self.all_cranes:
            depot_node = self.depot_start + k
            arcs = []
            
            # Variables Presence y Self-Loops
            for i in self.all_tasks:
                self.presence[i, k] = self.model.NewBoolVar(f'pres_{i}_{k}')
                arcs.append([i, i, self.presence[i, k].Not()])

            # Arcos Tarea -> Tarea
            for i in self.all_tasks:
                for j in self.all_tasks:
                    if i == j: continue
                    
                    lit = self.model.NewBoolVar(f'r_{i}_{j}_{k}')
                    arcs.append([i, j, lit])
                    
                    self.model.AddImplication(lit, self.presence[i, k])
                    self.model.AddImplication(lit, self.presence[j, k])
                    
                    dist = abs(locations[i] - locations[j])
                    travel = int(dist * self.t0)
                    self.model.Add(self.starts[j] >= self.ends[i] + travel).OnlyEnforceIf(lit)

            # Arcos Inicio/Fin (Depósito)
            for i in self.all_tasks:
                # Start
                s_lit = self.model.NewBoolVar(f'start_{k}_{i}')
                arcs.append([depot_node, i, s_lit])
                self.model.AddImplication(s_lit, self.presence[i, k])
                dist = abs(locations[depot_node] - locations[i])
                self.model.Add(self.starts[i] >= int(dist * self.t0)).OnlyEnforceIf(s_lit)
                
                # End
                e_lit = self.model.NewBoolVar(f'end_{i}_{k}')
                arcs.append([i, depot_node, e_lit])
                self.model.AddImplication(e_lit, self.presence[i, k])

            # Empty
            empty = self.model.NewBoolVar(f'empty_{k}')
            arcs.append([depot_node, depot_node, empty])

            self.model.AddCircuit(arcs)

        # 3. Partitioning
        for i in self.all_tasks:
            self.model.Add(sum(self.presence[i, k] for k in self.all_cranes) == 1)

        # 4. Non-Crossing (solo grúas adyacentes)
        count_constraints = 0
        
        for k in range(self.num_cranes - 1):
            next_k = k + 1
            
            for i in self.all_tasks:
                for j in self.all_tasks:
                    if locations[i] + self.s <= locations[j]:
                        continue 
                    
                    i_before_j = self.model.NewBoolVar(f'b_{i}_{j}')
                    j_before_i = self.model.NewBoolVar(f'b_{j}_{i}')
                    
                    self.model.Add(self.ends[i] <= self.starts[j]).OnlyEnforceIf(i_before_j)
                    self.model.Add(self.ends[j] <= self.starts[i]).OnlyEnforceIf(j_before_i)
                    
                    self.model.AddBoolOr([i_before_j, j_before_i]).OnlyEnforceIf(
                        [self.presence[i, k], self.presence[j, next_k]]
                    )
                    count_constraints += 1

        # 5. Makespan
        for i in self.all_tasks:
            self.model.Add(self.makespan >= self.ends[i])
        self.model.Minimize(self.makespan)
        
        build_time = time.time() - start_build
        print(f"   [Modelo construido en {build_time:.2f}s. Restricciones de choque: {count_constraints}]")

    def solve(self):
        self.solver = cp_model.CpSolver()
        # Límite interno de CP-SAT (primera línea de defensa)
        self.solver.parameters.max_time_in_seconds = float(self.time_limit)
        self.solver.parameters.num_search_workers = 8
        self.solver.parameters.log_search_progress = False
        
        print(f"   [Iniciando Solver... Límite: {self.time_limit}s]")
        start_time = time.time()
        
        self.status = self.solver.Solve(self.model)
        self.solve_time = time.time() - start_time
        
        return self._get_results()

    def _get_results(self):
        result = {
            'instance_name': self.instance.name,
            'status': 'UNKNOWN',
            'makespan': None,
            'lower_bound': None,
            'gap': None,
            'time': self.solve_time
        }
        
        if self.status == cp_model.OPTIMAL:
            result['status'] = 'OPTIMAL'
            result['makespan'] = self.solver.ObjectiveValue()
            result['lower_bound'] = result['makespan']
            result['gap'] = 0.0
        elif self.status == cp_model.FEASIBLE:
            result['status'] = 'FEASIBLE'
            result['makespan'] = self.solver.ObjectiveValue()
            result['lower_bound'] = self.solver.BestObjectiveBound()
            if result['lower_bound'] > 0:
                result['gap'] = (result['makespan'] - result['lower_bound']) / result['lower_bound'] * 100
        else:
            if self.solve_time >= self.time_limit * 0.95:
                result['status'] = 'TIMEOUT'
            else:
                result['status'] = 'INFEASIBLE'
        
        return result


# =========================================================
# FUNCIÓN PARA EJECUTAR EN PROCESO SEPARADO (TIMEOUT REAL)
# =========================================================
def _solve_instance_worker(filepath, time_limit, result_queue):
    """Función que se ejecuta en un proceso hijo.
    
    Construye y resuelve el modelo CP-SAT, y envía el resultado
    a través de una Queue compartida con el proceso padre.
    """
    try:
        inst = load_instance_from_json(filepath)
        solver = GCSP_CP_SAT_Solver(inst, time_limit=time_limit)
        solver.build_model()
        res = solver.solve()
        result_queue.put(res)
    except Exception as e:
        inst = load_instance_from_json(filepath)
        result_queue.put({
            'instance_name': inst.name,
            'status': 'ERROR',
            'makespan': None,
            'lower_bound': None,
            'time': 0,
            'gap': None
        })


def solve_with_hard_timeout(filepath, time_limit):
    """Ejecuta el solver en un proceso separado con timeout garantizado.
    
    Si el proceso excede time_limit, se termina forzosamente y se
    devuelve un resultado TIMEOUT. Esto garantiza que ninguna instancia
    supere el límite de tiempo, independientemente de CP-SAT.
    """
    result_queue = multiprocessing.Queue()
    
    process = multiprocessing.Process(
        target=_solve_instance_worker,
        args=(filepath, time_limit, result_queue)
    )
    
    start_time = time.time()
    process.start()
    
    # Esperar al proceso con un margen de 30s extra para build_model + overhead
    process.join(timeout=time_limit + 30)
    
    elapsed = time.time() - start_time
    
    if process.is_alive():
        # El proceso sigue vivo -> matarlo
        print(f"   [!!! TIMEOUT FORZADO después de {elapsed:.0f}s !!!]")
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
            process.join()
        
        # Recuperar el nombre de la instancia del filepath
        inst = load_instance_from_json(filepath)
        return {
            'instance_name': inst.name,
            'status': 'TIMEOUT',
            'makespan': None,
            'lower_bound': None,
            'time': elapsed,
            'gap': None
        }
    
    # El proceso terminó a tiempo -> recoger resultado
    if not result_queue.empty():
        return result_queue.get()
    else:
        inst = load_instance_from_json(filepath)
        return {
            'instance_name': inst.name,
            'status': 'ERROR',
            'makespan': None,
            'lower_bound': None,
            'time': elapsed,
            'gap': None
        }


# =========================================================
# MAIN
# =========================================================
def get_sort_key(filepath):
    filename = os.path.basename(filepath)
    numbers = re.findall(r'\d+', filename)
    if len(numbers) >= 3:
        return int(numbers[0]), int(numbers[1]), int(numbers[2])
    return 0, 0, 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=str, required=True, choices=['small', 'medium', 'large'])
    parser.add_argument('--time_limit', type=int, default=7200,
                        help='Límite de tiempo POR INSTANCIA en segundos (default: 7200 = 2h)')
    args = parser.parse_args()
    
    files = glob.glob(f"instances/{args.size}_*.json")
    files.sort(key=get_sort_key)
    
    if not files:
        print("No se encontraron instancias.")
        return

    out_file = f"resultados_exacto_riguroso_{args.size}.txt"
    
    print(f"\n{'='*90}")
    print(f" SOLVER EXACTO CP-SAT | SIZE: {args.size.upper()} | LIMIT: {args.time_limit}s/instancia")
    print(f"{'='*90}")
    print(f"{'Instancia':<25} | {'Status':<10} | {'Makespan':<10} | {'Time':<8} | {'Gap'}")
    print("-" * 90)
    
    with open(out_file, "w") as f:
        f.write("Instancia,Status,Makespan,Time,Gap\n")
        
        for filepath in files:
            # Ejecutar solver con timeout REAL garantizado por multiprocessing
            res = solve_with_hard_timeout(filepath, args.time_limit)

            mk = f"{res['makespan']:.1f}" if res['makespan'] else "-"
            gap = f"{res['gap']:.2f}" if res['gap'] is not None else "-"
            
            print(f"{res['instance_name']:<25} | {res['status']:<10} | {mk:<10} | {res['time']:.2f} s   | {gap}%")
            f.write(f"{res['instance_name']},{res['status']},{mk},{res['time']},{gap}\n")

if __name__ == "__main__":
    main()