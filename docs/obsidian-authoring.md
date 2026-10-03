# Obsidian authoring workflow

The website is designed so that the Hugo `content/` directory is also the Obsidian vault. Obsidian is therefore an editor for the editorial layer only; the knowledge-graph snapshot remains outside the vault in `data/kg/`.

## One-time setup

1. Clone the repository locally if it is not already present.
2. In Obsidian choose **Open folder as vault** and select the repository's `content/` directory.
3. Enable **Community plugins**, install **Templater**, and enable it.
4. In **Settings → Templater** set **Template folder location** to:
   `_templates`
5. Prefer manual template creation instead of automatic folder rules. In Templater's **Template Hotkeys**, add the templates you use frequently. This exposes a **Create** command for each template that can also receive an Obsidian hotkey.

The repository ignores `content/.obsidian/`, so local workspace/plugin settings do not become website source. The shared templates in `content/_templates/` are versioned in Git.

## Included templates

### `_templates/new-insight.md`

Use this for a substantive article or analysis in **Publicaties / Insights**.

The template asks for:
- language;
- title;
- URL slug;
- `translationKey`;
- optional primary `kgRef`.

It then creates a Hugo leaf bundle at:

`<lang>/insights/<slug>/index.md`

Put page-owned images and other local media in that same `<slug>/` folder.

### `_templates/new-page.md`

Use this for an evergreen content page below an existing section such as Expertise, Experience, Speaking or About.

It creates:

`<lang>/<section>/<slug>/index.md`

### `_templates/new-section.md`

Use this only when a genuinely new top-level section is needed. It creates:

`<lang>/<slug>/_index.md`

A new section is not automatically added to navigation or to the page-specific KG projection. If the section belongs in the public menu, update the relevant `config/_default/menus.*.toml`. If it needs a contextual entity projection, update `data/kg/sections.json` through the normal KG/site workflow as well.

## Front matter rules

Keep the editorial metadata small and explicit:

- `title`: visible page title.
- `description`: concise search/snippet description that accurately reflects the page.
- `date`: original publication date for dated content.
- `lastmod`: update when the substantive content changes.
- `draft`: keep `true` while writing; change to `false` when publication is intended.
- `translationKey`: use exactly the same value on the Dutch and English versions of the same page.
- `kgRef`: stable KG entity ID for the primary entity represented by the page, when applicable.
- `about`: KG entity IDs that are actual subjects of the visible page.
- `mentions`: KG entity IDs that are materially mentioned but are not primary subjects.
- `topics`: editorial topic labels where useful.
- `formats`: normally `article` for an insight and `page` for an evergreen page.

Do not copy full entity records, identifiers, rights metadata or relationship graphs into Markdown. Those remain knowledge-graph data.

## Links and media

Use ordinary Markdown links, not Obsidian-only wikilinks, because the source must remain portable and directly renderable by Hugo.

For page-owned media use a Hugo page bundle:

```text
nl/insights/example/
├── index.md
├── photo.webp
└── diagram.svg
```

Do not paste third-party iframe or script embeds into Markdown. Use the site's privacy-preserving media patterns instead.

## Recommended editing cycle

Before starting:

```bash
git switch main
git pull --ff-only
git switch -c content/<short-topic-name>
```

Then:

1. Create the note with one of the Templater **Create** commands.
2. Write the content in Obsidian.
3. Add `about`, `mentions` and `kgRef` only when the entity relationship is visible and defensible from the page itself.
4. Create the other language version with the same `translationKey` when both languages are ready.
5. Set `draft: false`.
6. From the repository root run the same source/build checks used in CI, or push the branch and let the PR validation run.
7. Review the staging result before treating the change as published.

## Division of responsibility

Use Obsidian for prose and page-level editorial metadata. Use the knowledge-graph repository/process for stable identities, `sameAs` links, identifiers, factual relations, media rights and provenance. The site build combines those two layers; neither should silently overwrite the other.
