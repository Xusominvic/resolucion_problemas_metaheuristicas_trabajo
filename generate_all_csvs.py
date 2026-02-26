"""
Script para generar los CSVs de resumen para TODAS las instancias (small, medium, large).
Calcula la media aritmética por combinación (NxM) a partir de los archivos de resultados.
"""
import csv
import os
from collections import defaultdict
from typing import Dict, List, Tuple

BASE_DIR = r"c:\Users\jocarles\Documents\resolucion_problemas_metaheuristicas_trabajo\results_v2"


def parse_exact(file_path: str) -> Dict[str, dict]:
    """Parsea el archivo CSV del solver exacto.

    Args:
        file_path: Ruta al archivo de resultados exactos.

    Returns:
        Diccionario {combinación: {'MK exacto': media, 'Time Exacto': media}}.
    """
    results: Dict[str, List[dict]] = defaultdict(list)
    if not os.path.exists(file_path):
        print(f"  [WARN] No encontrado: {file_path}")
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Instancia'):
                continue
            # Extraer combinación: e.g., "small_6x2_1" -> "6x2"
            parts = row['Instancia'].split('_')
            comb = parts[1]  # "6x2", "30x3", etc.
            try:
                mk = float(row.get('Makespan', 0))
                # El campo de tiempo puede llamarse 'Tiempo' o 'Time'
                time_val = row.get('Tiempo') or row.get('Time') or '0'
                time_val = float(time_val)
                results[comb].append({'mk': mk, 'time': time_val})
            except (ValueError, TypeError) as e:
                print(f"  [ERROR] Fila exacto: {row} -> {e}")

    summary = {}
    for comb, values in results.items():
        n = len(values)
        avg_mk = round(sum(v['mk'] for v in values) / n, 4)
        avg_time = round(sum(v['time'] for v in values) / n, 4)
        summary[comb] = {'MK exacto': avg_mk, 'Time Exacto': avg_time}
        print(f"  Exacto [{comb}]: n={n}, MK={avg_mk}, Time={avg_time}")
    return summary


def parse_metaheuristic(file_path: str, prefix: str) -> Dict[str, dict]:
    """Parsea el archivo de resultados de metaheurística (formato separado por '|').

    Si hay entradas duplicadas para la misma instancia, se queda con la ÚLTIMA
    ocurrencia (asumiendo que es una re-ejecución corregida).

    Args:
        file_path: Ruta al archivo de resultados.
        prefix: Prefijo para las columnas ('random' o 'Grasp').

    Returns:
        Diccionario {combinación: {'MK <prefix>': media, ...}}.
    """
    # Paso 1: Leer todas las entradas, usando dict para deduplicar por instancia
    instance_data: Dict[str, dict] = {}  # clave: nombre completo de instancia
    if not os.path.exists(file_path):
        print(f"  [WARN] No encontrado: {file_path}")
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or '|' not in line:
                continue
            if not any(line.startswith(p) for p in ['small_', 'medium_', 'large_']):
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 5:
                continue
            instancia = parts[0]
            try:
                mk = float(parts[1])
                tiempo = float(parts[2])
                gap = float(parts[4])
                # Si la instancia ya existe, se sobreescribe con la última entrada
                if instancia in instance_data:
                    print(f"  [WARN] Duplicado detectado: {instancia} -> usando última entrada")
                instance_data[instancia] = {'mk': mk, 'time': tiempo, 'gap': gap}
            except (ValueError, IndexError):
                continue

    # Paso 2: Agrupar por combinación (NxM)
    results: Dict[str, List[dict]] = defaultdict(list)
    for instancia, data in instance_data.items():
        comb = instancia.split('_')[1]
        results[comb].append(data)

    # Paso 3: Promediar por combinación
    summary = {}
    for comb, values in results.items():
        n = len(values)
        avg_mk = round(sum(v['mk'] for v in values) / n, 4)
        avg_time = round(sum(v['time'] for v in values) / n, 4)
        avg_gap = round(sum(v['gap'] for v in values) / n, 4)
        summary[comb] = {
            f'MK {prefix}': avg_mk,
            f'Time {prefix}': avg_time,
            f'GAP {prefix}': avg_gap
        }
        print(f"  {prefix} [{comb}]: n={n}, MK={avg_mk}, Time={avg_time}, GAP={avg_gap}")
    return summary


def generate_csv(size: str) -> None:
    """Genera el CSV de resumen para un tamaño de instancia dado.

    Args:
        size: Tamaño ('small', 'medium', 'large').
    """
    print(f"\n{'='*60}")
    print(f"Procesando: {size.upper()}")
    print(f"{'='*60}")

    exact_path = os.path.join(BASE_DIR, size, f"resultados_exacto_{size}.txt")
    random_path = os.path.join(BASE_DIR, size, f"resultados_random_{size}.txt")
    grasp_path = os.path.join(BASE_DIR, size, f"resultados_grasp_{size}.txt")

    exact_summary = parse_exact(exact_path)
    random_summary = parse_metaheuristic(random_path, 'random')
    grasp_summary = parse_metaheuristic(grasp_path, 'Grasp')

    all_combs = set(exact_summary.keys()) | set(random_summary.keys()) | set(grasp_summary.keys())
    combinations = sorted(list(all_combs), key=lambda x: [int(c) for c in x.split('x')])

    output_path = os.path.join(BASE_DIR, f"resumen_resultados_{size}.csv")

    fieldnames = [
        'Combination',
        'MK exacto', 'Time Exacto',
        'MK random', 'Time Random', 'GAP Random',
        'MK Grasp', 'Time GRASP', 'GAP GRASP'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for comb in combinations:
            row = {'Combination': comb}

            # Exacto
            ex = exact_summary.get(comb, {})
            row['MK exacto'] = ex.get('MK exacto', '')
            row['Time Exacto'] = ex.get('Time Exacto', '')

            # Random
            rn = random_summary.get(comb, {})
            row['MK random'] = rn.get('MK random', '')
            row['Time Random'] = rn.get('Time random', '')
            row['GAP Random'] = rn.get('GAP random', '')

            # Grasp
            gr = grasp_summary.get(comb, {})
            row['MK Grasp'] = gr.get('MK Grasp', '')
            row['Time GRASP'] = gr.get('Time Grasp', '')
            row['GAP GRASP'] = gr.get('GAP Grasp', '')

            writer.writerow(row)

    print(f"\n  -> CSV guardado en: {output_path}")
    print(f"  -> Combinaciones: {len(combinations)}")

    # Verificar
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"\n  --- CONTENIDO DEL CSV ---")
    print(content)


if __name__ == '__main__':
    for size in ['small', 'medium', 'large']:
        generate_csv(size)
    print("\n=== COMPLETADO ===")
