---
name: ecology-methods-literature-list
description: 面向生态学研究的“方法学文献收集清单”工作流：将模糊研究思路转为可执行的分析路线，优先通过方法选择型验证点筛选合适方法，并产出 reading-list.md（候选文献清单，含相关性与适用边界）。适用于：为方法选择/参数阈值/适用边界生成可核对的候选文献清单（标题+摘要初筛），并要求用户后续精读全文补全要点。
---

# Research Methods Reading List（意图对齐 + 候选文献清单）

本 skill 只做两件事：
1) 通过最多每轮 3 个问题，快速对齐研究方法框架（不猜测、不补编）  
2) 生成 `reading-list.md`（候选文献清单），供用户自行获取全文并精读补全

## 📌 路径说明（避免复制命令不可用）

本仓库内该 skill 的根目录为：`ecology-methods-literature-list/`

- **在本仓库直接运行脚本**：使用 `ecology-methods-literature-list/scripts/...`
- **在 Codex 安装后的 skill 目录运行**：路径通常类似 `.agent/skills/ecology-methods-literature-list/...`（取决于你的安装位置）

下文示例默认按“本仓库直接运行”的路径写；若你是在安装目录运行，请将前缀替换为实际 skill 路径。

## ✅ 核心约束

- **不猜测**：关键信息不明确就问
- **不捏造**：不编造论文/DOI/期刊名
- **渐进提问**：每轮最多 3 个问题
- **先确认再继续**：每轮先复述用户答案并让其确认
- **只做初筛**：检索仅基于标题+摘要等元数据；不抓取全文

---

## Stage 1：意图对齐（最多每轮 3 问）

**参考**：`references/step1-intent/`

### 开场白（固定）
> 为了帮你写出清晰、可复现的生态学 Methods，我需要先确认少量关键信息。请按编号简要回答：

### 首轮 3 问（固定）
1. 研究主题（种群/群落/生态系统/保护等）？研究系统与区域？核心目标/假设？
2. 数据如何获得（样方/陷阱/相机/传感器/遥感/公开数据）？时空尺度与样本量？
3. 响应变量/指标？解释变量？计划使用的分析方法与软件？

### 每轮输出：研究方法信息卡（内联）
```markdown
## 研究方法信息卡

### 已确认信息
- 研究主题：
- 研究系统：
- 研究区域：
- 数据采集：
- 核心指标：
- 分析方法：

### 关键缺口（最多 3 条）
1.
2.
3.

### 下一轮问题（≤3）
1.
2.
3.
```

完成标准：研究系统清晰 + 数据来源明确 + 分析路径可执行

---

## Stage 2：生成候选文献清单（reading-list.md）

**参考**：`references/step2-retrieval/`

### Step 2.0：先问用户选哪种检索方式（必须显式确认）
1. **内置脚本（推荐）**：Semantic Scholar（结构化元数据、可复现、稳定）  
2. **Google Scholar（脚本）**：基于 `scholarly` 的非官方访问（覆盖更全，但更易触发风控/验证码/限流）

### Step 2.1：提取验证点（1–3 个）
从“研究方法信息卡”里挑 1–3 个**最关键、最不确定**的“方法决策点”作为验证点。

> 默认优先选择“方法选择型验证点”（因为很多用户此时还没选定方法）。

#### A) 方法选择型验证点（优先）
用于把“模糊想法 → 候选方法集合 → 推荐路径”变成可查证的证据链。

常见验证点模板（任选 1–2 个即可）：
- **方法候选对比**：在【数据类型 + 采样设计 + 研究目标】下，哪些方法更合适（A vs B vs C）？各自前提、优缺点与适用边界是什么？
- **关键假设/诊断**：选用该类方法时，必须检查哪些假设/诊断（如过度离散、零膨胀、离散度差异、空间自相关、重复测量）？若不满足，常见替代路径是什么？
- **研究语境匹配**：在类似生态系统/尺度/抽样力度下，主流研究通常采用哪些分析路线？为什么（而不是“哪个最好”）？

示例（把括号替换为你的语境）：
- “在（群落组成差异）问题中，PERMANOVA vs 基于排序/模型的替代方案在（分层/区组设计）下如何选择？”
- “在（计数型响应变量）且存在（零膨胀/过度离散）时，GLMM（负二项/ZIP/hurdle）该如何选型与报告？”

#### B) 参数/实现型验证点（方法候选确定后再选）
用于把“选定方法 → 可复现实现细节”补齐证据。
- **参数依据**：窗口/阈值/间距/置换策略/平滑参数等推荐设置与其前提条件是什么？
- **软件实现差异**：不同包/函数在默认设置、统计量、置换/随机化策略上有何差异，如何避免误用？

### Step 2.2：执行检索（只取元数据）
**A) Semantic Scholar（推荐）**
```bash
python ecology-methods-literature-list/scripts/search_literature.py "your query" --limit 10 --format json
python ecology-methods-literature-list/scripts/search_literature.py "your query" --year-start 2015 --year-end "$(date +%Y)" --limit 15 --format json
python ecology-methods-literature-list/scripts/search_literature.py "your query" --limit 10 --format md
```

**B) Google Scholar（脚本）**
```bash
pip install -r ecology-methods-literature-list/requirements-google-scholar.txt
python ecology-methods-literature-list/scripts/search_google_scholar.py "your query" --limit 10 --format json
python ecology-methods-literature-list/scripts/search_google_scholar.py "your query" --year-start 2015 --year-end "$(date +%Y)" --limit 15 --sort-by citations --format json
python ecology-methods-literature-list/scripts/search_google_scholar.py "your query" --limit 10 --format md
```

#### 检索式建议（与“方法选择型验证点”对齐）

当验证点是“选方法/比方法”时，检索式不要只写方法名，建议用：
- **问题 + 方法类关键词**：`(method OR framework OR guideline OR protocol OR best practice OR recommendation)`
- **数据/设计约束**：`(zero-inflated OR overdispersed OR repeated measures OR spatial autocorrelation OR blocked design)`
- **生态学语境**：`(ecology OR ecological OR community OR biodiversity OR camera trap OR quadrat)`

例：
- `"PERMANOVA" AND (dispersion OR betadisper) AND ecology AND (guideline OR recommendation)`
- `("zero-inflated" AND "negative binomial" AND ecology) AND (GLMM OR mixed model) AND (review OR guideline)`

### Step 2.3：输出 reading-list.md（Skill1 产物）
- 使用 `ecology-methods-literature-list/assets/reading-list-template.md` 的结构
- Skill1 填充：验证点、候选论文元数据、相关性说明、初步边界/警告
- **用户后续精读全文必须补全**：`精读要点（必填）`、`原文定位（必填）`

#### 结构化填充规则（让输出可复现）

对每个验证点（Verification Point），用同一套字段规则填入 Paper 条目：
- 标题：脚本输出 `title`
- 作者：脚本输出 `authors`（建议只展示前 3 位 + et al.）
- 年份：`year`
- 期刊/会议：`venue`
- DOI：`doi`（若无则留空或写“未知”）
- 链接：优先用 `url`（Google Scholar 还可能有 `eprintUrl`）
- 相关性（Skill1 填）：**一句话**说明它能支撑哪个“方法决策点”（优先是“方法选择型验证点”，其次是参数/实现与适用边界）
- 适用边界/警告（Skill1 初填）：至少写出 1 条“成立前提/不适用情形/注意事项”（例如数据类型、抽样设计、空间尺度、样本量、置换/随机化策略等）

建议做法：
1) 每个验证点先写 1 条“可核对的决策句”（例如“PERMANOVA 置换应在分层/区组内进行”）
2) 针对该句构造 1–2 条检索式（方法名 + 场景关键词 + guideline/recommendation/comparison）
3) 每个验证点保留 5–12 篇候选即可，避免清单膨胀导致无法精读

#### 可选：用脚本把 JSON 机械映射成段落

如果你已经用检索脚本拿到 JSON（Semantic Scholar 或 Google Scholar 都可），可以用下列脚本生成“单个验证点段落”，再粘贴/追加到 `reading-list.md`：

```bash
python ecology-methods-literature-list/scripts/make_reading_list_section.py \
  --input search_results.json \
  --verification-point "PERMANOVA 置换策略" \
  --decision "在分层/区组设计下，置换应限制在区组内进行" \
  --limit 10
```
