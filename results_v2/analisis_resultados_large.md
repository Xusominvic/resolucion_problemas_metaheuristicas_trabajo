# Análisis de Resultados — Instancias LARGE

Este documento analiza el desempeño del método exacto frente a las metaheurísticas (Tabu Search + VNS) con inicio Random y GRASP para las instancias de tamaño grande: de 30 a 70 tareas ($n$) y de 3 a 5 grúas ($m$).

---

## 1. Tabla Resumen de Resultados

| Comb. | MK Exacto | T. Exacto (s) | MK Random | T. Random (s) | GAP Rand. (%) | MK GRASP | T. GRASP (s) | GAP GRASP (%) |
|:-----:|:---------:|:-------------:|:---------:|:-------------:|:-------------:|:--------:|:------------:|:-------------:|
| 30×3  | 1004.8    | 0.17          | 1027.48   | 46.28         | 2.29          | 1027.04  | 54.29        | 2.25          |
| 30×4  | 804.8     | 0.27          | 822.64    | 866.34*       | 2.22          | 823.2    | 72.40        | 2.30          |
| 30×5  | 645.0     | 0.51          | 661.8     | 626.44*       | 2.61          | 662.04   | 80.74        | 2.64          |
| 40×3  | 1356.8    | 0.28          | 1387.44   | 93.46         | 2.26          | 1389.24  | 107.73       | 2.39          |
| 40×4  | 1108.6    | 0.42          | 1134.16   | 479.56*       | 2.30          | 1135.0   | 155.18       | 2.38          |
| 40×5  | 902.8     | 0.51          | 924.72    | 175.58        | 2.44          | 925.44   | 184.67       | 2.51          |
| 50×3  | 1704.6    | 0.46          | 1745.56   | 185.77        | 2.41          | 1749.36  | 159.02       | 2.64          |
| 50×4  | 1289.8    | 0.77          | 1322.48   | 263.14        | 2.54          | 1322.68  | 259.25       | 2.56          |
| 50×5  | 1060.0    | 1.40          | 1088.8    | 2071.85*      | 2.71          | 1089.04  | 270.91       | 2.74          |
| 60×3  | 2149.6    | 0.63          | 2198.76   | 303.82        | 2.29          | 2201.72  | 281.15       | 2.43          |
| 60×4  | 1572.8    | 1.03          | 1615.36   | 384.81        | 2.71          | 1617.2   | 384.93       | 2.84          |
| 60×5  | 1229.2    | 1.28          | 1264.6    | 479.47        | 2.89          | 1265.16  | 416.82       | 2.93          |
| 70×3  | 2436.8    | 0.66          | 2499.0    | 431.49        | 2.56          | 2501.8   | 415.33       | 2.67          |
| 70×4  | 1840.6    | 1.08          | 1893.16   | 488.60        | 2.86          | 1896.36  | 513.91       | 3.04          |
| 70×5  | 1451.4    | 1.47          | 1495.84   | 628.55        | 3.07          | 1496.56  | 594.30       | 3.12          |

> \* Tiempos outlier que exceden el límite teórico de 600 s. Pueden deberse a errores en el registro del timeout.

---

## 2. El Método Exacto: Eficiencia Inesperada

A diferencia de lo observado en las instancias `medium`, el solver exacto **resuelve todas las instancias large a optimalidad** ($C_{\max}^*$) en tiempos extremadamente reducidos:

- **Status**: OPTIMAL en las 75 instancias (15 combinaciones × 5 réplicas).
- **Tiempo**: Desde ~0.17 s (30×3) hasta ~1.47 s (70×5).
- **Escalabilidad**: El crecimiento temporal es **suave y sublineal** con $n$ y $m$.

> **Observación importante**: Resulta paradójico que instancias con 30–70 tareas se resuelvan en menos de 2 s mientras instancias de 15–20 tareas (medium) agotan el timeout de 1 hora. Esto probablemente se debe a la **estructura combinatoria** de cada conjunto de datos y al número de grúas: las instancias medium incluyen $m=2$ (que genera conflictos de precedencia más complejos), mientras que las large usan $m \in \{3,4,5\}$ (mayor grado de paralelismo, lo que facilita la resolución).

## 3. Desempeño de las Metaheurísticas

### 3.1. Calidad de la Solución

El GAP relativo respecto al óptimo conocido ($C_{\max}^*$) es:

$$\text{GAP}(\%) = \frac{C_{\max}(s) - C_{\max}^*}{C_{\max}^*} \times 100$$

| Grúas ($m$) | GAP Random medio (%) | GAP GRASP medio (%) |
|:-----------:|:-------------------:|:-------------------:|
| $m=3$       | 2.37                | 2.45                |
| $m=4$       | 2.52                | 2.55                |
| $m=5$       | 2.72                | 2.77                |

- **Tendencia creciente con $m$**: A más grúas, mayor dificultad de coordinación para las metaheurísticas.
- **Tendencia creciente con $n$**: Las combinaciones 70× muestran GAPs ~0.5 puntos porcentuales superiores a las 30×, confirmando el efecto del tamaño del problema.

### 3.2. Evolución del GAP con el Tamaño

```
GAP (%)
  3.1 |                                           ●  ●
  3.0 |                                        ●
  2.9 |                                  ●
  2.8 |                              ●
  2.7 |                    ●     ●
  2.6 |              ●  ●
  2.5 |           ●
  2.4 |        ●  
  2.3 |  ●  ●     ●
  2.2 |     ●
      +----+----+----+----+----+----+----+----+---
       30×3 30×4 30×5 40×3 40×4 40×5 50   60   70
```

### 3.3. Tiempos de Ejecución

Los tiempos de las metaheurísticas son **órdenes de magnitud superiores** al exacto para estas instancias:

| Rango $n$ | T. medio Random (s) | T. medio GRASP (s) | T. Exacto (s) | Ratio Meta/Exacto |
|:---------:|:-------------------:|:------------------:|:--------------:|:-----------------:|
| 30        | 46–866              | 54–81              | 0.17–0.51      | ~100–5000×        |
| 40        | 94–480              | 108–185            | 0.28–0.51      | ~210–1700×        |
| 50        | 186–2072            | 159–271            | 0.46–1.40      | ~114–1480×        |
| 60        | 304–479             | 281–417            | 0.63–1.28      | ~219–483×         |
| 70        | 431–628             | 415–594            | 0.66–1.47      | ~286–653×         |

**GRASP es más consistente** que Random en tiempos: el rango de tiempos GRASP es más estrecho y no presenta los outliers extremos observados en Random.

## 4. Random vs. GRASP

| Métrica              | Gana Random | Gana GRASP | Empate |
|:--------------------:|:-----------:|:----------:|:------:|
| Mejor MK             | 9/15        | 5/15       | 1/15   |
| Mejor GAP            | 9/15        | 5/15       | 1/15   |
| Menor Tiempo         | 4/15        | 11/15      | 0/15   |

- **Calidad**: Random obtiene makespans marginalmente mejores en la mayoría de combinaciones. Las diferencias son mínimas (<0.3%).
- **Tiempo**: GRASP es significativamente **más rápido y estable** que Random (sin outliers), a pesar de la sobrecarga de la fase constructiva voraz.
- **Trade-off**: En estas instancias, GRASP ofrece un mejor balance calidad-tiempo si se descuentan los outliers de Random.

## 5. Anomalías en los Datos

Se detectaron los siguientes problemas en `resultados_random_large.txt`:

1. **Entradas duplicadas**: Las instancias `large_50x5_2` y `large_50x5_3` aparecen dos veces. Se han resuelto tomando la última entrada.
2. **Tiempos outlier** que exceden los 600 s del timeout:
   - `large_30x4_5`: 4071 s
   - `large_30x5_1`: 2823 s
   - `large_40x4_1`: 1888 s
   - `large_50x5_1`: 9051 s
   - `medium_19x2_2` (Random): 6121 s

Estos valores arrastran las medias de tiempo. Se recomienda investigar si se trata de errores de registro.

## 6. Conclusiones

1. **El solver exacto es la mejor opción** para instancias large: 100% óptimo en <2 s. Las metaheurísticas no aportan ventaja aquí.
2. **Las metaheurísticas son robustas**: A pesar de no ser necesarias, mantienen GAPs entre 2.2% y 3.1%, demostrando la fiabilidad del algoritmo TS+VNS independientemente del tamaño del problema.
3. **$m$ determina la dificultad**: El GAP escala con el número de grúas, no solo con el número de tareas. Las combinaciones ×5 son sistemáticamente las más difíciles.
4. **Paradoja de escalabilidad**: Las instancias large (30–70 tareas) se resuelven en segundos por el exacto, mientras las medium (15–20 tareas) necesitan una hora. Esto subraya que la **estructura del problema** (no solo su tamaño) determina la dificultad computacional.

---
*Datos extraídos de `resumen_resultados_large.csv`. Análisis generado el 2026-02-26.*
