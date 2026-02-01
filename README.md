# 生态学 AI Skill 仓库

这个仓库包含两个给生态学研究用的 AI Skill：

- **academic-paper-template**: 学术论文模板生成器，快速创建标准化的 Quarto 论文框架
- **ecology-research-assistant**: 生态学文献助手，帮你检索和整理文献

## 目录结构

- `academic-paper-template/`: 学术论文模板（支持多种论文类型和输出格式）
- `ecology-research-assistant/`: 文献检索脚本和关键词策略

## 环境配置

### 数据分析助手

**基础软件**

- **R** (建议 4.2+)
  - 下载地址：https://cran.r-project.org/

- **RStudio** (推荐)
  - 下载地址：https://posit.co/download/rstudio-desktop/

- **Quarto CLI**
  - macOS:
    ```bash
    brew install quarto
    ```
  - Windows: 下载安装包 https://quarto.org/docs/get-started/
  - Linux:
    ```bash
    # Ubuntu/Debian
    sudo apt-get install quarto

    # 或从官网下载 deb/rpm 包
    # https://quarto.org/docs/get-started/
    ```

**LaTeX 环境（生成 PDF 必需）**

Quarto 生成 PDF 需要 LaTeX 发行版，特别是 XeLaTeX 引擎来支持中文。根据你的系统选择：

- **macOS**: 安装 MacTeX
  ```bash
  brew install --cask mactex
  ```
  或者下载完整版：https://www.tug.org/mactex/

- **Windows**: 安装 MiKTeX 或 TeX Live
  - MiKTeX: https://miktex.org/download
  - TeX Live: https://www.tug.org/texlive/

- **Linux**: 安装 TeX Live
  ```bash
  sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra
  ```

**常用 LaTeX 宏包**

生成中文 PDF 通常需要这些宏包（大部分发行版会自动安装）：
- `xeCJK`: 中文支持
- `ctex`: 中文排版
- `fontspec`: 字体配置
- `geometry`: 页面布局
- `graphicx`: 图片插入
- `booktabs`: 表格美化

如果 Quarto 渲染时提示缺少宏包，可以手动安装：
```bash
# TeX Live
tlmgr install <package-name>

# MiKTeX (Windows)
mpm --install <package-name>
```

**验证环境**

检查 XeLaTeX 是否安装成功：
```bash
xelatex --version
```

测试 Quarto PDF 渲染：
```bash
quarto check
```

**R 包安装**

```r
# 必装
install.packages(c("tidyverse", "vegan", "showtext", "knitr", "rmarkdown"))

# 可选（特定分析用）
install.packages(c("ade4", "gclus", "ape"))
```

**中文字体配置**

为了让图表和 PDF 正确显示中文，需要配置 `showtext` 包。确认你系统里有对应字体：

| 系统 | 字体路径 |
| :--- | :--- |
| macOS | `/System/Library/Fonts/Supplemental/Songti.ttc` |
| Windows | `C:/Windows/Fonts/simsun.ttc` |
| Linux | `/usr/share/fonts/truetype/wqy/wqy-microhei.ttc` |

如果出现方框乱码，检查一下 `setup` 代码块里的 `font_add` 路径。

### 文献助手

需要 **Python 3.8+**。

安装依赖：
```bash
pip install scholarly
```

如果有 Semantic Scholar API Key，可以设置环境变量提高请求限额：
```bash
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"
```

## 安装 Skill

### Claude Code

将 skill 目录复制到以下位置之一：

**全局安装**（所有项目可用）：
```bash
# 复制到 Claude Code 的全局 skills 目录
cp -r academic-paper-template ~/.claude/skills/
cp -r ecology-research-assistant ~/.claude/skills/
```

**项目级安装**（仅当前项目可用）：
```bash
# 在项目根目录创建 .agent/skills 目录
mkdir -p .agent/skills
cp -r academic-paper-template .agent/skills/
cp -r ecology-research-assistant .agent/skills/
```

使用时直接调用 skill 名称：
```bash
/academic-paper-template
/ecology-research-assistant
```

### Codex

Codex 的 skill 安装方式类似：

```bash
# 全局安装
cp -r academic-paper-template ~/.codex/skills/
cp -r ecology-research-assistant ~/.codex/skills/

# 或项目级安装
mkdir -p .codex/skills
cp -r academic-paper-template .codex/skills/
cp -r ecology-research-assistant .codex/skills/
```

### Gemini CLI

Gemini CLI 的 skill 配置：

```bash
# 全局安装
cp -r academic-paper-template ~/.gemini/skills/
cp -r ecology-research-assistant ~/.gemini/skills/

# 或项目级安装
mkdir -p .gemini/skills
cp -r academic-paper-template .gemini/skills/
cp -r ecology-research-assistant .gemini/skills/
```

具体路径可能因版本而异，建议查看各工具的官方文档确认 skills 目录位置。

## 使用方法
直接调查SKILL后询问这个SKILL的用途和使用方法即可。

## 其他

- 代码出错的话，看看 `references/` 目录下的规范文档
- 欢迎补充 `references/` 里的生态学方法库
