<%*
const lang = await tp.system.suggester(
  ["Nederlands", "English"],
  ["nl", "en"],
  true,
  "Taal / language"
);
const section = await tp.system.suggester(
  ["Expertise", "Experience / Ervaring", "Speaking & media", "About / Over"],
  ["expertise", "experience", "speaking", "about"],
  true,
  "Sectie / section"
);
const title = await tp.system.prompt(
  lang === "nl" ? "Titel" : "Title",
  "",
  true
);
const slugify = (value) => value
  .normalize("NFD")
  .replace(/[\u0300-\u036f]/g, "")
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/^-+|-+$/g, "");
const defaultSlug = slugify(title);
const slug = await tp.system.prompt("Slug", defaultSlug, true, false, true);
const translationKey = await tp.system.prompt(
  "translationKey (exact gelijk houden voor NL/EN)",
  defaultSlug,
  true,
  false,
  true
);
const kgRef = (await tp.system.prompt(
  "kgRef (optioneel, stabiele entity-ID)",
  ""
)) || "";
const yaml = (value) => '"' + String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
const folder = `${lang}/${section}/${slug}`;
if (!tp.app.vault.getAbstractFileByPath(folder)) {
  await tp.app.vault.createFolder(folder);
}
await tp.file.move(`${folder}/index`);

tR += `---
title: ${yaml(title)}
description: ""
date: ${tp.date.now("YYYY-MM-DD")}
lastmod: ${tp.date.now("YYYY-MM-DD")}
draft: true
translationKey: ${yaml(translationKey)}
kgRef: ${yaml(kgRef)}
about: []
mentions: []
topics: []
formats:
  - page
---

`;

if (lang === "nl") {
  tR += `Schrijf hier een korte introductie die zelfstandig begrijpelijk is.

## Hoofdonderwerp

[Werk de inhoud hier uit.]

## Relevante bronnen

[Voeg alleen bronnen toe die de zichtbare claims op deze pagina ondersteunen.]
`;
} else {
  tR += `Write a short introduction that is understandable on its own.

## Main topic

[Develop the content here.]

## Relevant sources

[Add only sources that support visible claims on this page.]
`;
}
%>
