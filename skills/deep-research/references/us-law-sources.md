# US law sources: fetch the official text, cite it with an as-of date

Use this when a research question turns on US federal law: a statute (US Code), a regulation (CFR), or a new or
proposed rule (Federal Register). Search results, AI answers and blog posts are leads, never the source. Fetch the
text from the sources below and cite it in the form at the end. Endpoints were checked on 2026-10-11.

| Need | Source | How | Watch for |
|---|---|---|---|
| Regulations (CFR), current text | eCFR API (no key) | `GET https://www.ecfr.gov/api/versioner/v1/titles.json` gives each title's `up_to_date_as_of` date; then `GET https://www.ecfr.gov/api/versioner/v1/full/<that date>/title-26.xml?part=1&section=1.199A-1` returns one section as XML | Updated daily, but "an unofficial editorial compilation" (Office of the Federal Register). The eCFR web pages redirect scripted fetches to a block page; use the API |
| New and proposed rules | Federal Register API (no key) | `GET https://www.federalregister.gov/api/v1/documents.json?conditions[agencies][]=internal-revenue-service&order=newest` (JSON; swap the agency slug) | A proposed rule is not law: check each document's `type` |
| Statutes (US Code), current | uscode.house.gov (Office of the Law Revision Counsel) | read the section and the release point it is current through | The official current text, but the site can be down for maintenance (it was on 2026-10-11) |
| Statutes, fallback | Cornell LII, `https://www.law.cornell.edu/uscode/text/<title>/<section>` | the section plus its amendment notes | Unofficial. LII's own material is CC BY-NC-SA 2.5: research use, no commercial redistribution. Read the amendment notes for the newest public law |
| Published editions, public laws | GovInfo (GPO). Its API needs a free api.data.gov key; the `https://www.govinfo.gov/link/uscode/<title>/<section>` service needs none | the printed editions | Its US Code is the **2024 edition** (checked 2026-10-11), so it misses everything enacted since, including Pub. L. 119-21 of July 4, 2025. Never cite it as current law |
| (none) | america.gov | do not use | A federal citizen-services AI assistant (GSA), not a law source. Its terms ban automated scraping, say it "is not the agency of record", and say "Nothing here is legal, tax, medical, or financial advice" |

**Cite as:** section + source + as-of date + edition caveat. For example:

- `26 U.S.C. § 199A(i), as amended by Pub. L. 119-21 (July 4, 2025); Cornell LII (unofficial), read 2026-10-11.`
- `26 C.F.R. § 1.199A-1, eCFR, up to date as of 2026-10-08 (unofficial compilation).`

A citation with no as-of date, or one that cites the GovInfo US Code as current law, is incomplete. If a source could
not be reached, say so in the report's gaps rather than citing around it.
