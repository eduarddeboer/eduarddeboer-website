<%*
const lang = await tp.system.suggester(
  ["Nederlands", "English"],
  ["nl", "en"],
  true,
  "Taal / language"
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
  "kgRef (optioneel, bijv. article/...)",
  ""
)) || "";
const yaml = (value) => '"' + String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
const folder = `${lang}/insights/${slug}`;
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
  - article
---

`;

if (lang === "nl") {
  tR += `Schrijf hier een korte, zelfstandige introductie die de kernvraag en relevantie uitlegt.

## Kern

<% tp.file.cursor(1) %>

## Analyse

<% tp.file.cursor(2) %>

## Praktische betekenis

<% tp.file.cursor(3) %>

## Bronnen

- <% tp.file.cursor(4) %>
`;
} else {
  tR += `Write a short, self-contained introduction that explains the central question and why it matters.

## Key point

<% tp.file.cursor(1) %>

## Analysis

<% tp.file.cursor(2) %>

## Practical implications

<% tp.file.cursor(3) %>

## Sources

- <% tp.file.cursor(4) %>
`;
}
%>
