---
name: ecology-research-assistant
description: 帮助生态学研究人员收集和整理学术文献，将现有数据转化为可发表的研究成果。当用户请求收集文献、需要查找生态学相关论文、或想要整理研究参考文献时使用。专为拥有数据但需要文献支持来发展成学术出版物的生态学专业人士设计。支持意图对齐、关键词识别、通过Semantic Scholar和Google Scholar进行文献检索，以及生成带中文翻译的格式化文献清单。
---

# 生态学研究助手

## 概述

引导生态学研究人员完成系统化的文献收集流程：对齐研究意图、识别关键词、检索文献数据库、生成带中文翻译和方法分类的格式化清单。

## 工作流程

### 阶段1：意图对齐

通过高信息密度的问题快速识别用户的研究意图、学科背景和分析方法偏好。

**目标**：用最少的问题（通常2-3个）建立个性化的研究上下文。

**需要收集的关键信息**：
- 研究对象（物种/群落/生态系统/景观）
- 数据类型和范围（物种多样性/功能性状/环境因子/遥感数据）
- 研究目标（描述/预测/解释/保护）
- 偏好的分析方法（统计/模型/实验）

**参考资料**：查看 `references/intent-alignment.md` 获取问题模板和策略。该文件包含：
- 针对不同研究类型的核心问题模板
- 对话策略（快速建立上下文、渐进式引导、确认式对齐）
- 典型对话示例

**示例问题**：
```
请简要描述：
- 你的研究对象是什么？（物种/群落/生态系统/景观）
- 你希望通过这些数据回答什么研究问题？
- 你的研究目标是什么？（描述现状/预测变化/解释机制/指导保护）
```

**提示**：
- 避免一次性问太多问题；第一轮2-3个问题即可
- 根据用户回答调整后续问题
- 总结理解并在继续前与用户确认

### 阶段2：关键词确认

基于对齐的研究意图，识别并确认用于文献检索的关键词。

**目标**：生成兼顾查准率和查全率的有效检索关键词，包括特定对象研究和通用方法学文献。

**关键词构建策略**：

**重要原则**：不要只检索特定物种/对象的文献，还要检索通用方法学文献以拓宽思路。

**策略A：特定对象检索**（获取直接相关的研究）
1. **核心概念**：从研究对象和问题中提取（如"Hyphantria cunea"、"美国白蛾"）
2. **研究问题**：添加研究问题关键词（如"climate factors"、"occurrence"）
3. **研究方法**：如适用，添加相关分析方法（如"MaxEnt"、"prediction model"）
4. **组合策略**：特定对象 + 研究问题 + 方法

**策略B：通用方法学检索**（获取其他类似研究的方法参考）
1. **对象类别**：用更广泛的类别替代特定对象（如"insect pest"、"invasive species"、"forest pest"）
2. **研究问题**：保持研究问题关键词（如"climate factors"、"population dynamics"）
3. **研究方法**：强调分析方法（如"machine learning"、"species distribution model"）
4. **组合策略**：对象类别 + 研究问题 + 方法

**参考资料**：查阅 `references/ecology-subfields.md` 和 `references/research-methods.md` 以：
- 识别用户的生态学子领域
- 识别相关研究方法
- 生成适当的领域特定关键词

**示例1：美国白蛾发生量影响因子研究**
```
用户研究：探究气候因子和成虫种群动态对美国白蛾幼虫发生的影响

策略A - 特定对象检索（获取直接相关研究）：
- "Hyphantria cunea" AND "climate factors" AND "larva occurrence"
- "fall webworm" AND "temperature" AND "population dynamics"
- "Hyphantria cunea" AND "prediction model" AND "climate"

策略B - 通用方法学检索（获取方法参考）：
- "insect pest" AND "climate factors" AND "occurrence prediction"
- "forest pest" AND "population dynamics" AND "machine learning"
- "invasive species" AND "climate" AND "MaxEnt model"
- "lepidoptera pest" AND "temperature" AND "development model"

说明：策略B可以找到其他害虫（如舞毒蛾、松毛虫等）的类似研究，
提供分析方法和建模思路的参考。
```

**示例2：高山草甸植物多样性研究**
```
用户研究：海拔对高山草甸植物多样性的影响

策略A - 特定对象检索：
- "elevation gradient" AND "plant diversity" AND "alpine meadow"
- "elevational patterns" AND "species richness" AND "mountain"
- "altitudinal gradient" AND "community composition" AND "alpine"

策略B - 通用方法学检索：
- "elevation gradient" AND "biodiversity" AND "statistical analysis"
- "environmental gradient" AND "species diversity" AND "modeling"
- "altitude" AND "diversity patterns" AND "generalized linear model"
```

**确认**：向用户展示两类检索策略（各3-5个关键词组合），说明每类的目的，允许他们选择、修改或添加新的组合。

### 阶段3：文献检索

**重要：在开始检索前，必须先询问用户选择检索方式。**

#### 步骤3.1：选择检索API

使用AskUserQuestion工具询问用户想使用哪种检索方式：

**问题示例**：
```
您希望使用哪种方式进行文献检索？

选项：
1. Semantic Scholar API（推荐）
   - 官方API，更稳定
   - 无需额外依赖
   - 可能遇到速率限制（429错误）
   - 如有API密钥可获得更高限额

2. Google Scholar（通过scholarly库）
   - 覆盖面更广
   - 可能触发验证码或限流
   - 需要安装scholarly库

3. WebSearch（备用方案）
   - 使用Claude的WebSearch工具
   - 不需要API密钥
   - 结果可能不如专业学术API详细

4. 我有自己的API密钥
   - 请提供您的Semantic Scholar API密钥
```

**根据用户选择执行相应操作**：
- 如果选择1或2：使用相应的脚本
- 如果选择3：使用WebSearch工具进行检索
- 如果选择4：询问API密钥，然后使用Semantic Scholar

#### 步骤3.2：执行检索

使用提供的脚本或工具执行文献检索，获取元数据（标题、摘要、作者、DOI等）。

**可用检索工具**：

1. **Semantic Scholar**（推荐，更稳定）
   - 脚本：`scripts/search_literature.py`
   - 官方API，无第三方依赖
   - 支持年份过滤、翻页、重试机制
   - 限制：每次查询最多100条结果
   - 可选：设置API密钥以获得更高限额

2. **Google Scholar**（覆盖面更广，可能被限流）
   - 脚本：`scripts/search_google_scholar.py`
   - 需要 `scholarly` 库
   - 可能触发验证码或限流
   - 限制：每次查询最多200条结果

3. **WebSearch**（备用方案）
   - 使用Claude的WebSearch工具
   - 适合快速检索和初步了解
   - 结果格式可能需要额外处理

**使用方法**：

```bash
# Semantic Scholar（JSON输出）
python scripts/search_literature.py "elevation gradient plant diversity alpine" \
  --limit 20 --year-start 2015 --format json

# Semantic Scholar（Markdown输出）
python scripts/search_literature.py "elevation gradient plant diversity alpine" \
  --limit 20 --year-start 2015 --format md

# 使用API密钥（提高速率限制）
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"
python scripts/search_literature.py "elevation gradient plant diversity alpine" \
  --limit 20 --year-start 2015 --format json

# Google Scholar（JSON输出）
python scripts/search_google_scholar.py "elevation gradient plant diversity alpine" \
  --limit 20 --year-start 2015 --format json
```

**WebSearch使用方法**：

如果用户选择使用WebSearch，使用以下策略：

```
# 使用WebSearch工具进行学术检索
WebSearch(query="elevation gradient plant diversity alpine site:scholar.google.com")

# 或者针对特定数据库
WebSearch(query="elevation gradient plant diversity alpine site:semanticscholar.org")

# 组合多个关键词
WebSearch(query="elevation gradient AND plant diversity AND alpine meadow 2015-2025")
```

**注意**：WebSearch返回的结果可能需要额外处理和格式化。

**检索策略**：
- **首先询问用户**：使用AskUserQuestion工具让用户选择检索方式
- 优先推荐Semantic Scholar（更稳定，学术性强）
- 如用户有API密钥，优先使用以获得更高限额
- 如遇到速率限制，建议使用WebSearch作为备用方案
- Google Scholar可作为补充，但需注意可能的限流问题
- 每个关键词组合通常检索20-50篇论文
- 按年份范围过滤（如最近5-10年）以获取最新研究
- 按引用次数排序以优先获取有影响力的论文

**输出**：脚本返回JSON或Markdown格式的元数据（标题、作者、年份、期刊、摘要、DOI、引用次数、URL）。

### 阶段4：输出文献清单

处理检索到的元数据，生成带中文翻译、摘要、关键词和研究方法的格式化文献清单。

**输出格式**：

```markdown
# 文献清单

## 检索信息
- 关键词：[使用的关键词组合]
- 数据库：[Semantic Scholar / Google Scholar]
- 年份范围：[年份范围]
- 结果总数：[数量]

## 文献列表

1. **[中文标题翻译]**
   - 原标题：[英文标题]
   - 作者：[作者列表]
   - 年份：[发表年份]
   - 期刊/会议：[期刊或会议名称]
   - DOI：[DOI或稳定链接]
   - 引用次数：[引用次数]
   - 研究方法：[识别的方法，如"野外调查（样线法）、多元统计（CCA）"]
   - 关键词：[提取或生成的关键词]
   - 摘要（中文）：[摘要的中文翻译]
   - URL：[论文链接]

2. **[下一篇论文...]**
   ...
```

**处理步骤**：

1. **翻译标题**：将英文标题翻译为中文（准确、学术风格）
2. **翻译摘要**：将摘要翻译为中文（保留专业术语）
3. **提取/生成关键词**：
   - 如果元数据中有关键词则使用
   - 否则从标题和摘要中提取核心概念
   - 每篇论文通常3-5个关键词
4. **识别研究方法**：
   - 分析摘要和标题识别使用的方法
   - 查阅 `references/research-methods.md` 进行方法分类
   - 每篇论文列出1-3个主要方法
5. **格式化输出**：使用上述模板，确保一致性

**质量控制**：
- 验证翻译准确自然
- 确保识别的方法与论文内容匹配
- 检查DOI链接有效
- 删除重复条目

**交付**：向用户展示格式化的清单。说明这是基于标题和摘要的初步筛选，用户仍需阅读全文。

## 使用脚本

### 脚本位置
- `scripts/search_literature.py` - Semantic Scholar检索
- `scripts/search_google_scholar.py` - Google Scholar检索

### 环境设置

**Semantic Scholar**：
- 无需依赖（使用标准库）
- 可选：设置 `SEMANTIC_SCHOLAR_API_KEY` 环境变量以获得更高的速率限制

**Google Scholar**：
- 需要 `scholarly` 库：`pip install scholarly`
- 可能需要代理以提高稳定性（出于隐私考虑不推荐）

### 故障排除

**API选择建议**：
- 如果不确定使用哪个API，优先推荐Semantic Scholar
- 如果用户没有API密钥且遇到速率限制，建议使用WebSearch
- 如果需要更广泛的覆盖面，可以组合使用多个检索方式

**Semantic Scholar问题**：
- 速率限制（429错误）：
  - 建议用户使用WebSearch作为替代方案
  - 或询问用户是否有API密钥
  - 或等待后重试
- 网络错误：检查网络连接，使用更长的超时时间重试

**Google Scholar问题**：
- 验证码/速率限制：切换到Semantic Scholar或WebSearch
- 库未找到：使用 `pip install scholarly` 安装

**WebSearch问题**：
- 结果格式不统一：需要额外处理和格式化
- 信息不够详细：可能需要补充使用其他API
- 建议作为快速检索或备用方案使用

## 使用参考资料

### 何时加载参考资料

**`references/intent-alignment.md`**：在阶段1加载，以访问问题模板和对话策略。

**`references/ecology-subfields.md`**：在阶段2识别用户研究领域时加载，或在阶段4为文献解读提供领域背景时加载。

**`references/research-methods.md`**：在阶段4从论文摘要中识别研究方法时加载。

### 渐进式加载

不要一次性加载所有参考资料。根据当前阶段按需加载：
- 阶段1：如需要问题设计，加载 `intent-alignment.md`
- 阶段2：加载 `ecology-subfields.md` 和 `research-methods.md` 用于关键词生成
- 阶段4：加载 `research-methods.md` 用于方法识别

## 注意事项

- **聚焦元数据**：脚本仅检索元数据（标题、摘要等），不包含全文。用户需要通过机构或开放获取渠道获取全文。
- **初步筛选**：生成的清单用于初步筛选。用户在引用前应阅读全文。
- **迭代优化**：如果初始结果不足，可以优化关键词后再次检索。
- **维护参考资料**：参考资料文件设计为可演进的。用户可以根据使用经验添加新的子领域、方法或问题模板。
