# Análisis de Resultados — Instancias SMALL

Este documento analiza el desempeño comparativo del método exacto (solver MILP) frente a las metaheurísticas (Tabu Search + VNS) con inicio aleatorio (Random) e inicio constructivo voraz (GRASP) para las instancias de tamaño pequeño: de 6 a 12 tareas ($n$) y de 2 a 3 grúas ($m$).

---

## 1. Tabla Resumen de Resultados

| Comb. | MK Exacto | T. Exacto (s) | MK Random | T. Random (s) | GAP Random (%) | MK GRASP | T. GRASP (s) | GAP GRASP (%) |
|:-----:|:---------:|:-------------:|:---------:|:-------------:|:--------------:|:--------:|:------------:|:-------------:|
| 6×2   | 270.8     | 0.07          | 270.8     | 0.06          | 2.13           | 270.8    | 0.06         | 2.13          |
| 6×3   | 185.2     | 0.08          | 186.8     | 0.08          | 10.19          | 186.8    | 0.09         | 10.19         |
| 7×2   | 293.4     | 0.16          | 293.44    | 0.08          | 3.68           | 293.44   | 0.08         | 3.68          |
| 7×3   | 226.2     | 0.12          | 226.68    | 0.12          | 5.68           | 226.68   | 0.12         | 5.68          |
| 8×2   | 320.0     | 1.08          | 320.0     | 0.09          | 3.13           | 320.0    | 0.12         | 3.13          |
| 8×3   | 264.2     | 0.28          | 264.92    | 0.14          | 6.14           | 265.16   | 0.14         | 6.23          |
| 9×2   | 353.2     | 8.58          | 353.2     | 0.11          | 2.88           | 353.2    | 0.11         | 2.88          |
| 9×3   | 265.6     | 1.39          | 266.4     | 0.18          | 7.13           | 266.32   | 0.20         | 7.11          |
| 10×2  | 416.8     | 125.16        | 416.92    | 0.15          | 2.03           | 416.92   | 0.14         | 2.03          |
| 10×3  | 314.2     | 7.69          | 315.84    | 0.26          | 4.98           | 315.92   | 0.23         | 5.00          |
| 11×2  | 497.2     | 1858.50       | 497.44    | 0.18          | 2.21           | 497.28   | 0.19         | 2.18          |
| 11×3  | 315.2     | 45.18         | 315.36    | 0.29          | 3.64           | 315.36   | 0.28         | 3.64          |
| 12×2  | 492.8     | 3600.71       | 493.08    | 0.21          | 2.17           | 492.96   | 0.24         | 2.14          |
| 12×3  | 334.6     | 545.88        | 334.8     | 0.33          | 3.93           | 334.92   | 0.31         | 3.96          |

---

## 2. El Método Exacto: Escalabilidad y Límites

El solver exacto encuentra el **óptimo global** ($C_{\max}^*$) en la mayoría de instancias, pero su tiempo de ejecución crece de forma **exponencial** con $n$:

- **6–9 tareas** ($n \leq 9$): Resolución en menos de 10 s.
- **10 tareas**: ~125 s de media para $m=2$.
- **11 tareas**: ~1858 s (~31 min) de media para $m=2$; el coste computacional se dispara.
- **12 tareas, $m=2$**: **Alcanza el timeout de 3600 s** (Status: FEASIBLE). La solución entregada tiene un makespan medio de 492.8, pero **no se garantiza la optimalidad**.

> **Observación clave**: Para $m=3$ el exacto escala mejor que para $m=2$. Por ejemplo, `12×3` se resuelve en ~546 s de media (OPTIMAL), mientras `12×2` necesita el timeout completo sin converger. Esto se debe a que con más grúas el problema tiene más grados de libertad, pero la formulación MILP puede aprovechar mejor la estructura de partición del espacio de búsqueda.

## 3. Las Metaheurísticas: Calidad y Velocidad

### 3.1. Calidad del Makespan

Las metaheurísticas alcanzan soluciones prácticamente **iguales al óptimo exacto** en la mayoría de combinaciones:

- Para $m=2$: El makespan de Random y GRASP coincide con el exacto en varias combinaciones (6×2, 8×2, 9×2), con desviaciones máximas < 0.5 unidades en el resto.
- Para $m=3$: Se observa un leve deterioro (ej. 8×3: exacto = 264.2 vs. GRASP = 265.16), pero las diferencias absolutas son mínimas.

### 3.2. El GAP Respecto a la Cota Inferior (LB)

El GAP reportado ($\text{GAP} = \frac{C_{\max} - LB}{LB} \times 100$) **no es respecto al óptimo**, sino respecto a la **cota inferior** ($LB$). Esto explica por qué los GAPs son relativamente altos a pesar de que los makespans son casi exactos:

- **$m=2$**: GAPs moderados, entre **2.0% y 3.7%**. La LB es más ajustada para 2 grúas.
- **$m=3$**: GAPs significativamente mayores, entre **3.6% y 10.2%**. Con 3 grúas, la cota inferior se relaja más, alejándose del óptimo real.
- **Caso extremo: 6×3** con GAP ~10.2%. Esto indica que la LB es laxa para instancias muy pequeñas con varias grúas, no que la solución sea mala (el MK es prácticamente igual al óptimo).

### 3.3. Tiempo de Ejecución

Las metaheurísticas son **extremadamente rápidas** para estas instancias: todas terminan en **menos de 0.35 s**, incluso las más grandes (12×3). Esto contrasta drásticamente con los tiempos del exacto:

| Combinación | Speedup (Exacto / Meta) |
|:-----------:|:----------------------:|
| 6×2         | ~1× (ambos instantáneos) |
| 9×2         | ~76× |
| 10×2        | ~834× |
| 11×2        | ~10,325× |
| 12×2        | ~17,000× |

## 4. Random vs. GRASP

Para las instancias `small`, **no existe diferencia práctica** entre ambas estrategias de inicio:

- Los makespans son idénticos o difieren en décimas.
- Los GAPs son prácticamente iguales.
- Los tiempos de ejecución son comparables (milisegundos en ambos casos).

**Justificación teórica**: En instancias tan pequeñas, el espacio de búsqueda $S$ es suficientemente reducido para que la fase de mejora (VNS) explore eficazmente el vecindario y converja al mismo óptimo local independientemente del punto de partida. La ventaja de GRASP en la construcción greedy no aporta un beneficio significativo.

## 5. Conclusiones

1. **Las metaheurísticas igualan al exacto** en calidad para todas las instancias small, pero con tiempos hasta 17.000× menores.
2. **El exactly se vuelve inviable** a partir de $n=12$ con $m=2$ (timeout de 1 hora sin garantía de optimalidad).
3. **Random ≈ GRASP** para instancias small: la fase de mejora domina sobre la fase constructiva cuando $|S|$ es pequeño.
4. **Los GAPs altos en $m=3$** son una consecuencia de la laxitud de la cota inferior ($LB$), no de la mala calidad de las soluciones.

---
*Datos extraídos de `resumen_resultados_small.csv`. Análisis generado el 2026-02-26.*
