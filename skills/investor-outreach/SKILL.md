---
name: investor-outreach
description: Draft cold emails, warm intro blurbs, follow-ups, update emails, and investor communications for fundraising. Use when the user wants outreach to angels, VCs, strategic investors, or accelerators and needs concise, personalized, investor-facing messaging. Invoke with /investor-outreach.
origin: ECC
---

# Investor Outreach

Write investor communication that is short, concrete, and easy to act on.

## When to Activate

- writing a cold email to an investor
- drafting a warm intro request
- sending follow-ups after a meeting or no response
- writing investor updates during a process
- tailoring outreach based on fund thesis or partner fit

## Core Rules

1. Personalize every outbound message.
2. Keep the ask low-friction.
3. Use proof instead of adjectives.
4. Stay concise.
5. Never send copy that could go to any investor.

## Voice Handling

If the user's voice matters, run `brand-voice` first and reuse its `VOICE PROFILE`.
This skill should keep the investor-specific structure and ask discipline, not recreate its own parallel voice system.

## Hard Bans

Delete and rewrite any of these:
- "I'd love to connect"
- "excited to share"
- generic thesis praise without a real tie-in
- vague founder adjectives
- begging language
- soft closing questions when a direct ask is clearer

## Cold Email Structure

1. subject line: short and specific
2. opener: why this investor specifically
3. pitch: what the company does, why now, and what proof matters
4. ask: one concrete next step
5. sign-off: name, role, and one credibility anchor if needed

## Personalization Sources

Reference one or more of:
- relevant portfolio companies
- a public thesis, talk, post, or article
- a mutual connection
- a clear market or product fit with the investor's focus

If that context is missing, state that the draft still needs personalization instead of pretending it is finished.

## Follow-Up Cadence

Default:
- day 0: initial outbound
- day 4 or 5: short follow-up with one new data point
- day 10 to 12: final follow-up with a clean close

Do not keep nudging after that unless the user wants a longer sequence.

## Warm Intro Requests

Make life easy for the connector:
- explain why the intro is a fit
- include a forwardable blurb
- keep the forwardable blurb under 100 words

## Post-Meeting Updates

Include:
- the specific thing discussed
- the answer or update promised
- one new proof point if available
- the next step

## Worked Examples

All names and numbers are synthetic. Lumen Analytics is a seed-stage product analytics startup; the investor is invented.

### Cold email, annotated

Subject: Lumen Analytics — analytics for mid-market SaaS, 11 paying teams

> [Company, category, one proof number. Fully readable in a phone notification — no "quick question" bait.]

Hi Dana,

Your post on why mid-market SaaS teams get priced out of enterprise BI matched what our first 11 customers told us almost word for word.

> [Opener names one real, checkable artifact tied to this investor. If the draft can't do this, it isn't finished — see Personalization Sources.]

Lumen Analytics gives mid-market SaaS teams product analytics without needing a data team. Eight months post-launch: 11 paying teams, $40k MRR growing ~15% month over month, 124% net revenue retention.

> [One sentence of what, one sentence of proof. The numbers persuade — no "excited," no adjectives.]

We're raising a $2M seed. Are you open to a 25-minute call next Tuesday or Thursday afternoon?

> [One concrete, time-bounded ask with options. Not "would love to connect."]

Priya Shah
Co-founder & CEO, Lumen Analytics — previously led analytics at a 400-person SaaS company

> [Sign-off carries exactly one credibility anchor, nothing else.]

### Warm intro forwardable blurb

Written in third person so the connector can forward it verbatim, no editing required. Under 100 words.

Lumen Analytics builds product analytics for mid-market SaaS teams that don't have a data team. Eight months after launch they're at $40k MRR across 11 paying teams, with 124% net revenue retention. Priya (CEO) previously led analytics at a 400-person SaaS company, and her co-founder built that company's data pipeline. They're raising a $2M seed and asked if you'd be open to a 25-minute call — happy to connect you if it's a fit.

## Quality Gate

Before delivering:
- the message is genuinely personalized
- the ask is explicit
- the proof point is concrete
- filler praise and softener language are gone
- word count stays tight
