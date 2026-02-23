# Implementación de Metaheurísticas Híbridas para GCSP

El sistema utiliza una arquitectura de tres niveles para equilibrar la exploración y la intensificación en el espacio de búsqueda del **Gantry Crane Scheduling Problem (GCSP)**.

## 1. Fase de Construcción: GRASP
Para evitar empezar desde soluciones aleatorias de baja calidad, se utiliza **Greedy Randomized Adaptive Search Procedure (GRASP)**:
- **Componente Greedy:** Calcula el tiempo de finalización más temprano para cada tarea pendiente considerando todas las grúas disponibles.
- **Componente Adaptativo:** Se construye una **Restricted Candidate List (RCL)** con las mejores tareas según un parámetro $\alpha \in [0, 1]$.
- **Propósito:** Proporcionar una solución inicial factible y de alta calidad para la fase de mejora, evitando el estancamiento prematuro.

## 2. Fase de Mejora Global: VNS
**Variable Neighborhood Search (VNS)** actúa como el meta-algoritmo de búsqueda sistemática:
- **Estructuras de Vecindad:** Se han implementado tres niveles crecientes de perturbación:
    1. `Swap`: Intercambio de dos posiciones en la secuencia.
    2. `Insert`: Extraer una tarea y reinsertarla en otra posición.
    3. `Invert`: Inversión de un segmento completo de la secuencia.
- **Shaking (Agitación):** Cuando no se encuentra mejora, el algoritmo aplica un movimiento aleatorio del vecindario actual para saltar a una región inexplorada.

## 3. Fase de Intensificación: Tabu Search
Dentro de cada vecindario de VNS, se emplea **Búsqueda Tabú** como motor de búsqueda local:
- **Lista Tabú:** Mantiene un registro de los últimos movimientos realizados para evitar ciclos y obligar al algoritmo a explorar soluciones nuevas.
- **Criterio de Aspiración:** Permite realizar un movimiento tabú si este resulta en una solución mejor que la mejor encontrada hasta el momento.

---

# Métricas de Evaluación: LB y GAP

Para medir el rendimiento del algoritmo, se utilizan dos indicadores clave:

## Cota Inferior (Lower Bound - LB)
Dado que para instancias grandes es imposible conocer el valor óptimo, calculamos una **Cota Inferior Teórica**:
$$LB = \max \left( \frac{\sum p_i^0}{m}, \max(p_i^0) \right)$$
Donde:
- El primer término es la **carga promedio** entre las $m$ grúas.
- El segundo término es la **tarea más larga** (ninguna solución puede ser menor al tiempo que tarda la tarea más costosa).

## El GAP (%)
El GAP mide la distancia relativa entre nuestro resultado y la referencia (ya sea el Óptimo o el LB):
$$GAP (\%) = \frac{\text{Makespan} - \text{Referencia}}{\text{Referencia}} \times 100$$
- Un **GAP = 0%** con respecto al LB indica que hemos alcanzado el límite físico del problema.
- Un **GAP bajo** en instancias grandes demuestra la robustez de la metaheurística frente a la complejidad del problema.
