# eduarddeboer.com

Source repository for the human-facing site at https://eduarddeboer.com/.

The site is deliberately split into two layers:

- `content/` is the editorial layer and can be opened directly as an Obsidian vault.
- `data/kg/snapshot.json` is the versioned website projection of the knowledge graph.
- Hugo combines both layers into one self-contained static release candidate.
- Cloudflare serves the exact same candidate on staging and production. The edge worker makes every non-production hostname noindex without rebuilding the HTML.

## Local workflow

Requirements:

- Hugo Extended 0.167.0
- Go (for Hugo Modules)
- Python 3.11+
- Node.js 22+

Commands:

    python3 scripts/validate.py
    node --test tests/edge-worker.test.mjs
    python3 scripts/build.py
    python3 scripts/verify_dist.py
    python3 scripts/archive_article_urls.py --list-only --output /tmp/wayback-inventory.json

For authoring, open the `content/` directory as an Obsidian vault. Use normal Markdown links rather than Obsidian-only wikilinks so the source remains portable. Shared Templater templates live in `content/_templates/`; see `docs/obsidian-authoring.md`.

Public copy also follows `CONTENT_POLICY.md`. The validator enforces selected environmental-claim guardrails and requires the public trademark form `FSC®`.

See `ARCHITECTURE.md` for the source-of-truth rules and deployment model.

Article source URLs can be preserved with the Wayback workflow described in `docs/wayback-archiving.md`.
