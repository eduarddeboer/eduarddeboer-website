# Content policy

This site uses precise, verifiable language. Marketing copy must not outrun the underlying evidence.

## Professional context

The homepage must make Eduard de Boer's current professional context explicit:

- specialist in timber legality, deforestation-free supply chains and due diligence;
- currently working at Ingenieursbureau Evan Buytendijk (IEB).

eduarddeboer.com is the personal knowledge, publication and authority layer. It must not present itself as a replacement for IEB or obscure the current IEB affiliation.

## Environmental and sustainability claims

Because environmental marketing claims require particular care under the EU consumer-law framework, including the EmpCo/ECGT context, public copy must prefer specific, verifiable descriptions over generic sustainability slogans.

Preferred language describes the actual subject or evidence, for example:

- timber legality;
- due diligence;
- traceability;
- risk assessment and risk mitigation;
- deforestation-free supply chains when used in the relevant legal or otherwise substantiated sense;
- EUDR and EUTR compliance requirements;
- FSC® and PEFC certification;
- audits, evidence and documented controls.

Do not use vague promotional claims such as "duurzame impact", "duurzame toekomst", "duurzame kansen", "milieuvriendelijk", "ecovriendelijk", "green choice", "sustainable impact" or similar language unless a future, explicit legal/content review adds a narrowly defined exception.

Words such as "duurzaamheid" or "sustainability" are not prohibited when they name a field, rule, policy topic or otherwise specific subject. The rule targets unqualified promotional claims, not factual discussion of sustainability.

"Ontbossingsvrij" / "deforestation-free" is not decorative marketing language. Use it where the legal definition, evidence or context supports the term.

## FSC trademark

In public-facing copy, always write:

    FSC®

Do not publish standalone `FSC` without the registered trademark symbol. This applies to headings, body copy, navigation, cards, metadata and generated website text.

Internal identifiers, filenames and source-code symbols are not public copy and do not need the symbol.

## Automated enforcement

`python3 scripts/validate.py` checks public-facing text sources for:

1. standalone `FSC` without `®`;
2. a controlled list of vague environmental/sustainability marketing phrases;
3. the existing portability, privacy and knowledge-graph contracts.

The automated list is intentionally narrow. It is a guardrail, not a substitute for substantive review of claims in context.
