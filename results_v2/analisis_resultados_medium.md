# Análisis de Resultados - Instancias MEDIUM

Este documento analiza el desempeño del método exacto frente a las metaheurísticas (Tabu Search + VNS) para instancias de tamaño medio. A diferencia de las instancias pequeñas, aquí se observan cambios significativos en el comportamiento de los algoritmos.

## 1. El Límite del Método Exacto

- **Timeouts Generalizados**: En las instancias `medium`, el método exacto **agota el tiempo límite de 3600 segundos (1 hora)** en prácticamente todas las ejecuciones sin alcanzar la convergencia (Status: FEASIBLE).
- **Calidad de la Solución**: Debido a que no logra terminar la búsqueda, el solver exacto entrega soluciones con un GAP interno muy elevado. En muchos casos, **la metaheurística logra soluciones mejores en apenas segundos** que el método exacto en una hora completa. Por ejemplo, en `medium_15x2_1`, la metaheurística baja de 812.0 a 811.2 de promedio.

## 2. Ventaja Competitiva de la Metaheurística

- **Eficiencia Extrema**: La metaheurística resuelve las instancias en un rango de **6 a 30 segundos** (con algunas excepciones específicas de 60-100s en configuraciones complejas).
- **Estabilidad del GAP**: A pesar del incremento en el tamaño del problema (hasta 20 tareas x 4 grúas), el GAP respecto a la cota inferior (LB) se mantiene muy bajo, generalmente **entre el 1.5% y el 4%**. Esto demuestra una excelente escalabilidad del algoritmo híbrido Tabu Search + VNS.

## 3. Comparativa: Inicio Random vs. GRASP

- **Resultados Similares**: Sorprendentemente, el impacto de GRASP sigue siendo moderado en este rango. Aunque en algunas instancias `19x4` o `20x4` GRASP muestra una ligera ventaja en términos de estabilidad, los resultados finales de makespan son muy parecidos a los del inicio aleatorio.
- **Tiempo de Cómputo**: Se observa que las ejecuciones con inicio GRASP tienden a tomar un poco más de tiempo en la fase constructiva inicial, pero el VNS posterior iguala la calidad de la solución en ambos casos.

## 4. Conclusiones

1.  **Superioridad Práctica**: Para problemas de tamaño medio hacia arriba, las metaheurísticas son la única opción viable, superando en calidad y tiempo al solver exacto limitado a una hora.
2.  **Robustez del VNS**: La combinación de búsqueda tabú con cambios de vecindad variable (VNS) es extremadamente eficaz para escapar de los óptimos locales que detienen el progreso de solvers genéricos.
3.  **Configuraciones Críticas**: Las instancias con 4 grúas muestran los GAPs más altos (hasta 5%), lo que sugiere que la complejidad de coordinación aumenta más con el número de recursos que con el número de tareas.

---
*Archivo generado automáticamente para complementar el resumen CSV en results_v2.*
