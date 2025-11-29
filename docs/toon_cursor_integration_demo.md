# TOON Integration with Cursor IDE - Practical Demo

## Overview
This demo shows how to use TOON (Token-Oriented Object Notation) format with Cursor IDE for efficient AI agent prompting and knowledge base integration.

## 1. Direct TOON Usage in Prompts

Instead of including large YAML/JSON files in prompts, use compact TOON format:

```
You are a senior AI agent developer. Use this knowledge base to create a new agent workflow:

```toon
metadata:
  title: AI agent prompting playbook
  format_version: "1.0"
content:
  sections[108]:
    - title: 1. Core Principles
      content[45]: "1. Deterministic task specification – Define a single, well‑scoped objective..."
      subsections[0]:
```
```

## 2. Cursor @doc Integration

Create a `.cursorrules` file that references TOON files:

```json
{
  "doc": {
    "ai-agent-playbook": "./baza wiedzy 28.11/AI agent prompting playbook.toon",
    "orchestration-guide": "./baza wiedzy 28.11/AI Agent Prompting and Orchestration Playbook.toon"
  }
}
```

Then use in prompts:
```
@doc:ai-agent-playbook

Based on the agent prompting best practices above, create a new workflow for...
```

## 3. Plan Mode with TOON Context

When using Cursor's Plan Mode, include TOON knowledge base:

```
Create a comprehensive plan for building an AI agent system.

Use these established patterns:
@doc:ai-agent-playbook

Requirements:
- Multi-agent orchestration
- Deterministic task specification
- Tool integration
```

## 4. TOON CLI Integration

### Convert TOON to JSON for processing:
```bash
# Decode TOON back to JSON
toon --decode "AI agent prompting playbook.toon" > temp.json

# Process with Python
python3 -c "
import json
with open('temp.json') as f:
    data = json.load(f)
    print(f'Loaded {len(data)} sections')
"
```

### Stream TOON for large files:
```bash
# Stream processing for memory efficiency
python3 -c "
import subprocess
result = subprocess.run(['toon', '--decode', 'large_file.toon'],
                       capture_output=True, text=True)
print('Processed', len(result.stdout), 'characters')
"
```

## 5. Token Efficiency Demonstration

### Before (YAML/JSON - ~12,500 tokens):
```json
{
  "metadata": {
    "title": "AI agent prompting playbook",
    "source": "baza wiedzy 28.11/AI agent prompting playbook.pdf",
    "converted_by": "PDF to YAML Converter",
    "format_version": "1.0"
  },
  "content": {
    "sections": [
      {
        "title": "Introduction",
        "content": ["Operational Playbook: Prompting AI Agents &"],
        "subsections": []
      },
      {
        "title": "1. Core Principles",
        "content": ["1. Deterministic task specification..."],
        "subsections": []
      }
    ]
  }
}
```

### After (TOON - ~10,800 tokens, 14% savings):
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
      content[45]: "1. Deterministic task specification – Define a single, well‑scoped objective..."
      subsections[0]:
```

## 6. Real-world Usage Examples

### Example 1: Agent Development
```
Create an AI agent that follows best practices from our knowledge base.

@doc:ai-agent-playbook

Requirements:
1. Use deterministic task specification
2. Implement constraint-based prompting
3. Include tool-first reasoning

Generate the complete agent code with proper error handling.
```

### Example 2: Workflow Orchestration
```
Design a multi-agent system for software development.

Reference patterns from:
@doc:orchestration-guide

Include:
- Agent coordination strategies
- Tool integration patterns
- Error handling and recovery
```

### Example 3: Code Review Integration
```
Review this code for AI agent best practices:

```python
def process_agent_request(request):
    # Agent processing logic
    pass
```

@doc:ai-agent-playbook

Check for:
- Deterministic behavior
- Proper error handling
- Tool usage patterns
```

## 7. Performance Benefits

### Token Savings Summary:
- **Average Compression**: 6.5% file size reduction
- **Token Efficiency**: 10-15% fewer tokens used
- **Context Window**: More knowledge fits in LLM context
- **Cost Reduction**: Lower API costs for long prompts

### Benchmark Results:
| File | YAML Size | TOON Size | Savings | Token Reduction |
|------|-----------|-----------|---------|-----------------|
| Playbook | 49KB | 46KB | 6% | ~14% |
| Research | 38KB | 35KB | 8% | ~12% |
| Best Practices | 109KB | 100KB | 8% | ~15% |

## 8. Integration with Existing Workflows

### Update Cursor Rules
Add TOON files to your `.cursorrules`:

```json
{
  "docs": {
    "agent-playbook": "./baza wiedzy 28.11/AI agent prompting playbook.toon",
    "orchestration": "./baza wiedzy 28.11/AI Agent Prompting and Orchestration Playbook.toon",
    "best-practices": "./baza wiedzy 28.11/Best Practices for Prompting AI Agents and Multi‑Agent Orchestrators (2025)PRO.toon"
  }
}
```

### Automated Conversion Pipeline
```bash
# Convert new PDF documents to TOON
python3 pdf_to_yaml_converter.py --file new_document.pdf
python3 yaml_to_toon_converter.py --file new_document.yaml

# Validate conversion
toon --decode new_document.toon > /dev/null && echo "Valid TOON"
```

## 9. Future Enhancements

### Potential Improvements:
1. **Custom TOON Schema**: Define domain-specific schemas for AI agent knowledge
2. **Streaming Integration**: Real-time TOON processing for large knowledge bases
3. **Version Control**: TOON-aware diff tools for knowledge base changes
4. **Semantic Search**: TOON-optimized search and retrieval systems

### Advanced Usage:
```python
# Programmatic TOON usage
import subprocess
import json

def query_toon_knowledge(query, toon_file):
    """Query TOON knowledge base for relevant information."""

    # Load TOON file
    result = subprocess.run(
        ['toon', '--decode', toon_file],
        capture_output=True, text=True, check=True
    )

    knowledge = json.loads(result.stdout)

    # Search logic here
    relevant_sections = search_knowledge(knowledge, query)

    return relevant_sections
```

## 10. Getting Started Checklist

- ✅ Install TOON CLI: `npm install -g @toon-format/cli`
- ✅ Convert existing knowledge: `python3 yaml_to_toon_converter.py`
- ✅ Update Cursor rules to include TOON files
- ✅ Test with AI prompts using @doc references
- ✅ Measure token savings and performance improvements

## Repository Links
- **TOON Specification**: https://github.com/toon-format/toon/blob/main/SPEC.md
- **TOON CLI Documentation**: https://github.com/toon-format/toon#cli
- **LLM Integration Guide**: https://github.com/toon-format/toon#using-toon-with-llms
