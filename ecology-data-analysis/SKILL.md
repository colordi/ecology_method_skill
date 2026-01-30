---
name: ecology-data-analysis
description: "生态学数据分析助手，通过四阶段工作流程生成专业 Quarto PDF 报告。"
---

# 生态学数据分析

## 概述

本 skill 通过四阶段工作流程指导生态学数据分析，生成包含 R 代码、统计结果和生态学解释的专业 Quarto 报告。

## 工作流程

### 阶段 1：意图对齐

**目标**：理解用户的数据和研究目标

**操作**：
1. 阅读 `references/intent-questions.md` 获取提问框架
2. 使用 `references/analysis-methods.md` 识别合适的分析方法

### 阶段 2：结构冻结

**目标**：创建分析大纲

**操作**：
1. 复制 `assets/analysis_report_template.qmd` 作为起点
2. 根据阶段 1 定制模板，保存为 .qmd 文件

### 阶段 3：渐进式分析

**目标**：逐步执行分析并填入报告

**关键原则**：
- **先执行后解释**：用 `Rscript` 执行代码获取实际结果，再编写解释（详见 `references/code-execution-guide.md`）
- **变量引用**：正文数值必须通过内联 R 代码引用变量，禁止硬编码（详见 `references/inline-code-guide.md`）
- **表格生成**：描述性统计表、组间比较表、回归结果表**必须**使用 gtsummary 包生成（详见 `references/tables-guide.md`）
- **逐章节进行**：每章节经过"执行→讨论→填充→确认"循环
- **文本为主**：优先撰写文字说明，代码默认隐藏

**操作**：
1. 阅读 `references/content-generation-guide.md` 了解章节结构
2. 用 `Rscript -e "代码"` 执行分析，**验证**结果正确性
3. 在 qmd 代码块中保存关键统计量为变量
4. 正文使用 `` `r variable` `` 引用变量，**禁止**硬编码数值
5. 使用 `references/interpretation-guide.md` 解释结果

### 阶段 4：渲染与检查

**目标**：生成符合规范的 PDF 报告

**操作**：
1. 阅读 `references/rendering-guide.md` 了解渲染规范
2. 按检查清单核对表格、图表、字体配置
3. 执行 `quarto render xxx.qmd --to pdf` 渲染
4. 根据错误信息修正问题

> [!CAUTION]
> **核心禁止项**（详见 `references/rendering-guide.md`）：
> - ❌ 严禁生成 HTML 格式
> - ❌ 严禁手动编号 Markdown 标题
> - ❌ 严禁在表格中使用 `full_width=TRUE`
> - ❌ 严禁省略 `format = "latex"` 参数
> - ❌ 严禁在正文中硬编码数值（必须用 `` `r var` `` 引用）
> - ❌ 严禁手动编号图表（必须用 `@fig-xxx`、`@tbl-xxx` 交叉引用）

## 资源

### references/
- `rendering-guide.md`：PDF渲染规范（表格、图表、字体、交叉引用）
- `tables-guide.md`：gtsummary 表格生成模板
- `inline-code-guide.md`：内联代码与变量引用规范
- `code-execution-guide.md`：Rscript 代码执行方法
- `content-generation-guide.md`：分析章节结构指南
- `intent-questions.md`：意图对齐提问框架
- `analysis-methods.md`：分析方法选择决策树
- `interpretation-guide.md`：结果解释指南
- `r-packages.md`：推荐 R 包

### assets/
- `analysis_report_template.qmd`：Quarto 报告模板
