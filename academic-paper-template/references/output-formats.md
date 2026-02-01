# 输出格式配置指南

## 概述

Quarto支持多种输出格式，每种格式都有其特定的用途和配置选项。本文档详细说明如何配置PDF、Word和HTML输出。

## PDF输出

PDF是学术论文最常用的格式，适合打印和正式提交。

### 基础配置

```yaml
format:
  pdf:
    pdf-engine: xelatex  # 支持中文的引擎
    toc: true            # 生成目录
    toc-depth: 3         # 目录深度
    number-sections: true # 章节编号
    colorlinks: true     # 彩色链接
```

### 页面设置

```yaml
format:
  pdf:
    geometry:
      - top=2.5cm
      - bottom=2.5cm
      - left=3cm
      - right=3cm
    papersize: a4
    fontsize: 12pt
```

### 字体配置

```yaml
format:
  pdf:
    mainfont: "Songti SC"      # 主字体
    CJKmainfont: "Songti SC"   # 中文字体
    monofont: "Courier New"    # 等宽字体（代码）
```

### 文档类别

```yaml
format:
  pdf:
    documentclass: article  # 或 report, book
    classoption:
      - twocolumn  # 双栏（可选）
```

## Word输出

Word格式便于协作编辑和审阅。

### 基础配置

```yaml
format:
  docx:
    toc: true
    number-sections: true
    highlight-style: github
```

### 使用参考文档

可以使用自定义的Word模板来控制样式：

```yaml
format:
  docx:
    reference-doc: custom-template.docx
```

### 图表设置

```yaml
format:
  docx:
    fig-width: 6
    fig-height: 4
    fig-dpi: 300
```

## HTML输出

HTML格式适合在线分享和交互式内容。

### 基础配置

```yaml
format:
  html:
    toc: true
    toc-location: left
    number-sections: true
    code-fold: true        # 代码折叠
    code-tools: true       # 代码工具栏
```

### 主题设置

```yaml
format:
  html:
    theme: cosmo  # 或 flatly, journal, etc.
    css: custom.css
```

### 交互式功能

```yaml
format:
  html:
    code-fold: true
    code-summary: "显示代码"
    code-overflow: wrap
    embed-resources: true  # 生成单个HTML文件
```

## 多格式输出

可以在一个文档中配置多种输出格式：

```yaml
format:
  pdf:
    pdf-engine: xelatex
    toc: true
    mainfont: "Songti SC"
  docx:
    toc: true
    reference-doc: template.docx
  html:
    toc: true
    theme: cosmo
```

渲染特定格式：

```bash
quarto render document.qmd --to pdf
quarto render document.qmd --to docx
quarto render document.qmd --to html
```

## 表格格式化

不同输出格式需要不同的表格处理：

### PDF表格

```r
# 使用kableExtra
library(kableExtra)

data %>%
  kable(format = "latex", booktabs = TRUE) %>%
  kable_styling(latex_options = c("hold_position", "striped"))
```

### Word/HTML表格

```r
# 使用kable
data %>%
  kable(format = "html") %>%
  kable_styling(bootstrap_options = c("striped", "hover"))
```

### 通用表格（gtsummary）

```r
# gtsummary自动适配输出格式
library(gtsummary)

data %>%
  tbl_summary() %>%
  as_kable()  # 自动检测输出格式
```

## 图片格式化

### 图片尺寸

```yaml
execute:
  fig-width: 8
  fig-height: 6
  fig-dpi: 300
```

### 图片标题

在代码块中设置：

```r
#| fig-cap: "这是图片标题"
#| label: fig-example

plot(x, y)
```

### 多图布局

```r
#| layout-ncol: 2
#| fig-cap:
#|   - "图A"
#|   - "图B"

plot1
plot2
```

## 引用和参考文献

### 配置文献库

```yaml
bibliography: references.bib
csl: ecology.csl  # 引用格式
```

### 常用引用格式

- `ecology.csl` - Ecology期刊格式
- `nature.csl` - Nature期刊格式
- `apa.csl` - APA格式
- `chicago.csl` - Chicago格式

下载CSL文件：https://www.zotero.org/styles

## 交叉引用

### 章节引用

```markdown
见 @sec-methods 部分
```

### 图表引用

```markdown
如 @fig-example 所示
见 @tbl-results
```

### 公式引用

```markdown
根据公式 @eq-model
```

## 输出优化建议

### PDF优化

1. 使用矢量图（PDF/SVG）而非位图
2. 设置合适的DPI（300用于打印）
3. 使用专业的表格包（booktabs）
4. 避免过宽的表格

### Word优化

1. 使用参考文档统一样式
2. 避免复杂的LaTeX公式
3. 简化表格格式
4. 测试在不同Word版本中的兼容性

### HTML优化

1. 启用代码折叠提高可读性
2. 使用embed-resources生成独立文件
3. 优化图片大小
4. 考虑响应式设计

## 常见问题

### 问题1：PDF中表格超出页面

**解决方案：**
```r
kable(...) %>%
  kable_styling(latex_options = "scale_down")
```

### 问题2：Word中公式显示异常

**解决方案：**
使用简单的LaTeX语法，或考虑使用图片

### 问题3：HTML文件过大

**解决方案：**
```yaml
format:
  html:
    embed-resources: false
    self-contained: false
```

## 格式选择建议

| 用途 | 推荐格式 | 原因 |
|------|---------|------|
| 期刊投稿 | PDF | 专业、格式稳定 |
| 协作编辑 | Word | 易于修改和批注 |
| 在线分享 | HTML | 交互性强、易访问 |
| 打印 | PDF | 高质量输出 |
| 初稿 | HTML | 快速预览 |
