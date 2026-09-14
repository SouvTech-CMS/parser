# AGENTS.md - Agent Rules (parser)

Etsy orders parser for SouvTech CMS: fetches receipts from Etsy API every minute and uploads
them to the backend. Only Etsy is implemented and used (Amazon/Ebay parsing does not exist).

## Read first

- `agent-docs/README.md` - index of short docs (loop, payload, Etsy auth, servers)
- `../backend/agent-docs/overview.md` - the whole system and where the parser fits

## Non-negotiables

- Minimal diff: change only what the task requires, match local style
- Parser cannot be run locally: no Etsy tokens, `data/` is server-only state. Verify with
  syntax/static checks and by calling backend `POST /parser/orders/upload/` with a sample payload
- Never call Etsy API from a developer machine, never print or log Etsy tokens
- Don't shorten the 60s cycle or add per-order Etsy requests without checking API quota
- No new dependencies without approval

## Tech & workflow

- Python 3.11, `requests`, `etsyv3`, `loguru`, `pydantic`; deps in `requirements.txt`
- Runs in Docker (`docker-compose.yml`, `python3 /app/src/parser.py`), `src/` and `data/` are
  bind-mounted, so deploy = `git pull` + restart on the server (no CI workflow)
- Branch `main` is production; feature branches with semantic names, PR into `main`
- Conventional Commits: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`

## Code style

- 4 spaces, double quotes, f-strings, `X | None` instead of `Optional`, lines under 88 chars
- Keyword arguments where it improves clarity; comments explain why (`# NOTE:`, `# TODO:`)
