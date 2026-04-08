# Smart Manufacturing Midterm Project

這個目錄整理的是 Smart Manufacturing 期中作業的原始資料、題目說明，以及可直接交給 AI 使用的 prompt 文件。

目前重點不是程式碼實作，而是先把作業規格、案例背景、實驗邏輯與 app 方向整理清楚，方便後續直接開發一個英文版、具高質感 UI 的模擬系統。

## 目錄內容

- `4-1 Kanban Experiment(Description).csv`
  作業原始說明、5 個 experiment 的參數設定、Push / Kanban 卡數概念。

- `4-1 Kanban Experiment(Question).csv`
  作業報告題目，共 10 題，主軸是比較 WIP、throughput、variation、Kanban / Push 與 bottleneck 位置的影響。

- `4-1 Kanban Experiment((1)+(a)).csv`
- `4-1 Kanban Experiment((1)+(b)).csv`
- `4-1 Kanban Experiment((2)+(a)).csv`
- `4-1 Kanban Experiment((2)+(b)).csv`
  四個作業模板。這些檔案保留了原始 case 的輸入格式與 Excel 模板結構。

- `caseStudy.md`
  針對 SSMC CMP dispatching case 的整理版筆記。這份文件不是原作業模板，而是用來加強 app 的故事性、實務背景與 dispatching 邏輯。

- `prompt.md`
  第一版 AI handoff prompt。重點是忠實重建原始作業的 5-station Kanban / Push 模擬 dashboard。

- `prompt_cmp_case_lab.md`
  第二版 AI handoff prompt。這是進階版，將 SSMC CMP case 與原作業的實驗精神整合成一個更完整的 English-language case lab app。

## 建議使用方式

### 如果你要做「原始作業版」app

請使用：

- `prompt.md`

這份適合做：

- 5-station serial line
- 200-day simulation
- 5 experiment tabs
- Large / Small Variation
- Push / Kanban comparison
- 作業導向的 WIP / throughput 分析

### 如果你要做「案例強化版」app

請使用：

- `prompt_cmp_case_lab.md`

這份適合做：

- SSMC CMP dispatching case app
- Push vs Pull 比較
- queue-time、water tank、cassette、changeover 等真實限制
- 具故事性、分析性與高質感 UI 的英文版互動案例系統
- 保留作業式的實驗精神與可重現的比較框架

## 目前最重要的規格判讀

這份作業原始資料中，`(a)` / `(b)` 的系統標註在部分說明欄位存在歧義，因此目前統一採用以下解讀：

- `Case (1)` = `Large Variation`
- `Case (2)` = `Small Variation`
- `Case (a)` = `Push`
- `Case (b)` = `Kanban`

採用這個判讀的原因是：

- 原始模板中的 buffer 卡數設定與後續 prompt 邏輯一致
- `Push` 對應 `Buffers 2~5 = Infinity`
- `Kanban` 對應 `Buffers 2~5 = 9`

後續實作時應以這個版本為準，不要反過來做。

## 推薦開發方向

如果要做最完整且最有展示價值的版本，建議以 `prompt_cmp_case_lab.md` 為主，因為它同時保留了兩個層次：

1. 作業需要的實驗嚴謹性
2. 真實 case 需要的管理與 dispatching 故事性

這樣做出來的 app 不會只是「把 CSV 視覺化」，而會更像一個真正的 operations case lab。

## 目前狀態

目前此目錄包含：

- 原始作業資料
- case study 摘要
- 兩份 AI-ready prompt

尚未開始正式實作 app。

## 下一步

建議下一步直接擇一進行：

1. 根據 `prompt.md` 開發作業版 dashboard。
2. 根據 `prompt_cmp_case_lab.md` 開發案例強化版 dashboard。

如果目標是做出更完整、更有質感、也更能展示能力的成果，優先建議走第二條路線。
