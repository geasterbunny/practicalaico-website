# Getting practicalaico.ai found

State as of 2026-09-02, after the agency revamp went live.

## Done

- `robots.txt` exists and points at the sitemap. The site had none.
- `sitemap.xml` lists all 33 pages, every one verified to return 200.
- Canonicals, the sitemap and internal links all use the **extensionless** URLs
  Cloudflare actually serves. Previously they pointed at `.html` URLs that
  308-redirect, which told Google the canonical URL was a redirect.
- `llms.txt` covers the services, FRANK and the approval gate, for AI search.
- Every guide ends with a link to FRANK early access. Before this, all 27 guides
  were dead ends.
- IndexNow submits the whole sitemap to Bing/Yandex: `py indexnow.py`.
  Re-run it after publishing anything. Bing feeds Copilot and ChatGPT search.

## Only Glen can do these

### 1. Google Search Console — nothing gets into Google without it

IndexNow does not reach Google. Google needs Search Console.

1. https://search.google.com/search-console → Add property → **Domain** →
   `practicalaico.ai`
2. It gives a TXT record. Add it in Cloudflare → DNS → Records → Add record
   (Type `TXT`, Name `@`, Content = the string Google gives you). Verify.
3. Sitemaps → submit `sitemap.xml`
4. URL Inspection → paste `https://practicalaico.ai/` → Request indexing.
   Repeat for `/guides/` and `/#frank`.

Expect nothing for 1–2 weeks. Check Performance → Queries after that.

### 2. Bing Webmaster Tools (optional, 5 minutes)

https://www.bing.com/webmasters — import straight from Search Console once
step 1 is done. IndexNow already pushes URLs, but this shows what Bing did
with them.

### 3. The MailerLite list

The list is the only audience that already exists. A launch email announcing
FRANK early access is the fastest traffic available and costs nothing —
draft is in `.drafts/` when written.

## Measuring

Baseline on the day the revamp shipped: no Search Console property, so zero
recorded impressions. Re-check Search Console → Performance four weeks after
step 1 is complete. If impressions are still ~0 with everything above done,
search is not going to carry this site and the effort belongs elsewhere.
