# Wayback preservation of article URLs

The website repository can preserve the public source URLs of Article entities through the Internet Archive's Wayback Machine.

## Scope

The source inventory is `data/kg/snapshot.json`.

Every entity with:

```json
"type": "Article"
```

and a valid HTTP(S) `url` is included. Duplicate URLs are collapsed while retaining the entity IDs in the report.

## Normal behavior

The workflow `.github/workflows/archive-article-urls.yml` runs when the KG snapshot or the archiving implementation changes on `main`.

For each URL it:

1. queries Wayback availability;
2. skips the URL when a capture already exists;
3. submits the URL to Save Page Now when no capture is available;
4. continues when an individual publisher blocks or rejects archiving;
5. uploads `wayback-report.json` as a 30-day GitHub Actions artifact.

This keeps routine runs idempotent and avoids repeatedly submitting the same historical URLs.

## Manual fresh captures

The workflow also supports **Run workflow** from GitHub Actions. Set **force** to true to request a new capture even when an older Wayback snapshot exists.

Use forced recaptures selectively, for example after a source article has materially changed.

## Local inventory check

No network access is needed to inspect what would be processed:

```bash
python3 scripts/archive_article_urls.py --list-only --output /tmp/wayback-inventory.json
```

For a small live test:

```bash
python3 scripts/archive_article_urls.py --limit 1 --output /tmp/wayback-test.json
```

## Limitations

A submitted URL is not guaranteed to become a usable public capture. Publishers can block archival crawlers, require authentication, return bot challenges or rate-limit the Internet Archive. Those cases are recorded as failures in the report and do not block the website release pipeline.

The archive workflow is deliberately separate from site validation and Cloudflare deployment: preservation is useful, but an external Wayback outage must not prevent publishing the website.
