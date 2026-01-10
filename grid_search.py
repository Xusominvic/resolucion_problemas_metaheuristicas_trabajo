import time
from src.problem import generate_all_small_instances, generate_all_medium_instances, generate_all_large_instances
from src.algorithms import multi_start_solver, variable_neighborhood_search

def run_grid_search_small():
    # 1. Definir los parámetros a probar (El "Menú")
    tabu_tenure_list = [2, 4, 6, 8]
    candidates_list = [20, 60, 120, 200, 264]

    # 2. Cargar las instancias (El banco de pruebas)
    print("Generando instancias SMALL para el test...")
    instances = generate_all_small_instances()
    
    print(f"\n--- INICIANDO GRID SEARCH ({len(tabu_tenure_list) * len(candidates_list)} combinaciones) ---")
    
    best_config = None
    best_avg_score = float('inf')

    # 3. Bucles Anidados: Probar cada combinación
    for tenure in tabu_tenure_list:
        for candidates in candidates_list:
            
            print(f"\n[Evaluando Configuración] Tenure: {tenure} | Candidates: {candidates}")
            start_time = time.time()
            
            total_makespan = 0
            
            # Parametros fijos para la prueba
            current_params = {
                'grasp_alpha': 0.5,      # Mantenemos fijo el GRASP
                'tabu_tenure': tenure,   # Variable del bucle 1
                'candidates_per_iter': candidates, # Variable del bucle 2
                'max_iter': 50,          # Iteraciones un poco más bajas para que sea rápido
                'vns_loops': 5
            }

            # Probar esta configuración en TODAS las instancias
            for instance in instances:
                _, makespan = multi_start_solver(
                    instance=instance,
                    algorithm_func=variable_neighborhood_search,
                    n_restarts=3,  # Pocos reinicios para el tuning (ahorrar tiempo)
                    **current_params
                )
                total_makespan += makespan
            
            # Calcular promedio
            avg_makespan = total_makespan / len(instances)
            elapsed = time.time() - start_time
            
            print(f"  -> Resultado: Promedio Makespan = {avg_makespan:.2f} (Tiempo: {elapsed:.2f}s)")
            
            # ¿Es el nuevo campeón?
            if avg_makespan < best_avg_score:
                best_avg_score = avg_makespan
                best_config = (tenure, candidates)
                print(f"  🏆 ¡Nuevo Mejor Candidato!")

    print("\n" + "="*40)
    print(f"GRID SEARCH FINALIZADO")
    print(f"Mejor Configuración Encontrada:")
    print(f"  - Tabu Tenure: {best_config[0]}")
    print(f"  - Candidates:  {best_config[1]}")
    print(f"  - Makespan Promedio: {best_avg_score:.2f}")
    print("="*40)

if __name__ == "__main__":
    run_grid_search_small()

def run_grid_search_medium():
    # 1. Definir los parámetros a probar (El "Menú")
    tabu_tenure_list = [2, 4, 6, 8]
    candidates_list = [20, 60, 120, 200, 264]

    # 2. Cargar las instancias (El banco de pruebas)
    print("Generando instancias MEDIUM para el test...")
    instances = generate_all_medium_instances()
    
    print(f"\n--- INICIANDO GRID SEARCH ({len(tabu_tenure_list) * len(candidates_list)} combinaciones) ---")
    
    best_config = None
    best_avg_score = float('inf')

    # 3. Bucles Anidados: Probar cada combinación
    for tenure in tabu_tenure_list:
        for candidates in candidates_list:
            
            print(f"\n[Evaluando Configuración] Tenure: {tenure} | Candidates: {candidates}")
            start_time = time.time()
            
            total_makespan = 0
            
            # Parametros fijos para la prueba
            current_params = {
                'grasp_alpha': 0.5,      # Mantenemos fijo el GRASP
                'tabu_tenure': tenure,   # Variable del bucle 1
                'candidates_per_iter': candidates, # Variable del bucle 2
                'max_iter': 50,          # Iteraciones un poco más bajas para que sea rápido
                'vns_loops': 5
            }

            # Probar esta configuración en TODAS las instancias
            for instance in instances:
                _, makespan = multi_start_solver(
                    instance=instance,
                    algorithm_func=variable_neighborhood_search,
                    n_restarts=3,  # Pocos reinicios para el tuning (ahorrar tiempo)
                    **current_params
                )
                total_makespan += makespan
            
            # Calcular promedio
            avg_makespan = total_makespan / len(instances)
            elapsed = time.time() - start_time
            
            print(f"  -> Resultado: Promedio Makespan = {avg_makespan:.2f} (Tiempo: {elapsed:.2f}s)")
            
            # ¿Es el nuevo campeón?
            if avg_makespan < best_avg_score:
                best_avg_score = avg_makespan
                best_config = (tenure, candidates)
                print(f"  🏆 ¡Nuevo Mejor Candidato!")

    print("\n" + "="*40)
    print(f"GRID SEARCH FINALIZADO")
    print(f"Mejor Configuración Encontrada:")
    print(f"  - Tabu Tenure: {best_config[0]}")
    print(f"  - Candidates:  {best_config[1]}")
    print(f"  - Makespan Promedio: {best_avg_score:.2f}")
    print("="*40)

if __name__ == "__main__":
    run_grid_search_medium()