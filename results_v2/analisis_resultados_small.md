# Análisis de Resultados - Instancias SMALL

Este documento presenta una comparativa detallada entre el método exacto y las metaheurísticas (Tabu Search + VNS) con inicios Aleatorio (Random) y GRASP, basada en los promedios obtenidos de las instancias de tamaño pequeño.

## 1. Calidad de la Solución (Makespan)

- **Método Exacto vs. Metaheurísticas**: Como es de esperar, el método exacto obtiene los valores más bajos de makespan (óptimos). Las metaheurísticas mantienen un desempeño muy sólido, con un **GAP promedio que oscila generalmente entre el 2% y el 5%**.
- **Caso Atípico (6x3)**: Se observa un GAP más elevado (~10.19%) en la combinación 6x3. Esto sugiere que para problemas con pocas tareas y mayor proporción de grúas, las metaheurísticas podrían tener más dificultad en escapar de óptimos locales o la estructura del problema es más sensible a decisiones iniciales.

## 2. Análisis de Tiempos de Ejecución

- **Eficiencia Total**: Todos los métodos resuelven estas instancias en menos de **0.4 segundos**, lo cual es excelente para aplicaciones en tiempo real.
- **Ventaja del Exacto en Small**: Curiosamente, el método exacto es ligeramente más rápido que las metaheurísticas en casi todas las instancias "small". Esto ocurre porque la complejidad del árbol de búsqueda para estos tamaños es tan reducida que la sobrecarga (overhead) inicial de configurar la Tabu Search y el VNS supera el tiempo que le toma al solver exacto encontrar el óptimo.

## 3. Comparativa: Inicio Random vs. GRASP

- **Desempeño Idéntico**: Para estas instancias pequeñas, la diferencia entre usar un inicio aleatorio o uno basado en GRASP es **mínima o inexistente**. En la mayoría de las filas (p.ej., 6x2, 7x2, 9x2, 10x2), ambos métodos obtuvieron exactamente el mismo makespan promedio.
- **Impacto de GRASP**: En instancias más grandes (Medium/Large), se esperaría que GRASP proporcione una ventaja competitiva al iniciar en una región más prometedora del espacio de búsqueda. En las instancias small, el espacio es tan pequeño que el VNS logra llegar a las mismas soluciones de alta calidad independientemente del punto de partida.

## 4. Conclusiones

1.  **Fiabilidad**: La metaheurística es altamente confiable, manteniéndose siempre muy cerca del óptimo teórico.
2.  **Escalabilidad**: Aunque el método exacto brilla en estas instancias, la tendencia sugiere que su tiempo crecerá exponencialmente, mientras que la metaheurística mantendrá un crecimiento mucho más controlado.
3.  **Simplicidad**: Para el rango "small", un inicio aleatorio es suficiente para obtener resultados idénticos a los de un método constructivo sofisticado como GRASP.

---
*Archivo generado automáticamente para complementar el resumen CSV en results_v2.*
