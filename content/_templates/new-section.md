<%*
const lang = await tp.system.suggester(
  ["Nederlands", "English"],
  ["nl", "en"],
  true,
  "Taal / language"
);
const title = await tp.system.prompt(
  lang === "nl" ? "Sectietitel" : "Section title",
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
const yaml = (value) => '"' + String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
const folder = `${lang}/${slug}`;
if (!tp.app.vault.getAbstractFileByPath(folder)) {
  await tp.app.vault.createFolder(folder);
}
await tp.file.move(`${folder}/_index`);

tR += `---
title: ${yaml(title)}
description: ""
translationKey: ${yaml(translationKey)}
---

`;

if (lang === "nl") {
  tR += `Schrijf hier de introductie van de sectie.

## Onderwerp

[Beschrijf wat bezoekers in deze sectie vinden.]
`;
} else {
  tR += `Write the introduction for this section.

## Topic

[Describe what visitors will find in this section.]
`;
}
%>
