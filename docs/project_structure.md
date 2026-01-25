# Estructura y Funcionamiento del Proyecto GCSP

Este documento detalla la estructura de archivos y el flujo de ejecución del proyecto de resolución del problema de programación de grúas (GCSP) utilizando metaheurísticas.

## 1. Estructura de Archivos

```
/
├── main.py                     # Punto de entrada principal para ejecutar experimentos
├── validations.py              # Scripts de validación y pruebas unitarias de algoritmos
├── grid_search_*.py            # Scripts para ajuste de parámetros (Grid Search) por tamaño de instancia
├── *_results.txt               # Archivos de texto con los resultados de los experimentos
├── src/                        # Código fuente del núcleo
│   ├── algorithms.py           # Implementación de las metaheurísticas (VNS, Tabu, GRASP)
│   ├── problem.py              # Definición del problema (Task, Crane) y generadores de instancias
│   └── __init__.py             # Archivo de inicialización del paquete
└── README.md                   # Documentación general (si existe)
```

## 2. Descripción de Componentes

### `src/problem.py`
Define el dominio del problema:
- **`Task`**: Representa una tarea con ID, ubicación y tiempo de procesamiento.
- **`Crane`**: Representa una grúa con ID y ubicación inicial.
- **`GCSP_Instance`**: Clase contenedora para una instancia del problema (lista de tareas y grúas).
- **Generadores**: Funciones (`generate_all_small_instances`, etc.) que crean instancias de prueba (Pequeñas, Medianas, Grandes) automáticamente.

### `src/algorithms.py`
Contiene la lógica de resolución:
- **`calculate_makespan`**: Función crítica que evalúa una secuencia de tareas y calcula el tiempo total (makespan), gestionando la asignación de grúas y las interferencias.
- **`construct_grasp_solution`**: Algoritmo constructivo (GRASP) para generar una solución inicial válida.
- **`tabu_search`**: Metaheurística de Búsqueda Tabú para mejorar una solución mediante exploración de vecindarios.
- **`variable_neighborhood_search` (VNS)**: Algoritmo principal que combina cambios de vecindario (Shaking) con Búsqueda Tabú (Local Search).
- **`multi_start_solver`**: Estrategia que reinicia el VNS varias veces desde diferentes puntos para evitar óptimos locales.

### `main.py`
El orquestador del proyecto:
1.  **Argumentos**: Recibe parámetros por línea de comandos (tamaño de instancia, iteraciones, etc.).
2.  **Generación**: Crea el conjunto de instancias solicitado (Small/Medium/Large).
3.  **Ejecución**: Para cada instancia, corre el `multi_start_solver`.
4.  **Reporte**: Compara el resultado con una Cota Inferior (Lower Bound) teórica y calcula el "Gap" (porcentaje de desviación del óptimo). Mide y muestra el tiempo de ejecución.

### `validations.py`
Contiene bloques de código independientes para verificar partes específicas:
- `test_validation_phase_2_explicit`: Verifica si el cálculo del makespan coincide con un caso conocido (del paper original).
- `test_phase_3_moves`: Prueba los operadores de movimiento (swap, insert, invert).
- `run_optimization` / `compare_algorithms`: Ejecuciones de prueba para comparar algoritmos (ej. Simulated Annealing vs Tabu) fuera del flujo principal.

## 3. Flujo de Funcionamiento

1.  **Inicio**: Se ejecuta `main.py` (ej. `python main.py --size medium`).
2.  **Carga**: Se importan las clases de `src.problem` y los algoritmos de `src.algorithms`.
3.  **Instanciación**: Se generan las tareas y grúas según las reglas definidas en `problem.py`.
4.  **Optimización**:
    - Se construye una solución inicial (GRASP).
    - Se mejora iterativamente usando VNS + Tabu Search.
    - Se repite el proceso `n_restarts` veces.
5.  **Evaluación**: En cada paso, `calculate_makespan` simula el movimiento de las grúas para validar la calidad de la secuencia.
6.  **Salida**: Se imprime una tabla con los resultados (Makespan obtenido, Gap %, Tiempo) y la mejor secuencia encontrada.
