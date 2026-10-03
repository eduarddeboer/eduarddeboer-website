# Website entity-review CI

This is bridge step 2 of the website/KG publishing loop.

The website remains the editorial source of truth for Markdown. The private
knowledge-graph repository remains the source of truth for canonical entity
identity, aliases and factual relations.

## What this workflow does

For trusted branches in this repository, the entity-review workflow:

1. selects the preferred local macOS runner when it is online and idle;
2. otherwise falls back to `ubuntu-latest`;
3. checks out the website proposal without persisted credentials;
4. checks out `eduarddeboer/eduarddeboer-kg` read-only;
5. scans only changed website Markdown on pull requests;
6. runs the PR86 Markdown adapter against the full curated KG;
7. publishes a sanitized summary and JSON artifact;
8. fails only on deterministic front-matter links to KG ids that do not exist.

Known KG mentions without an explicit `about`/`mentions` relation and unknown
proper-noun candidates are review signals, not automatic publication blockers at
this stage.

A manual workflow dispatch scans all website Markdown.

## Privacy boundary

The website repository is public while the KG source repository is private.

The public CI output therefore does **not** contain canonical resolver ids for
automatically matched KG entities. It may only contain:

- website source paths;
- aliases already present in public website content;
- candidate phrases already present in public website content;
- explicit KG ids that were already written into public website front matter;
- aggregate counts;
- the KG commit hash used for the review.

The raw resolver response is never uploaded as an artifact.

External fork pull requests never receive private-KG access and never run on the
self-hosted runner. They continue to receive the ordinary public website
validation only.

## Credentials

Preferred long-term configuration:

- repository secret: `KG_READ_TOKEN`;
- token type: fine-grained PAT or GitHub App token;
- repository access: only `eduarddeboer/eduarddeboer-kg`;
- permission: **Contents: Read** only.

The workflow deliberately does not reuse `RUNNER_ROUTER_TOKEN` for KG content.
If `KG_READ_TOKEN` is absent, the private-KG review is reported as not yet
configured and is skipped without weakening the ordinary website validation.
The checkout uses `persist-credentials: false`.

Bridge step 4 can replace the PAT with a dedicated GitHub App or equivalent
least-privilege cross-repository orchestration mechanism.

## Relationship with the pinned website snapshot

Entity review and website rendering are deliberately separate:

- entity review sees the current full curated KG and can identify semantic work;
- Hugo renders only from `data/kg/snapshot.json`, pinned to an exact KG commit.

A newly discovered entity therefore does not silently enter the website build.
Acceptance and projection refresh remain separate reviewed steps.

## Current failure policy

The review is intentionally conservative:

- unknown explicit `kgRef`, `about` or `mentions` id in the full KG: **fail**;
- known entity mentioned in prose but not linked: **review signal**;
- unknown proper-noun candidate: **review signal**;
- no changed Markdown: **pass**.

Bridge step 3 will add the machine-readable candidate lifecycle and reviewed
reconciliation/enrichment proposals.
