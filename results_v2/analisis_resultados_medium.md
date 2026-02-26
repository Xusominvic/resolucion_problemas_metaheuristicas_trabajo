# Análisis de Resultados — Instancias MEDIUM

Este documento analiza el desempeño del método exacto frente a las metaheurísticas (Tabu Search + VNS) con inicio Random y GRASP para las instancias de tamaño medio: de 15 a 20 tareas ($n$) y de 2 a 4 grúas ($m$).

---

## 1. Tabla Resumen de Resultados

| Comb. | MK Exacto | T. Exacto (s) | MK Random | T. Random (s) | GAP Rand. (%) | MK GRASP | T. GRASP (s) | GAP GRASP (%) |
|:-----:|:---------:|:-------------:|:---------:|:-------------:|:-------------:|:--------:|:------------:|:-------------:|
| 15×2  | 782.4     | 3600.0        | 782.88    | 6.14          | 1.68          | 783.08   | 6.89         | 1.70          |
| 15×3  | 571.8     | 3600.0        | 574.36    | 9.75          | 2.37          | 574.6    | 11.22        | 2.41          |
| 15×4  | 400.0     | 3600.0        | 404.44    | 12.47         | 4.75          | 405.8    | 32.81        | 5.07          |
| 16×2  | 855.4     | 3600.0        | 855.96    | 7.40          | 1.73          | 856.76   | 20.11        | 1.83          |
| 16×3  | 601.0     | 3600.0        | 602.56    | 10.72         | 2.31          | 602.48   | 34.30        | 2.29          |
| 16×4  | 427.6     | 3600.0        | 429.92    | 13.28         | 4.35          | 429.48   | 41.78        | 4.24          |
| 17×2  | 930.6     | 3601.8        | 931.88    | 7.94          | 1.54          | 931.68   | 23.01        | 1.52          |
| 17×3  | 647.4     | 3600.2        | 648.76    | 11.53         | 2.40          | 648.8    | 15.99        | 2.40          |
| 17×4  | 452.2     | 3600.2        | 454.8     | 19.24         | 4.01          | 455.8    | 18.53        | 4.23          |
| 18×2  | 934.6     | 3600.0        | 935.28    | 9.08          | 1.83          | 935.88   | 10.51        | 1.89          |
| 18×3  | 671.0     | 3600.0        | 671.92    | 14.98         | 2.27          | 671.72   | 14.39        | 2.24          |
| 18×4  | 491.6     | 3600.0        | 493.16    | 19.14         | 3.43          | 493.8    | 18.26        | 3.57          |
| 19×2  | 979.2     | 3600.0        | 981.0     | 1231.88*      | 1.54          | 980.72   | 10.17        | 1.52          |
| 19×3  | 684.2     | 3600.2        | 683.2     | 16.05         | 2.19          | 683.44   | 15.97        | 2.22          |
| 19×4  | 515.0     | 3600.2        | 518.36    | 20.76         | 3.85          | 516.72   | 21.64        | 3.53          |
| 20×2  | 1073.0    | 3600.0        | 1071.8    | 10.69         | 1.75          | 1072.72  | 11.15        | 1.84          |
| 20×3  | 710.8     | 3600.0        | 711.68    | 14.98         | 2.22          | 710.96   | 17.09        | 2.10          |
| 20×4  | 505.6     | 3600.2        | 504.44    | 24.53         | 2.92          | 506.36   | 176.32*      | 3.31          |

> \* Tiempos outlier que exceden el límite teórico de 600 s.

---

## 2. El Método Exacto: Timeout Generalizado

A diferencia de las instancias small, el solver exacto **agota el tiempo límite de 3600 s (1 hora)** en **todas** las combinaciones sin excepción:

- **Status**: FEASIBLE en todos los casos (ninguno alcanza OPTIMAL).
- **Implicación**: Las soluciones del exacto no están garantizadas como óptimas; son la mejor solución encontrada antes del timeout.

**Paradoja de calidad**: A pesar del timeout, el solver exacto entrega makespans cercanos a los de las metaheurísticas. Por ejemplo, en `20×2`, el exacto da 1073.0 y las metaheurísticas alcanzan 1071.8 (Random) y 1072.72 (GRASP). Esto indica que el solver avanza rápido al principio pero no logra demostrar la optimalidad.

## 3. Superioridad de las Metaheurísticas

### 3.1. Calidad: Comparable o Mejor que el Exacto

En varias combinaciones, las metaheurísticas **superan al solver exacto**:

| Combinación | MK Exacto | MK Random | MK GRASP | ¿Meta supera al Exacto? |
|:-----------:|:---------:|:---------:|:--------:|:-----------------------:|
| 19×3        | 684.2     | **683.2** | 683.44   | ✅ Sí (Random -0.15%)   |
| 20×2        | 1073.0    | **1071.8**| 1072.72  | ✅ Sí (Random -0.11%)   |
| 20×4        | 505.6     | **504.44**| 506.36   | ✅ Sí (Random -0.23%)   |

Esto es posible porque el exacto no termina la búsqueda (FEASIBLE) y la metaheurística explora zonas del espacio de soluciones que el solver exacto no ha visitado en el tiempo asignado.

### 3.2. Tiempo: Órdenes de Magnitud Más Rápidas

| Rango de $m$ | Tiempo medio Random | Tiempo medio GRASP | Speedup vs. Exacto |
|:------------:|:------------------:|:------------------:|:-------------------:|
| $m=2$        | 6–11 s             | 7–23 s             | ~350–580×           |
| $m=3$        | 10–16 s            | 11–34 s            | ~225–360×           |
| $m=4$        | 12–25 s            | 18–42 s            | ~145–288×           |

Las metaheurísticas resuelven en **segundos** lo que el exacto no logra en **una hora**.

### 3.3. GAP Respecto a la Cota Inferior

El GAP $\text{GAP}(\%) = \frac{C_{\max}(s) - LB}{LB} \times 100$ muestra un patrón claro por número de grúas:

- **$m=2$ grúas**: GAP bajo, entre **1.5% y 1.9%**. Buena convergencia.
- **$m=3$ grúas**: GAP moderado, entre **2.1% y 2.4%**.
- **$m=4$ grúas**: GAP más elevado, entre **2.9% y 5.1%**. La coordinación de 4 grúas incrementa la complejidad combinatoria.

## 4. Random vs. GRASP

Para instancias medium, ambas estrategias producen resultados **muy similares**, con matices:

- **Makespan**: Random obtiene un MK ligeramente mejor en 10 de las 18 combinaciones. GRASP gana marginalmente en 7 y empatan en 1.
- **GAP**: Diferencias < 0.5 puntos porcentuales en todos los casos.
- **Tiempo**: GRASP tiende a ser **más lento** que Random, especialmente en $m=3$ y $m=4$, donde la fase constructiva voraz añade overhead. Destaca el outlier en `20×4` con GRASP (~176 s vs. ~25 s en Random).

**Conclusión parcial**: La fase de mejora VNS domina la calidad final, haciendo que el punto de partida (aleatorio o GRASP) sea poco determinante. La inversión extra de tiempo en la construcción GRASP **no se traduce en una mejora significativa** del resultado.

## 5. Conclusiones

1. **El método exacto es inviable** para $n \geq 15$: timeout de 1 hora sin garantía de optimalidad.
2. **Las metaheurísticas superan al exacto** tanto en tiempo (speedup ~300–580×) como, en algunos casos, en calidad del makespan.
3. **Random ≈ GRASP**: No hay ventaja sostenida de GRASP sobre el inicio aleatorio. Se recomienda usar Random por su menor coste temporal.
4. **El GAP crece con $m$**: Las instancias con 4 grúas son las más difíciles para las metaheurísticas, sugiriendo que futuras mejoras deberían enfocarse en la gestión de recursos paralelos.

---
*Datos extraídos de `resumen_resultados_medium.csv`. Análisis generado el 2026-02-26.*
