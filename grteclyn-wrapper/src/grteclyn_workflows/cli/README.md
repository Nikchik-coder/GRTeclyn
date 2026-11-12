# CLI

Command-line interface for `python -m grteclyn_workflows` and the `grteclyn-workflows` console script.

`__main__.py` is a thin entry point; parsing and dispatch live here.

## Layout

| Path | Role |
|------|------|
| `parser.py` | `build_parser()` — global options and subcommands |
| `main.py` | `main()` — parse args, resolve initial data, dispatch |
| `args.py` | `--set KEY=VALUE` parsing and score-weight helpers |
| `grtresna_args.py` | GRTresna/postload CLI flags shared by optimize and qd |
| `grtresna_context.py` | Build search space + `GRTresnaConfig` from CLI args |
| `episode.py` | `reproduce` and `sweep` single-episode runners |
| `commands/` | One module per subcommand handler |

## Public API

```python
from grteclyn_workflows.cli import main, build_parser
from grteclyn_workflows.__main__ import main, build_parser  # same symbols
```
