# 内联代码与变量引用规范

本文档定义了在 Quarto 报告中使用内联 R 代码引用变量的规范，确保报告的可重复性和数据一致性。

## 核心原则

**必须遵守**：
- ✅ 正文中的所有数值**必须**通过内联 R 代码引用变量，而非硬编码
- ✅ 阶段3执行 Rscript 是为了**验证结果**，不是为了获取硬编码数值
- ✅ 关键统计量必须在代码块中保存为变量，供正文引用

**禁止使用**：
- ❌ **绝不**在正文中直接写入具体数值（如"均值为2.37"）
- ❌ **绝不**将 Rscript 执行结果复制粘贴到正文中


## 工作流程

### 阶段3的正确流程

```
1. 用 Rscript 执行分析代码
   ↓
2. 查看输出，验证结果合理性
   ↓
3. 在 qmd 代码块中保存关键统计量为变量
   ↓
4. 在正文中使用 `r variable` 引用变量
```

### 错误示例 vs 正确示例

**❌ 错误做法**：

```markdown
对照样地平均物种丰富度为2.37，有火蚁样地为2.03。
Wilcoxon检验结果显示差异不显著（p = 0.362）。
```

**✅ 正确做法**：

```markdown
对照样地平均物种丰富度为`r round(mean_control, 2)`，
有火蚁样地为`r round(mean_invaded, 2)`。
Wilcoxon检验结果显示差异不显著（p = `r round(p_richness, 3)`）。
```


## 变量命名规范

### 描述性统计变量

```r
# 在代码块中计算并保存
stats_by_site <- diversity_df %>%
  group_by(样地类型) %>%
  summarise(
    n = n(),
    mean_richness = mean(物种丰富度),
    sd_richness = sd(物种丰富度),
    mean_shannon = mean(Shannon),
    sd_shannon = sd(Shannon)
  )

# 提取为独立变量，便于引用
n_control <- stats_by_site$n[stats_by_site$样地类型 == "对照样地"]
n_invaded <- stats_by_site$n[stats_by_site$样地类型 == "有火蚁样地"]
mean_richness_control <- stats_by_site$mean_richness[stats_by_site$样地类型 == "对照样地"]
mean_richness_invaded <- stats_by_site$mean_richness[stats_by_site$样地类型 == "有火蚁样地"]
sd_richness_control <- stats_by_site$sd_richness[stats_by_site$样地类型 == "对照样地"]
sd_richness_invaded <- stats_by_site$sd_richness[stats_by_site$样地类型 == "有火蚁样地"]
```

### 统计检验变量

```r
# 执行检验并保存结果
test_richness <- wilcox.test(物种丰富度 ~ 样地类型, data = diversity_df)

# 提取关键统计量
W_richness <- test_richness$statistic
p_richness <- test_richness$p.value
```

### 变量命名约定

| 类型 | 命名模式 | 示例 |
|------|----------|------|
| 样本量 | `n_组名` | `n_control`, `n_invaded` |
| 均值 | `mean_指标_组名` | `mean_richness_control` |
| 标准差 | `sd_指标_组名` | `sd_richness_control` |
| 检验统计量 | `统计量_指标` | `W_richness`, `F_shannon` |
| p值 | `p_指标` | `p_richness`, `p_shannon` |


## 内联代码语法

### 基本语法

在 Markdown 正文中使用反引号包裹 `r` 和表达式：

```markdown
样本量为`r n_total`个。
```

### 数值格式化

```markdown
# 保留2位小数
均值为`r round(mean_value, 2)`

# 保留3位小数（用于p值）
p = `r round(p_value, 3)`

# 均值±标准差格式
`r round(mean_value, 2)` ± `r round(sd_value, 2)`

# 百分比格式
占比为`r round(proportion * 100, 1)`%

# 科学计数法（极小p值）
p `r ifelse(p_value < 0.001, "< 0.001", paste("=", round(p_value, 3)))`
```

### 条件文本

```markdown
差异`r ifelse(p_value < 0.05, "具有", "不具有")`统计学显著性
```


## 代码块组织建议

### 推荐的代码块结构

```r
```{r analysis-diversity}
# ===== 1. 计算描述性统计 =====
stats_summary <- diversity_df %>%
  group_by(样地类型) %>%
  summarise(
    n = n(),
    mean_richness = mean(物种丰富度),
    sd_richness = sd(物种丰富度)
  )

# ===== 2. 提取变量供正文引用 =====
n_control <- stats_summary$n[1]
n_invaded <- stats_summary$n[2]
mean_richness_control <- stats_summary$mean_richness[1]
mean_richness_invaded <- stats_summary$mean_richness[2]
sd_richness_control <- stats_summary$sd_richness[1]
sd_richness_invaded <- stats_summary$sd_richness[2]

# ===== 3. 统计检验 =====
test_richness <- wilcox.test(物种丰富度 ~ 样地类型, data = diversity_df)
W_richness <- test_richness$statistic
p_richness <- test_richness$p.value
```
```

### 变量作用域

- 在一个代码块中定义的变量，可以在**后续所有代码块和正文**中引用
- 建议在报告前部的代码块中集中定义所有需要引用的变量


## 完整示例

### 代码块

```r
```{r diversity-stats}
# 计算描述性统计
stats <- diversity_df %>%
  group_by(样地类型) %>%
  summarise(
    n = n(),
    mean_rich = mean(物种丰富度),
    sd_rich = sd(物种丰富度)
  )

# 提取变量
n_ctrl <- stats$n[stats$样地类型 == "对照样地"]
n_inv <- stats$n[stats$样地类型 == "有火蚁样地"]
mean_ctrl <- stats$mean_rich[stats$样地类型 == "对照样地"]
mean_inv <- stats$mean_rich[stats$样地类型 == "有火蚁样地"]
sd_ctrl <- stats$sd_rich[stats$样地类型 == "对照样地"]
sd_inv <- stats$sd_rich[stats$样地类型 == "有火蚁样地"]

# 统计检验
test <- wilcox.test(物种丰富度 ~ 样地类型, data = diversity_df)
W_val <- test$statistic
p_val <- test$p.value
```
```

### 正文引用

```markdown
本研究共调查了`r n_ctrl + n_inv`个样方，其中对照样地`r n_ctrl`个，
有火蚁样地`r n_inv`个。

对照样地的本地蚂蚁物种丰富度（`r round(mean_ctrl, 2)` ± `r round(sd_ctrl, 2)`）
高于有火蚁样地（`r round(mean_inv, 2)` ± `r round(sd_inv, 2)`）。
Wilcoxon秩和检验表明，两组之间的差异`r ifelse(p_val < 0.05, "具有", "不具有")`
统计学显著性（W = `r round(W_val, 1)`, p = `r round(p_val, 3)`）。
```


## 检查清单

在撰写报告时，请确认：

- [ ] 所有数值都通过 `` `r variable` `` 引用，没有硬编码
- [ ] 关键统计量都已保存为变量
- [ ] 变量命名清晰、一致
- [ ] p值保留3位小数，其他数值保留2位小数
- [ ] 使用 `round()` 函数控制小数位数


## 为什么这样做

1. **可重复性**：数据更新后，报告自动更新所有数值
2. **一致性**：避免代码结果与正文数值不一致的错误
3. **效率**：无需手动复制粘贴数值
4. **可维护性**：修改分析方法后，正文自动反映新结果

---

**最后更新**：2026-01-30
