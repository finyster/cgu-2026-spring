# Requirement Checklist

Last checked: `2026-04-08`

This file maps the current project status to the midterm assignment requirements.

## Requirement 1. 基金基本資訊

Status: `Mostly ready`

What is already prepared:

- 3 檔基金的 PDF 重點整理已完成：
  - `report_digest.md`
- 已整理資訊包括：
  - 基金類型
  - 投信公司
  - 經理人
  - 成立日期
  - 資產規模
  - 費用比率
  - 管理費
  - 最低申購金額
  - 投資區域
  - 投資風格
  - 基準資訊

Current limitation:

- 配息政策、經理人異動、保管費、TER 等欄位還沒有全部補成正式報告表格。

## Requirement 2. 不同期間表現與同類型基金排名

Status: `Ready`

What is already prepared:

- 不同期間績效：
  - `analysis_outputs/tables/performance_summary.csv`
- 同類型基金排名 / 百分位：
  - `analysis_outputs/tables/peer_ranking_summary.csv`
- README 已整合：
  - `README.md`

What can already be written:

- 1Y / 3Y / 5Y 報酬表現
- 同類排名
- 同類百分位
- 短中長期相對績效比較

Current limitation:

- 排名觀察月份是官方最新可用的 `2026-02`
- 本地績效分析跑到 `2026-03`
- 報告要註明兩者截止日不同

## Requirement 3. Factor Analysis（Carhart 4-factor, 過去 5 年）

Status: `Ready`

What is already prepared:

- 正式因子原始檔：
  - `data/tej_carhart_4factor_raw_2026-04-08.csv`
- 標準化因子檔：
  - `data/tej_carhart_4factor_monthly_2020-01_to_2026-03.csv`
- 回歸結果：
  - `analysis_outputs/tables/carhart_summary.csv`
  - `analysis_outputs/tables/carhart_coefficients.csv`
  - `analysis_outputs/tables/carhart_ols_summary_*.txt`

Current 5Y regression window:

- `2021-04` to `2026-03`
- `60` monthly observations per fund

What can already be written:

- Alpha
- MKT beta
- SMB
- HML
- MOM
- Adjusted R²
- 顯著性判讀

## Requirement 4. 績效歸因分析（Attribution Analysis）

Status: `Partial only`

What is already prepared:

- 部分持股資料
- 前十大集中度
- 持股重疊
- 可做簡化版持股結構觀察

Current limitation:

- 沒有完整基金持股
- 沒有同季完整 benchmark 權重
- 沒有完整產業配置對照

What can be done now:

- 簡化版分析：
  - 前十大持股貢獻結構
  - 高集中度風險
  - 主動基金與 ETF 的結構差異

What is not yet defensible:

- 正式 Brinson allocation / selection / interaction decomposition

## Requirement 5. Active Share Analysis

Status: `Partial only`

What is already prepared:

- 持股檔數
- 前十大持股集中度
- 最大單一持股權重
- 持股重疊的初步觀察

Current limitation:

- 持股資料不是完整投組
- 缺 benchmark 完整成分股與權重

What can be done now:

- 簡化版主動程度觀察

What is not yet defensible:

- 精確 Active Share
- 精確 Active Weight

## Requirement 6. 綜合 1-5 給星號評等

Status: `Can do preliminary version`

Why only preliminary:

- Requirement 1, 2, 3 已經可支撐大部分判斷
- Requirement 4, 5 目前只能做簡化版

What is feasible now:

- 先給「初步星等」
- 並在報告中註明：
  - 績效歸因與 Active Share 仍屬簡化判讀

## Requirement 7. 是否推薦投資人買該基金

Status: `Can do preliminary version`

What is feasible now:

- 根據：
  - 績效
  - 同類排名
  - Carhart 回歸
  - 持股集中風險
  - 費用結構
- 先寫出初步投資建議

What should be disclosed:

- 目前 recommendation 仍受持股資料完整度限制

## Overall Assessment

Current project completion by requirement:

1. 基金基本資訊: `Mostly ready`
2. 不同期間績效與同類排名: `Ready`
3. Carhart 四因子分析: `Ready`
4. 績效歸因分析: `Partial only`
5. Active Share Analysis: `Partial only`
6. 星等評等: `Preliminary version can be done now`
7. 投資建議: `Preliminary version can be done now`

## Recommended Next Step

The most efficient next step is:

- directly write the first full draft of the midterm report,
- and explicitly label Attribution / Active Share as simplified analysis based on partial holdings data.
