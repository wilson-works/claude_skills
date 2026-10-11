# Judging pages with a System One classifier (optional)

Pattern after AgriciDaniel/jev-seo (MIT, © 2026 Agrici Daniel). The method only: don't install or run its CLI.

Use this when an audit needs judgments code can't make (what a page is for, whether it helps a visitor) and you have
API access to a System One classifier such as TypeSafe Jev: typed Choice, Score and yes/no questions, answered with
probabilities. Without one, the audit stays a checklist and these judgments are reported as "not assessed".

## Rules

- The crawl finds, code decides, the classifier judges, the writer explains. Never ask what code can see: a page with
  no meta description gets no meta question, and code labels the homepage itself.
- Every Choice carries an escape option (`other` or `unclear`).
- Score levels describe situations from low to high (four levels here), normalised as level ÷ (levels − 1). Never
  stretch them to 1–10.
- Send bounded text: page text capped (about 6,000 characters, flagged when cut) and an opening that starts after
  the H1 (about 500 characters), so breadcrumbs and navigation aren't read as the opening. Wrappers often cap each
  item at 2,000 characters.
- Put every independent question about one page in one request.

## Decision bands

- Choice: decided at confidence ≥ 0.80.
- Score: decided only when ≥ 0.80 of its probability falls on one side of the midpoint, the side every finding
  threshold uses. Spread between two neighbouring levels on the same side is not doubt.
- Yes/no: decided at P(yes) ≥ 0.80 or ≤ 0.20.
- Everything else is labelled "to verify": a prompt for a person, never a finding on its own.

## Question set

Site questions (send the homepage text, its navigation and up to 80 page titles):

| ID | Type | Question |
|---|---|---|
| business_model | Choice (8 + other) | What kind of organisation runs the site (local service, shop, software, B2B services, publisher, education, nonprofit, personal)? |
| value_prop | Score (4) | Can a first-time visitor tell what is offered, to whom, and why choose it? |
| entity_clarity | Yes/no | Does the homepage plainly give the name, the activity and the market or place? |
| topical_focus | Score (4) | Do the page titles form one coherent set of topics? |
| serves_local_area | Yes/no | Does it serve customers in a named physical area? (Gates any LocalBusiness schema advice.) |

Page questions (send the site context and the page):

| ID | Type | Question | Becomes a finding when |
|---|---|---|---|
| page_type | Choice (10 + other) | Homepage, product or service, listing, article, about, contact, pricing, proof, support or docs, legal? | Never; it filters and groups |
| intent | Choice (5 + unclear) | Informational, commercial, transactional, navigational or local? | Commercial pages get the next-step check |
| importance | Score (4) | How much does this page do to win customers? | Never; it weights every action on the page |
| action | Choice (3) | Keep or improve, rewrite, or merge or remove? | Rewrite; or merge or remove, never on a page of 600+ words |
| helpfulness | Score (4) | Would a visitor who came for this topic need to look elsewhere? | < 0.45 on pages with importance ≥ 0.5 |
| specificity | Score (4) | Generic claims, or concrete first-hand detail? | < 0.45 |
| trust | Score (4) | How much proof of expertise and accountability is shown? | < 0.45 on important pages |
| citable | Score (4) | How many self-contained facts could an AI answer quote? | < 0.45 |
| answer_first | Yes/no, on the opening | Does it say what the reader gets within two sentences? | P(yes) < 0.5 |
| clear_next_step | Yes/no | Is a concrete next action offered? | P(yes) < 0.5 on commercial pages |
| title_fit | Score (4) | Does the title say what the page holds, in a searcher's words? | < 0.45 |
| meta_fit | Score (4) | Does the description summarise what the page delivers? | < 0.45 |
| h1_fit | Yes/no | Does the H1 name the page's topic? | P(yes) < 0.5 |

Policy and contact pages, once decided, get no content or AI findings beyond title and H1 fit.

Competing pages: code shortlists pairs whose title and H1 word sets overlap (Jaccard ≥ 0.4, identical text excluded,
at most 40 pairs). Ask one yes/no per pair: would a searcher be equally well served by either page? P(yes) ≥ 0.6 is
a cannibalisation finding.

## Scoring

- **Area score:** 100 minus, for each finding, its severity points (critical 25, high 12, medium 6, low 2) ×
  (0.5 + 0.5 × reach). Reach is the share of HTML pages affected, or 1 for a site-wide finding.
- **Content quality** = 70% the importance-weighted mean of helpfulness, specificity and trust + 30% rules.
  **AI readiness** = 70% citability, answer-first and entity clarity + 30% rules.
- **Overall:** weighted mean of the scored areas (crawl 20, on-page 15, content 20, links 10, structured data 8,
  AI 12, performance 10, security 5). An unscored area is left out, never counted as zero. A blocked site caps at 20;
  no reliable HTTPS caps at 60.
- **Impact:** severity weight (10, 6, 3, 1) × (0.6 + 0.4 × reach) × (0.6 + 0.8 × the highest importance among the
  affected pages), scaled so the top action is 100.
- **Priority:** P1 = critical, or high with impact ≥ 40. P2 = impact ≥ 30, or any high. P3 otherwise. Quick win =
  impact ≥ 35 with effort in hours.

## Through an MCP wrapper

A classify tool covers Choice: set its auto-accept to 0.80 and its minimum margin to 0 so its band matches the one
above. A Score is a classify over the ordered levels; sum the returned distribution on each side of the midpoint. A
yes/no-probability tool covers the yes/no questions, with auto-accept 0.80.

## How far to trust it

The source measured repeatability (page type identical on 58 of 59 pages across two runs) and agreement with a blind
second model, not with a human answer key; its thresholds are not tuned against human labels. Treat decided answers
as prioritised signals for review and "to verify" answers as open questions.
