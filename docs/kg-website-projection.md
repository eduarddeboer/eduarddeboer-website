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
