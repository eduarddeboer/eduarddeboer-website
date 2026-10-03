# Production KG projection sync

Status: bridge step 5/5 — website half.

## Purpose

The website keeps a pinned, local KG snapshot for reproducible builds. It does
not query the knowledge graph at runtime.

After the KG has been validated, staged and explicitly promoted to production,
the website synchronizer checks the public handoff:

- `https://data.eduarddeboer.com/site-snapshot.json`
- `https://data.eduarddeboer.com/release-manifest.json`

Both files must identify the exact same KG commit.

## Semantic drift

A newer KG commit alone is not enough to create a website PR.

`scripts/sync_kg_projection.py` compares the semantic projection while ignoring
only `source.commit`. The comparison includes:

- schema version;
- source repository and production base;
- projected entities;
- projected relations;
- projected media.

If those are unchanged, the existing website snapshot remains valid and no PR is
created.

## Changed projection

When semantic drift exists, the sync workflow:

1. validates the production snapshot structure;
2. validates that the release manifest and snapshot pin the same KG commit;
3. verifies that all existing website section entity references still exist;
4. reuses the stable branch `bridge/kg-projection-sync`;
5. writes `data/kg/snapshot.json`;
6. updates only the matching `source_commit` in `data/kg/sections.json`;
7. runs source validation and projection-sync unit tests;
8. creates or refreshes one website pull request.

The pull request is never auto-merged.

Normal website PR validation then remains authoritative:

- content/source contracts;
- contextual JSON-LD graph checks;
- Hugo build;
- accessibility/performance quality gates;
- Mobile Lighthouse.

## Runner policy

The scheduled sync follows the same preferred-runner policy as the rest of the
project:

- online and idle local macOS runner first;
- GitHub-hosted Ubuntu fallback.

The workflow runs hourly at minute 17 and can also be dispatched manually.

## Production-only handoff

The website intentionally reads the **production** KG endpoint, not staging.

That means a newly merged KG change does not enter the website before the exact
validated KG artifact has been promoted through the existing staging-to-production
release path.

If `site-snapshot.json` is not yet present on production, the sync workflow
reports the handoff as unavailable and exits successfully without modifying the
website.

## Trust boundary

No private KG credential is required.

The closed loop is:

```text
Obsidian / website content
        ↓
website PR entity review
        ↓
private KG review proposal
        ↓
reviewed KG merge
        ↓
validated KG build + staging
        ↓
explicit KG production promotion
        ↓
public site-snapshot.json
        ↓
website semantic drift sync
        ↓
reviewable website PR
        ↓
website validation + publication
```

This keeps both repositories independently buildable and prevents a private
cross-repository write token from becoming part of the normal publishing path.
