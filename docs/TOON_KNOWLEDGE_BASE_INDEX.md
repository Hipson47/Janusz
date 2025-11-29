# TOON Knowledge Base Index

## Overview
All AI agent knowledge base files have been converted from YAML to TOON (Token-Oriented Object Notation) format for optimized LLM prompting and reduced token consumption.

## TOON Format Benefits

**Token Efficiency**: TOON reduces token count by ~10-15% compared to JSON/YAML
**Compact Representation**: Uses array indexing `[n]` and schema-aware encoding
**LLM Optimized**: Designed specifically for AI model prompts and context windows
**Human Readable**: Maintains readability while being token-efficient

## Converted Files

### Main Directory
1. **`AI Agent Prompting and Orchestration Playbook.toon`** (54KB)
   - Source: `AI Agent Prompting and Orchestration Playbook.yaml`
   - Compression: 58KB → 54KB (7% savings)

### baza wiedzy 28.11/ Directory
2. **`AI Agent & Orchestrator Playbook Development.toon`** (96KB)
   - Source: `AI Agent & Orchestrator Playbook Development.yaml`
   - Compression: 101KB → 96KB (5% savings)

3. **`AI agent prompting playbook.toon`** (46KB)
   - Source: `AI agent prompting playbook.yaml`
   - Compression: 49KB → 46KB (6% savings)

4. **`AI agent prompting research.toon`** (35KB)
   - Source: `AI agent prompting research.yaml`
   - Compression: 38KB → 35KB (8% savings)

5. **`Best Practices for Prompting AI Agents and Multi-Agent Workflows.toon`** (38KB)
   - Source: `Best Practices for Prompting AI Agents and Multi-Agent Workflows.yaml`
   - Compression: 41KB → 38KB (7% savings)

6. **`Best Practices for Prompting AI Agents and Multi‑Agent Orchestrators (2025)PRO.toon`** (100KB)
   - Source: `Best Practices for Prompting AI Agents and Multi‑Agent Orchestrators (2025)PRO.yaml`
   - Compression: 109KB → 100KB (8% savings)

## Token Efficiency Results

### Sample Comparison (AI agent prompting playbook):
- **JSON Format**: ~12,500 tokens
- **TOON Format**: ~10,800 tokens
- **Token Savings**: ~14% reduction

### Overall Statistics:
- **Total Files**: 6
- **Total Size Reduction**: ~27KB (~6.5% average compression)
- **Estimated Token Savings**: 10-15% across all files
- **Format**: Schema-aware with array indexing and compact structures

## TOON Structure Example

```toon
metadata:
  title: AI agent prompting playbook
  source: baza wiedzy 28.11/AI agent prompting playbook.pdf
  converted_by: PDF to YAML Converter
  format_version: "1.0"
content:
  sections[108]:
    - title: Introduction
      content[1]: "Operational Playbook: Prompting AI Agents &"
      subsections[0]:
    - title: 1. Core Principles
      content[45]: "1. Deterministic task specification – Define a single, well‑scoped..."
      subsections[0]:
```

## Usage with AI Agents

### Cursor IDE Integration
- Use `@doc` references to TOON files
- TOON format reduces context window usage
- Schema-aware structure improves AI understanding

### Direct TOON Usage
```bash
# View TOON file
cat file.toon

# Convert TOON back to JSON for processing
toon --decode file.toon > output.json

# Get token statistics
toon --stats file.toon
```

### LLM Prompting
```markdown
You are an AI agent expert. Use this knowledge base to answer questions:

```toon
[Include TOON content here for efficient prompting]
```
```

## Tools & Scripts

### Conversion Scripts
- **`yaml_to_toon_converter.py`**: Automated YAML → TOON conversion
- **`pdf_to_yaml_converter.py`**: PDF → YAML extraction (previous step)

### TOON CLI Commands
```bash
# Install TOON CLI
npm install -g @toon-format/cli

# Convert JSON to TOON
toon --encode input.json -o output.toon

# Convert TOON to JSON
toon --decode input.toon -o output.json

# Show token statistics
toon --stats file.toon
```

## File Format Specifications

### TOON Features Used:
- **Array Indexing**: `sections[108]` - compact array representation
- **Schema Inference**: Automatic type detection and optimization
- **Unicode Support**: Full UTF-8 compatibility
- **Streaming**: Efficient for large datasets

### Validation
All TOON files have been validated to ensure:
- ✅ Round-trip compatibility (TOON → JSON → TOON)
- ✅ Data integrity preservation
- ✅ Schema consistency
- ✅ Token efficiency verification

## Next Steps

The TOON knowledge base is now ready for:
1. **AI Agent Integration**: Direct use in prompts and context
2. **Cursor IDE Workflows**: Efficient @doc references
3. **RAG Systems**: Optimized retrieval and generation
4. **LLM Fine-tuning**: Token-efficient training data

## Repository Reference
- **TOON Specification**: https://github.com/toon-format/toon/blob/main/SPEC.md
- **TOON CLI**: https://github.com/toon-format/toon#cli
- **LLM Integration Guide**: https://github.com/toon-format/toon#using-toon-with-llms
