import csv
import json
import os
import sys

file_path = r'c:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Mods\zzzzzzzzzz_TraditionalChineseTranslation\Config\Localization.txt'
temp_path = file_path + ".tmp"

try:
    with open('translation_dict.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
        # Convert list to dict mapping key -> tchinese
        if isinstance(translations, list): # handle in case we output a list of dicts
            t_map = {item['key']: item['tchinese'] for item in translations if 'key' in item and 'tchinese' in item}
        else:
            t_map = translations  # if it's already a dict
            
    with open(file_path, 'r', encoding='utf-8-sig') as f, open(temp_path, 'w', encoding='utf-8-sig', newline='') as out:
        reader = csv.reader(f)
        writer = csv.writer(out)
        
        header = next(reader, None)
        writer.writerow(header)
        
        h_lower = [h.strip().lower() for h in header]
        tc_idx = h_lower.index("tchinese")
        en_idx = h_lower.index("english")
        
        applied_count = 0
        for row in reader:
            key = row[0].strip()
            if key in t_map:
                tc_text = t_map[key]
                
                # Make sure the row is long enough
                while len(row) <= tc_idx:
                    row.append("")
                
                current_tc = row[tc_idx].strip()
                if not current_tc: # only fill if empty
                    row[tc_idx] = tc_text
                    applied_count += 1
            writer.writerow(row)
            
    os.replace(temp_path, file_path)
    print(f"Applied {applied_count} translations to Localization.txt")

except Exception as e:
    print(f"Error: {e}")
