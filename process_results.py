import csv
import os
import sys
from collections import defaultdict

def log(msg):
    with open("script_log.txt", "a") as f:
        f.write(msg + "\n")
    print(msg)

def parse_exact(file_path):
    log(f"Parsing exact: {file_path}")
    results = defaultdict(list)
    if not os.path.exists(file_path):
        log(f"File not found: {file_path}")
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Instancia'): continue
            comb = row['Instancia'].split('_')[1]
            try:
                mk = float(row.get('Makespan', 0))
                time_val = row.get('Tiempo') or row.get('Time')
                if time_val:
                    time_val = float(time_val)
                else:
                    time_val = 0.0
                results[comb].append({
                    'MK exacto': mk,
                    'Time Exacto': time_val
                })
            except Exception as e:
                log(f"Error parsing row {row}: {e}")
    
    summary = {}
    for comb, values in results.items():
        avg_mk = sum(v['MK exacto'] for v in values) / len(values)
        avg_time = sum(v['Time Exacto'] for v in values) / len(values)
        summary[comb] = {'MK exacto': avg_mk, 'Time Exacto': avg_time}
    return summary

def parse_metaheuristic(file_path, prefix):
    log(f"Parsing meta: {file_path}")
    results = defaultdict(list)
    if not os.path.exists(file_path):
        log(f"File not found: {file_path}")
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
            if values:
                summary[comb][key] = sum(v[key] for v in values) / len(values)
            else:
                summary[comb][key] = None
    return summary

def main(size='medium'):
    try:
        base_dir = r"c:\Users\jocarles\Documents\resolucion_problemas_metaheuristicas_trabajo\results_v2"
        
        exact_path = os.path.join(base_dir, size, f"resultados_exacto_{size}.txt")
        random_path = os.path.join(base_dir, size, f"resultados_random_{size}.txt")
        grasp_path = os.path.join(base_dir, size, f"resultados_grasp_{size}.txt")
        
        log(f"Processing {size} instances...")
        
        exact_summary = parse_exact(exact_path)
        random_summary = parse_metaheuristic(random_path, 'random')
        grasp_summary = parse_metaheuristic(grasp_path, 'Grasp')
        
        log(f"Exact keys: {len(exact_summary)}")
        log(f"Random keys: {len(random_summary)}")
        log(f"Grasp keys: {len(grasp_summary)}")

        all_combs = set(exact_summary.keys()) | set(random_summary.keys()) | set(grasp_summary.keys())
        # Sort combinations numerically: e.g., 30x3, 30x4, 40x3...
        combinations = sorted(list(all_combs), key=lambda x: [int(c) for c in x.split('x')])
        
        output_path = os.path.join(base_dir, f"resumen_resultados_{size}.csv")
        log(f"Output path: {output_path}")

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
                    elif k == 'GAP random':
                        row['GAP RAndom'] = v
                
                g_data = grasp_summary.get(comb, {})
                for k, v in g_data.items():
                    if k in field_mapping:
                        row[field_mapping[k]] = v
                
                clean_row = {k: row.get(k) for k in fieldnames}
                for k in fieldnames:
                    if clean_row[k] is not None and k != 'Combination':
                        try:
                            clean_row[k] = round(float(clean_row[k]), 4)
                        except:
                            pass
                writer.writerow(clean_row)
        log(f"File successfully saved to {output_path}")
    except Exception as e:
        log(f"CRITICAL ERROR in main: {e}")

if __name__ == '__main__':
    open("script_log.txt", "w").close() # Clear log
    target_size = 'large'
    if len(sys.argv) > 1:
        target_size = sys.argv[1]
    main(target_size)
