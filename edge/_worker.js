const CANONICAL_HOST = "eduarddeboer.com";
const WWW_HOST = "www.eduarddeboer.com";

function isCanonicalHost(hostname) {
  return hostname === CANONICAL_HOST;
}

function robotsBody(indexable) {
  if (!indexable) return "User-agent: *\nDisallow: /\n";
  return [
    "User-agent: *",
    "Allow: /",
    "Sitemap: https://eduarddeboer.com/sitemap.xml",
    "",
  ].join("\n");
}

function withSiteHeaders(response, indexable) {
  const headers = new Headers(response.headers);
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()");
  if (!indexable) headers.set("X-Robots-Tag", "noindex, nofollow, noarchive");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.hostname === WWW_HOST) {
      url.hostname = CANONICAL_HOST;
      return Response.redirect(url.toString(), 308);
    }

    const indexable = isCanonicalHost(url.hostname);

    if (url.pathname === "/robots.txt") {
      return withSiteHeaders(
        new Response(robotsBody(indexable), {
          headers: { "Content-Type": "text/plain; charset=utf-8" },
        }),
        indexable
      );
    }

    return withSiteHeaders(await env.ASSETS.fetch(request), indexable);
  },
};
