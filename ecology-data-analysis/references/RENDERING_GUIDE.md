# 生态学数据分析报告渲染规范

本文档定义了使用本项目模板生成PDF报告时必须遵循的规范，确保每次渲染都能成功且效果一致。

## 1. 表格样式规范

### 1.1 基本原则

**必须遵守**：
- ✅ 使用默认表格宽度，让LaTeX自动处理
- ✅ 使用 `kable()` + `kable_styling()` 组合
- ✅ 使用 `latex_options = c("striped", "hold_position")`
- ✅ 使用 `as_kable()` 转换 gtsummary 表格

**禁止使用**：
- ❌ 不要使用 `full_width = TRUE`
- ❌ 不要使用 `scale_down`
- ❌ 不要手动指定表格宽度参数
- ❌ 不要在caption中添加"表 x"或"Table x"编号

### 1.2 标准代码模板

#### 普通表格
```r
kable(data,
      caption = "表格标题",
      align = "c") %>%
  kable_styling(latex_options = c("striped", "hold_position"))
```

#### gtsummary表格
```r
data %>%
  tbl_summary(
    by = 分组变量,
    statistic = list(all_continuous() ~ "{mean} ({sd})")
  ) %>%
  add_p() %>%
  add_overall() %>%
  modify_header(label ~ "**变量**") %>%
  bold_labels() %>%
  as_kable(caption = "描述性统计表") %>%
  kable_styling(latex_options = c("striped", "hold_position"))
```

### 1.3 为什么这样做

**问题**：使用 `full_width = TRUE` 或 `scale_down` 会导致LaTeX计算表格尺寸时出现"Dimension too large"错误，导致PDF渲染失败。

**解决方案**：使用默认宽度让LaTeX根据内容自动调整表格大小，避免维度计算错误。


## 2. 图表样式规范

### 2.1 基本原则

**必须遵守**：
- ✅ 使用 `fig.cap` 参数添加图表标题
- ✅ 使用 `fig.width` 和 `fig.height` 控制图表尺寸
- ✅ 使用 `fig.showtext = TRUE` 确保中文字体正确显示
- ✅ 设置 `dpi = 300` 确保图表清晰度

**禁止使用**：
- ❌ 不要在 `fig.cap` 中添加"图 x"或"Figure x"编号
- ❌ 不要在代码中使用 `ggtitle()` 添加标题（应使用 `fig.cap`）

### 2.2 标准代码模板

```r
```{r plot-name, fig.cap="图表标题", fig.width=8, fig.height=6}
ggplot(data, aes(x = x_var, y = y_var)) +
  geom_point() +
  labs(
    x = "X轴标签",
    y = "Y轴标签"
  ) +
  theme_minimal(base_family = "cjk")
```
```

### 2.3 为什么这样做

- PDF会自动为图表添加"Figure 1:", "Figure 2:"等编号前缀
- 使用 `fig.cap` 而不是 `ggtitle()` 可以让图表标题出现在图表下方，符合学术规范
- `fig.showtext = TRUE` 确保showtext包正确渲染中文字体


## 3. 字体配置规范

### 3.1 基本原则

**必须遵守**：
- ✅ 使用 showtext 包处理中文字体
- ✅ 根据操作系统自动选择字体路径
- ✅ 在 setup chunk 中配置字体
- ✅ 使用 `showtext_auto()` 启用自动渲染
- ✅ 设置 `fig.showtext = TRUE` 全局选项

### 3.2 标准配置代码

```r
library(showtext)

# 根据操作系统自动添加系统中文字体
if (Sys.info()["sysname"] == "Darwin") {  # macOS
  font_add("cjk", regular = "/System/Library/Fonts/Supplemental/Songti.ttc")
} else if (Sys.info()["sysname"] == "Windows") {
  font_add("cjk", regular = "C:/Windows/Fonts/simsun.ttc")
} else {  # Linux
  font_add("cjk", regular = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
}

showtext_auto()

# 设置 ggplot2 默认主题使用中文字体
theme_set(theme_minimal(base_family = "cjk"))

# 设置全局选项
knitr::opts_chunk$set(
  fig.showtext = TRUE  # 启用showtext渲染
)
```

### 3.3 YAML配置

```yaml
format:
  pdf:
    pdf-engine: xelatex
    mainfont: "Songti SC"
    CJKmainfont: "Songti SC"
```

### 3.4 为什么这样做

- showtext包可以在所有操作系统上一致地处理中文字体
- 自动检测操作系统确保跨平台兼容性
- xelatex引擎支持Unicode和中文字体


## 4. 常见问题和解决方案

### 4.1 LaTeX "Dimension too large" 错误

**症状**：
```
Dimension too large.
I can't work with sizes bigger than about 19 feet.
```

**原因**：表格宽度设置（`full_width = TRUE` 或 `scale_down`）导致LaTeX无法正确计算表格尺寸。

**解决方案**：
- 移除所有 `full_width = TRUE` 和 `scale_down` 参数
- 使用默认宽度：`kable_styling(latex_options = c("striped", "hold_position"))`

### 4.2 中文字体不显示

**症状**：PDF中中文显示为方框或乱码。

**原因**：未正确配置中文字体或showtext包。

**解决方案**：
- 确保安装了 showtext 包
- 按照第3节配置字体
- 确保 `fig.showtext = TRUE` 已设置

### 4.3 gtsummary表格不显示caption

**症状**：使用 `modify_caption()` 后caption不显示在PDF中。

**原因**：gtsummary的caption需要通过 `as_kable()` 转换。

**解决方案**：
```r
# 错误做法
tbl_summary(...) %>% modify_caption("标题")

# 正确做法
tbl_summary(...) %>% as_kable(caption = "标题")
```


## 5. 渲染前检查清单

在渲染PDF之前，请确认以下事项：

### 5.1 表格检查
- [ ] 所有 `kable_styling()` 都没有使用 `full_width = TRUE`
- [ ] 所有 `kable_styling()` 都没有使用 `scale_down`
- [ ] 所有表格caption都没有手动添加编号（如"表1"）
- [ ] 所有 gtsummary 表格都使用了 `as_kable()` 转换

### 5.2 图表检查
- [ ] 所有图表都使用了 `fig.cap` 参数
- [ ] 所有图表caption都没有手动添加编号（如"图1"）
- [ ] 全局选项中设置了 `fig.showtext = TRUE`
- [ ] 图表使用了 `theme_minimal(base_family = "cjk")`

### 5.3 字体检查
- [ ] setup chunk 中加载了 showtext 包
- [ ] 配置了操作系统自动检测字体路径
- [ ] 调用了 `showtext_auto()`
- [ ] YAML中配置了 xelatex 引擎

### 5.4 代码规范检查
- [ ] 所有代码chunk都有有意义的名称
- [ ] 没有使用 `echo = TRUE` 显示不必要的代码
- [ ] 没有使用 `print()`, `cat()`, `glimpse()` 等输出原始文本

## 6. 推荐的包版本

以下是经过测试的包版本组合：

```r
# 核心包
library(tidyverse)    # 数据处理和可视化
library(vegan)        # 群落生态学分析
library(gtsummary)    # 专业表格
library(knitr)        # 文档生成
library(kableExtra)   # 表格样式
library(showtext)     # 中文字体支持
```

## 7. 使用说明

1. **开始新分析时**：复制 `assets/analysis_report_template.qmd` 作为起点
2. **编写代码时**：参考本文档的标准代码模板
3. **渲染前**：使用第5节的检查清单进行检查
4. **遇到问题时**：查阅第4节的常见问题和解决方案

---

**最后更新**：2026-01-29
**维护者**：Ecology-SKILL项目组
