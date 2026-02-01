---
name: academic-paper-template
description: 帮助研究生快速创建标准、规范的学术论文模板，特别是生态学领域的论文。支持多种论文类型（数据分析报告、实验报告、文献综述等）和多种输出格式（PDF、Word、HTML）。当用户请求创建论文模板、需要学术写作框架、或想要生成Quarto/R Markdown文档时使用。支持交互式定制（询问标题、作者、研究类型等）和跨平台字体配置。
---

# Academic Paper Template Generator

This skill helps graduate students create standardized, well-structured academic paper templates using Quarto Markdown (.qmd format), with a focus on ecological research but adaptable to other fields.

## When to Use This Skill

Use this skill when users request:
- "创建一个论文模板" / "Create a paper template"
- "生成学术论文框架" / "Generate academic paper structure"
- "我需要一个数据分析报告模板" / "I need a data analysis report template"
- "帮我建立一个标准的研究报告" / "Help me set up a standard research report"
- Any request involving Quarto (.qmd) or R Markdown academic templates

## Supported Paper Types

1. **学术报告 (Academic Report)** - Standard academic paper with Abstract, Introduction, Methods, Results, Discussion, and Conclusion (IMRaD format)
2. **实验报告 (Experimental Report)** - Lab or field experiment documentation with methods and results
3. **文献综述 (Literature Review)** - Systematic review of existing research
4. **研究提案 (Research Proposal)** - Project proposal with background, methods, and expected outcomes

## Workflow

### Step 1: Gather Requirements

Ask the user about their needs using AskUserQuestion:

1. **Paper type**: Which type of paper template do they need?
2. **Output format**: PDF, Word (docx), HTML, or multiple formats?
3. **Language preference**: Chinese, English, or bilingual?
4. **Customization level**: Quick start with defaults, or customize title/author/sections?

### Step 2: Collect Custom Information (if requested)

If the user wants customization, ask for:
- Paper title (论文标题)
- Author name(s) (作者姓名)
- Institution/affiliation (单位)
- Specific sections to include/exclude
- Any special requirements (e.g., specific citation style, additional packages)

### Step 3: Generate the Template

Based on the gathered information:

1. Select the appropriate base template from `assets/` directory
2. Customize the YAML frontmatter with user's information
3. Adjust output format settings based on user's choice
4. Configure font settings for cross-platform compatibility
5. Write the .qmd file to the user's working directory
6. **Copy `quarto-guide.md` from `references/` to the user's working directory** (same location as the .qmd file)

### Step 4: Provide Usage Instructions

After generating the template, inform the user:

1. **Files created**:
   - `[filename].qmd` - Your paper template
   - `quarto-guide.md` - Complete Quarto usage guide (in the same directory)

2. How to render the document:
   ```bash
   quarto render filename.qmd
   ```

3. Required R packages (if applicable):
   ```r
   install.packages(c("tidyverse", "gtsummary", "knitr", "kableExtra", "showtext"))
   ```

4. **For detailed Quarto installation and usage instructions, see `quarto-guide.md` in your working directory**

5. Font configuration notes for their platform (see quarto-guide.md or references/font-config.md)

6. Next steps: filling in content, adding data, running analyses

## Template Structure Guidelines

All templates should follow these principles:

### YAML Frontmatter
- Include title, author, date
- Configure output format(s) with appropriate options
- Set up Chinese font support for cross-platform compatibility
- Include sensible defaults for margins, font sizes, TOC settings

### Document Sections
- Clear hierarchical structure with numbered sections
- Placeholder text in [brackets] to guide users
- Code chunks with descriptive names and comments
- Balance between guidance and flexibility

### Code Chunks
- Use meaningful chunk names (e.g., `data-loading`, `descriptive-stats`)
- Set appropriate chunk options (echo, warning, message, fig.cap)
- Include commented examples of common operations
- Provide best practices in comments

### Best Practices
- Use professional table formatting (gtsummary, kableExtra)
- Configure proper figure captions (without manual numbering)
- Include assumption checking for statistical methods
- Provide interpretation guidance for results

## Cross-Platform Font Configuration

For Chinese text support, configure fonts based on the user's platform:

**macOS:**
```yaml
mainfont: "Songti SC"
CJKmainfont: "Songti SC"
```

**Windows:**
```yaml
mainfont: "SimSun"
CJKmainfont: "SimSun"
```

**Linux:**
```yaml
mainfont: "Noto Serif CJK SC"
CJKmainfont: "Noto Serif CJK SC"
```

For detailed font configuration, see [references/font-config.md](references/font-config.md).

## Output Format Options

### PDF Output
- Uses XeLaTeX engine for Chinese support
- Professional academic formatting
- Suitable for submission and printing

### Word Output
- Compatible with Microsoft Word
- Easier for collaborative editing
- May require manual formatting adjustments

### HTML Output
- Interactive and web-friendly
- Good for sharing online
- Supports dynamic content

For detailed format configuration, see [references/output-formats.md](references/output-formats.md).

## Template Assets

Base templates are stored in `assets/` directory:
- `academic-report.qmd` - Standard academic paper template (IMRaD format: Abstract, Introduction, Methods, Results, Discussion, Conclusion)
- `experimental-report.qmd` - Lab/field experiment template
- `literature-review.qmd` - Systematic review template
- `research-proposal.qmd` - Research proposal template

## Important Notes

- Always ask before overwriting existing files
- Verify Quarto is installed before generating templates
- Provide clear instructions for rendering and customization
- Remind users to install required R packages if using R code chunks
- Be helpful in explaining template structure and best practices
