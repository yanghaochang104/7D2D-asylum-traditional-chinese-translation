# 7 Days To Die - 模組繁體中文翻譯與一致性整合計畫

這個計畫的目標是為 89 個模組的 `Localization.txt` 補上繁體中文（`tchinese`）翻譯，並確保這些翻譯在遊戲中與原版《7 Days To Die》的專有名詞、語氣及體驗保持完美一致。

## User Review Required

> [!IMPORTANT]  
> 由於牽涉到 89 個檔案且文本量大，這將是一個系統性的工程。請您檢視以下的流程，並在下方 **Open Questions** 給予您的看法，確認無誤後我們再開始執行。

## Proposed Approach (執行流程)

### Phase 1: 建立核心術語庫 (Glossary Building)
我們不能靠直覺翻譯。在開始翻譯任何一個模組前，我會先利用腳本或搜尋工具，從原廠的 `/Data/Config/Localization.txt` 中提取常見詞彙的官方翻譯。
例如：
- 武器類型 (Melee, Ranged), 屬性 (Perception, Strength)
- 工具提示常見用語 (e.g., "Scales with Deep Cuts" 原版如何翻譯 "Deep Cuts" 流血技能？)
- 狀態效果 (Buffs), 裝備修復 (Repair kit)
這些將作為我們翻譯所有模組時的「最高準則」。

### Phase 2: CSV/文本結構標準化 (Formatting & Structural Alignment)
分析模組的 `Localization.txt` 後發現，大部分模組只有英文欄位：
`Key,File,Type,UsedInMainMenu,NoTranslate,english`
而遊戲本體有包含其他語系（繁體中文通常位於最後一欄 `tchinese`）。

我會撰寫 Python 腳本或精準的處理流程：
1. 將原本的標題列加上 `,tchinese`。
2. 針對每一行文本，根據逗號 (CSV格式) 解析出英文原文。
3. 產生翻譯後，嚴格遵循雙引號 `""` 規則包覆翻譯文本（尤其是裡面有換行 `\n` 和顏色代碼 `[FF0000]` 的情況），並加在該行最後。

### Phase 3: 批次翻譯與整合 (Batch Execution & Translation)
為確保品質並避免語境斷裂：
1. **Pilot Test（前導測試）**：先挑選 1~2 個模組（例如剛剛看過的 `AsylumLegendaryWeapons`）進行翻譯，並提供給您放進遊戲中測試，確認顏色代碼沒有跑版、術語一致、且遊戲能正常讀取。
2. **批次執行**：確認前導測試沒問題後，我們會分批（例如一次 5-10 個模組）進行翻譯。我會確保每批翻譯都遵守已經建立的術語庫。

---

## Open Questions

在此計畫開始前，有幾個問題需要與您確認：

> [!QUESTION]
> 1. **前導測試**：您是否同意我們先拿 1 到 2 個模組作為範例進行翻譯和格式修改？確認遊戲能正常讀取、且翻譯風格符合預期後，再擴展到其他檔案？
> 2. **翻譯風格與語氣**：目前的模組（如 Asylum 瘋人院系列）有許多暗黑、恐怖的敘述。您偏好「直白還原」還是稍微「潤飾得更有代入感（如魂系遊戲般的文本）」？
> 3. **遊戲內術語**：有些英文可能是模組自創的技能（例如 `Scales with Pummel Pete` 這裡的 `Pummel Pete` 是遊戲原版技能「棒球好手」）。遇到這類原版既有技能，我會去抓原版字詞，您是否贊同？ 
> 4. **只補繁體中文嗎？** 有些玩家會一併補上簡體中文 (`schinese`) 防範簡體系統下變成亂碼，還是我們專注加 `tchinese` 即可？

## Verification Plan

### Automated Tests
* 撰寫簡單的 Python 腳本來驗證每個修改後的檔案，確保它的 CSV 欄位數量前後一致，沒有漏掉的引號或逗號（以防破壞遊戲讀取）。

### Manual Verification
* 測試階段完成後，我會請您開啟遊戲，進入裝備或物品選單中，確認翻譯正常顯示，且原版的顏色標籤（如 `[FFD700]`）有正確渲染成顏色而不是直接顯示英文字符。
