import csv
import os
from collections import defaultdict

def parse_exact(file_path):
    results = defaultdict(list)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Instancia'): continue
            comb = row['Instancia'].split('_')[1]
            results[comb].append({
                'MK exacto': float(row['Makespan']),
                'Time Exacto': float(row['Tiempo'])
            })
    
    summary = {}
    for comb, values in results.items():
        avg_mk = sum(v['MK exacto'] for v in values) / len(values)
        avg_time = sum(v['Time Exacto'] for v in values) / len(values)
        summary[comb] = {'MK exacto': avg_mk, 'Time Exacto': avg_time}
    return summary

def parse_metaheuristic(file_path, prefix):
    results = defaultdict(list)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '|' in line and any(line.startswith(p) for p in ['small_', 'medium_', 'large_']):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5:
                    instancia = parts[0]
                    try:
                        mk = float(parts[1])
                        tiempo = float(parts[2])
                        gap = float(parts[4])
                        comb = instancia.split('_')[1]
                        results[comb].append({
                            f'MK {prefix}': mk,
                            f'Time {prefix}': tiempo,
                            f'GAP {prefix}': gap
                        })
                    except ValueError:
                        continue
    
    summary = {}
    for comb, values in results.items():
        summary[comb] = {}
        for key in [f'MK {prefix}', f'Time {prefix}', f'GAP {prefix}']:
            summary[comb][key] = sum(v[key] for v in values) / len(values)
    return summary

def main():
    size = 'medium'
    base_dir = r"c:\Users\jocarles\Documents\resolucion_problemas_metaheuristicas_trabajo\results_v2"
    
    exact_path = os.path.join(base_dir, size, f"resultados_exacto_{size}.txt")
    random_path = os.path.join(base_dir, size, f"resultados_random_{size}.txt")
    grasp_path = os.path.join(base_dir, size, f"resultados_grasp_{size}.txt")
    
    print(f"Processing {size} instances...")
    
    exact_summary = parse_exact(exact_path)
    random_summary = parse_metaheuristic(random_path, 'random')
    grasp_summary = parse_metaheuristic(grasp_path, 'Grasp')
    
    print(f"Exact keys: {list(exact_summary.keys())[:3]}")
    print(f"Random keys: {list(random_summary.keys())[:3]}")
    print(f"Grasp keys: {list(grasp_summary.keys())[:3]}")

    combinations = sorted(exact_summary.keys(), key=lambda x: [int(c) for c in x.split('x')])
    output_path = os.path.join(base_dir, f"resumen_resultados_{size}_v2.csv")

    field_mapping = {
        'MK random': 'MK random',
        'Time random': 'Time Random',
        'GAP random': 'GAP RAndom',
        'MK Grasp': 'MK Grasp',
        'Time Grasp': 'Time GRASP',
        'GAP Grasp': 'GAP GRASP'
    }

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'Combination',
            'MK exacto', 'Time Exacto',
            'MK random', 'Time Random', 'GAP RAndom',
            'MK Grasp', 'Time GRASP', 'GAP GRASP'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for comb in combinations:
            row = {'Combination': comb}
            row.update(exact_summary.get(comb, {}))
            
            r_data = random_summary.get(comb, {})
            for k, v in r_data.items():
                if k in field_mapping:
                    row[field_mapping[k]] = v
            
            g_data = grasp_summary.get(comb, {})
            for k, v in g_data.items():
                if k in field_mapping:
                    row[field_mapping[k]] = v
            
            # Rounding
            for k in fieldnames:
                if k in row and row[k] is not None:
                    if k != 'Combination':
                        row[k] = round(float(row[k]), 4)
                else:
                    row[k] = None
            
            writer.writerow(row)

    print(f"File saved to {output_path}")

if __name__ == '__main__':
    main()
