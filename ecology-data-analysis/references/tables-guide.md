# 表格生成指南

本文档提供使用 gtsummary 包生成各类专业表格的模板。

## 1. 描述性统计表

### 基本用法

```r
library(gtsummary)

data %>%
  tbl_summary(
    include = c(var1, var2, var3),
    statistic = list(
      all_continuous() ~ "{mean} ± {sd}",
      all_categorical() ~ "{n} ({p}%)"
    ),
    digits = all_continuous() ~ 2
  ) %>%
  as_kable_extra(format = "latex", booktabs = TRUE, caption = "描述性统计") %>%
  kable_styling(latex_options = "hold_position")
```

### 分组描述性统计

```r
data %>%
  tbl_summary(
    by = 分组变量,
    include = c(var1, var2, var3),
    statistic = list(
      all_continuous() ~ "{mean} ± {sd}",
      all_categorical() ~ "{n} ({p}%)"
    )
  ) %>%
  add_p() %>%
  add_overall() %>%
  as_kable_extra(format = "latex", booktabs = TRUE, caption = "分组描述性统计") %>%
  kable_styling(latex_options = "hold_position")
```


## 2. 组间比较表

### 两组比较

```r
data %>%
  tbl_summary(
    by = group,
    include = c(response_var),
    statistic = all_continuous() ~ "{median} ({p25}, {p75})"
  ) %>%
  add_p(test = all_continuous() ~ "wilcox.test") %>%
  as_kable_extra(format = "latex", booktabs = TRUE, caption = "组间比较") %>%
  kable_styling(latex_options = "hold_position")
```

### 多组比较

```r
data %>%
  tbl_summary(
    by = group,
    include = c(response_var),
    statistic = all_continuous() ~ "{mean} ± {sd}"
  ) %>%
  add_p(test = all_continuous() ~ "kruskal.test") %>%
  as_kable_extra(format = "latex", booktabs = TRUE, caption = "多组比较") %>%
  kable_styling(latex_options = "hold_position")
```


## 3. 回归结果表

### 线性回归

```r
model <- lm(y ~ x1 + x2, data = data)

tbl_regression(model,
  intercept = TRUE,
  estimate_fun = function(x) round(x, 3)
) %>%
  add_glance_source_note(include = c(r.squared, adj.r.squared, nobs)) %>%
  as_kable_extra(format = "latex", booktabs = TRUE, caption = "线性回归结果") %>%
  kable_styling(latex_options = "hold_position")
```

### 广义线性模型 (GLM)

```r
model <- glm(y ~ x1 + x2, family = poisson, data = data)

tbl_regression(model,
  exponentiate = TRUE,  # 输出 OR 或 RR
  estimate_fun = function(x) round(x, 2)
) %>%
  add_glance_source_note(include = c(AIC, nobs)) %>%
  as_kable_extra(format = "latex", booktabs = TRUE, caption = "GLM 结果") %>%
  kable_styling(latex_options = "hold_position")
```

### 混合效应模型

```r
library(lme4)
model <- lmer(y ~ x1 + x2 + (1|random_effect), data = data)

tbl_regression(model) %>%
  as_kable_extra(format = "latex", booktabs = TRUE, caption = "混合效应模型结果") %>%
  kable_styling(latex_options = "hold_position")
```


## 4. 常用统计量格式

| 统计量 | 语法 |
|--------|------|
| 均值±标准差 | `"{mean} ± {sd}"` |
| 中位数(四分位) | `"{median} ({p25}, {p75})"` |
| 计数(百分比) | `"{n} ({p}%)"` |
| 范围 | `"{min} - {max}"` |
| 均值(95%CI) | `"{mean} ({ci})"` |


## 5. 提取变量供正文引用

```r
# 创建表格并保存
tbl <- data %>%
  tbl_summary(by = group) %>%
  add_p()

# 提取 p 值
p_val <- tbl$table_body %>%
  filter(variable == "var_name") %>%
  pull(p.value)

# 提取统计量
stat_val <- tbl$table_body %>%
  filter(variable == "var_name", row_type == "label") %>%
  pull(stat_1)
```

正文引用：
```markdown
组间差异`r ifelse(p_val < 0.05, "显著", "不显著")`（p = `r round(p_val, 3)`）。
```
