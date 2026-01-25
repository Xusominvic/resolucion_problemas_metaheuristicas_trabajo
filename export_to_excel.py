import pandas as pd

# Datos extraídos de la comparación
data = [
    ["6 x 2", 267.40, 270.80, 1.27, 0.31, 0.07],
    ["6 x 3", 182.00, 186.80, 2.64, 0.22, 0.13],
    ["7 x 2", 284.20, 293.40, 3.24, 0.53, 0.14],
    ["7 x 3", 221.00, 226.50, 2.49, 0.63, 0.26],
    ["8 x 2", 311.00, 320.00, 2.89, 0.52, 0.14],
    ["8 x 3", 255.20, 264.90, 3.80, 1.00, 0.20],
    ["9 x 2", 343.60, 353.20, 2.79, 0.53, 0.16],
    ["9 x 3", 251.20, 266.70, 6.17, 1.69, 0.27],
    ["10 x 2", 409.00, 416.90, 1.93, 1.92, 0.22],
    ["10 x 3", 303.00, 315.60, 4.16, 6.99, 0.40],
    ["11 x 2", 486.80, 497.50, 2.20, 0.41, 0.47],
    ["11 x 3", 305.80, 315.30, 3.11, 6.75, 0.46],
    ["12 x 2", 483.00, 493.00, 2.07, 9.49, 0.39],
    ["12 x 3", 323.00, 335.20, 3.78, 5.08, 0.82],
]

columns = [
    "Tamaño (NxM)", 
    "AVG Makespan (Exacto)", 
    "AVG Makespan (Heurístico)", 
    "Diferencia (Gap %)", 
    "Tiempo AVG (Exacto)", 
    "Tiempo AVG (Heurístico)"
]

df = pd.DataFrame(data, columns=columns)

# Exportar a Excel en la carpeta docs
output_path = r"c:\Users\Josep\Documents\resolucion_problemas_metaheuristicas_trabajo\docs\resultados_instancia_pequeña.xlsx"
df.to_excel(output_path, index=False)

print(f"Archivo exportado con éxito a: {output_path}")
