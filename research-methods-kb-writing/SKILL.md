---
name: research-methods-kb-writing
description: 将用户精读后补全的 reading-list.md 转写为可追溯的生态学方法知识库（facts），并基于知识库与已确认的研究规格逐步生成可复现的 Methods 章节。适用于：把“文献精读要点+原文定位”沉淀为结构化证据链，再据此撰写方法学文本并保持每个关键决策可回链。
---

# Research Methods KB + Writing（入库 + 写作）

本 skill 只接受一个输入：用户已精读补全的 `reading-list.md`（来自 Skill1）。

## ✅ 核心约束

- **只用用户提供的精读内容**：不自行补编论文细节，不自行推断缺失信息
- **可追溯**：每条知识库条目必须包含“原文定位”（章节/页码/表图/段落）
- **先入库后写作**：先把证据链沉淀成 facts，再用 facts 生成 Methods

---

## Stage 1：检查 reading-list.md 的“入库门槛”

对每篇文献，若缺少以下任一项，先暂停并要求用户补全：
- `精读要点（必填，用户填）`
- `原文定位（必填，用户填）`

建议项（缺失可继续，但需提示风险）：
- DOI 或稳定链接至少其一
- 适用边界/警告（若文献强调限制）

---

## Stage 2：从 reading-list.md 转写知识库（facts）

使用模板：`assets/fact-entry-template.md`
（路径：`.agent/skills/research-methods-kb-writing/assets/fact-entry-template.md`）

建议用户项目内的知识库结构（在用户工作区创建，不属于 skill 包）：
```
knowledge-base/
└── facts/
    ├── [verification-point]-[paper-key].md
    └── ...
```

每条 fact 的最小要求：
- 可用于 Methods 的事实陈述（1–2 句）
- 适用边界/前提条件/局限性（与精读要点一致）
- 引用信息（DOI/链接）
- 原文定位（从 reading-list.md 复制）

---

## Stage 3：基于知识库逐步生成 Methods

**参考**：`references/step3-structure/` 与 `references/step4-generation/`

规则：
- 先生成大纲与规格确认清单（变量定义/阈值/方法选择/软件版本）
- 按模块逐段生成（每段结束都等待用户确认/修订）
- 每个关键决策点都要能回链到对应 fact（可用占位符如 `[F:xxx]`）
