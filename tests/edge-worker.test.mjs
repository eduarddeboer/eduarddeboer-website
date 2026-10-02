import test from "node:test";
import assert from "node:assert/strict";
import worker from "../edge/_worker.js";

function envWith(body = "<html>ok</html>") {
  return {
    ASSETS: {
      async fetch() {
        return new Response(body, {
          status: 200,
          headers: { "Content-Type": "text/html; charset=utf-8" },
        });
      },
    },
  };
}

test("preview hosts are noindex without changing the artifact", async () => {
  const response = await worker.fetch(
    new Request("https://preview.example.pages.dev/en/"),
    envWith()
  );
  assert.equal(response.headers.get("X-Robots-Tag"), "noindex, nofollow, noarchive");
});

test("canonical production host is indexable", async () => {
  const response = await worker.fetch(
    new Request("https://eduarddeboer.com/en/"),
    envWith()
  );
  assert.equal(response.headers.get("X-Robots-Tag"), null);
});

test("robots.txt blocks every non-production hostname", async () => {
  const response = await worker.fetch(
    new Request("https://staging.example.pages.dev/robots.txt"),
    envWith()
  );
  assert.match(await response.text(), /Disallow: \/$/m);
  assert.equal(response.headers.get("X-Robots-Tag"), "noindex, nofollow, noarchive");
});

test("www redirects to the canonical apex host", async () => {
  const response = await worker.fetch(
    new Request("https://www.eduarddeboer.com/nl/about/?x=1"),
    envWith()
  );
  assert.equal(response.status, 308);
  assert.equal(response.headers.get("Location"), "https://eduarddeboer.com/nl/about/?x=1");
});
