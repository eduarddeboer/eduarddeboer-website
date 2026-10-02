# Content authoring

Open this `content/` directory as the Obsidian vault.

## Rules

- Use normal Markdown links: `[label](../path/)`.
- Keep page-owned media in the same page bundle as the Markdown file.
- Do not paste iframe or script embeds into Markdown.
- Use the privacy shortcodes for video and audio.
- Use `kgRef` for the primary graph entity represented by a page.
- Use `about` and `mentions` for graph entities discussed by a page.
- Keep factual identifiers, rights metadata and entity relationships in the knowledge graph rather than duplicating them here.
- Give corresponding EN/NL pages the same `translationKey`.

A later KG-sync workflow will update `../data/kg/snapshot.json`; that machine-generated file is not part of the Obsidian vault.
