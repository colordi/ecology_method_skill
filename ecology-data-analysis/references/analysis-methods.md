# 生态学分析方法决策树

本文档帮助根据研究问题和数据类型选择合适的分析方法。

## 决策流程图

```
研究目标是什么？
│
├─ 描述群落特征
│  ├─ 物种多样性 → α多样性指数（Shannon, Simpson, 物种丰富度）
│  ├─ 群落组成 → 物种累积曲线、rank-abundance曲线
│  └─ 均匀度 → Pielou均匀度指数
│
├─ 比较组间差异
│  ├─ 两组比较
│  │  ├─ 连续变量 → t检验（正态）或 Wilcoxon检验（非正态）
│  │  └─ 群落组成 → PERMANOVA, ANOSIM
│  └─ 多组比较
│     ├─ 连续变量 → ANOVA（正态）或 Kruskal-Wallis（非正态）
│     └─ 群落组成 → PERMANOVA, ANOSIM
│
├─ 探索变量关系
│  ├─ 物种与环境 → RDA（线性）或 CCA（单峰）
│  ├─ 相关分析 → Pearson（线性）或 Spearman（单调）
│  └─ 回归分析 → 线性回归、GLM、GAM
│
├─ 群落格局分析
│  ├─ 排序分析
│  │  ├─ 无约束排序 → PCA（线性）、CA（单峰）、NMDS（非参数）
│  │  └─ 约束排序 → RDA、CCA、db-RDA
│  └─ 聚类分析 → 层次聚类、K-means
│
└─ β多样性分析
   ├─ 组成差异 → Bray-Curtis, Jaccard距离
   ├─ 系统发育β多样性 → UniFrac距离
   └─ 功能β多样性 → 功能性状距离
```

## 常见分析方法速查

### 1. 多样性分析

**α多样性（Alpha Diversity）**
- **适用**: 描述单个样方/群落的物种多样性
- **常用指数**:
  - Shannon指数：考虑丰富度和均匀度
  - Simpson指数：优势种的概率
  - 物种丰富度：物种数量
- **R包**: `vegan::diversity()`

**β多样性（Beta Diversity）**
- **适用**: 比较不同样方/群落间的组成差异
- **常用方法**:
  - Bray-Curtis距离：基于丰度
  - Jaccard距离：基于存在/缺失
  - Sørensen指数
- **R包**: `vegan::vegdist()`, `betapart`

### 2. 群落组成比较

**PERMANOVA（置换多元方差分析）**
- **适用**: 检验组间群落组成是否存在显著差异
- **假设**: 组内方差齐性
- **R包**: `vegan::adonis2()`

**ANOSIM（相似性分析）**
- **适用**: 检验组间差异，对方差齐性要求较低
- **R包**: `vegan::anosim()`

### 3. 排序分析

**PCA（主成分分析）**
- **适用**: 线性响应，环境变量分析
- **R包**: `vegan::rda()` 或 `stats::prcomp()`

**NMDS（非度量多维尺度分析）**
- **适用**: 群落组成数据，无线性假设
- **优点**: 稳健性强，适用范围广
- **R包**: `vegan::metaMDS()`

**RDA（冗余分析）**
- **适用**: 物种与环境的线性关系
- **R包**: `vegan::rda()`

**CCA（典范对应分析）**
- **适用**: 物种与环境的单峰关系
- **R包**: `vegan::cca()`

### 4. 统计检验

**参数检验**
- t检验: `t.test()`
- ANOVA: `aov()`, `anova()`
- 线性回归: `lm()`

**非参数检验**
- Wilcoxon检验: `wilcox.test()`
- Kruskal-Wallis检验: `kruskal.test()`
- Spearman相关: `cor.test(method="spearman")`

### 5. 广义线性模型

**GLM（Generalized Linear Models）**
- **适用**: 非正态分布的响应变量
- **常用分布**:
  - 计数数据 → Poisson或负二项分布
  - 二元数据 → 二项分布
  - 比例数据 → Beta分布
- **R包**: `glm()`, `MASS::glm.nb()`

## 数据类型与方法匹配

| 数据类型 | 推荐方法 | R包 |
|---------|---------|-----|
| 物种丰度矩阵 | NMDS, PERMANOVA | vegan |
| 存在/缺失数据 | Jaccard距离, CA | vegan |
| 环境变量 | PCA, RDA | vegan |
| 计数数据 | GLM (Poisson/NB) | stats, MASS |
| 功能性状 | 功能多样性指数 | FD, fundiv |
| 系统发育树 | 系统发育多样性 | picante, ape |

## 选择建议

1. **先探索后检验**: 先用排序分析可视化数据，再进行统计检验
2. **检查假设**: 使用参数方法前检查正态性和方差齐性
3. **多重比较校正**: 多次检验时使用FDR或Bonferroni校正
4. **样本量考虑**: 小样本优先选择非参数方法
5. **生态学意义**: 统计显著不等于生态学重要，需结合效应量
