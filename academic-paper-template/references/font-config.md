# 跨平台中文字体配置指南

## 概述

在Quarto文档中正确配置中文字体对于生成高质量的PDF输出至关重要。不同操作系统有不同的默认中文字体，本文档提供跨平台的配置方案。

## 平台特定配置

### macOS

macOS系统自带优质的中文字体，推荐使用：

```yaml
format:
  pdf:
    pdf-engine: xelatex
    mainfont: "Songti SC"
    CJKmainfont: "Songti SC"
```

**可选字体：**
- `Songti SC` - 宋体（衬线字体，适合正文）
- `Heiti SC` - 黑体（无衬线字体，适合标题）
- `Kaiti SC` - 楷体（手写风格）
- `STHeiti Light` - 华文黑体（较细）

### Windows

Windows系统推荐使用：

```yaml
format:
  pdf:
    pdf-engine: xelatex
    mainfont: "SimSun"
    CJKmainfont: "SimSun"
```

**可选字体：**
- `SimSun` - 宋体（最常用）
- `SimHei` - 黑体
- `KaiTi` - 楷体
- `Microsoft YaHei` - 微软雅黑（现代感）

### Linux

Linux系统需要安装中文字体包，推荐使用Noto字体：

```bash
# Ubuntu/Debian
sudo apt-get install fonts-noto-cjk

# Fedora/RHEL
sudo dnf install google-noto-sans-cjk-fonts
```

配置：

```yaml
format:
  pdf:
    pdf-engine: xelatex
    mainfont: "Noto Serif CJK SC"
    CJKmainfont: "Noto Serif CJK SC"
```

**可选字体：**
- `Noto Serif CJK SC` - 衬线字体
- `Noto Sans CJK SC` - 无衬线字体

## R代码块中的字体配置

对于ggplot2图表，需要在R代码中配置字体：

### 使用showtext包（推荐）

```r
library(showtext)

# macOS
font_add("cjk", regular = "/System/Library/Fonts/STHeiti Light.ttc")

# Windows
font_add("cjk", regular = "C:/Windows/Fonts/simhei.ttf")

# Linux
font_add("cjk", regular = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc")

showtext_auto()

# 设置ggplot2主题
theme_set(theme_minimal(base_family = "cjk"))
```

### 使用extrafont包（备选）

```r
library(extrafont)
font_import()  # 首次使用需要导入字体
loadfonts()

# 设置ggplot2主题
theme_set(theme_minimal(base_family = "STHeiti"))  # macOS
# theme_set(theme_minimal(base_family = "SimHei"))  # Windows
```

## 通用配置模板

如果需要跨平台兼容，可以在模板中提供注释说明：

```yaml
format:
  pdf:
    pdf-engine: xelatex
    # 根据您的操作系统选择合适的字体：
    # macOS: "Songti SC" 或 "Heiti SC"
    # Windows: "SimSun" 或 "SimHei"
    # Linux: "Noto Serif CJK SC" 或 "Noto Sans CJK SC"
    mainfont: "Songti SC"
    CJKmainfont: "Songti SC"
```

## 常见问题

### 问题1：PDF生成失败，提示字体找不到

**解决方案：**
1. 检查字体名称是否正确（区分大小写）
2. 使用系统字体查看器确认字体名称
3. 尝试使用字体文件的完整路径

### 问题2：图表中的中文显示为方框

**解决方案：**
1. 确保在R代码块中配置了字体（使用showtext或extrafont）
2. 设置 `fig.showtext = TRUE` 在chunk选项中
3. 检查字体是否正确加载

### 问题3：不同平台生成的PDF字体不一致

**解决方案：**
1. 使用跨平台字体（如Noto CJK系列）
2. 在项目中包含字体文件并使用相对路径
3. 在文档中说明推荐的字体配置

## 字体测试

生成模板后，可以使用以下简单文档测试字体配置：

```markdown
---
title: "字体测试"
format:
  pdf:
    pdf-engine: xelatex
    mainfont: "Songti SC"
---

# 中文标题测试

这是正文测试：中文、English、数字123。

**粗体测试**、*斜体测试*
```

运行 `quarto render test.qmd` 检查输出是否正常。
