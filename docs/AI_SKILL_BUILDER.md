# Experimental AI Skill Builder

`janusz skill ai` is an experimental workflow for generating a skill draft with
an AI model and then rendering the final skill package with deterministic Janusz
code.

## Contract

- The AI provider returns only a strict JSON draft.
- Janusz validates the draft with `AISkillDraft`.
- Janusz rejects secret-like draft output before writing files.
- Janusz renders `SKILL.md` and `references/source.json` itself.
- Janusz runs the existing skill lint and score gates on the generated package.
- Unit tests use fake providers and never call external AI services.

The deterministic command remains unchanged:

```bash
janusz skill --file source.json --output-dir skills
```

The experimental AI command is:

```bash
janusz skill ai --file source.json --output-dir skills
```

## Provider Setup

Install the optional AI extra and configure OpenRouter before using the real
provider:

```bash
pip install "janusz[ai]"
export JANUSZ_OPENROUTER_API_KEY=...
```

## Security Model

Source material is wrapped as untrusted data in the prompt. The prompt tells the
model not to follow source instructions, not to reproduce secrets, not to copy
long passages, and to output JSON only.

The model never writes files directly. If the model returns malformed JSON,
schema-invalid JSON, or secret-like content, the command fails with an actionable
error. Generated skills remain experimental and should be reviewed before global
installation.
