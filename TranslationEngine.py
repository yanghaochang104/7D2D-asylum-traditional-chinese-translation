import csv
import glob
import os
import re
import urllib.request
import urllib.parse
import json
import time
import sys

# 設定路徑
base_game_loc = r"C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Data\Config\Localization.txt"
src_folder = r"C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Mods"
out_folder = os.path.join(src_folder, "zzzzzzzzzz_TraditionalChineseTranslation", "Config")
if not os.path.exists(out_folder):
    os.makedirs(out_folder)
dst = os.path.join(out_folder, "Localization.txt")
temp_dst = dst + ".tmp"

print("正在從遊戲原始資料建構動態官方辭典 (Dynamic Glossary)...")
sc_to_tc = {}

# 1. 讀取原廠遊戲 Localization.txt
with open(base_game_loc, "r", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    header = next(reader, None)
    
    h_lower = [h.strip().lower() for h in header]
    en_idx = h_lower.index("english")
    sc_idx = h_lower.index("schinese")
    tc_idx = h_lower.index("tchinese")
    
    for row in reader:
        if len(row) > max(en_idx, sc_idx, tc_idx):
            sc_text = row[sc_idx].strip()
            tc_text = row[tc_idx].strip()
            
            # 從簡中 -> 繁中進行嚴格映射
            if sc_text and tc_text and sc_text != tc_text and len(sc_text) >= 2:
                # 避開純數字或符號
                if sc_text.replace(".", "").replace("-", "").replace("+", "").isnumeric(): continue
                sc_to_tc[sc_text] = tc_text

# 2. 加入手動強校正術語字典 (針對 Mod 翻譯容易翻車的特定名稱)
sc_to_tc['深度刀伤'] = '深切口'
sc_to_tc['击球手佩特'] = '打擊者'
sc_to_tc['头骨粉碎者'] = '頭顱破碎機'
sc_to_tc['矿工69'] = '礦工 69'
sc_to_tc['电击器'] = '觸電者'
sc_to_tc['大锤'] = '大槌'
sc_to_tc['棍棒'] = '棍棒'
sc_to_tc['丧尸'] = '喪屍'

print(f"成功建構包含 {len(sc_to_tc)} 筆官方術語的真理詞典。")
sorted_sc_keys = sorted(sc_to_tc.keys(), key=len, reverse=True)

# 2.5 讀取已經翻譯好的「歷史快取」(斷點續傳快取)
translation_cache = {}
if os.path.exists(dst):
    with open(dst, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        h = next(reader, None)
        if h:
            h_low = [col.strip().lower() for col in h]
            if "english" in h_low and "tchinese" in h_low:
                e_i = h_low.index("english")
                t_i = h_low.index("tchinese")
                for row in reader:
                    if len(row) > max(e_i, t_i):
                        en_t = row[e_i].strip()
                        tc_t = row[t_i].strip()
                        if en_t and tc_t:
                            translation_cache[en_t] = tc_t

print(f"讀取翻譯歷史快取：發現 {len(translation_cache)} 筆已經完成的心血，將自動沿用避免重複呼叫。")

# 3. 蒐集所有 Mod 的 Localization.txt
files = []
for root, _, filenames in os.walk(src_folder):
    if 'zzzzzzzzzz_TraditionalChineseTranslation' in root:
        continue
    for filename in filenames:
        if filename.lower() == 'localization.txt':
            files.append(os.path.join(root, filename))

print(f"共發現了 {len(files)} 個模組翻譯檔。")

out_rows = []
header = ["Key", "File", "Type", "UsedInMainMenu", "NoTranslate", "english", "tchinese"]
out_rows.append(header)

queue = []
items = []

# --- 標籤保護器 ---
def clean_tags(text):
    tags = re.findall(r'(\[[-A-Fa-f0-9]*\]|\\n)', text)
    safe_text = text
    for i, tag in enumerate(tags):
        safe_text = safe_text.replace(tag, f" <{i}> ", 1)
    return safe_text, tags

def restore_tags(text, tags):
    for i, tag in enumerate(tags):
        text = re.sub(rf'<\s*{i}\s*>', tag, text)
    return text.replace('  ', ' ')

# --- Google 防火牆鐵壁翻譯請求器 ---
def translate_batch(english_list):
    """將一批英文文本打包送給免費的 Google Translate 引擎，自備無限重試裝甲。"""
    if not english_list: return []
    combined = " ||| ".join(english_list)
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-tw&dt=t&q=" + urllib.parse.quote(combined)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    attempts = 0
    while True:
        try:
            response = urllib.request.urlopen(req)
            data = json.loads(response.read().decode("utf-8"))
            translated = "".join([x[0] for x in data[0] if x[0]])
            results = translated.split("|||")
            return [r.strip() for r in results]
        
        except urllib.error.HTTPError as e:
            attempts += 1
            if e.code in [429, 500, 503]:
                # 如果遇到 429 Too Many Requests，直接進入深度休眠
                sleep_time = min(300, 30 * attempts) # 從 30 秒開始等，最高等 5 分鐘
                print(f"警告: 觸發 Google API 流量限制 ({e.code})。為避免封鎖，腳本進入休息狀態 {sleep_time} 秒 (第 {attempts} 次重試)...")
                time.sleep(sleep_time)
            else:
                print(f"未知錯誤 ({e.code})，跳過這批...")
                return english_list
                
        except Exception as e:
            print(f"網路異常: {e}，等待 10 秒後再試...")
            time.sleep(10)

# 4. 開始處理每個檔案的 CSV 資料
for fpath in files:
    try:
        with open(fpath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header_row = next(reader, None)
            if not header_row: continue
            
            h_lower = [h.strip().lower() for h in header_row]
            if "key" not in h_lower: continue
            
            key_idx = h_lower.index("key")
            file_idx = h_lower.index("file") if "file" in h_lower else -1
            type_idx = h_lower.index("type") if "type" in h_lower else -1
            ui_idx = h_lower.index("usedinmainmenu") if "usedinmainmenu" in h_lower else -1
            nt_idx = h_lower.index("notranslate") if "notranslate" in h_lower else -1
            en_idx = h_lower.index("english") if "english" in h_lower else -1
            sc_idx = h_lower.index("schinese") if "schinese" in h_lower else -1
            tc_idx = h_lower.index("tchinese") if "tchinese" in h_lower else -1
            
            for row in reader:
                if not row or len(row) <= key_idx: continue
                key = row[key_idx].strip()
                if not key or key.startswith("#"): continue
                
                en_text = row[en_idx] if en_idx != -1 and len(row) > en_idx else ""
                sc_text = row[sc_idx] if sc_idx != -1 and len(row) > sc_idx else ""
                tc_text = row[tc_idx] if tc_idx != -1 and len(row) > tc_idx else ""
                
                base = [
                    key,
                    row[file_idx] if file_idx != -1 and len(row) > file_idx else "",
                    row[type_idx] if type_idx != -1 and len(row) > type_idx else "",
                    row[ui_idx] if ui_idx != -1 and len(row) > ui_idx else "",
                    row[nt_idx] if nt_idx != -1 and len(row) > nt_idx else "",
                    en_text
                ]
                
                final_zh = ""
                # A. 優先檢查是否在歷史快取中？有就直接抓出來用！
                if en_text and en_text in translation_cache:
                    final_zh = translation_cache[en_text]
                
                # B. 本身就有繁中文本
                elif tc_text: 
                    final_zh = tc_text
                    
                # C. 如果有原本 Mod 原作者的簡中翻譯，直接對其應用「動態官方辭典」強迫替換
                elif sc_text and not tc_text:
                    final_zh = sc_text
                    for k in sorted_sc_keys:
                        if k in final_zh:
                            final_zh = final_zh.replace(k, sc_to_tc[k])
                            
                # D. 上述皆無，純英文 -> 放進待機翻佇列
                else:
                    if en_text:
                        safe_en, tags = clean_tags(en_text)
                        queue.append(safe_en)
                        items.append((base, tags, en_text))
                        continue
                
                if final_zh:
                    base.append(final_zh)
                    out_rows.append(base)
                    
    except Exception as e:
        pass

print(f"共有 {len(queue)} 筆未知的純英文單字準備進入保證不會被斷線的「愚公移山機翻列隊」...")

# 5. 背景機翻處理 (包含即時存檔功能)
BATCH_SIZE = 15 # 縮減每批的數量，減輕伺服器負荷
processed = 0

for i in range(0, len(queue), BATCH_SIZE):
    batch_en = queue[i:i+BATCH_SIZE]
    batch_items = items[i:i+BATCH_SIZE]
    
    trans = translate_batch(batch_en)
    
    # 防護機制，確保能配對
    if len(trans) == len(batch_en):
        for j, translated_text in enumerate(trans):
            base, tags, orig_en = batch_items[j]
            restored = restore_tags(translated_text, tags)
            
            # 手動強校正: 把機翻可能錯翻的名稱拉回繁中
            restored = restored.replace('深度切割', '深切口').replace('深部切割', '深切口')
            
            base.append(restored)
            out_rows.append(base)
    else:
        # 如果長度對齊失敗，留白保護陣列不崩潰
        for b_item in batch_items:
            b_item[0].append("")
            out_rows.append(b_item[0])
            
    processed += len(batch_en)
    
    # [核心改進] 每批次強制冷卻 2.5 秒，這能避開 99% 的 Rate Limit
    if processed % 15 == 0:
        print(f"進度：已翻譯 {processed} / {len(queue)} 筆...")
        time.sleep(2.5)
        
    # [核心改進] 每 150 筆就將全部結果寫入一次硬碟
    if processed % 150 == 0:
        with open(temp_dst, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(out_rows + [b[0] for b in items[i+BATCH_SIZE:]]) # 補上還沒翻完的空白佔位符
        os.replace(temp_dst, dst)
 
# 6. 最後將結果寫入大統一檔案
with open(temp_dst, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(out_rows)
os.replace(temp_dst, dst)

print(f"徹底大功告成！全自動繁中外掛檔案已產生於 {dst}！共計寫入了 {len(out_rows)} 筆。")
