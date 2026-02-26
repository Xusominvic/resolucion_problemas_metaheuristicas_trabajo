# RESEARCH LOG - Metaheurísticas de IA

## [2026-02-26 18:15]
- **Cambio**: Modificación de `process_results.py` para generalizar el procesamiento de resultados de diferentes tamaños (small, medium, large) y permitir la especificación de tamaño por argumento de línea de comandos.
- **Hipótesis**: Se espera automatizar la generación de reportes CSV para la fase de experimentación a gran escala, asegurando que la agregación de datos (promedios de makespan, tiempos y GAPs) sea consistente entre todos los conjuntos de instancias.
- **Resultado**: Generado exitosamente `resumen_resultados_large.csv` y el análisis correspondiente `analisis_resultados_large.md`. El script ahora es reutilizable para cualquier nuevo conjunto de datos.

## [2026-02-26 18:20]
- **Cambio**: Análisis y reporte de resultados para instancias de tamaño `LARGE` (30-70 tareas).
- **Hipótesis**: Las metaheurísticas deberían mantener GAPs bajos (<5%) incluso en instancias grandes, mientras que el método exacto podría empezar a mostrar signos de fatiga.
- **Resultado**: Sorprendentemente, el solver exacto alcanzó la optimalidad en <2s para todas las instancias LARGE. Las metaheurísticas mantuvieron GAPs consistentes entre 2-3%, confirmando su robustez, aunque con tiempos de ejecución mayores (hasta 600s) que el método exacto para estas instancias específicas.

## [2026-02-26 18:36]
- **Cambio**: Creación de `generate_all_csvs.py` — script independiente que genera los 3 CSVs (small, medium, large) de una sola ejecución. Incluye deduplicación de instancias (toma la última entrada cuando hay duplicados) y logging detallado de n, medias y combinaciones.
- **Hipótesis**: El CSV anterior de medium contenía medias incorrectas debido a un error de mapeo de columnas en `process_results.py`. El nuevo script debería generar medias verificables.
- **Resultado**: Medias verificadas manualmente (ej. MK exacto 15x2 = (812+765+877+784+674)/5 = 782.4 ✓). Se detectaron entradas duplicadas en `resultados_random_large.txt` (50x5_2 y 50x5_3).

## [2026-02-26 18:52]
- **Cambio**: Reescritura completa de los 3 documentos de análisis (`analisis_resultados_small.md`, `_medium.md`, `_large.md`) basándose en los CSVs corregidos.
- **Hipótesis**: Los análisis anteriores podrían contener conclusiones basadas en datos incorrectos.
- **Resultado**: Hallazgos principales:
  - **Small**: MK de metaheurísticas ≈ óptimo exacto. Speedup hasta 17.000× en 12x2. GAP alto en m=3 causado por LB laxa, no por mala calidad.
## [2026-02-26 19:10]
- **Cambio**: Extracción de un nuevo CSV (`resumen_metaheuristicas_large.csv`) y creación del Markdown (`analisis_metaheuristicas_large.md`) centrado exclusivamente en la comparativa de Random vs. GRASP para el set LARGE, excluyendo intencionalmente los resultados del solver exacto.
- **Hipótesis**: Desvincular el desempeño del Exacto permitiría entender si la construcción GRASP influye a nivel de varianza computacional frente al Random start, ya que en la heurística pura la calidad suele equilibrarse por el VNS/TS.
- **Resultado**: Aunque en todas las variaciones $n \times m$ el GAP ($\approx 2\% - 3\%$) y los valores $C_{\max}$ finales resultan virtualmente idénticos, se ratifica que **GRASP provee estabilidad temporal**. Random exhibe *outliers extremos* (e.g., sobrepasando $2000\text{ s}$) por inicializarse previsiblemente muy alejado de dominios conexos explorables, sugiriendo GRASP como la opción más segura a escala industrial real.
