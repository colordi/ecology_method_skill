# 代码执行与结果验证指南

为确保报告中的解释文字与实际分析结果一致，必须先执行代码获取真实结果，再编写解释。

## 执行方法

使用 Bash 工具通过 `Rscript` 命令执行 R 代码。

**基本语法**：
```bash
Rscript -e "R代码"
```

## 常用示例

### 1. 读取数据并查看结构
```bash
Rscript -e "data <- read.delim('Table B.txt'); str(data); head(data)"
```

### 2. 执行统计检验并查看结果
```bash
Rscript -e "library(tidyverse); data <- read.csv('data.csv'); wilcox.test(value ~ group, data = data)"
```

### 3. 计算描述性统计
```bash
Rscript -e "library(tidyverse); data <- read.csv('data.csv'); data %>% group_by(group) %>% summarise(mean = mean(value), sd = sd(value))"
```

### 4. 执行多行复杂代码（使用分号分隔）
```bash
Rscript -e "library(vegan); data <- read.csv('species.csv'); div <- diversity(data, index='shannon'); print(div)"
```

## 工作流程

1. 先用 `Rscript` 执行分析代码，获取实际的 p 值、均值、标准差等数值
2. 根据实际结果判断统计显著性和生态学意义
3. 基于真实数值编写准确的解释文字
4. 将代码和解释整合到 .qmd 文件中

## 优势

- 解释文字基于实际结果，避免预期与结果矛盾
- 可以根据结果动态调整分析策略
- 更接近真实的数据分析流程
