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

For authoring, open the `content/` directory as an Obsidian vault. Use normal Markdown links rather than Obsidian-only wikilinks so the source remains portable.

See `ARCHITECTURE.md` for the source-of-truth rules and deployment model.
