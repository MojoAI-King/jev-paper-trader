# 04: What makes an AI forecaster more accurate

Researched 2026-10-09 for `docs/research/briefs/04-ai-forecasting-techniques.md`.

Method: deep-research workflow (5 search angles, 22 sources fetched, 107 claims extracted, 25 checked by three
independent verifiers each: 22 confirmed, 3 refuted), plus a manual check of the failure-mode papers and of the
Metaculus calibration notebook. Each claim below says which kind of check it got.

## Answer in five lines

1. Our gap to the market (0.207 vs 0.172, −0.035) is normal. No published forecaster that can't see the price beats a liquid market. The best ones trail by 0.015 to 0.04 Brier (Bridgewater AIA −0.015 on 1,610 questions; a fine-tuned 14B −0.039 on 1,265; Halawi et al. −0.030 on 914).
2. The best-supported cheap fix is **post-hoc calibration fitted on our own resolved forecasts**. Fitted on older forecasts and tested on newer ones, it cut Brier by 0.016 for Metaculus bots and by 0.017 for Claude Sonnet 4 (1,614 questions), at zero extra Claude calls. It can backfire when fitted on different questions, so fit it on ours.
3. Higher reasoning effort and small ensembles help a little: effort won 8 of 8 paired comparisons (size in Brier unknown), and 3 to 10 samples gave −0.003 to −0.004. Each costs plan usage on every forecast, and very high effort has made calibration worse in one study.
4. Prompt tricks don't work: 38 prompts gave no significant gain; "reason like a Bayesian" and "superforecaster" prompts made forecasts *worse*. Base-rate-first prompting is the only weak positive (about −0.01, not robust). Fine-tuning gives the biggest gains but isn't possible on a Claude subscription.
5. Overconfidence on our bets is most likely a selection effect (we bet where we disagree most with the market, so we pick our biggest errors). Recency bias from news is a documented second cause. Even fully fixed, the literature gives no reason to expect a price-blind Claude to beat the market by more than our 8.4% trading cost.

## Findings

### Where the best systems stand (2026)

**F1. The best AI systems are near human experts on curated question sets, but not on liquid markets.**
- ForecastBench (FRI, update of 2026-01-29): superforecasters are still #1. The best model (Grok 4.20 Preview) scores a difficulty-adjusted Brier of 0.102, and superforecasters lead the best models by 0.017. ([FRI post](https://forecastingresearch.substack.com/p/llms-are-closing-the-gap-on-human))
- Bridgewater's AIA Forecaster (arXiv 2511.07678, Nov 2025), ForecastBench subset FB-7-21 (n=498): 0.1076, against 0.1110 for the superforecaster median and 0.1221 for o3. The authors call it "statistically indistinguishable" from superforecasters. ([paper](https://arxiv.org/html/2511.07678v1))
- Metaculus Spring 2026 FutureEval (2026-01-07 to 2026-04-15, 99 questions): the bot team trailed 10 Pros by −1.25 peer points per question (95% CI −4.87 to 2.37, not significant). Earlier quarters: −11.3, −8.9, −17.7 and −20.0. ([Metaculus results](https://www.lesswrong.com/posts/wZBbDqzfBjYG58CxK/futureeval-spring-results-pros-beat-bots-but-the-gap-is))
- Caveats: AIA is a vendor's own backtest; ForecastBench scores are difficulty-adjusted, not head-to-head; Metaculus uses peer scores, not Brier, and has low power.
- Strength: **strong** on direction (three independent primary sources, verified 3-0, 3-0, 2-1). FRI's own forecast of the date models reach superforecaster level was **refuted** in verification (0-3), so it isn't used.

**F2. Against liquid prediction markets, systems that don't see the price lose by 0.015 to 0.04 Brier.**

| System | Study | Questions | System Brier | Market or crowd Brier |
|---|---|---|---|---|
| Bridgewater AIA | arXiv 2511.07678 | 1,610 from 322 liquid markets | 0.1258 | 0.1106 (o3 alone: 0.1324) |
| Fine-tuned 14B, 7-sample ensemble | Turtel et al., arXiv 2505.17989 v4 | 1,265 Polymarket | 0.190 | 0.151 (Polymarket) |
| Retrieval + fine-tuned GPT-4 | Halawi et al., NeurIPS 2024, arXiv 2402.18563 | 914 | 0.179 (SE .003) | 0.149 (SE .003, competitive crowd) |

- Our 0.207 vs 0.172 (−0.035 on 327) sits inside this range.
- Strength: **strong** (three primary papers, all 3-0; only Halawi is peer reviewed).
- Verification refuted one framing of the Turtel numbers (0-3), the one that also claimed a "−0.013 vs o1, p<0.01" margin. The 0.190 vs 0.151 market comparison itself was confirmed.

**F3. "LLMs match the market" results usually let the model see the price.**
- Prophet Arena (arXiv 2510.17638, Oct 2025): 1,367 Kalshi events (72,136 markets, 76% sports). GPT-5 scored 0.184, against a market baseline of 0.187. Claude Sonnet 4 scored 0.194.
- The models had market data in the prompt and "generally align closely with market predictions". Even so, GPT-5 lost money betting (0.943 returned per unit staked).
- Strength: **moderate** (one preprint, 3-0). It is not evidence that a forecaster that can't see the price can match the market.

**F4. Without research, most models do worse than always guessing the base rate.**
- KalshiBench (arXiv 2512.16030, Dec 2025, single-author preprint): 300 Kalshi questions that resolved Oct–Nov 2025, no retrieval. Only Claude Opus 4.5 beat always guessing the 40% base rate (Brier 0.227). GPT-5.2-XHigh scored 0.433.
- All five models were overconfident. In the 90–100% bin, Opus 4.5 averaged 94.6% confidence and was right 70% of the time (n=20); GPT-5.2-XHigh averaged 95.9% and was right 33.7% (n=104).
- Strength: **moderate** (the abstract was checked by hand; the per-bin figures were extracted from the body but not independently verified). It matches our "Jev alone ≈ coin flip" finding: without good facts, model knowledge alone is weak.

### Techniques and their measured gains

**F5. Post-hoc calibration on resolved questions: −0.006 to −0.017 Brier, near-zero cost, but only when fitted on matching questions.**

| Study | Questions | Before | After | Change |
|---|---|---|---|---|
| Metaculus calibration notebook (2026-05-01), bot forecasts from 2025 Q1–Q2 | per forecaster with 500+ forecasts; total not reported | — | — | logistic (Platt) −0.0164 binary (p=0.0005), −0.0054 multiple choice |
| Dai et al., arXiv 2605.27668: Claude Sonnet 4, no retrieval | 1,614 held-out (resolved Aug 2025 – Jan 2026); Platt fitted on 1,917 | 0.146 | Platt 0.129, isotonic 0.129 | −0.017 |
| AIA, FB-7-21 | 498 | 0.1140 | fixed Platt 0.1076; in-distribution Platt 0.1071 | −0.006 to −0.007 |
| Dai et al., Qwen3-32B on Kalshi, Platt fitted on Metaculus/Polymarket (the mismatched case) | 3,208 | 0.238 | Platt 0.251, isotonic 0.244 | **+0.006 to +0.013 (worse)** |

- Metaculus fit each adjuster per forecaster: oldest 70% of forecasts to fit, newest 30% to test. Logistic recalibration beat uniform shift, step shift, k-means and decision-tree adjusters. ([notebook](https://www.metaculus.com/notebooks/43356/calibration-adjustment-analysis/))
- In the Dai table, Sonnet 4's expected calibration error fell from 0.104 to 0.034. A trained 1B-parameter calibrator reached 0.125, so plain Platt captured about 80% of its gain. ([paper](https://arxiv.org/html/2605.27668))
- In AIA, fixed log-odds extremizing gave 0.1085, isotonic 0.1097, and Platt fitted on different questions 0.1104. ([paper](https://arxiv.org/html/2511.07678v1))
- Direction matters. In AIA and Halawi the raw model hedged toward 50%, so calibration pushed forecasts *out*. Dai et al. and KalshiBench found verbalized LLM probabilities *overconfident*, as ours are on bets, so a fit on our data should pull them *in*.
- AIA also notes that calibration only helps forecasts already on the right side of 50%. It improves Brier but can't create an edge.
- Strength: **strong** for the gain inside matching data (three independent sources, the first checked by hand, the others 3-0). Neither paper gives confidence intervals.

**F6. Better retrieval: about −0.020 Brier in the one clean test, but more news isn't always better.**
- Halawi et al. (n=914): GPT-4 with no retrieval 0.206, with retrieval 0.186 (−0.020); fine-tuning then took it to 0.179. ([paper](https://arxiv.org/abs/2402.18563))
- Halawi, validation set: accuracy improved with 5 or more relevant articles, and at earlier retrieval dates.
- FutureSim (arXiv 2605.15188, May 2026, 330 questions from Jan–Mar 2026): full agentic search doubled accuracy compared with a single query, and removing daily news updates cut GPT-5.5's accuracy from 24.8% to 17.9%.
- Against: Karkar & Chopra (arXiv 2511.18394, 150 questions, 4 models) found that adding news helped in Finance and Sports but hurt in Entertainment and Technology. Prophet Arena found that "more information is not necessarily better".
- Metaculus found no clear difference between search providers (Sonar Pro vs AskNews).
- AIA's claim that agentic search drives most of the gain was **refuted** (1-2) in verification.
- Strength: **moderate**. The −0.020 comes from one GPT-4-era paper, and Paleka et al. (arXiv 2506.00723) warn that backtests using date-limited search leak future information, which inflates retrieval gains.

**F7. More reasoning effort: helps on average, with diminishing and sometimes negative returns, especially for calibration.**
- For it:
  - Metaculus Spring 2026: the high-reasoning version of a bot beat its standard twin in 8 of 8 pairs (one-sided p=0.004), including pairs built on Claude Sonnet 4.5 and Opus 4.5. One published pair: 11.32 vs 4.56 peer points.
  - FutureSim: GPT-5.5's accuracy rose with effort up to "high", and "xhigh" added nothing.
- Against:
  - Metaculus Q2 2025: extra reasoning helped o1 but *hurt* o3 at "high".
  - KalshiBench: GPT-5.2-XHigh had the worst calibration (ECE 0.395) while its accuracy was similar to the others'.
  - The prompt study's no-retrieval baseline (F9): o1 (0.216) and o1-mini (0.217) were no better than Claude 3.5 Sonnet (0.207).
- Strength: **moderate** for a small positive effect on accuracy (verified 3-0; peer scores, no Brier size). **Weak** on calibration: more reasoning may raise confidence faster than accuracy.

**F8. Ensembles: small gains (−0.002 to −0.009), little difference between median and mean, and very large teams get worse.**
- Repeated samples of one model:
  - AIA, 10 forecasts (n=498): one forecast 0.1182; mean 0.1140, median 0.1138, trimmed mean 0.1142. An LLM "supervisor" that reconciles them scored 0.1125.
  - Claude Sonnet 4, 3 samples: 0.146 → 0.143 (Dai et al.).
  - Lu (arXiv 2507.04562, 334 Metaculus questions), 5 samples: median vs mean within 0.004 (o3 0.1352 vs 0.1362).
  - Halawi validation set: trimmed mean 0.1649, median 0.1651, mean 0.1656, no ensemble 0.1676.
  - Qwen3-32B: a sample ensemble barely helped Brier (0.2472 → 0.2390) and made calibration error *worse* (0.2175 → 0.2289).
- Teams of different bots, Metaculus Spring 2026: the top bot alone scored −4.51 against the Pros, and teams of 2 to 10 bots about −2. Results got worse beyond about 10 bots and were clearly worse at 30 or more.
- Different models, Schoenegger et al. (31 questions): the median of 12 different LLMs scored 0.20, against 0.19 for a 925-person crowd. With equivalence bounds of ±0.081 the test is too small to tell much. The LLMs also leaned toward "yes" (mean forecast 57%, while 45% resolved yes).
- Observational evidence: 86% of the winning bots in Metaculus Fall 2025 averaged several runs.
- Strength: **moderate** (four sources, 3-0; they measure different things and give no confidence intervals).

**F9. Prompting techniques: mostly no effect; "Bayesian" and "superforecaster" prompts hurt.**
- Schoenegger, Jones, Tetlock & Mellers (arXiv 2506.01578, Jun 2025, preprint): 38 prompts against a minimal control, on Claude 3.5 Sonnet, Claude 3.5 Haiku, GPT-4o and Llama 3.1 405B. 100 ForecastBench questions, preregistered, no retrieval.
  - Under the preregistered analysis, no prompt improved Brier significantly.
  - The best point estimates were small: frequency-based reasoning −0.014, base rate first −0.011, chain of thought −0.011, step-back −0.011.
  - Bayesian-reasoning and propose-evaluate-select prompts made Brier *worse*, by +0.030 and +0.033 (p<0.001).
- Their Study 2, which added o1 and o1-mini: a superforecaster-written odds-ratio prompt worsened Brier by +0.023, and a long superforecaster persona changed it by −0.002 (not significant).
- Lu (334 questions): a direct "give a probability" prompt beat a "tell a story from the future" prompt with the same news (o3 0.135 vs 0.199).
- Metaculus Q2 2025: "the most important factor … is the base model", and scaffolding gave marginal gains.
- Strength: **moderate** (the abstract was checked by hand, the per-prompt numbers were extracted from the body; one preregistered study plus a tournament analysis). Our `DIRECT_PROMPT` is already the minimal kind that did as well as anything.

**F10. Fine-tuning on resolved outcomes: the largest gains (−0.015 to −0.068), but only for open-weight models.**
- Halawi et al.: fine-tuning added −0.007 on top of retrieval.
- arXiv 2601.06336 (Jan 2026): Qwen3-32B trained with reinforcement learning on outcomes went from 0.2472 to 0.1793 on 293 Metaculus questions, from a weak, near-coin-flip start.
- arXiv 2502.05253 (Feb 2025), 2,300 Polymarket questions: Phi-4 14B went from 0.221 to 0.200, but a control trained on random labels also improved, to 0.214. Only about −0.015 comes from learning outcomes.
- Strength: **moderate** (3-0; mostly vendor preprints with weak baselines). **Not usable** on a Claude subscription. The nearest thing we can do is calibration (F5) plus the research playbook.

**F11. Decomposition, reference classes and self-critique or debate: unmeasured, not shown to fail.**
- No claim giving a Brier gain from breaking a question into parts, or from debate or self-critique, survived extraction and verification.
- Base rates have only weak support: the prompt study's −0.011 (F9), and a correlation among winning Metaculus bots between "explicitly calculating base rates" and score (r=+0.38, p=0.032; observational).
- FutureSim found that updating step by step as news arrived did worse than one forecast made with all the information (31.2% vs 24.8% accuracy).
- Strength: **weak** or no evidence.

### Failure modes and their fixes

**F12. Overconfidence: common in today's models when they state a probability, worst on what they think likely, and not fixed by more reasoning.**
- Dai et al.: overconfident across all four models tested.
- Lu: "models are typically overconfident, especially for events that models think are likely to happen".
- FutureSim: 27.4% of GPT-5.5's wrong answers put 0.5 or more on the wrong outcome.
- KalshiBench: in the 90–100% bin, Opus 4.5 was right 70% of the time (n=20).
- Older GPT-4-era systems hedged toward 50% instead (Halawi, AIA), so the direction depends on the model and the setup.
- Fixes with evidence: calibration fitted on your own resolved forecasts (F5). The Metaculus Fall 2025 survey found "capping predictions at a max/min" was the strongest difference among winning bots (r=+0.48, p=0.005; observational; checked through the secondary summary by Wilson, 2026-07-08).
- Strength: **moderate**.

**F13. Our overconfidence on *bets* is probably mostly a selection effect, which calibration on all forecasts won't fully catch.**
- This is reasoning, not a finding from the sources. When you act only where your estimate is furthest from a reference, the chosen estimates are biased toward error: the "optimizer's curse" (Smith & Winkler, *Management Science*, 2006; cited from general knowledge, not fetched this session).
- Two published results fit the idea:
  - Halawi's system was only competitive where the crowd was uncertain (0.238 vs 0.240 when the crowd sat between 0.3 and 0.7).
  - Turtel et al.'s simulated trading edge came only from markets priced 40–60%, where bets won 11.8 points more often than the price implied; where the market was confident the model did no better than chance (1,265 questions).
- Our worst group, betting against the favourite at 30–50¢ (15 wins of 55 where the market expected 22), is consistent with this.
- Strength: **weak** (an inference); the main session can test it (T1 below).

**F14. Anchoring on recent news and misreading the question.**
- Karkar & Chopra (arXiv 2511.18394; 150 questions, 4 models, temperature 0; checked by hand against the paper's text):
  - "Models tend to overweight recent news over historical trends encoded during pretraining."
  - On the threshold question "S&P 500 above 6050 on June 13?", news flipped a correct NO (0.66) into a wrong YES, turning "a correct mean-reversion call into an overconfident breakout bet".
  - "Models frequently anchor to unverified information or speculation present in retrieved snippets."
  - News also caused definition drift: a model read "MATS" as the Mid-America Trucking Show.
- Prophet Arena lists "misunderstanding of data sources" (how a question's resolution source measures it) among the main bottlenecks, and finds markets absorb breaking news faster than LLMs close to resolution.
- Strength: **weak to moderate**. The mechanisms are documented with single examples on a small set and no overall rate. Our WTI miss (81–93% that oil would reach $95, against 7¢) looks like the S&P case: recent headlines outweighing how far and how fast the price would have to move.

**F15. Questions about a number crossing a threshold: no verified study.**
- No source measured LLM accuracy on "will X be above Y by date" questions specifically. The S&P example in F14 is the only one found.
- Metaculus found bots did worst on numeric questions (Q2 2025: −23.2 for numeric against −14.8 for binary), but those were range forecasts, not thresholds.
- Strength: **anecdotal**. The principled fix (price the threshold from the asset's volatility) belongs to briefs 06–08.

**F16. Backtests flatter LLM forecasters.**
- Paleka et al. (arXiv 2506.00723): date-limited search leaks the future because article dates are often wrong. At least 3.8% of Halawi's questions had resolved "early". When many systems are compared, the top one's score is likely overstated (winner's curse).
- arXiv 2512.23847 (Dec 2025): a model's tendency to recall the real outcome is "materially positive" before its training cutoff and "collapses essentially to zero right after".
- Strength: **moderate** (Paleka's abstract checked by hand; details extracted from the body).
- For us this matters little, because our forecasts were made live. It does matter for any replay of old markets: a replay with today's model or today's search would be contaminated.

## What it means for our trader

Today's setup:
- Claude direct is Opus 5.5 at `effort: medium`. It makes one call per market, with no web access, on the minimal `DIRECT_PROMPT` ([news.py:70](../../papertrade/news.py#L70)).
- The research desk already asks for `base_rate` facts.
- `learn.fit_calibration` already fits a Platt map (a·logit p + b, pulled toward "no change" by a prior), but only for Jev + research. Nothing calibrates Claude direct.

Ranked techniques for about 200 markets every 30 minutes on a fixed plan (the brief's deliverable):

| # | Technique | Expected Brier gain for us | Cost per forecast | Evidence | Needs |
|---|---|---|---|---|---|
| 1 | **Calibrate Claude direct on our own resolved forecasts.** Start with the existing Platt map (2 parameters, with its prior); only try isotonic once there are 1,000+ resolved markets; refit on a schedule | −0.005 to −0.017 if it carries over; most likely shrinks our forecasts toward 50% | None (arithmetic) | Strong: 3 sources, n=498 to 1,614 plus a Metaculus per-bot fit tested on later forecasts; one counterexample when fitted on mismatched questions | Code change (Joey). Test T2 first |
| 2 | **Cap forecasts** (for example at 3% and 97%) as a backstop | Small; protects against the single 0.8+ misses that dominate Brier | None | Weak (observational correlation among winning bots) | Code or policy change (Joey). Test T3 |
| 3 | **Research desk: pair the latest news with how things usually go.** For every question, ask for the historical base rate next to the recent news, and for threshold questions the distance still to travel and how often moves that size happened before the deadline | Unknown; aimed at the WTI-type miss | A few more tokens per research run; no extra runs | Weak (recency-bias examples; base-rate prompts about −0.01, not robust) | A playbook rule (the loop can add it) or a prompt change (Joey) |
| 4 | **Raise Claude direct's effort from medium to high** | Positive but unknown size; could hurt calibration | About 2–4× the tokens of a direct call (not verified for Opus 5.5); research calls unchanged | Moderate for accuracy (8 of 8 pairs), weak on calibration | A shadow challenger first (T6); a policy change |
| 5 | **Median of 3 direct samples** | −0.002 to −0.004 | 3× the direct calls | Moderate, consistent and small | Code change. Last priority given plan limits |
| 6 | More or broader research per market | −0.02 measured in GPT-4-era work; we already do research, so the remaining gain is unknown and can be negative | Limited by about 150 runs a day | Moderate, mixed | Not recommended until T4 shows where research helps |
| — | Bayesian, superforecaster or narrative prompts; debate; ensembles of more than 10; updating step by step | Zero or worse (+0.02 to +0.03 for Bayesian or superforecaster prompts) | — | Moderate (negative) | Don't do |
| — | Fine-tuning on outcomes | −0.015 to −0.068 | Impossible on the plan | Moderate | Not available |

How sure I am: fairly sure that #1 lowers Claude direct's Brier on all forecasts and that it reduces the
overconfident bets. Not sure about the size, because published fits corrected hedging, not overconfidence.
Applied all together, the best literature case brings a model that can't see the price to within about
0.015 of a liquid market (AIA). It does not put it ahead. **Better accuracy alone shouldn't be expected to
overcome the 8.4% trading cost.** Its realistic value is fewer bad bets (the overconfident 30–50¢ ones), and
better inputs for whatever brief 05's answer is.

## How to test it on our history

The main session runs these on the ~1,100 finished markets, using each market's first look. Report n and a
bootstrap 95% CI for every number, and split each result into all markets and the 327 or so with a real price
(spread 10¢ or less).

- **T1. Where is the overconfidence?**
  - Compute: Claude direct's calibration curve (10 bins, n per bin, expected calibration error) on (a) all first-look forecasts and (b) only the forecasts we bet on, at the bet-time forecast.
  - Confirms selection (F13): (a) near the diagonal while (b) is badly overconfident.
  - Kills it: (a) is overconfident by a similar amount; then calibration on all forecasts is the whole fix.
- **T2. Does a calibration map fitted on our data help on later markets?**
  - Compute: sort markets by resolution time and fit `learn.fit_calibration` (Platt with the existing prior) on Claude direct for the oldest 70%. Score Brier on the newest 30%. Also run rolling refits (refit on everything before each week, score that week).
  - Report: the fitted slope a (a<1 means shrinking, which is the prediction) and the Brier change.
  - Confirms: an improvement of at least 0.005 with a CI that excludes 0.
  - Kills it: the CI includes 0 or the change is worse.
  - Repeat the fit by category (sports, crypto/finance thresholds, politics, weather) only if each group has 200+ markets.
- **T3. Capping:**
  - Compute: Brier on all markets with Claude direct clipped to [0.03, 0.97], [0.05, 0.95] and [0.10, 0.90].
  - Confirms: the Brier change is below 0, the gain comes from a handful of big misses, and it costs almost nothing elsewhere.
- **T4. Where is Claude furthest behind the market?**
  - Compute: the Brier gap (Claude − market) with its SE, by category, by time left until close (under 1 day, 1–7 days, over 7 days; Prophet Arena predicts we are worst close to resolution), by market price bucket (0–20, 20–40, 40–60, 60–80, 80–100¢; Halawi and Turtel predict we are least bad at 40–60¢), and by number of screened facts in the dossier (0, 1–4, 5+).
  - Use: this shows where to stop forecasting rather than how to forecast better.
- **T5. Threshold questions:**
  - Compute: tag markets whose question names a number to be crossed (price, index, rate), using a regex or the existing category. Give the Claude − market Brier gap with its SE against all other markets.
  - Confirms the routing: a gap clearly larger than the rest says to hand these to the model-based pricing of briefs 06–08 instead of Claude.
- **T6. Live checks, which need Joey's OK because they are code or policy changes:**
  - Shadow challengers on the same markets: (a) `effort: high` and (b) a median of 3 samples, both logged but not bet.
  - Judge on the paired Brier difference against Claude direct, and only after 300+ resolved markets (the project's own rule from REBUILD_SCOPE §8).
  - Also record plan usage per forecast, so the gain can be weighed against the research runs it displaces.

## Data sources

No paid data needed.
- **ForecastBench** ([forecastbench.org](https://www.forecastbench.org)): a public leaderboard and question sets, free. Useful as a fixed benchmark that never leaks the answer, if we ever want to compare Claude-direct setups outside our own markets.
- **Metaculus FutureEval and AI benchmark notebooks**: free. A source of new findings each quarter.

## Not verified

- The Brier size of the reasoning-effort gain. Metaculus reports peer scores only, and only one pair's numbers are published.
- How much more an `effort: high` direct call costs on Opus 5.5, in tokens or plan share.
- How many questions are in the Metaculus calibration notebook (it isn't stated), and whether Metaculus bots were over- or underconfident before the fit.
- The per-prompt numbers in Schoenegger et al. 2025 and the per-bin figures in KalshiBench: extracted from the papers' bodies by one agent, not independently re-checked. The headline claims in both abstracts were checked.
- The S&P threshold example and the per-category news effects in Karkar & Chopra: confirmed in the text, but each rests on a handful of questions.
- Whether Schoenegger et al. 2024 ("Wisdom of the silicon crowd") was published in *Science Advances*.
- The optimizer's-curse reference (Smith & Winkler 2006): cited from general knowledge, not fetched.
- Refuted in verification and not used: AIA's claim that agentic search drives most of the gain; FRI's year-on-year improvement figure and its date for reaching superforecaster level; one framing of Turtel et al.'s margin over o1.
- Nothing verified on gains from breaking questions into parts, debate or self-critique, or on how accurate LLMs are on threshold-crossing questions specifically.
