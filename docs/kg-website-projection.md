# KG → website section projection

The website does not mirror the complete knowledge graph. It consumes a pinned,
reviewed projection of the KG at build time.

## Goals

- keep `eduarddeboer.com` independent from the runtime availability of
  `data.eduarddeboer.com`;
- reuse verified KG entities instead of duplicating factual metadata in page copy;
- expose enough semantic context to make each public section useful without
  turning the website into a database dump;
- make every website build reproducible by pinning one exact KG commit.

## Files

- `data/kg/snapshot.json` contains the projected entities and relations.
- `data/kg/sections.json` maps public website sections to groups of entity IDs.
- page front matter uses `kg_section` to select a section projection.
- `layouts/partials/kg-section.html` renders the generic entity cards.
- `scripts/validate.py` verifies the snapshot, source commit, section mappings
  and all relation endpoints.

## Selection policy

An entity belongs in the website projection when it materially supports current
public content. The initial projection covers:

- **About:** Eduard de Boer, IEB, ISO 19011 and current EUDR/EUTR/FSC®/PEFC context.
- **Expertise:** EUDR, EUTR, due diligence, geolocation, traceability, risk
  assessment, auditing and selected authoritative guidance/certification context.
- **Experience:** countries explicitly mentioned in the current professional
  profile and selected public audit articles that substantiate field experience.
- **Speaking & media:** current professional speaking plus the five documented
  De Rijdende Rechter appearances.
- **Publications:** selected current professional articles in the pinned KG.

The projection deliberately excludes unrelated historical entities merely because
they exist in the KG. Historical material can be added when it serves a specific
page or editorial purpose.

## Update rule

A KG refresh is a controlled content change:

1. choose and record an exact KG commit;
2. update the projected entity fields from that commit;
3. update section membership only where editorial relevance changed;
4. run validation and Lighthouse checks;
5. deploy the exact validated website artifact.

The site never fetches live KG data at request time.


## Contextual JSON-LD projection

The human-readable site and the structured-data graph use the same pinned KG
projection, but they serve different audiences.

For each page:

1. visible, editorially relevant KG entities are the **seed entities**;
2. the page node links those seeds with the most accurate Schema.org relation
   (`about`, `mentions`, `hasPart`, `mainEntity`, etc.);
3. each seed entity is emitted as a compact JSON-LD node;
4. direct relation targets of a seed are also emitted so relationships such as
   `Article -> about -> Legislation`, `TVEpisode -> contributor -> Person` and
   `Person -> knowsAbout -> DefinedTerm` resolve inside the same graph;
5. expansion stops after that direct target. The website never recursively dumps
   the complete knowledge graph into a page.

The canonical website Person node remains `https://eduarddeboer.com/#person`.
KG relations that target `person/eduard_de_boer` are reconciled to that node.
The Person node in turn uses `sameAs` to connect to the canonical KG entity URI
and reviewed external identities.

### Page semantics

- Home: `ProfilePage` with Eduard de Boer as `mainEntity`, visible professional
  entities as `mentions`, and the three visible latest publications as `hasPart`.
- About: `AboutPage` with Eduard de Boer as `mainEntity`.
- Expertise: `WebPage` with substantive legislation/concepts under `about` and
  guidance/certification context under `mentions`.
- Experience: `WebPage` with Eduard de Boer as `mainEntity`, plus visible
  countries and selected audit publications.
- Speaking & media: `CollectionPage` with explicit `ItemList` collections.
- Publications: `CollectionPage` with separate authored-publication and
  interview/media `ItemList` collections.

CI validates both the source projection contract and the generated JSON-LD in the
production-canonical Hugo artifact. A page may not silently show a configured KG
entity while omitting it from its structured-data projection.
