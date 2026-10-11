---
name: systematic-debugging
description: "Find a bug's cause before fixing it. Use when something is broken, failing, slow, hanging or wrong, when a fix did not hold, or before proposing any fix: reproduce the user's signal cheaply at the real entry point, compare a working control, treat facts as constraints, split competing hypotheses with the cheapest check, instrument component boundaries, and stop after three failed fixes."
---

# Systematic debugging

Pattern after obra/superpowers (MIT).
Pattern after Cindy Sridharan, "How to effectively debug when you no longer understand the code" (copyconstruct, Medium,
2026-10-10; no licence stated, ideas only).

No fix is proposed until the failure has been shown and its cause narrowed by evidence. Spend no more time on tests than
finding the bug needs.

## 1. Reproduce first, cheaply, at the real door
- The real door is the entry point the user went through: the HTTP route, the page, the command, the job.
- Show the failure with the cheapest thing that reaches it: a curl, a query through the product's own read path (never a
  hand-written query standing in for it), a browser step, or a throwaway `repro_*` script kept out of the test tree. If
  your process does not let this session run test suites, the repro is one of these, not a test.
- It counts only if it shows the user's signal: the same error, the same wrong value. A repro that fails some other way
  proves that *a* bug exists, not that it is this one.
- Three tries without a faithful repro: stop building repros and gather facts (§3).
- Run it before the fix and again after your last edit; quote both outputs beside the claim.

## 2. A working control beside the failing case
Name the failing case and a control: the same flow working (another account, the flag off, the last good build), or the
same flow failing differently when the working path is too unlike it. A fact present in both is noise: it can rule a
hypothesis out, never in. A fact present only in the failing case is a signal, and every hypothesis starts from one.

## 3. Facts are constraints
- Facts are logs, traces, configs, versions, measurements and the user's report. Each one carries where and when it was
  gathered (host, build, tree, time window, viewport). A fact is re-gathered, never argued with; a figure you remember is
  not a fact until you re-read it.
- The user's report is a fact. A green suite is not evidence against it: it shows only what the tests' author expected,
  so read what the tests assert.
- A hypothesis lives only while it fits every fact. Read the code last: it shows what can happen, not what did.

## 4. Competing hypotheses, cheapest discriminating check
- Write 2-5 hypotheses that fit the facts, each with the observation that would kill it, named before you look.
- Prefer the signal that the fewest hypotheses explain. A symptom metric (latency up, errors up) fits them all and
  narrows nothing; a hypotheses-by-facts table turns this into a count.
- Run the cheapest check whose result tells the survivors apart. Then test fixes one at a time: one change, one re-run.
- A reviewer, human or model, is for elimination: one cited contradicting fact kills a hypothesis, and an objection that
  cites no fact is dropped. The same model with the same context is one opinion, not two.

## 5. Instrument the boundaries before fixing a cross-component failure
When the data crosses more than one component (page -> API -> service -> store, process -> process), put a log or probe
on each side of every boundary it crosses, run the repro once, and read which hop lost or changed the value. Only then
state the hypothesis and propose the fix.

## 6. When no hypothesis fits every fact
In order:
1. Re-check how each fact was gathered (§3).
2. Split a coarse hypothesis into its parts.
3. Merge hypotheses that each explain only one symptom.
4. Combine two partial fits, then remove each part in turn to prove it is necessary.
5. Only then write a new hypothesis, from the facts alone.

Still nothing: gather facts one layer deeper, cheapest layer first, and stop at the first strong signal.

## 7. Three failed fixes: stop
Three fixes that did not hold mean the model of the system is wrong. Stop patching. Ask which assumption all three
shared, and take that design question to whoever owns the design before a fourth attempt.

## 8. Keeping the repro
After the fix, the repro becomes a committed test only if all of these hold:
- the bug class can recur: wiring, a contract, a permission, money, data;
- it drives the real door, not a helper that re-derives the code under test;
- it is written from the requirement or the bug report, never from the diff;
- it names the requirement or incident it protects;
- it is seen failing on the pre-fix code, by whoever your process lets run tests.

Otherwise the command and its before/after output stay with the fix's evidence. A cheap door check (a status code, a
count through the read path) can become one smoke-check step instead. No test is added for count or coverage.
