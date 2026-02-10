import time
from src.problem import generate_all_small_instances
from src.algorithms import multi_start_solver, variable_neighborhood_search

def run_grid_search_small():
    # 1. Definir los parámetros a probar
    tabu_tenure_list = [2, 4, 6, 8]
    candidates_list = [20, 60, 120, 200, 264]

    # 2. Cargar las instancias
    print("Generando instancias SMALL para el test...")
    instances = generate_all_small_instances()
    
    print(f"\n--- INICIANDO GRID SEARCH ({len(tabu_tenure_list) * len(candidates_list)} combinaciones) ---")
    print(f"Usando límite de iteraciones dinámico: 6 * n * m")
    
    best_config = None
    best_avg_score = float('inf')

    # 3. Bucles Anidados: Probar cada combinación de Hiperparámetros
    for tenure in tabu_tenure_list:
        for candidates in candidates_list:
            
            print(f"\n[Evaluando Configuración] Tenure: {tenure} | Candidates: {candidates}")
            start_time = time.time()
            total_makespan = 0

            # Probar esta configuración en TODAS las instancias del grupo
            for instance in instances:
                # Calculamos n y m para esta instancia específica (según el paper)
                n = len(instance.tasks)
                m = len(instance.cranes)
                
                # Configuramos los parámetros actuales
                current_params = {
                    'grasp_alpha': 0.5,
                    'tabu_tenure': tenure,
                    'candidates_per_iter': candidates,
                    'max_iter': 6 * n * m,  # Aplicación de la fórmula del paper 
                    'vns_loops': 5
                }

                # Ejecutamos el solver con multi-start
                _, makespan, _ = multi_start_solver(
                    instance=instance,
                    algorithm_func=variable_neighborhood_search,
                    n_restarts=3, # Se mantiene en 3 para agilizar el tuning
                    **current_params
                )
                total_makespan += makespan
            
            # Calcular promedio de la configuración actual
            avg_makespan = total_makespan / len(instances)
            elapsed = time.time() - start_time
            
            print(f"  -> Resultado: Promedio Makespan = {avg_makespan:.2f} (Tiempo: {elapsed:.2f}s)")
            
            # Actualizar el mejor candidato encontrado
            if avg_makespan < best_avg_score:
                best_avg_score = avg_makespan
                best_config = (tenure, candidates)
                print(f"¡Nuevo Mejor Candidato!")

    print("\n" + "="*40)
    print(f"GRID SEARCH FINALIZADO")
    print(f"Mejor Configuración Encontrada:")
    print(f"  - Tabu Tenure: {best_config[0]}")
    print(f"  - Candidates:  {best_config[1]}")
    print(f"  - Makespan Promedio: {best_avg_score:.2f}")
    print("="*40)

if __name__ == "__main__":
    run_grid_search_small()