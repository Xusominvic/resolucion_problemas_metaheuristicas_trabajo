# Metodología de Generación del Dataset

Para validar el algoritmo y permitir comparaciones científicas, se desarrolló un generador de instancias propio (`generate_dataset.py`).

## Clasificación de Instancias
Se han definido tres categorías según la complejidad del espacio de búsqueda:

| Categoría | Tareas ($n$) | Grúas ($m$) | Propósito |
| :--- | :--- | :--- | :--- |
| **Small** | 6 - 12 | 2 - 3 | Validación contra el **Método Exacto**. |
| **Medium** | 15 - 20 | 2 - 4 | Pruebas de rendimiento intermedio. |
| **Large** | 30 - 70 | 3 - 5 | Evaluación de la escalabilidad de la metaheurística. |

## Parámetros de Generación
- **Distribución Espacial:** Las tareas se ubican en posiciones discretas a lo largo de la bahía.
- **Tiempos de Procesamiento ($p_i^0$):** Generados aleatoriamente mediante una distribución uniforme para asegurar diversidad en la carga de trabajo.
- **Configuración de Grúas:** Se utiliza una disposición **equidistante** calculada mediante interpolación lineal:
  $$Pos_k = 1 + (k-1) \cdot \frac{n-1}{m-1}$$
  Esto asegura una distribución de partida óptima que el algoritmo debe gestionar para evitar colisiones.
- **Física del Problema:** Velocidad de desplazamiento constante ($t_0$) y distancia de seguridad mínima obligatoria ($s$) para prevenir colisiones físicas entre los pórticos.
