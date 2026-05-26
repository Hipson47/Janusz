# Janusz Examples

This directory contains small source documents and generated outputs for the
document -> YAML -> JSON -> skill workflow.

## Inputs

- `inputs/sample_architecture.md`
- `inputs/sample_architecture.yaml`
- `inputs/sample_spec.txt`
- `inputs/sample_spec.yaml`

## Outputs

- `outputs/sample_architecture_janusz.yaml`
- `outputs/sample_spec_janusz.yaml`

## Try The Pipeline

```bash
# Convert a source document to YAML
janusz convert --file examples/inputs/sample_architecture.md

# Create a JSON package from YAML
janusz json --file examples/inputs/sample_architecture.yaml

# Inspect a package
janusz test examples/inputs/sample_architecture.yaml

# Create a skill package from a YAML or JSON package
janusz skill --file examples/inputs/sample_architecture.yaml --output-dir /tmp/janusz-skills
```

## Programmatic Usage

```python
from janusz.converter import UniversalToYAMLConverter
from janusz.json_packager import JSONPackageConverter
from janusz.skill_packager import create_skill_package

converter = UniversalToYAMLConverter("document.md")
converter.convert_to_yaml()

json_converter = JSONPackageConverter("document.yaml")
json_converter.convert()

create_skill_package("document.json", output_dir="skills")
```

## GUI Demo

Run:

```bash
python examples/gui_demo.py
```

The GUI demo describes local document conversion, JSON packaging, skill package
creation, schema management, RAG search, and prompt tooling.
