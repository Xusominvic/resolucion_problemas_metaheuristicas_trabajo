# Análisis de Desempeño: Metaheurísticas en Instancias LARGE

Este documento presenta el análisis comparativo exclusivo entre las estrategias de metaheurística (Tabu Search + VNS) implementadas con:
1. **Inicio Aleatorio (Random)**: Construcción de la solución inicial de forma estocástica.
2. **Inicio GRASP**: Construcción voraz adaptativa probabilística para la solución inicial.

El conjunto de prueba abarca las **instancias grandes** (LARGE): de 30 a 70 tareas ($n$) coordinadas por 3 a 5 grúas ($m$).

---

## 1. Calidad de las Soluciones (Makespan y GAP)

Ambas técnicas persiguen la minimización del Makespan global ($C_{\max}$). La calidad se evalúa también respecto a una cota inferior teórica ($LB$) mediante el $\text{GAP}(\%)$:

$$\text{GAP}(\%) = \frac{C_{\max} - LB}{LB} \times 100$$

### 1.1. Equivalencia Práctica en Calidad

Al observar los valores de $C_{\max}$ finales y el GAP en el `resumen_metaheuristicas_large.csv`:

*   **Valores Estrechos**: El $\text{GAP}$ promedio oscila entre el **2.22% y el 3.11%** para todas las combinaciones, evidenciando una excepcional capacidad del algoritmo para converger a zonas prometedoras del espacio de búsqueda independientemente del vector inicial.
*   **Comparativa Directa**: 
    *   **Random** obtiene Makespans ligeramente mejores en la mayoría de las combinaciones (ej. `50x3`, `60x4`, `70x5`). 
    *   **GRASP** logra imponerse solo en unos pocos casos (ej. `30x3`: $1027.04$ vs $1027.48$).
    *   Las diferencias absolutas o relativas resultan estadísticamente e industrialmente insignificantes (diferencias de $<0.2\%$ en el $\text{GAP}$).

**Conclusión**. La fase de intensificación/diversificación (VNS apoyado en Búsqueda Tabú) es lo suficientemente robusta como para superar cualquier ineficiencia del punto de partida estocástico, restando protagonismo a la fase constructiva voraz del método GRASP.

### 1.2. Escalabilidad de la Dificultad (Efecto del parámetro $m$)

El $\text{GAP}$ correlaciona positivamente con el número de grúas ($m$):
*   Para $m=3$, el GAP suele rondar $\approx 2.3\% - 2.6\%$
*   Para $m=5$, el GAP se sitúa en $\approx 2.6\% - 3.1\%$

Coordinar un mayor número de recursos paralelos incrementa las colisiones de precedencia, haciendo que el entorno de vecindad de la búsqueda Tabú/VNS enfrente óptimos locales más pronunciados.

---

## 2. Esfuerzo Computacional (Tiempos de Ejecución)

Dado que las soluciones en términos de minimización de Makespan son prácticamente equivalentes, el factor decisivo para escoger la estrategia radica en el coste de CPU (Tiempo en segundos).

### 2.1. Estabilidad de GRASP vs. Inestabilidad de Random

La varianza del tiempo de ejecución revela una de las dinámicas subyacentes más interesantes:

*   **GRASP (Estable y Predecible)**: 
    Los tiempos muestran un crecimiento razonablemente sub-cuadrático conforme aumentan $n$ y $m$. Comienza en $\approx 54\text{ s}$ (`30x3`) y escala progresivamente hasta los $\approx 594\text{ s}$ (`70x5`), manteniéndose en los rangos teóricos esperables para el tope de iteraciones.
*   **Random (Outliers Extremos)**:
    Aunque en las combinaciones `60x` y `70x` presenta competitividad temporal (a veces más rápido que GRASP temporalmente), sufre **anomalías severas (outliers)** que comprometen la viabilidad:
    *   `30x4`: $866.34\text{ s}$ (frente a $72.40\text{ s}$ de GRASP)
    *   `30x5`: $626.44\text{ s}$ (frente a $80.73\text{ s}$ de GRASP)
    *   `40x4`: $479.55\text{ s}$ (frente a $155.18\text{ s}$ de GRASP)
    *   `50x5`: $2071.84\text{ s}$ (frente a $270.91\text{ s}$ de GRASP)

**Hipótesis Analítica:** El método **Random** puede caer esporádicamente en zonas muy estériles del dominio topológico, causando que los criterios iterativos del VNS tarden muchísimo más en provocar saltos de diversificación efectivos. **GRASP**, por el contrario, nos asegura arrancar siempre de una estructura heurísticamente conexa, limitando el esfuerzo computacional desproporcionado.

---

## 3. Conclusión y Recomendación Final

Si bien la fase de búsqueda local avanzada aplana las diferencias respecto a la *calidad de solución* (haciendo que parezcan métodos gemelos en la métrica del Makespan), **el modelo GRASP se impone como la variante preferible a nivel ingenieril**. 

La capacidad de GRASP para ofrecer tiempos de ejecución previsibles y amortiguar explosiones de tiempo derivadas de inicializaciones estocásticas pobres lo confiere como el sistema más seguro y escalable para producción en instancias masivas.
