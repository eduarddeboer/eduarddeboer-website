# Architecture

## Purpose

eduarddeboer.com is the human publishing and authority layer. The knowledge graph at data.eduarddeboer.com is the semantic identity and factual relation layer.

The website must remain useful when the knowledge-graph host is temporarily unavailable. There is therefore no runtime dependency between the two sites.

## Source-of-truth rules

| Concern | Source of truth | Website use |
| --- | --- | --- |
| Essays, landing pages, narrative copy | `content/` | Rendered by Hugo |
| Entity identity, identifiers and factual relations | knowledge graph | Imported as a versioned build snapshot |
| Media rights, creator, credit, depicts and canonical metadata | knowledge graph | Resolved from the snapshot |
| Page-specific editorial emphasis | front matter | `kgRef`, `about`, `mentions` |
| Site navigation and presentation | Hugo config/layouts | Never written back to the graph |

The graph should be enriched because a website page needs a fact or relationship, not simply to maximise entity count.

## Content and Obsidian

The directory `content/` is the Obsidian vault and Hugo content root.

1. Keep content in portable Markdown.
2. Do not use Obsidian wikilinks as the canonical linking syntax.
3. Use page bundles for local images, posters, transcripts and other page-owned media.
4. Keep machine-generated graph data outside `content/`.
5. Front matter may link to graph entities through stable IDs; it must not duplicate entire entity records.
6. Uncertain entity reconciliation belongs in the graph review process, not in published prose.

## Knowledge-graph build contract

The website consumes only `data/kg/snapshot.json`.

That file is a website-specific projection, not a copy of the full graph. It has an explicit schema version and records the graph commit from which it was produced. It may contain only the entities, relations and media metadata required by the current website build.

A future cross-repository workflow can download a validated graph artifact and run:

    python3 scripts/import_kg_snapshot.py path/to/site-snapshot.json

The website build itself never queries data.eduarddeboer.com over HTTP.

## Semantic model

Stable identities:

- Person: `https://eduarddeboer.com/#person`
- WebSite: `https://eduarddeboer.com/#website`
- Content page: canonical production URL plus `#content`

Pages can link `mainEntity`, `about` and `mentions` to stable graph entity URIs below `https://data.eduarddeboer.com/entity/...`.

## Multilingual structure

English is primary, with explicit language roots:

- `/en/`
- `/nl/`

Corresponding pages use Hugo translations and `translationKey`.

## Media and privacy

No third-party iframe is present in initial HTML. Video uses a local poster and click-to-load. Audio uses `preload="none"`. External maps remain links unless an accurate privacy-preserving local representation exists. Decorative or knowingly inaccurate geographic placeholders are not used.

## Build and release

    Markdown + pinned KG snapshot + pinned theme -> Hugo -> verification -> immutable dist artifact

The artifact always contains production canonical URLs.

Cloudflare staging and production receive the exact same artifact. The included `_worker.js` checks the hostname:

- canonical production host: indexable;
- every other host: `X-Robots-Tag: noindex, nofollow, noarchive`;
- staging `robots.txt`: `Disallow: /`.

This preserves build-once/test-once/promote-exactly.

## CI strategy

The scripts in `scripts/` and the edge-worker tests are the canonical checks. CI calls the same commands that can run locally on the Mac.

The first workflow is intentionally one validation/build workflow. Deployment workflows are added only after the Cloudflare Pages project and repository secrets are configured. The deployment design remains: green main artifact -> staging -> smoke test -> explicit promotion of the exact same artifact -> rollback from retained artifacts.

## Theme

Congo is a pinned Hugo Module. Local customisations live only in this repository; theme files are never edited directly.

## Non-goals

- No client-side application framework.
- No runtime graph API dependency.
- No analytics or advertising tracker by default.
- No account system.
- No hidden remote media preload.
- No automatic publication of uncertain entity matches.
