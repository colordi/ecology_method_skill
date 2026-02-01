# Quarto使用指南

## 目录

1. [什么是Quarto](#什么是quarto)
2. [安装与配置](#安装与配置)
3. [基本使用](#基本使用)
4. [图表与引用](#图表与引用)
5. [文档渲染](#文档渲染)
6. [中文支持配置](#中文支持配置)
7. [R包安装](#r包安装)
8. [常见问题](#常见问题)
9. [其他进阶技巧](#其他进阶技巧)

---

## 什么是Quarto

Quarto是新一代的科学和技术出版系统，是R Markdown的继任者。它支持：

- **多种编程语言**：R、Python、Julia、Observable JS
- **多种输出格式**：PDF、HTML、Word、PPT、网站、书籍等
- **优秀的中文支持**：通过XeLaTeX引擎完美支持中文
- **现代化工具**：独立于RStudio，可在任何编辑器中使用

**为什么选择Quarto？**
- 文档、代码、结果融合在一起，确保可重复性
- 自动生成图表编号和交叉引用
- 专业的学术论文排版
- 易于版本控制（纯文本格式）

---

## 安装与配置

### 第一步：安装Quarto

#### Windows系统

1. 访问Quarto官网：https://quarto.org/docs/get-started/
2. 下载Windows安装包（.msi文件）
3. 双击安装包，按照提示完成安装
4. 验证安装：
   ```bash
   quarto --version
   ```

#### macOS系统

**方法1：使用安装包**
1. 下载macOS安装包（.pkg文件）
2. 双击安装
3. 验证安装

**方法2：使用Homebrew**
```bash
brew install quarto
```

#### Linux系统

**Ubuntu/Debian:**
```bash
# 下载deb包
wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.4.550/quarto-1.4.550-linux-amd64.deb

# 安装
sudo dpkg -i quarto-1.4.550-linux-amd64.deb
```

**Fedora/RHEL:**
```bash
# 下载rpm包
wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.4.550/quarto-1.4.550-linux-amd64.rpm

# 安装
sudo dnf install quarto-1.4.550-linux-amd64.rpm
```

### 第二步：安装LaTeX（用于PDF输出）

Quarto生成PDF需要LaTeX引擎。推荐使用TinyTeX（轻量级）：

```bash
quarto install tinytex
```

这个命令会自动下载和安装TinyTeX，包含生成PDF所需的所有组件。

**验证LaTeX安装：**
```bash
quarto check
```

### 第三步：安装R和RStudio（可选但推荐）

如果模板中包含R代码，需要安装R：

#### 安装R

- **Windows/macOS**: 访问 https://cran.r-project.org/
- **Linux**:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install r-base

  # Fedora/RHEL
  sudo dnf install R
  ```

#### 安装RStudio（可选）

RStudio提供了友好的Quarto编辑界面：
- 访问 https://posit.co/download/rstudio-desktop/
- 下载并安装适合您系统的版本

### 第四步：安装VS Code扩展（可选）

如果使用VS Code编辑器：

1. 安装VS Code
2. 安装Quarto扩展：在扩展市场搜索"Quarto"
3. 安装后可以在VS Code中预览和渲染Quarto文档

---

## 基本使用

### Quarto文档结构

一个典型的.qmd文件包含三部分：

````markdown
---
title: "我的论文"
author: "张三"
format: pdf
---

# 这是标题

这是正文内容。

```{r}
# 这是R代码块
plot(1:10)
```
````

**三个组成部分：**

1. **YAML头部**（`---`之间）：配置文档元数据和输出格式
2. **Markdown文本**：正文内容
3. **代码块**：可执行的代码（R、Python等）

### 代码块语法

**R代码块：**
````markdown
```{r}
# R代码
x <- 1:10
mean(x)
```
````

**Python代码块：**
````markdown
```{python}
# Python代码
import numpy as np
x = np.array([1, 2, 3])
```
````

**代码块选项：**
````markdown
```{r}
#| label: fig-plot
#| fig-cap: "这是图表标题"
#| echo: false
#| warning: false

plot(1:10)
```
````

常用选项：
- `echo: false` - 隐藏代码，只显示结果
- `warning: false` - 隐藏警告信息
- `message: false` - 隐藏消息
- `fig-cap: "标题"` - 图表标题
- `fig-width: 8` - 图表宽度
- `fig-height: 6` - 图表高度

---

## 图表与引用

这是学术论文写作中最重要的部分！Quarto可以自动为图表编号，并支持交叉引用。

### 生成并引用图表

**第一步：创建带标签的图表**

使用 `label` 和 `fig-cap` 选项：

````markdown
```{r}
#| label: fig-scatter
#| fig-cap: "身高与体重的关系"
#| fig-width: 6
#| fig-height: 4

library(ggplot2)
ggplot(mtcars, aes(x = wt, y = mpg)) +
  geom_point() +
  labs(x = "车重 (1000 lbs)", y = "油耗 (mpg)")
```
````

**第二步：在正文中引用**

```markdown
如@fig-scatter所示，车重与油耗呈负相关关系。
```

**重要提示：**
- `label` 必须以 `fig-` 开头
- 引用时使用 `@fig-scatter` 格式
- PDF会自动生成"Figure 1"、"Figure 2"等编号

### 生成并引用表格

**第一步：创建带标签的表格**

````markdown
```{r}
#| label: tbl-summary
#| tbl-cap: "汽车数据描述性统计"

library(gtsummary)
mtcars %>%
  select(mpg, cyl, wt) %>%
  tbl_summary(
    statistic = all_continuous() ~ "{mean} ({sd})"
  ) %>%
  as_kable(format = "latex", booktabs = TRUE)
```
````

**第二步：在正文中引用**

```markdown
@tbl-summary展示了主要变量的描述性统计结果。
```

**重要提示：**
- `label` 必须以 `tbl-` 开头
- 引用时使用 `@tbl-summary` 格式
- 使用 `as_kable(format = "latex")` 确保PDF格式正确

### 完整的最小可运行例子

下面是一个完整的示例，包含图表、表格和引用。您可以直接复制使用：

````markdown
---
title: "图表引用示例"
author: "您的姓名"
format:
  pdf:
    pdf-engine: xelatex
    mainfont: "Songti SC"  # macOS
    # mainfont: "SimSun"   # Windows
execute:
  echo: false
  warning: false
---

# 引言

本文展示如何在Quarto中生成和引用图表。

# 方法

我们使用R语言的mtcars数据集进行分析。@tbl-data展示了数据的基本统计信息。

```{r}
#| label: tbl-data
#| tbl-cap: "数据描述性统计"

library(tidyverse)
library(knitr)

mtcars %>%
  select(mpg, cyl, wt) %>%
  summary() %>%
  kable(format = "latex", booktabs = TRUE)
```

# 结果

@fig-relationship展示了车重与油耗之间的关系。

```{r}
#| label: fig-relationship
#| fig-cap: "车重与油耗的关系"
#| fig-width: 5
#| fig-height: 4

library(ggplot2)
ggplot(mtcars, aes(x = wt, y = mpg)) +
  geom_point(size = 3, alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE) +
  labs(x = "车重 (1000 lbs)", y = "油耗 (mpg)") +
  theme_minimal()
```

从@fig-relationship可以看出，车重与油耗呈显著负相关。

# 结论

本文展示了Quarto中图表引用的基本用法。
````

**使用方法：**
1. 将上述内容保存为 `example.qmd`
2. 确保已安装R包：`install.packages(c("tidyverse", "knitr", "ggplot2"))`
3. 运行：`quarto render example.qmd`
4. 查看生成的PDF文件

---

## 文档渲染

### 基本渲染命令

在终端/命令行中，进入文档所在目录，然后运行：

```bash
# 渲染为默认格式（YAML中指定的格式）
quarto render document.qmd

# 渲染为特定格式
quarto render document.qmd --to pdf
quarto render document.qmd --to html
quarto render document.qmd --to docx
```

### 在RStudio中渲染

1. 打开.qmd文件
2. 点击工具栏的"Render"按钮（或按Ctrl+Shift+K）
3. 文档会自动渲染并预览

### 在VS Code中渲染

1. 打开.qmd文件
2. 按Ctrl+Shift+K（或点击右上角的"Preview"按钮）
3. 预览窗口会显示渲染结果

### 实时预览

```bash
# 启动预览服务器，文件修改后自动重新渲染
quarto preview document.qmd
```

这会在浏览器中打开预览，每次保存文件时自动更新。

---

## 中文支持配置

### PDF中文支持

生成中文PDF需要配置XeLaTeX引擎和中文字体：

```yaml
format:
  pdf:
    pdf-engine: xelatex
    mainfont: "Songti SC"        # macOS
    # mainfont: "SimSun"         # Windows
    # mainfont: "Noto Serif CJK SC"  # Linux
    CJKmainfont: "Songti SC"
```

### 常见中文字体

**macOS:**
- `Songti SC` - 宋体（衬线）
- `Heiti SC` - 黑体（无衬线）
- `Kaiti SC` - 楷体

**Windows:**
- `SimSun` - 宋体
- `SimHei` - 黑体
- `KaiTi` - 楷体
- `Microsoft YaHei` - 微软雅黑

**Linux:**
- `Noto Serif CJK SC` - 思源宋体
- `Noto Sans CJK SC` - 思源黑体

### 检查可用字体

**macOS/Linux:**
```bash
fc-list :lang=zh
```

**Windows:**
打开"字体"设置查看已安装的中文字体。

### 中文字体问题排查

如果PDF生成失败，提示字体找不到：

1. 确认字体名称正确（区分大小写）
2. 使用系统字体查看器确认字体名称
3. 尝试使用字体文件的完整路径
4. 安装推荐的字体包（如Noto CJK）

---

## R包安装

模板中使用的R代码需要安装相应的R包。

### 安装必需的R包

在R或RStudio中运行：

```r
# 安装基础包
install.packages(c(
  "tidyverse",    # 数据处理和可视化
  "knitr",        # 文档编译
  "rmarkdown"     # Markdown支持
))

# 安装表格相关包
install.packages(c(
  "gtsummary",    # 专业统计表格
  "kableExtra",   # 表格样式控制
  "gt",           # 现代表格包
  "flextable"     # 灵活的表格
))

# 安装中文字体支持
install.packages("showtext")

# 安装其他常用包
install.packages(c(
  "ggplot2",      # 高级绘图
  "dplyr",        # 数据处理
  "readr",        # 数据读取
  "here"          # 路径管理
))
```

### 检查包是否安装成功

```r
# 检查单个包
library(tidyverse)

# 检查所有包
packages <- c("tidyverse", "gtsummary", "knitr", "kableExtra", "showtext")
sapply(packages, require, character.only = TRUE)
```

### 包安装问题排查

**问题1：安装失败，提示需要编译工具**

- **Windows**: 安装Rtools (https://cran.r-project.org/bin/windows/Rtools/)
- **macOS**: 安装Xcode Command Line Tools (`xcode-select --install`)
- **Linux**: 安装build-essential (`sudo apt-get install build-essential`)

**问题2：包版本冲突**

```r
# 更新所有包
update.packages(ask = FALSE)

# 重新安装特定包
remove.packages("包名")
install.packages("包名")
```

**问题3：网络问题导致下载失败**

```r
# 更换CRAN镜像
options(repos = c(CRAN = "https://mirrors.tuna.tsinghua.edu.cn/CRAN/"))

# 然后重新安装
install.packages("包名")
```

---

## 常见问题

### 问题1：渲染PDF失败，提示"LaTeX Error"

**可能原因：**
- LaTeX未安装或安装不完整
- 缺少必要的LaTeX包

**解决方案：**
```bash
# 重新安装TinyTeX
quarto install tinytex

# 或者更新TinyTeX
quarto update tinytex

# 检查LaTeX安装
quarto check
```

### 问题2：中文显示为方框或乱码

**可能原因：**
- 字体配置错误
- 未使用XeLaTeX引擎

**解决方案：**
1. 确认YAML中配置了`pdf-engine: xelatex`
2. 检查字体名称是否正确
3. 确认系统已安装指定的中文字体

### 问题3：图表中的中文显示异常

**可能原因：**
- R代码块中未配置中文字体

**解决方案：**
在setup代码块中添加：
```r
library(showtext)
font_add("cjk", regular = "字体路径")
showtext_auto()
theme_set(theme_minimal(base_family = "cjk"))
```

并在chunk选项中设置：
```markdown
```{r}
#| fig.showtext: true
```
```

### 问题4：表格格式不正确

**可能原因：**
- 表格包使用不当
- 输出格式不匹配

**解决方案：**
使用gtsummary时，确保转换为正确的格式：
```r
# PDF输出
table %>%
  as_kable(format = "latex", booktabs = TRUE)

# HTML输出
table %>%
  as_kable(format = "html")
```

### 问题5：代码块执行失败

**可能原因：**
- R包未安装
- 代码路径错误
- 工作目录不正确

**解决方案：**
```r
# 检查工作目录
getwd()

# 使用here包管理路径
library(here)
data <- read_csv(here("data", "file.csv"))
```

### 问题6：渲染速度很慢

**可能原因：**
- 每次都重新执行所有代码
- 数据量大或计算复杂

**解决方案：**
使用缓存功能：
````markdown
```{r}
#| cache: true

# 耗时的计算
```
````

### 问题7：无法生成Word文档

**可能原因：**
- 系统未安装Microsoft Word或LibreOffice

**解决方案：**
Quarto生成docx不需要安装Word，但需要pandoc（Quarto自带）。如果仍然失败：
```bash
# 检查pandoc
quarto check

# 尝试简单文档
quarto render test.qmd --to docx
```

---

## 其他进阶技巧

### 交叉引用

Quarto支持自动编号和交叉引用：

**图表引用：**
````markdown
```{r}
#| label: fig-scatter
#| fig-cap: "散点图示例"

plot(x, y)
```

如@fig-scatter所示...
````

**表格引用：**
````markdown
```{r}
#| label: tbl-summary
#| tbl-cap: "描述性统计表"

kable(data)
```

见@tbl-summary...
````

**章节引用：**
```markdown
# 方法 {#sec-methods}

详见@sec-methods部分...
```

### 参数化报告

创建可重复使用的模板：

```yaml
---
title: "参数化报告"
params:
  year: 2024
  region: "华东"
---

本报告分析`r params$year`年`r params$region`地区的数据。
```

渲染时指定参数：
```bash
quarto render report.qmd -P year:2023 -P region:华南
```

### 使用参考文献

**配置文献库：**
```yaml
---
bibliography: references.bib
csl: ecology.csl
---
```

**引用文献：**
```markdown
根据研究[@smith2020]，我们发现...

多个引用[@smith2020; @jones2021]
```

**生成.bib文件：**
使用Zotero等文献管理软件导出BibTeX格式。

### 多格式输出

在一个文档中配置多种输出格式：

```yaml
format:
  pdf:
    toc: true
    number-sections: true
  html:
    theme: cosmo
    code-fold: true
  docx:
    reference-doc: template.docx
```

### 使用模板

创建自定义模板：

```bash
# 创建项目
quarto create-project myproject

# 使用模板
quarto use template username/template-name
```

### 代码折叠

在HTML输出中添加代码折叠功能：

```yaml
format:
  html:
    code-fold: true
    code-summary: "显示代码"
```

### 嵌入交互式内容

**Plotly交互图表：**
```r
library(plotly)
plot_ly(data, x = ~x, y = ~y, type = "scatter")
```

**DT交互表格：**
```r
library(DT)
datatable(data)
```

### 使用子文档

将大型文档拆分为多个文件：

```markdown
# 主文档

{{< include _introduction.qmd >}}
{{< include _methods.qmd >}}
{{< include _results.qmd >}}
```

### 自定义CSS样式

为HTML输出添加自定义样式：

```yaml
format:
  html:
    css: custom.css
```

### 使用Lua过滤器

扩展Quarto功能：

```yaml
filters:
  - custom-filter.lua
```

---

## 快速参考

### 常用命令

```bash
# 渲染文档
quarto render document.qmd

# 预览文档
quarto preview document.qmd

# 检查安装
quarto check

# 查看版本
quarto --version

# 查看帮助
quarto --help
```

### 常用YAML配置

```yaml
---
title: "标题"
author: "作者"
date: "2024-01-01"
format:
  pdf:
    toc: true
    number-sections: true
    colorlinks: true
  html:
    theme: cosmo
    code-fold: true
execute:
  echo: false
  warning: false
  message: false
---
```

### 常用代码块选项

````markdown
```{r}
#| label: chunk-name
#| echo: false
#| warning: false
#| message: false
#| fig-cap: "图表标题"
#| fig-width: 8
#| fig-height: 6
#| cache: true
```
````

---

## 学习资源

### 官方文档

- **Quarto官网**: https://quarto.org/
- **Quarto指南**: https://quarto.org/docs/guide/
- **Quarto参考**: https://quarto.org/docs/reference/

### 中文资源

- **Quarto中文教程**: 搜索"Quarto中文教程"
- **R Markdown中文书**: https://bookdown.org/yihui/rmarkdown/

### 社区支持

- **GitHub讨论**: https://github.com/quarto-dev/quarto-cli/discussions
- **Stack Overflow**: 搜索"quarto"标签
- **RStudio社区**: https://community.rstudio.com/

---

## 总结

使用Quarto创建学术论文的基本流程：

1. **安装环境**：Quarto + LaTeX + R
2. **获取模板**：使用academic-paper-template skill
3. **编辑内容**：填写YAML配置和正文
4. **添加代码**：插入R代码块进行分析
5. **渲染文档**：`quarto render document.qmd`
6. **检查输出**：查看生成的PDF/HTML/Word文档
7. **迭代修改**：根据需要调整内容和格式

**记住：**
- 保持文档结构清晰
- 使用有意义的代码块标签
- 定期保存和备份
- 利用版本控制（Git）
- 参考官方文档解决问题

祝您使用Quarto愉快！
