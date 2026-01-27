---
name: research-methods-intake
description: Four-stage progressive workflow for writing comprehensive, reproducible ecology research methodology sections. Use this skill when users need help with: (1) Structuring research methods for ecology papers, (2) Writing methodology sections that meet reproducibility standards, (3) Organizing complex field study protocols (sampling design, data collection, statistical analysis), (4) Preparing methods for journals like Current Biology, (5) Ensuring methodological rigor with proper citations and evidence, or (6) Any task involving ecology research methodology writing from initial concept to final draft.
---

# Research Methods Intake

A four-stage progressive workflow that transforms vague research intentions into complete, reproducible methodology sections for ecology research papers.

## Core Constraints

- **No guessing**: Ask when critical information is unclear
- **No fabrication**: Never invent papers, DOIs, or journal names
- **Progressive steps**: Maximum 3 questions per round
- **Confirm before proceeding**: Paraphrase user responses for verification

---

## Workflow Overview

### Stage 1: Intent Alignment

**Goal**: Collect research information and confirm methodological framework

**References**: See `references/step1-intent/`

**Process**:
1. Start with opening prompt to initiate information gathering
2. Ask up to 3 questions per round covering:
   - Research context and study system
   - Data collection methods
   - Materials and tools
   - Analysis procedures
3. Output "Research Method Information Card" after each round

**Opening Prompt**:
> "To help you write a clear and reproducible ecology methods section, I need to confirm a few key details. Please answer briefly by number:"

**First Three Questions**:
1. Research theme (population/community/ecosystem/conservation)? Study system and region? Objectives?
2. How is data acquired (plots/traps/cameras/sensors)? Spatiotemporal scale? Sample size?
3. Core response variables/metrics? Explanatory variables? Analysis methods and software?

**Output Format**: Research Method Information Card (inline)

```markdown
## Research Method Information Card

### Confirmed Information
- Research theme:
- Study system:
- Study region:
- Data collection:
- Core metrics:
- Analysis methods:

### Information Gaps
1. ...

### Next Round Questions (≤3)
1. ...
```

**Completion Criteria**: Study system clear + data sources specified + analysis pathway executable

---

### Stage 2: Information Retrieval

**Goal**: Provide citable literature evidence for methodological choices

**References**: See `references/step2-retrieval/`

**Trigger Conditions** (any of):
- Need citation support for method selection
- Need to confirm method applicability boundaries for target system
- Writing for high-quality journals

**Process**:
1. Extract 1-3 "verification points" from information card
2. Design and execute search queries
3. Evaluate evidence quality and applicability boundaries
4. Deposit as knowledge base entries

**Output**: `knowledge-base/`

```
knowledge-base/
├── search-log.md      # Search history
├── index.md           # Knowledge base index
└── facts/             # Fact entries
    └── [topic].md
```

**Fact Entry Format**: See template in `assets/fact-entry-template.md`

---

### Stage 3: Structure Finalization

**Goal**: Establish detailed outline and key specifications

**References**: See `references/step3-structure/方法论详细大纲-outline.md`

**Process**:
1. Based on research information card, determine modules to populate
2. Confirm key specifications one by one:
   - Variable definitions (operational definitions of response/explanatory variables)
   - Threshold settings (deduplication thresholds, valid sample criteria, significance levels)
   - Method selection (distance metrics, distribution families, random effect structures)
   - Software versions (core packages/functions and version numbers)
3. Generate "Specification Confirmation Checklist"

**Output**: Confirmed outline and specifications

```markdown
## Specification Confirmation Checklist

### Variable Definitions
- [Variable name]: [Definition/specification] ✅

### Threshold Settings
- [Threshold name]: [Value and unit] ✅

### Method Selection
- [Method]: [Selected method and rationale] ✅

### Software Versions
- [Package name]: [Version number] ✅
```

**Completion Criteria**: All key specifications confirmed

---

### Stage 4: Progressive Generation

**Goal**: Populate methodology content module by module

**References**: See `references/step4-generation/`

**Outline Template**: `references/step3-structure/方法论详细大纲-outline.md`

#### Generation Strategy

**Dynamic Granularity**: Adjust generation unit based on complexity
- Simple modules: Generate entire module at once
- Medium modules: Generate by second-level headings
- Complex modules: Generate by third-level headings step by step

**Generation Sequence**:
```
Module 1 (Study Design) → Module 2 (Data Collection) → Module 3 (Data Processing) → Module 4 (Statistical Analysis) → Module 5 (Data & Code Availability) → Appendix (Reference List)
```

#### Checkpoint Mechanism

**Pause for user confirmation after each generation unit**:
1. Output generated content
2. Show key specification confirmation
3. Preview next unit
4. Wait for user response

**Post-Confirmation Actions**:
- ✅ Confirmed → Proceed to next unit
- ⚠️ Revision needed → Revise and re-confirm
- ↩️ Backtrack → Return to modify previous unit

#### Information Gap Handling

**Immediately pause when gaps are discovered**:
```
⚠️ Information gap detected, pausing generation:

Gap 1: [Missing information]
- Affects module: [Module number]
- Question: [Specific question]

Please provide information to continue.
```

#### Writing Rules

- **Reproducibility first**: Parameters, units, thresholds, versions must be explicit
- **Citation backflow**: Use `[R#]` placeholders, consolidate DOIs in appendix
- **Specification consistency**: Maintain alignment with previous modules
- **Style reference**: Current Biology (concise, short paragraphs)

**Intermediate outputs**: `drafts/`
**Final outputs**: `output/`

```
drafts/
├── 01_study_design.md
├── 02_data_collection.md
├── 03_data_processing.md
├── 04_statistical_analysis.md
└── 05_data_availability.md

output/
├── methodology.md           # Complete methodology
└── references_evidence.md   # Reference and evidence list
```

---

## Directory Structure

```
research-methods-intake/
├── SKILL.md                    # Main file
├── assets/                     # Templates for output
│   ├── fact-entry-template.md
│   └── venue-entry-template.md
├── knowledge-base/             # Stage 2 output (user workspace)
├── drafts/                     # Stage 4 intermediate outputs (user workspace)
├── output/                     # Stage 4 final outputs (user workspace)
└── references/                 # Reference materials
    ├── step1-intent/           # Intent alignment
    ├── step2-retrieval/        # Information retrieval
    ├── step3-structure/        # Structure finalization
    └── step4-generation/       # Progressive generation
```

---

## Usage Notes

- Read reference files in `references/step*-*/` as needed for detailed guidance
- Templates in `assets/` are used to create knowledge base entries
- Output directories (`knowledge-base/`, `drafts/`, `output/`) are user workspaces and should not be included in the skill package
