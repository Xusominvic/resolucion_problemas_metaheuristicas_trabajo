
def test_validation_phase_2_explicit():
    print("--- FASE 2: Validación con Mapeo Explícito (ID -> Tiempo) ---")
    
    # [cite_start]DICCIONARIO DE DATOS (Fuente: Etiquetas visuales Figura 5) [cite: 323-335]
    # Clave = ID de Tarea
    # Valor = Tiempo de procesamiento
    task_data = {
        1: 10,  # Etiqueta visual "1(10)"
        2: 10,  # Etiqueta visual "2(10)" -> Tu corrección
        3: 20,  # Etiqueta visual "3(20)"
        4: 40,  # Etiqueta visual "4(40)"
        5: 30,  # Etiqueta visual "5(30)" (Estimado por longitud similar a T7)
        6: 60,  # Etiqueta visual "6(60)" -> Tu corrección
        7: 40,  # Etiqueta visual "7(40)"
        8: 25   # Etiqueta visual "8(25)" (Termina en 130)
    }
    
    tasks = []
    # Creamos las tareas iterando por los IDs del 1 al 8
    for t_id in range(1, 9):
        # Asumimos que Tarea ID i está en Ubicación i (según paper)
        p_time = task_data[t_id]
        tasks.append(Task(task_id=t_id, location=t_id, base_processing_time=p_time))
        
    # Grúas en posiciones 1 y 3
    cranes = [Crane(1, 1), Crane(2, 3)]
    
    instance = GCSP_Instance(tasks, cranes, safety_margin=1, travel_speed=1)
    
    # Secuencia de entrada (Orden de ejecución)
    sequence = [1, 6, 2, 3, 4, 7, 5, 8]
    
    makespan = calculate_makespan(instance, sequence)
    
    print(f"Secuencia: {sequence}")
    print(f"Tiempos usados (ID: Tiempo): {task_data}")
    print(f"Makespan Calculado: {makespan}")
    
    if makespan == 130:
        print("✅ ¡ÉXITO! Resultado exacto al del paper.")
    else:
        print(f"Resultado: {makespan} (Cercano al objetivo 130)")

if __name__ == "__main__":
    test_validation_phase_2_explicit()



from src.algorithms import get_neighbor

def test_phase_3_moves():
    print("--- FASE 3: Test de Movimientos de Vecindad ---")
    
    # Secuencia base simple para visualizar fácil
    seq = [1, 2, 3, 4, 5, 6, 7, 8]
    print(f"Secuencia Original: {seq}")
    print("-" * 30)
    
    # Probar SWAP
    print(f"SWAP (Forzado):   {get_neighbor(seq, 'swap')}")
    
    # Probar INSERT
    print(f"INSERT (Forzado): {get_neighbor(seq, 'insert')}")
    
    # Probar INVERT
    print(f"INVERT (Forzado): {get_neighbor(seq, 'invert')}")
    
    print("-" * 30)
    print("Prueba de Aleatoriedad (5 intentos):")
    for k in range(5):
        # Aquí no sabemos qué hará, pero debe cambiar la lista
        print(f"Random #{k+1}: {get_neighbor(seq, 'random')}")

if __name__ == "__main__":
    test_phase_3_moves()



import random
from src.problem import Task, Crane, GCSP_Instance
from src.algorithms import calculate_makespan, simulated_annealing

def run_optimization():
    print("--- FASE 4: Ejecutando Recocido Simulado ---")
    
    # 1. Crear Instancia (Datos corregidos Fig 5)
    task_data = {
        1: 10, 2: 10, 3: 20, 4: 40, 
        5: 30, 6: 60, 7: 40, 8: 25
    }
    tasks = [Task(tid, tid, time) for tid, time in task_data.items()]
    cranes = [Crane(1, 1), Crane(2, 3)]
    instance = GCSP_Instance(tasks, cranes)
    
    # 2. Generar Solución Inicial Aleatoria
    # No usamos la del paper, inventamos una mala para ver si mejora
    initial_sol = list(task_data.keys()) # [1, 2, 3, 4, 5, 6, 7, 8]
    random.shuffle(initial_sol) 
    
    initial_makespan = calculate_makespan(instance, initial_sol)
    print(f"Solución Inicial: {initial_sol}")
    print(f"Makespan Inicial: {initial_makespan}")
    print("-" * 30)
    
    # 3. Ejecutar SA
    # Temp alta, enfriamiento lento para asegurar convergencia en test pequeño
    best_seq, best_val, history = simulated_annealing(
        instance, 
        initial_sol, 
        initial_temp=500, 
        cooling_rate=0.99, 
        max_iter=2000
    )
    
    print(f"--- RESULTADOS ---")
    print(f"Mejor Secuencia: {best_seq}")
    print(f"Mejor Makespan: {best_val}")
    
    if best_val <= 130:
        print("🚀 ¡Excelente! El algoritmo encontró una solución óptima o casi óptima.")
    else:
        print("⚠️ No llegó al óptimo conocido (125/130). Intenta ajustar parámetros.")

if __name__ == "__main__":
    run_optimization()


# main.py
import random
import time
from src.problem import Task, Crane, GCSP_Instance
from src.algorithms import calculate_makespan, simulated_annealing, tabu_search

def compare_algorithms():
    print("--- COMPARATIVA: SA vs TABU ---")
    
    # 1. Instancia (Datos corregidos visuales Fig 5)
    task_data = {
        1: 10, 2: 10, 3: 20, 4: 40, 
        5: 30, 6: 60, 7: 30, 8: 30
    }
    tasks = [Task(tid, tid, time) for tid, time in task_data.items()]
    cranes = [Crane(1, 1), Crane(2, 3)]
    instance = GCSP_Instance(tasks, cranes)
    
    # Solución Inicial Aleatoria (Misma semilla para ambos)
    base_sol = list(task_data.keys())
    random.seed(42) # Semilla fija para reproducibilidad
    random.shuffle(base_sol)
    initial_sol = base_sol[:]
    
    initial_makespan = calculate_makespan(instance, initial_sol)
    print(f"Inicio Aleatorio: {initial_makespan}")
    print("-" * 40)
    
    # --- A. Recocido Simulado ---
    start_time = time.time()
    _, sa_best, _ = simulated_annealing(instance, initial_sol, max_iter=1000)
    sa_time = time.time() - start_time
    print(f"[Simulated Annealing] Mejor: {sa_best} | Tiempo: {sa_time:.4f}s")
    
    # --- B. Búsqueda Tabú ---
    start_time = time.time()
    # tenure=10 (memoria corta), iter=100 (menos iteraciones pero 20 candidatos por iter)
    # Total evaluaciones ~ 100 * 20 = 2000 (similar esfuerzo computacional que SA)
    _, ts_best, _ = tabu_search(instance, initial_sol, tabu_tenure=10, max_iter=100, candidates_per_iter=20)
    ts_time = time.time() - start_time
    print(f"[Tabu Search]       Mejor: {ts_best} | Tiempo: {ts_time:.4f}s")
    
    print("-" * 40)
    if min(sa_best, ts_best) <= 125:
        print("✅ Objetivo cumplido (125).")
    else:
        print("⚠️ Aún se puede mejorar.")

if __name__ == "__main__":
    compare_algorithms()

import random
from src.problem import Task, Crane, GCSP_Instance
from src.algorithms import calculate_makespan, simulated_annealing, tabu_search, multi_start_solver

def run_multi_start_strategy():
    print("=== ESTRATEGIA MULTI-ARRANQUE ===")
    
    # 1. Instancia (Tus datos corregidos)
    task_data = {
        1: 10, 2: 10, 3: 20, 4: 40, 
        5: 30, 6: 60, 7: 40, 8: 25
    }
    tasks = [Task(tid, tid, time) for tid, time in task_data.items()]
    cranes = [Crane(1, 1), Crane(2, 3)]
    instance = GCSP_Instance(tasks, cranes)
    
    # 2. Configuración
    # Vamos a lanzar 10 búsquedas tabú independientes.
    # Cada una tendrá 100 iteraciones (menos que antes, porque compensamos con cantidad de arranques).
    
    best_seq, best_val = multi_start_solver(
        instance=instance,
        algorithm_func=tabu_search,   # Le pasamos la función, NO el resultado
        n_restarts=10,                # 10 Intentos
        # Parámetros para la Tabú Search:
        tabu_tenure=8,
        max_iter=100,
        candidates_per_iter=20
    )
    
    print("-" * 40)
    print(f"🏆 MEJOR RESULTADO FINAL: {best_val}")
    print(f"Secuencia: {best_seq}")

if __name__ == "__main__":
    run_multi_start_strategy()