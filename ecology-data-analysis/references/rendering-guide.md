# PDF 渲染规范

## 1. 文档格式

**必须**：
- ✅ YAML 指定 `format: pdf` 和 `pdf-engine: xelatex`
- ✅ 使用 Markdown 标题自动编号

**禁止**：
- ❌ 生成 HTML 格式
- ❌ 手动编号标题（❌ `# 1. 引言` → ✅ `# 引言`）


## 2. 表格规范

**必须**：
- ✅ `kable(format = "latex", booktabs = TRUE)`
- ✅ `kable_styling(latex_options = "hold_position")`
- ✅ gtsummary 用 `as_kable_extra(format = "latex")` 转换

**禁止**：
- ❌ `full_width = TRUE`
- ❌ `scale_down`
- ❌ `striped`
- ❌ caption 中手动编号

**模板**：
```r
kable(data, format = "latex", booktabs = TRUE, caption = "标题") %>%
  kable_styling(latex_options = "hold_position")
```


## 3. 图表规范

**必须**：
- ✅ 使用 `#| fig-cap` 添加标题
- ✅ 设置 `fig.showtext = TRUE`
- ✅ 使用 `theme_minimal(base_family = "cjk")`

**禁止**：
- ❌ caption 中手动编号
- ❌ 使用 `ggtitle()` 添加标题


## 4. 交叉引用

**必须**：
- ✅ 图表设置 `#| label: fig-xxx`，表格设置 `#| label: tbl-xxx`
- ✅ 正文用 `@fig-xxx`、`@tbl-xxx` 引用
- ✅ 每个图表前有引用，后有解读段落

**禁止**：
- ❌ 手动编号（❌ "图1"、"表2"）
- ❌ 孤立图表（无引用、无解读）

**示例**：
```r
```{r}
#| label: fig-diversity
#| fig-cap: "多样性比较"
ggplot(...)
```
```

```markdown
如 @fig-diversity 所示，两类样地存在差异。
```


## 5. 字体配置

```r
library(showtext)
font_add("cjk", regular = "/System/Library/Fonts/STHeiti Light.ttc")
showtext_auto()
theme_set(theme_minimal(base_family = "cjk"))
knitr::opts_chunk$set(fig.showtext = TRUE)
```

```yaml
format:
  pdf:
    pdf-engine: xelatex
    mainfont: "Songti SC"
    CJKmainfont: "Songti SC"
```


## 6. 检查清单

**表格**：
- [ ] `format = "latex"` + `booktabs = TRUE`
- [ ] 无 `full_width`、`scale_down`、`striped`
- [ ] gtsummary 用 `as_kable(format = "latex")` 转换

**图表**：
- [ ] 设置 `#| label: fig-xxx` 和 `#| fig-cap`
- [ ] `fig.showtext = TRUE`

**交叉引用**：
- [ ] 正文用 `@fig-xxx`、`@tbl-xxx` 引用
- [ ] 无手动编号
- [ ] 每个图表有解读段落

**字体**：
- [ ] showtext 配置完成
- [ ] YAML 指定 xelatex
