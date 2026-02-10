"""
Solver Exacto CP-SAT para GCSP - Versión Optimizada
- Respeta el Timeout rigurosamente.
- Reduce la explosión combinatoria comprobando solo grúas adyacentes.
"""

import argparse
import glob
import os
import re
import time
from ortools.sat.python import cp_model
from src.io_handler import load_instance_from_json

class GCSP_CP_SAT_Solver:
    def __init__(self, instance, time_limit=600):
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
        # Hacemos un cálculo ajustado para no abusar del dominio
        total_p = sum(t.p_0 for t in self.tasks)
        max_dist = self.num_tasks * 20 # Estimación conservadora
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
                # Arco i->i (salto) activo si NO presence
                arcs.append([i, i, self.presence[i, k].Not()])

            # Arcos Tarea -> Tarea
            for i in self.all_tasks:
                for j in self.all_tasks:
                    if i == j: continue
                    
                    # Optimización: No crear arcos imposibles por tiempo (opcional, pero ayuda)
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

        # 4. Non-Crossing (OPTIMIZADO)
        # Solo chequeamos pares de grúas adyacentes (k, k+1)
        # Solo chequeamos tareas que violarían la distancia de seguridad
        
        # Ordenar tareas por ubicación ayuda a visualizar, pero aquí iteramos pares
        count_constraints = 0
        
        for k in range(self.num_cranes - 1):
            next_k = k + 1
            
            for i in self.all_tasks:
                for j in self.all_tasks:
                    # Si Grúa k hace 'i' y Grúa k+1 hace 'j':
                    # Como k está a la izquierda de k+1, 'i' debe estar a la izquierda de 'j'
                    # Condición física requerida: Loc(i) + S <= Loc(j)
                    
                    # Si la condición física YA se cumple siempre, no añadimos restricción
                    if locations[i] + self.s <= locations[j]:
                        continue 
                    
                    # Si llegamos aquí, es que Loc(i) + S > Loc(j).
                    # Esto es peligroso. Si k hace i y k+1 hace j, NO pueden solaparse en tiempo.
                    
                    # Implicación: (Pres[i,k] AND Pres[j,next_k]) => NO Overlap(i, j)
                    # Equivalentemente: (Pres[i,k] AND Pres[j,next_k] AND Overlap(i, j)) => FALSO
                    
                    # Detectar Overlap
                    # Overlap si: Start(i) < End(j) AND Start(j) < End(i)
                    
                    # Creamos boolvar para overlap solo si es necesario
                    # Usamos lógica booleana pura para evitar reificar todo
                    
                    # Opción eficiente:
                    # Si ambos presentes, entonces i debe acabar antes que j empiece O j antes que i
                    # Pero espera, si Loc(i) > Loc(j), k (izq) haciendo i y k+1 (der) haciendo j 
                    # es un CRUCE FÍSICO IMPOSIBLE DE RESOLVER SIMULTÁNEAMENTE.
                    # Ni siquiera vale que una acabe y empiece la otra si no se mueven. 
                    # Pero en este modelo simplificado asumimos que si no hay overlap temporal, 
                    # las grúas se han movido.
                    
                    # Restricción: No Overlap Temporal
                    i_before_j = self.model.NewBoolVar(f'b_{i}_{j}')
                    j_before_i = self.model.NewBoolVar(f'b_{j}_{i}')
                    
                    self.model.Add(self.ends[i] <= self.starts[j]).OnlyEnforceIf(i_before_j)
                    self.model.Add(self.ends[j] <= self.starts[i]).OnlyEnforceIf(j_before_i)
                    
                    # Si ambas grúas activas en estas tareas conflictivas -> Debe haber orden temporal
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
        # TIMEOUT RIGUROSO
        self.solver.parameters.max_time_in_seconds = self.time_limit
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
            # Detectar timeout real
            if self.solve_time >= self.time_limit * 0.95: # Margen del 5%
                result['status'] = 'TIMEOUT'
            else:
                result['status'] = 'INFEASIBLE'
        
        return result

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
    parser.add_argument('--time_limit', type=int, default=600)
    args = parser.parse_args()
    
    files = glob.glob(f"instances/{args.size}_*.json")
    files.sort(key=get_sort_key)
    
    if not files:
        print("No se encontraron instancias.")
        return

    out_file = f"resultados_exacto_riguroso_{args.size}.txt"
    
    print(f"\n{'='*90}")
    print(f" SOLVER EXACTO (OPTIMIZADO) | SIZE: {args.size.upper()} | LIMIT: {args.time_limit}s")
    print(f"{'='*90}")
    print(f"{'Instancia':<25} | {'Status':<10} | {'Makespan':<10} | {'Time':<8} | {'Gap'}")
    print("-" * 90)
    
    with open(out_file, "w") as f:
        f.write("Instancia,Status,Makespan,Time,Gap\n")
        
        for filepath in files:
            inst = load_instance_from_json(filepath)
            
            solver = GCSP_CP_SAT_Solver(inst, time_limit=args.time_limit)
            
            # Control de tiempo de construcción
            try:
                solver.build_model()
                res = solver.solve()
            except Exception as e:
                print(f"Error procesando {inst.name}: {e}")
                res = {'instance_name': inst.name, 'status': 'ERROR', 'makespan': None, 'time': 0, 'gap': None}

            mk = f"{res['makespan']:.1f}" if res['makespan'] else "-"
            gap = f"{res['gap']:.2f}" if res['gap'] is not None else "-"
            
            print(f"{res['instance_name']:<25} | {res['status']:<10} | {mk:<10} | {res['time']:.2f} s   | {gap}%")
            f.write(f"{res['instance_name']},{res['status']},{mk},{res['time']},{gap}\n")

if __name__ == "__main__":
    main()