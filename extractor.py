import csv
import json
import sys

file_path = r'c:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Mods\zzzzzzzzzz_TraditionalChineseTranslation\Config\Localization.txt'

batch_size = 150
batch = []

try:
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        h_lower = [h.strip().lower() for h in header]
        en_idx = h_lower.index("english")
        tc_idx = h_lower.index("tchinese")
        
        for row in reader:
            if len(row) > tc_idx:
                tc_text = row[tc_idx].strip()
                en_text = row[en_idx].strip()
                key = row[0].strip()
                if not tc_text and en_text:
                    batch.append({"key": key, "english": en_text})
            elif len(row) > en_idx:
                en_text = row[en_idx].strip()
                key = row[0].strip()
                if en_text:
                    batch.append({"key": key, "english": en_text})
            
            if len(batch) >= batch_size:
                break

    with open('batch.json', 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(batch)} items to batch.json")

except Exception as e:
    print(f"Error: {e}")
