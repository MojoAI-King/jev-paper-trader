# 14: Using Jev for what it's built for

Researched 2026-10-09 for `docs/research/briefs/14-jev-harness.md`.

## Answer in five lines

1. TypeSafe built Jev (System One, today `jev-1.13.0`) to make fast, typed judgments about a state you hand it:
   routing, classifying, ranking, picking the right value out of a text, and checking a claim against evidence.
   TypeSafe tells builders not to rely on what the model learned in training when current information can be put
   in the state. Its documentation never mentions forecasting or prediction markets.
2. Our main question, "will this market resolve YES under its rules by the time it closes?", goes against
   TypeSafe's own design rules. It hides several judgments in one answer (read the rules, recall the world, compare
   dates, judge the outcome) and leans on knowledge from training. It also lands on three failure modes TypeSafe
   lists for jev-1.13: date comparison, numbers, and multi-step indirection. A Brier of 0.249, Jev's answer
   sitting near 0.5, is the model saying it doesn't know, as TypeSafe's docs describe it.
3. Give Jev reading and checking jobs instead, each made of narrow questions, with code doing the dates, numbers
   and decisions. In order of value: (A) a market reader that pulls out what the market is about, the threshold,
   the comparison and the deadline, for the specialist pricers in briefs 06, 07 and 08; (C) a fact-by-fact check
   of whether Claude's research shows the YES condition already met or no longer possible; (E) labelling how two
   linked markets relate, for brief 02; (D) checking research facts against their source pages; (B) rule-risk
   flags.
4. Outside evidence supports verification over a supplied state. Small specialised checkers match large models
   when the evidence is in the input, and are much worse without it. It is weak for predicting trouble from rule
   text alone, and for finding linked markets with a model alone: in the arbitrage study below, 1,576 flagged pairs
   left 13 real ones. None of these studies used Jev.
5. Every new job needs its error rates measured on about 200 hand-labelled cases before anything acts on it. Its
   history tests cost cents, since Jev is $0.042 per million input tokens. Pin the model version, give each job its
   own question-set version, and leave `papertrade-v2` untouched while the frozen `original` yardstick depends on it.

## Findings

**F1. System One is a judgment model over a supplied state, not a knowledge or forecasting model.** Jev "evaluates
a state and returns typed answers and probabilities". It does not generate text, explain itself or choose its own
next step. The build guide says: "Do not rely on knowledge stored in model weights when current information can
come from your own knowledge base." The use-case map and the cookbooks cover routing, classification, re-ranking,
extracting values (the model picks among candidates found by code), checking citations, guardrails, insurance and
compliance triage, and turning text into features for classical models. Nothing covers forecasting future events,
and nothing rules it out either. Evidence: [System One](https://docs.typesafe.ai/concepts/system-one.md),
[How to build](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md),
[Use-case map](https://docs.typesafe.ai/concepts/use-case-map.md), read 2026-10-09; confirmed 3-0 by the
verification pass. Strength: **strong** as a description of what TypeSafe intends (vendor documentation). That our
forecasting use is a misuse is **our inference**, because TypeSafe says nothing about forecasting either way.

**F2. Three question types; the probability is the answer.** *Choice* picks one option from a set and returns a
probability for every option plus `confidence`. *Score* places the state on ordered, described levels. *Noul* is
the probability that a yes/no statement is true. A Noul has no separate confidence: a value near 0.5 "means the
model gives yes and no similar probability". A Noul value is not a degree of anything ("Is the candidate strong in
Python?" at 0.5 does not mean medium skill). Choice `confidence` = (p_max − 1/n)/(1 − 1/n). It measures how
concentrated the answer is, not the chance it's right. Every answer is limited to the options supplied, and
questions in one request are judged separately; none sees another's answer. Evidence:
[Primitives](https://docs.typesafe.ai/primitives.md), [Noul](https://docs.typesafe.ai/primitives/noul.md),
[Confidence](https://docs.typesafe.ai/confidence.md). Strength: **strong** (documented API behaviour).

**F3. Calibration is claimed as a training goal, not published as a measurement.** Jev is trained with "RLCD"
(reinforcement learning for calibrated decisions) so that "higher probability should correspond to a greater
chance that the answer is correct". TypeSafe adds that "calibration is measured across groups of predictions; it
does not guarantee that an individual answer is correct". It publishes no calibration figures, and says thresholds
"depend on your domain and the performance of the model for your use case". Evidence:
[AI primer](https://docs.typesafe.ai/introduction/machine-learning-primer.md), [System One](https://docs.typesafe.ai/concepts/system-one.md).
Strength: **moderate** (a stated design goal; no independent study of Jev exists). Our own 0.249 on 646 markets
is the only measurement we have of Jev on our task.

**F4. TypeSafe's design rules, and which of them our questions break.** The guide calls decomposition
"probably the most important concept": "Ask the most explicit, narrow, specific, atomic questions you can… Broad
questions hide several judgments behind one answer." Other rules:
- put domain rules and edge cases in `instructions` and `criteria`, and current facts in `state`;
- combine answers in code, with weights, rules or a downstream classical model;
- ask many independent questions in one request;
- send only the state each question needs;
- route unsure answers to a person or a reasoning model.

The [jev-1.13 jaggedness page](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md) (reviewed 2026-10-02) lists
these failure modes:
1. literal reading;
2. math and numbers ("keep the arithmetic in code");
3. date and time comparison ("reads dates as text, not as ordered quantities… Extract components; compare in code");
4. indirection and multi-hop questions;
5. a large state full of irrelevant detail;
6. adversarial content in the state;
7. instructions and criteria that disagree (a Noul where true means no performs worse);
8. Choice option order (it "leans toward the option that comes first");
9. generating text.

Strength: **strong** as TypeSafe's guidance. Caution: a sharper claim, that this page puts multi-hop forecasting
outside Jev's design, was **refuted 0-3** in verification. The page says these patterns cost accuracy, not that
forecasting is out of scope.

How our five `papertrade-v2` questions measure against this (our reading, not TypeSafe's):

| Question | What goes against the guidance |
|---|---|
| `p_yes` | One question for a whole outcome: read the rules, know the world, check timing ("by the time it closes", which is date comparison), and often a numeric threshold (WTI above $95). It leans on knowledge from training, which the guide says not to rely on. Without research the state holds nothing that decides the answer, so a Noul near 0.5 is the honest reply. |
| `p_no` | The same judgment again with a negation. TypeSafe claims Jev returns stable answers across repeated calls ([self-consistency cookbook](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook.md)), so the YES/NO "framing gap" may measure wording sensitivity rather than uncertainty. TypeSafe's own uncertainty signal for a Noul is its distance from 0.5. |
| `rules_clear` | Several judgments in one: is a source named, is the condition checkable, is there discretion, do the title and rules agree. "A neutral person would know exactly" is the vague kind of question the guide's spam example warns against. |
| `info_sufficient` | Asks Jev to judge what it doesn't know (whether "general knowledge" is enough), a judgment about its own training rather than about the state. |
| `already_decided` | A whole-state, multi-step judgment that turns on comparing dates ("as of `today`", "before the market closes"). TypeSafe's verifier pattern asks per item and combines with `max` instead (F6). It fired on 11 of 939 markets. |

**F5. Practical limits that matter for us.** From [Models](https://docs.typesafe.ai/models.md):
- **Version.** `jev-1.13.0` is current; `jev-latest` and `jev-preview` both point to it. "An alias moves when a new release ships, so the answers behind it can change without a change on your side… pin that version's ID". `policy.json` uses `jev-latest`.
- **Price.** $0.042 per million input tokens; output is free.
- **Limits.** 80 requests a second; 64k tokens per request, of which 32k is for the state plus the longest question.
- **Input.** Text only, best in English.
- **Same weights for everyone.** There is no fine-tuning, so domain rules can only go in the request.
- **No ensembling.** TypeSafe offers no ensembling feature. Its "self-consistent" claim means asking Jev the same thing several times and averaging is not a lever (not verified on our questions). TypeSafe's version of ensembling is many narrow questions combined in code, or a classical model trained on Jev's probabilities.

Strength: **strong** for the facts as of 2026-10-09. Rate limits "are adjusting dynamically".

**F6. TypeSafe's verifier recipe.** The [SDE cascade](https://docs.typesafe.ai/cookbooks/sde_cascade.md) appendix
sets out what makes a good verifier signal:
- **narrow and grounded:** "one checkable yes/no about one field against the source", because "vague questions give mushy, uncalibrated scores";
- **bad = TRUE:** frame each question so the problem case is the yes answer, with explicit criteria;
- **per item, then `max`:** check each field separately, then flag the record if any check fires ("one confident red flag escalates, instead of being averaged into silence").

TypeSafe's internal 100-prompt result says a cheap extractor plus Jev's check plus escalation to a reasoning
model reaches "most of the top model's quality at a fraction of its cost". The
[citation-check cookbook](https://docs.typesafe.ai/cookbooks/citation_check.md) uses one Choice
(`supports` / `contradicts` / `says_nothing`) per claim against the cited section, auto-accepting at confidence
≥ 0.8. Its demo set is 8 citations. The [re-ranking cookbook](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md)
moves top-1 from 5% to 18% on 40 legal queries. Strength: **moderate** as recipes; **anecdotal** as performance
evidence (vendor demos, tiny samples, internal results).

**F7. Small checkers can verify well when the evidence is in the input, and badly without it.**
- **MiniCheck** ([Tang et al., EMNLP 2024](https://arxiv.org/abs/2404.10774)), a 770M-parameter checker fine-tuned for the task, roughly ties GPT-4 on LLM-AggreFact. The authors built that benchmark themselves.
- **Guan et al.** ([NAACL 2024](https://arxiv.org/pdf/2310.14564)) found FLAN-T5-11B, "the least factual generator in our study, performs the best as a fact verifier". With retrieved evidence it was better calibrated than GPT-3.5 (FEVER ECE 3.1 vs 7.6). Without evidence every checker got worse (FLAN 3.1 → 11.1).

The lesson that carries over: put the evidence in the state. Strength: **moderate** (peer-reviewed, but 2023-era
models, Wikipedia claims, not Jev).

**F8. A judge's flag rate is biased until its error rates are measured.** Using a judge model's yes/no answers to
estimate how often something happens gives a biased rate. Correct it with the Rogan-Gladen estimator,
θ = (p + spec − 1)/(sens + spec − 1), whose interval includes the uncertainty of the hand-labelled set. About 200
labels is the suggested scale, and very small sets make the correction unstable.
[Lee et al., preprint, v4 May 2026](https://arxiv.org/abs/2511.21140); the estimator dates from Rogan and Gladen,
1978. Separately, general LLM judges are badly overconfident about themselves. On JudgeBench (350 pairs), GPT-4o's
self-confidence ECE was 39.25, while stronger reasoning models did much better
([Tian et al., preprint 2025](https://arxiv.org/pdf/2508.06225)). Strength: **strong** for the statistics,
**moderate** for the overconfidence numbers (small benchmark, Jev not tested).

**F9. A model alone is a poor detector of linked markets; it needs code before and after it.** Saguillo et al.
([AFT 2025](https://arxiv.org/abs/2508.03474)) ran an LLM (DeepSeek-R1-Distill-Qwen-32B) over 46,360 same-topic,
same-end-date US-election pairs on Polymarket:
- it flagged 1,576 pairs as dependent;
- after a subset checker and a manual review of 374, 13 met the definition of a combinatorial arbitrage;
- on single multi-outcome ("NegRisk") markets, 4 of 128 outputs were invalid JSON, and 101 of the 124 valid ones were fully correct.

A [December 2025 preprint](https://arxiv.org/html/2512.02436v1) on 778 Polymarket markets found agent-proposed
"resolve together / resolve opposite" pairs right only about 60–70% of the time, and 41–51% in July. That study
measured correlation, not strict logic. Strength: **moderate** (one peer-reviewed study and one preprint, neither
using Jev).

**F10. Checking resolution given evidence works; predicting disputes from rule text doesn't.** Wen, Zhou and
Huang ([preprint, April 2026](https://arxiv.org/abs/2604.15674)) tested frontier models on a balanced set of 1,098
Polymarket events:
- **Rule text alone:** the best model, Claude Sonnet 4.5, reached 0.570 accuracy (F1 0.44) at predicting which markets would be disputed, against a 0.50 baseline.
- **With web search:** on 259 disputed-and-resolved markets, the models agreed with UMA's final ruling 88–90% of the time (GPT-4o 78%).

Caveats: the ground truth is UMA's vote, searches may have leaked answers, and the models were large web-search
models rather than a state-only judge. Strength: **weak to moderate** (single preprint). For us, this argues
against expecting much from rule-text flags (job B), and for checking given evidence (jobs C and D).

## What it means for our trader

Ranked by expected value. Every item is a code change, so each waits for Joey's yes.

1. **Stop betting on Jev's `p_yes` as a forecast** (once test T0a below confirms it carries no information beyond
   the base rate). *Effect:* stops five strategies (`main`, `jev_alone`, `bold`, `jev_alone_bold`,
   `calibrated`) from betting on a forecaster scoring 0.043–0.073 worse than the market. *Sure:* high that Jev isn't
   a forecaster we can beat the market with; the data already shows it. *Catch:* the frozen `original` yardstick
   runs on `jev_research`. Keeping `papertrade-v2` running unchanged, logging only, costs about $0.0001 per market,
   so the yardstick and its history can continue while new jobs get their own question sets. Joey's call.
2. **Pin `jev-1.13.0` and record the answering model on every row.** `judgments.jsonl` already stores `model`.
   *Effect:* thresholds tuned on one version don't silently move. *Sure:* high; TypeSafe recommends it.
3. **Job A, the market reader**, feeding the specialist pricers (thresholds, weather, economic releases). Jev reads;
   code and a quant model price. *Effect:* only as large as the pricers' edge, but it is the piece those pipelines
   need, and parsing is squarely what Jev is built for. *Sure:* medium-high that Jev parses well with candidates
   supplied; unknown how much it beats regex alone.
4. **Job C, the fact-by-fact "already met / can't happen" check**, replacing `already_decided`. *Effect:* finds the
   only kind of edge a non-forecaster can supply, information the price hasn't absorbed, if any exists. *Sure:*
   medium that the reading is accurate; low that the market is often slow enough to profit after the 8.4% costs.
5. **Job E, labelling how linked markets relate**, as the meaning check inside brief 02's arithmetic. *Sure:*
   medium; F9 says it only works with code narrowing the candidates first and checking after.
6. **Job D, checking facts against their sources**, for research quality. *Sure:* medium-low that it pays: it needs
   source pages fetched and stored, and we don't yet know how often Claude's facts are wrong.
7. **Job B, rule-risk flags**, replacing `rules_clear` in research triage. *Sure:* low (F10). Keep it only if T0b or
   B's test shows the flags predict voids or surprise resolutions.

Lower priority, belonging to briefs 04 and 05: TypeSafe's use-case map suggests turning text into Jev features for
a classical model. Brief 05 found no forecaster adds weight over the price on real-priced markets, so this waits.

Design rules for all of them:
- each job is its own request with its own state and its own version string (for example `reader-v1`, `facts-v1`);
  never reword `papertrade-v2`;
- dates, numbers and thresholds are compared in code;
- problem cases are the TRUE side of each Noul;
- each item is checked separately, then combined with `max`;
- run every Choice in two option orders on the test set (failure mode 8);
- no market price ever goes into any state, keeping the screen in `CLAUDE.md`.

### The recommended question set

Wording here is a starting draft to test, not final. `{i}` questions are built in code, one per item.

**Job A: market reader** (one request per market; it can also carry job B's questions)

State (code fills `candidates` with regex matches, so Jev picks values rather than generating them):
```json
{"market": {"title": "...", "rules": "... (≤4,000 chars, as today)"},
 "candidates": {"numbers": ["95", "95.00", "2026"], "dates": ["September 30, 2026", "11:59 PM ET"]}}
```
| id | type | instructions | criteria / options |
|---|---|---|---|
| `market_kind` | Choice | Which kind of quantity or event decides `market.rules`? | `traded_asset_price` (crypto, commodity, index, stock), `weather_measurement`, `economic_data_release`, `sports_result`, `election_or_vote`, `official_decision`, `media_or_culture_metric`, `words_said_or_posted`, `other`. Each with `what` / `not_for` / `examples` |
| `comparison` | Choice | Under `market.rules`, how must the deciding number relate to the threshold for YES? | `above`, `at_or_above`, `below`, `at_or_below`, `between`, `exactly`, `not_a_numeric_threshold` |
| `threshold` | Choice | Which of `candidates.numbers` is the threshold that decides YES in `market.rules`? | each candidate, plus `none_listed` |
| `observation` | Choice | When is the deciding number observed under `market.rules`? | `single_time` (a close, settlement or release), `any_time_in_window` (a touch), `average_or_total_over_window`, `not_numeric` |
| `deadline` | Choice | Which of `candidates.dates` is the last moment the YES condition can be met? | each candidate, plus `not_stated` |
| `named_source` | Noul | Do `market.rules` name a specific source (an agency, data feed, league or index) whose report decides the outcome? | true: a named source decides; false: no source, or "reports" in general |

Code builds the deadline from the chosen date and compares it with `close_time` and today. Low confidence on any
field means no specialist price: skip the market.

**Job B: rule-risk flags** (Nouls, problem = TRUE, same state as A)

| id | instructions |
|---|---|
| `discretion` | Do `market.rules` let the exchange, a committee or a resolver decide by judgment rather than by a named source or measurement? |
| `title_rules_mismatch` | Do `market.rules` set a condition that differs from what `market.title` says (another deadline, threshold, source or definition of the event)? |
| `announcement_required` | Does YES under `market.rules` require an official announcement or report, rather than the event itself happening? |
| `no_fallback` | Do `market.rules` fail to say what happens if the event is postponed or cancelled, or the named source is unavailable? |

**Job C: fact-by-fact evidence check** (one request per researched event, after `screen_facts`)

State:
```json
{"market": {"title": "...", "rules": "..."},
 "facts": [{"kind": "status_now", "date": "2026-10-08", "source": "Reuters", "fact": "..."}]}
```
| id | type | instructions | options |
|---|---|---|---|
| `fact_{i}` | Choice | What does `facts[{i}].fact` show about the YES condition in `market.rules`? | `condition_already_met` (it reports that what the rules require for YES has happened), `condition_ruled_out` (it reports something that makes YES impossible under the rules), `relevant_not_decisive`, `not_about_this_market` |

Code keeps only facts dated on or before today and after the market opened, and takes the `max` over facts of
P(met) and of P(ruled out). Whether the deadline has passed is compared in code, never asked.

**Job D: fact against source** (one request per fact whose source page code could fetch)

State: `{"claim": "<fact>", "section": "<the source passage code found, leak-screened like research facts>"}`.
One Choice, as in TypeSafe's citation check: `supports` / `contradicts` / `says_nothing`, auto-accepted at
confidence ≥ 0.8, otherwise the fact is dropped (no human review in this loop). Code checks the date separately: a
Choice picks the fact's date from date candidates in the section, and code compares it.

**Job E: how two markets relate** (one request per candidate pair that code proposes: same event ticker, or
cross-venue with close times within a day and high text similarity)

State: `{"a": {"title": "...", "rules": "..."}, "b": {"title": "...", "rules": "..."}}`

| id | type | instructions | options |
|---|---|---|---|
| `relation` | Choice | Under their rules, how does YES on `a` relate to YES on `b`? | `same_condition`, `a_implies_b`, `b_implies_a`, `mutually_exclusive`, `overlap_neither_implies`, `unrelated` |
| `same_source` | Noul | Do `a.rules` and `b.rules` name the same source to decide the outcome? | true: same source; false: different or unstated |
| `definition_differs` | Noul | Do `a.rules` and `b.rules` define the event differently in any way that could make one resolve YES and the other NO? | true: some difference could split them; false: the definitions match |

Deadlines and thresholds come from job A's output and are compared in code. Ask every pair both ways (a,b) and
(b,a), and accept only when both orders agree. Brief 02's code then checks the prices.

## How to test it on our history

Run these in order. T0 uses data we already have and needs no Jev calls. Jobs A to E re-ask Jev on finished
markets. At about 2,500 input tokens a request, one pass over 1,133 markets is about 2.8M tokens, roughly $0.12.
Report every number with n and ± one standard error, and cluster by event.

**T0. What the current answers are worth** (from `judgments.jsonl` and the resolutions, first look per market)
- *T0a. Information in `p_yes`.*
  - **Measure:** for `jev_plain` and `jev_research`, the Brier split into reliability and resolution, AUC against the outcome, and Brier against always forecasting the base rate.
  - **Kill Jev as a forecaster:** AUC within 0.02 of 0.5 for `jev_plain`, or `jev_research` adding nothing over Claude's research once Claude direct is known (logistic regression with both).
- *T0b. `rules_clear`.*
  - **Measure:** bin it, and per bin compute the void or value-settlement rate, the market's own Brier on real-priced markets, and the count of "surprise" resolutions (mid ≥ 0.85 in the last 24h and resolved the other way).
  - **Keep a rules gate:** a monotonic trend with a top-to-bottom difference above 2 SE. Otherwise it gates nothing, and research triage should drop it.
- *T0c. `info_sufficient`.*
  - **Measure:** Jev-alone Brier and Claude-direct-minus-market Brier by bin.
  - **Keep:** only if it separates them by more than 2 SE.
- *T0d. Framing gap.*
  - **Measure:** whether |p_yes + p_no − 1| predicts |error| after controlling for |2p − 1|.
  - **Drop the `max_framing_gap` gate:** if it doesn't.
- *T0e. Model drift.*
  - **Measure:** list the distinct `model` values over time and the dates they changed. If the version changed mid-experiment, split every Jev score at that date.

**Job A (reader).**
1. **Label.** Hand-label 200 markets, stratified by category and source. Claude Opus may pre-label, with every label checked by a person.
2. **Score.** Per question: accuracy, accuracy in confidence bands, and coverage at confidence ≥ 0.8. Compare against a regex-only parser on the same 200.
3. **Automatic check.** For crypto and index threshold markets (enough of them in the 1,133), code combines the parsed (asset, comparison, threshold, observation, deadline) with the realised price from free history (for example exchange candles), predicts YES/NO, and compares with the actual settlement. Every disagreement is either a parsing error or a rules subtlety; read them all.
4. **Confirm:** at least 98% agreement on cases with confidence ≥ 0.8, covering at least 80% of threshold markets, and better than regex.
5. **Kill:** no better than regex, or under 95% on confident cases.

**Job B (rule-risk flags).**
- **Measure:** on all 1,133 finished markets, AUC of each flag, and of their `max`, for (a) voids or value settlements and (b) surprise resolutions as in T0b. Measure the flags' error rates against 200 hand labels, and correct flag rates with Rogan-Gladen (F8).
- **Confirm:** AUC ≥ 0.65 for (a) or (b) with at least 30 positive cases.
- **Kill:** AUC below 0.6. F10 makes this the likely result.

**Job C (fact-by-fact check).**
1. **Run.** For every researched market (about 646 or more), use the facts Jev saw then, stored in `recent_facts`.
2. **Score.** Take the market-level `max` P(met) and P(ruled out). At thresholds 0.7, 0.8 and 0.9, report precision against the outcome (met → YES, ruled out → NO), with n.
3. **Compare with the old check.** Report the same for `already_decided` on the same markets.
4. **Leakage control.** Re-run with `facts` emptied. If precision stays high, Jev is answering from training (its training cutoff is not published), and the history test is contaminated for markets that closed before it.
5. **Price comparison.** The main session does this after Jev answers; Jev never sees prices. For each flagged market, take the ask at that snapshot and compute the return of buying the indicated side after fees and slippage.
6. **Confirm:** precision ≥ 95%, and at least 30 flagged cases where the indicated side cost ≤ 90¢, with a positive return after costs (± SE).
7. **Kill:** precision no better than the price implied, or almost every flagged market already at 95¢ or more, so the market had already absorbed it. It is still worth keeping as a safety check that blocks bets against a decided outcome, if precision is high.

**Job D (fact against source).**
1. **Sample.** Take 200 facts from `research.jsonl` with their `source_urls`. Fetch the pages; use the Wayback Machine where the live page has changed. Record how many cannot be fetched.
2. **Label.** Hand-label supports, contradicts or says nothing.
3. **Score.** Measure Jev's sensitivity and specificity for the "not supported" outcome, and estimate the corrected share of unsupported facts with an interval (F8).
4. **Compare Brier.** On the full researched set, compare Claude direct's Brier on markets with and without any flagged fact.
5. **Confirm:** a corrected unsupported share of at least 5%, specificity ≥ 0.9, and markets with flagged facts scoring worse by more than 2 SE.
6. **Kill:** an unsupported share under 2% (nothing to catch), or under half of source pages fetchable.

**Job E (how two markets relate).**
1. **Build pairs.** From the history: every pair within one event, plus cross-venue candidates (close within a day, high word overlap). Take 200 for hand labels, oversampling likely matches.
2. **Score.** Precision and recall of `same_condition` and `implies` at confidence ≥ 0.9 with both orders agreeing, and the share each order rule removes.
3. **Confirm:** precision ≥ 95% at useful coverage. Then hand the accepted pairs to brief 02's price check and count real violations after costs.
4. **Kill:** precision below 95%. A false "same" turns an arbitrage into two unhedged bets.

**Research triage** (uses job A's `market_kind`; no new question)
- **Measure:** on researched markets, Claude-direct Brier minus market Brier by `market_kind`, with ±.
- **Confirm:** some kinds where Claude is within 1 SE of the market or better. Research only those.
- **Otherwise:** if none qualify, the triage answer is "research less" (it shows research doesn't beat the price in any kind), not a better gate.

## Data sources

| Name | URL | Cost | What it provides |
|---|---|---|---|
| TypeSafe docs index | https://docs.typesafe.ai/llms.txt | free | every page as Markdown (append `.md`) |
| Jev models page | https://docs.typesafe.ai/models.md | free | versions, aliases, price, limits |
| Jev 1.13 jaggedness | https://docs.typesafe.ai/model-jaggedness/jev-1.13.md | free | known failure modes, reviewed 2026-10-02 |
| TypeSafe Playground | https://console.typesafe.ai/playground | account | try a question by hand before coding it |
| Jev API | `POST https://api.typesafe.ai/v1/systemone` | $0.042 per million input tokens | the tests above (main session only) |
| Wayback Machine | https://web.archive.org | free, rate-limited | past versions of research source pages for job D |

## Not verified

- **No forecasting claim either way.** TypeSafe's docs never discuss forecasting. That `p_yes` misuses Jev is our inference from its general design rules. The stronger claim, that TypeSafe rules forecasting out, was refuted 0-3.
- **No published calibration numbers.** None exist for any Jev version, and there is no independent study of Jev.
- **Training-data cutoff and release dates.** Neither is published for `jev-1.13.0`, so history tests on older markets may be contaminated. Job C's leakage control is there for that.
- **Self-consistency on our questions.** That repeated calls return the same answer is TypeSafe's claim, shown on one insurance example; we haven't checked it on our questions.
- **That Jev parses rules better than regex.** Nothing tested shows this; job A's test decides it.
- **Outside evidence on triage and re-ranking.** Three triage and re-ranking papers were found but dropped before verification. That part of the design rests only on TypeSafe's cookbooks.
- **The size of the outside results.** MiniCheck, FLAN-T5, JudgeBench, the arbitrage, linked-market and dispute papers all used other models. Several are preprints with small samples (128 NegRisk markets, 259 disputes, 350 judge pairs).
- **Cost per request.** The roughly 2,500 input tokens is our estimate from 4,000-character rules plus a dozen questions; the real count comes back in each response's `usage`.
- **Whether Jev may see source pages.** Job D puts page text in Jev's state. It must pass the same price screen as research facts. Whether a non-forecasting Jev job may see unscreened text is Joey's call under `CLAUDE.md`, and this report assumes it may not.
