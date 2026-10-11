---
name: prelaunch-check
description: "Pre-launch check for a public website or web app. Every row is a probe that returns PASS, FAIL or N-A with the URL or command that decided it: four launch basics (share image, contact path, custom 404, consent banner), security, operations, secrets and indexing, plus an advance / hold / roll-back table for the hours after release. Findings only, never an authorization to deploy. Use before launching or relaunching a site, or when asked whether a site is ready to launch. Invoke with /prelaunch-check <url> [--repo <path>]."
metadata:
  version: 1.0.0
---

# Pre-Launch Check

Pattern after addyosmani/agent-skills (MIT).

Walk the site through every row below and report each one. The report is a set of findings for whoever owns the
release. This skill never deploys, never rolls back, and never calls a launch approved.

## Inputs

- `<url>`: the live or staging site. Required.
- `--repo <path>`: the source checkout, for the secrets, dependency and migration rows.
- For rows that sign in or write: a staging copy, two test accounts and test-mode payments. Never probe with a real
  card, a customer's account or production data; with no safe target, the row is N-A.

## Verdicts and evidence

- **PASS** or **FAIL**: name the URL or command, and what it returned.
- **N-A**: the row does not apply ("no sign-in on this site"), or this run could not reach what decides it ("needs
  the provider console"). Say which. A row nobody examined is never PASS.
- Read headers and raw HTML with `curl -s -D - -o <file> <url>`. A fetch tool that converts pages to text drops `<head>`.
- Secrets: write scanner output to a file and report counts, file paths and detector names only. Never print a secret.

## Launch basics (L1–L4)

Defined here once; other skills cite this block. Their near misses are not these checks: seo-audit's soft-404 item
reads only the status code, site-architecture's link audit never looks at the 404 page, analytics-tracking's consent
wiring doesn't show that a banner exists, and the image skill's OG markup doesn't prove every page has an image.

| ID | Check | PASS when | Decide with |
|---|---|---|---|
| L1 | Share image | Every public page's raw HTML has `og:image` (an absolute https URL answering 200 with an image type; 1200×630 suits most networks), `og:title` and `og:description` | `curl -s <page>` and read its `og:` meta tags; then GET the image URL |
| L2 | Contact path | Every public page reaches a person within two clicks (a form, an email address or a portal message; no phone number needed), and the path works. Best proof: a test message arrives. Read-only proof: the form's endpoint exists, or the address's domain has MX records. Name the proof used | The page's links; the form's endpoint; one test message |
| L3 | Custom 404 | A made-up URL shows the site's own page, with its navigation and a way back, not the host's or framework's default ("This page could not be found", "404 Not Found") | `curl -s <origin>/no-such-page-<random>` |
| L4 | Consent banner | If the site sets non-essential cookies or loads analytics, ad or session-replay scripts, a banner appears before they load and rejecting is as easy as accepting. Only essential cookies and no trackers: N-A, citing that evidence | `Set-Cookie` headers; script hosts in the raw HTML and in the browser's network list (a tag manager injects trackers after JS runs) |

## Security

| ID | Check | PASS when | Decide with |
|---|---|---|---|
| H1 | Security headers | The HTML response has `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, a `Content-Security-Policy` and a framing rule (`frame-ancestors` or `X-Frame-Options`) | `curl -s -D - -o /dev/null <url>` |
| H2 | CORS scoped | No route grants a foreign origin: it neither echoes the origin in `Access-Control-Allow-Origin` nor sends `*` with credentials | `curl -s -D - -o /dev/null -H "Origin: https://example.invalid" <api-route>` |
| H3 | Rate limits | Sign-in, sign-up, password reset and every route that spends money (sends email or SMS, calls a paid AI model, charges a card) answer 429 or lock out within 20 quick tries | 20 requests on staging, or the limiter on each route in code (file:line) |
| H4 | Auth on the server | Signed out, every page and API route that shows or changes private data answers 401, 403 or 404, or redirects to sign-in | GET each route in the router's list with no cookies |
| H5 | No cross-account reads | With two test accounts, A asking for B's record by ID gets 403 or 404 | B's record URL or API call, made as A |
| H6 | Bad input is a 4xx | Malformed JSON, wrong types and oversized fields on each write route answer 400 or 422, never 500 | One malformed request per write route, on staging |
| H7 | No internals in errors | No stack trace, file path, query text or debug page in any error this run triggered (L3, H6, a forced 500) | The response bodies |
| H8 | AI spend cap | Every paid AI provider the app calls has a spend limit or budget alert set at the provider; an in-app guard doesn't count | The provider's billing settings |

## Operations

| ID | Check | PASS when | Decide with |
|---|---|---|---|
| O1 | Migrations | Every schema change in the release is applied, or the deploy runs it exactly once | The migration list against the deploy step |
| O2 | Health endpoint | A health route answers 200 | `curl -s -o /dev/null -w '%{http_code}' <origin>/<health-route>` |
| O3 | Error reporting | Server and client errors reach an error tracker | A test error seen in the tracker, or the tracker's init in the shipped code carrying its key (a variable left unset at build time sends nothing) |
| O4 | Restore tested | A backup was restored to a scratch database within the last 90 days and its row counts matched | The restore log or ticket |
| O5 | 500 page | A server error shows the site's own error page, without internals | Force an error on staging, or find the framework's error page in the code |
| O6 | Phone run | The home page and the main flow work on a throttled mid-range phone with LCP ≤ 2.5 s and CLS ≤ 0.1 | The perf-trace skill's phone step, or PageSpeed Insights' mobile run |
| O7 | Flows end to end | Sign-up, payment and password reset each finish, send their email and land where they should | Walk each on staging with a test account and test-mode payments |

## Secrets and dependencies

Run trufflehog (on PATH or the team's tools folder) offline. Always pass `--no-verification` (without it, each
candidate secret is sent to its provider to be tested) and `--no-update` (no update check). `--fail` exits 183 when
anything is found.

| ID | Check | PASS when | Decide with |
|---|---|---|---|
| S1 | No secrets in shipped code | The built output (`dist/`, `build/`, `.next/static/`) has no findings. Build-time variables inlined into client code never reach git, so scan the build; from outside, save the JS the live site serves into an empty folder and scan that | `trufflehog filesystem <dir> --no-verification --no-update --fail > <out-file>` |
| S2 | No secrets in history | The history scan is clean, or every finding is listed as rotated at its provider (removing the commit does not un-leak a key) | `trufflehog git file://. --since-commit <base> --no-verification --no-update --trust-local-git-config --fail > <out-file>`; drop `--since-commit` before a first launch, to scan all history |
| S3 | Dependency audit | No critical or high advisories in production dependencies | `npm audit --omit=dev --audit-level=high`, `pip-audit`, or the ecosystem's equivalent |

`--trust-local-git-config` scans the repo in place; without it, trufflehog first clones it to a temp folder. Its
named detectors cover providers that gitleaks' default rules don't name (Railway and Tailscale tokens, for example),
but not every provider: it has no Intuit or Backblaze B2 detector, and it catches a Neon connection string only as a
Postgres URI. For a provider with no named detector, a generic rule or a targeted grep is the check.

## Indexing and rendering

| ID | Check | PASS when | Decide with |
|---|---|---|---|
| I1 | Page in the raw HTML | With no JavaScript, each key page's HTML carries its own title, meta description, H1 and opening text, not an empty app shell | `curl -s <page>`; fixes are in the seo-audit skill's rendering check |
| I2 | Canonical | Each key page has an absolute `<link rel="canonical">` to itself | The same response |
| I3 | robots.txt | `/robots.txt` answers 200 as text, blocks nothing public and names the sitemap | `curl -s -D - <origin>/robots.txt` |
| I4 | Sitemap | The sitemap answers 200 as XML and lists the public pages | `curl -s <origin>/sitemap.xml`, or the one robots.txt names |
| I5 | Unknown URLs are 404 | A made-up URL at the root and under each dynamic route answers 404; a 200 is a soft 404 on every typo | `curl -s -o /dev/null -w '%{http_code}' <url>` |

## After release: advance, hold or roll back

Read about 1 hour and 24 hours after release, and at each step of a staged rollout, against the same hours before it.

| Signal | Advance | Hold and look | Roll back |
|---|---|---|---|
| Server error rate (share of 5xx) | up to 1.1× baseline | 1.1× to 2× | over 2× |
| p95 response time | up to 1.2× baseline | 1.2× to 1.5× | over 1.5× |
| New client-side error types | none | in under 0.1% of sessions | in 0.1% of sessions or more |

Data loss, a leaked secret or an open security hole reads Roll back, whatever the table says. With no baseline (a
first launch), any 5xx on the walked flows or any new client error type reads Hold. The reading is a finding; the
release owner makes the call.

## Report

One table with every row, in the order L1–L4, H1–H8, O1–O7, S1–S3, I1–I5:

| ID | Verdict | Decided by (URL or command, and what it returned) | Note |
|---|---|---|---|

Then the counts (PASS, FAIL, N-A), the FAILs in fix order (anything that leaks data or money first), and the rollout
reading if a release has happened. Close with: "Findings only, not an approval to deploy."
