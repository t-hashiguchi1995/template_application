# Skill Scanner — Reference

## CLI Options (scan / scan-all)

| Option | Description |
|--------|-------------|
| `--policy` | Preset: `strict`, `balanced`, `permissive` or path to custom YAML |
| `--use-behavioral` | Enable behavioral (dataflow) analyzer |
| `--use-llm` | Enable LLM analyzer (needs API key) |
| `--llm-provider` | `anthropic` or `openai` |
| `--llm-consensus-runs N` | Run LLM N times, keep majority-agreed findings |
| `--use-virustotal` | VirusTotal binary scanner |
| `--vt-api-key KEY` | VirusTotal API key (optional) |
| `--vt-upload-files` | Upload unknown binaries to VT (optional) |
| `--use-aidefense` | Cisco AI Defense analyzer |
| `--aidefense-api-url URL` | Override AI Defense API URL |
| `--use-trigger` | Trigger specificity analyzer (vague descriptions) |
| `--enable-meta` | Meta-analyzer for false positive filtering |
| `--verbose` | Per-finding policy fingerprints, co-occurrence metadata |
| `--format` | `summary`, `json`, `markdown`, `table`, `sarif`, `html` |
| `--detailed` | Detailed findings in Markdown |
| `--compact` | Compact JSON |
| `--output PATH` | Write report to file |
| `--fail-on-findings` | Exit with error if HIGH/CRITICAL |
| `--custom-rules PATH` | Custom YARA rules directory |
| `--taxonomy PATH` | Custom taxonomy (JSON/YAML) |
| `--threat-mapping PATH` | Custom threat mapping (JSON) |
| `--check-overlap` | (scan-all) Cross-skill description overlap |

## Commands

| Command | Description |
|---------|-------------|
| `scan PATH` | Scan single skill directory |
| `scan-all PATH` | Scan multiple skills (`--recursive`, `--check-overlap`) |
| `generate-policy -o FILE` | Generate policy YAML |
| `configure-policy` | Interactive TUI for policy |
| `list-analyzers` | List available analyzers |
| `validate-rules` | Validate rule signatures |

## Environment (optional)

- `SKILL_SCANNER_LLM_API_KEY` — LLM analyzer / Meta-analyzer
- `SKILL_SCANNER_LLM_MODEL` — e.g. `claude-3-5-sonnet-20241022`
- `VIRUSTOTAL_API_KEY` — VirusTotal
- `AI_DEFENSE_API_KEY` — Cisco AI Defense

## Scope and Limitations (from upstream)

- **No findings ≠ no risk.** A clean scan does not guarantee the skill is safe.
- Coverage is incomplete; novel/zero-day techniques may be missed.
- False positives and false negatives can occur; tune policy to risk tolerance.
- Human review is essential for high-risk or production use.

## Links

- [GitHub](https://github.com/cisco-ai-defense/skill-scanner)
- [Quick Start](https://github.com/cisco-ai-defense/skill-scanner/blob/main/docs/quickstart.md)
- [Scan Policy](https://github.com/cisco-ai-defense/skill-scanner/blob/main/docs/scan-policy.md)
- [Threat Taxonomy](https://github.com/cisco-ai-defense/skill-scanner/blob/main/docs/threat-taxonomy.md)
