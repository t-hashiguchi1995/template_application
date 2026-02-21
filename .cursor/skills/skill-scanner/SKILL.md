---
name: skill-scanner
description: Runs Cisco AI Defense skill-scanner to audit Cursor/Agent Skills for prompt injection, data exfiltration, and malicious code. Use when the user asks to scan skills, audit agent skills, check skill security, run skill-scanner, or when reviewing or adding files under .cursor/skills or agent skill directories.
---

# Skill Scanner (Cisco AI Defense)

Run [skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) to perform best-effort security scanning of AI Agent Skills (Cursor Skills, OpenAI Codex Skills). Detects prompt injection, data exfiltration, and malicious code via static analysis, behavioral dataflow, and optional LLM/meta analysis.

**Scope:** Detection only; "No findings" does not guarantee a skill is safe. Human review remains essential for high-risk deployments.

---

## When to Use

- User asks to **scan**, **audit**, or **check security** of skills (e.g. `.cursor/skills/`, a skill directory).
- User mentions **skill-scanner**, **Cisco AI Defense**, or **agent skill security**.
- Before recommending or committing new/edited Agent Skills in security-sensitive contexts.

---

## Quick Start

### Install (if not present)

```bash
# Prefer uv (project rule)
uv pip install cisco-ai-skill-scanner

# Or pip
pip install cisco-ai-skill-scanner
```

Optional extras: `[bedrock]`, `[vertex]`, `[azure]`, `[all]` for cloud/LLM analyzers.

### Scan One Skill

```bash
skill-scanner scan /path/to/skill
```

Default: static + bytecode + pipeline. Add `--use-behavioral` for dataflow analysis.

### Scan All Skills (e.g. project skills)

```bash
skill-scanner scan-all .cursor/skills --recursive
```

Use `--check-overlap` to enable cross-skill description overlap checks.

---

## Common Commands

| Goal | Command |
|------|--------|
| Single skill, core only | `skill-scanner scan /path/to/skill` |
| Single skill + behavioral | `skill-scanner scan /path/to/skill --use-behavioral` |
| Full engines (LLM + meta) | `skill-scanner scan /path/to/skill --use-behavioral --use-llm --enable-meta` |
| CI: fail on findings | `skill-scanner scan-all ./skills --fail-on-findings --format sarif --output results.sarif` |
| HTML report | `skill-scanner scan /path/to/skill --format html --output report.html` |
| Stricter policy | `skill-scanner scan /path/to/skill --policy strict` |
| List analyzers | `skill-scanner list-analyzers` |
| Generate policy | `skill-scanner generate-policy -o my_policy.yaml` |

---

## Analyzers (summary)

| Analyzer | What it does | Requirement |
|----------|--------------|-------------|
| Static | YAML + YARA patterns | None |
| Bytecode | .pyc integrity | None |
| Pipeline | Shell command taint | None |
| Behavioral | AST dataflow (Python) | None |
| LLM | Semantic (SKILL.md + scripts) | API key |
| Meta | False positive filtering | API key |
| VirusTotal | Binary hash scan | API key |
| AI Defense | Cloud AI scan | API key |

LLM/Meta: set `SKILL_SCANNER_LLM_API_KEY`, `SKILL_SCANNER_LLM_MODEL` (e.g. `claude-3-5-sonnet-20241022`). `--llm-provider` accepts `anthropic` or `openai`.

---

## Output Formats

- `--format summary` (default), `json`, `markdown`, `table`, `sarif`, `html`
- `--output PATH` to write to file
- SARIF for GitHub Code Scanning; HTML for interactive report with correlation groups

---

## Limitations to Communicate

- **No findings ≠ no risk.** Scanner does not certify security.
- False positives/negatives possible; tune with `--policy` (strict/balanced/permissive) or custom YAML.
- High-risk or production: combine scanning with manual review and threat modeling.

---

## Python SDK (optional)

```python
from skill_scanner import SkillScanner
from skill_scanner.core.analyzers import BehavioralAnalyzer

scanner = SkillScanner(analyzers=[BehavioralAnalyzer()])
result = scanner.scan_skill("/path/to/skill")
# result.findings, result.max_severity, result.is_safe (no HIGH/CRITICAL)
```

---

## More

- [README](https://github.com/cisco-ai-defense/skill-scanner)
- [Quick Start](https://github.com/cisco-ai-defense/skill-scanner/blob/main/docs/quickstart.md)
- For full CLI options and policy tuning, see [reference.md](reference.md) in this skill.
