# 05: Combining our forecast with the market price

Researched 2026-10-09 for `docs/research/briefs/05-blend-with-market.md`.

## Answer in five lines

1. Start from the market and move away from it only as far as a source has earned. Use a log-odds pool fitted as
   a shrunk logistic regression with the market as an offset: `logit q = logit m + a + g·logit m + Σ w_k·(logit f_k − logit m)`,
   with priors pulling a, g and every w_k toward 0, which means "the market alone".
2. "Does the model add anything?" is a forecast-encompassing test: is w_k > 0? Run it as a likelihood-ratio test on
   strictly out-of-sample forecasts, clustered by event, with the sample size fixed in advance. A head-to-head Brier
   comparison is the wrong test: a model can lose to the market on Brier and still add information (AIA 2025, Dana 2019, Halawi 2024).
3. Information is not profit. In every study that looked at betting every positive disagreement, it lost money
   (Hubáček & Šír 2023; our own −13% to −21%). Bet only when the blend beats the full cost (ask + fee + slippage)
   by a margin that also covers the optimizer's curse and the uncertainty in the fitted weights.
4. At the weights the literature and our data suggest (w ≈ 0.15–0.5), a 50¢ market needs our model at roughly 63–86%
   before a bet clears costs plus 3¢. Bets this strong will be rare, and the rule should be allowed to place none.
5. Keep the price screen. LLMs shown a crowd number largely echo it (r = 0.88) and do worse than a mechanical average
   of their blind forecast and the crowd (Schoenegger 2024). Showing an LLM the raw price did worse than the price
   alone (Kim 2026). Blending in code after the forecast is the better-supported design.

## Findings

**F1. Combine on the log-odds scale and recalibrate. A plain linear average of the model and the price is
miscalibrated by construction.**
Ranjan & Gneiting (2010, JRSS-B 72(1):71–91) prove that a non-trivial weighted average of distinct calibrated
probability forecasts is itself uncalibrated and too timid, so a linear pool always needs recalibrating. A logistic
regression on log-odds, `logit p = a + b·logit(market) + c·logit(model)`, recalibrates as part of the fit. The 2023
combination review by Wang, Hyndman et al. (IJF; arXiv 2205.04216) repeats this point. It also notes that Baran &
Lerch (2018) found nonlinear pools gave no large gain over simpler ones in their case.
https://ideas.repec.org/a/bla/jorssb/v72y2010i1p71-91.html. Strength: **strong** (a theorem).

**F2. Extremizing is the same thing as scaling log-odds, so the stacking fit already contains it. The coefficients
it reports can look large without being trustworthy.**
Baron, Mellers, Tetlock et al. (2014, Decision Analysis 11(2)) show that extremizing `p^a/(p^a+(1−p)^a)` is exactly
`a·logit p`. On Good Judgment year 1 (1,973 forecasters, 80 binary questions), the best a for aggregated forecasts
was 1.78–3.08, and Brier fell from 0.187 to 0.148 (expert mean). That gain is **in-sample**: a was fitted on the same
questions. The AIA Forecaster report (Alur et al., arXiv 2511.07678, Nov 2025) shows that Platt scaling on log-odds is
the same as extremizing. On 498 questions, a fixed slope of √3 (Brier 0.1076) did as well as fitted slopes (1.72 to
2.27) and better than isotonic regression (0.1097). Lichtendahl et al. (2022, cited in the Wang–Hyndman review) find
that extremizing an average of binary forecasts is not always right, so it has to be checked out of sample.
Strength: **strong** that the two are the same thing; **moderate** on the size of the benefit.

**F3. A model worse than the market can still improve on it in a blend. The best evidence uses LLMs on liquid
prediction markets.**
- AIA Forecaster (2511.07678, Table 7, checked in the full text 2026-10-09): 1,610 questions from 322 resolved liquid
  markets. Market Brier 0.1106, LLM 0.1258, leave-one-out ensemble 0.106. Weights 0.67 market (95% CI 0.53–0.80) and
  0.33 LLM (0.12–0.47). The effective sample is closer to 322 than 1,610, because questions from the same market are
  correlated.
- Halawi et al. (2024, "Approaching human-level forecasting"; 914 test questions published after June 2023): the
  retrieval LLM scored 0.179 against the crowd's 0.149. A weighted average of the two beat both. The LLM matched the
  crowd only where the crowd sat between 0.3 and 0.7 (0.238 vs 0.240).
- Dana, Atanasov, Tetlock & Mellers (2019, JDM 14(2)): on 113 questions, aggregated beliefs beat the market by 12% on
  Brier without significance (p = 0.15). The 50/50 blend beat the market significantly (p = 0.004) and won on 85% of
  questions. Caveat: those beliefs were collected after the forecasters saw the order book.
- Rothschild (2009, POQ 73(5)): a probit of the 2008 race outcomes on transformed Intrade prices and polls, over 74
  races. Intrade's weight was 1.25 (SE 0.37). Debiased polls got 0.45 (SE 0.21), significant only on the full sample.
  The fit was in-sample, over one cycle.

Strength: **moderate**. Several independent studies point the same way, but each sample is small or clustered.

**F4. Weights fitted on small samples are unstable, and can hurt out of sample.**
- On the AIA's 76-question set, the leave-one-out blend scored worse than the LLM alone (0.079 vs 0.075). The weight
  intervals were huge: LLM 0.87 [0.42, 1.00], market 0.14 [0.00, 0.58].
- The forecast-combination puzzle (Wang, Hyndman et al. 2023 review; Smith & Wallis 2009; Claeskens et al. 2016):
  fitted "optimal" weights often lose to fixed simple weights, because estimation error outweighs the gain. The
  standard fix is to shrink the weights toward a simple default.

Strength: **strong** for the puzzle, which has a large literature; **moderate** for the 76-question example.

**F5. The test for "does the model add information" is forecast encompassing, run as a likelihood test, not an
ordinary least-squares t-test.**
- Fair & Shiller (NBER w2503, 1988; AER 1990): regress the outcome on both forecasts with an intercept and
  unconstrained weights, then test whether the second forecast's weight is zero. Harvey, Leybourne & Newbold (1998,
  JBES 16(2)) show that the ordinary least-squares version is not robust to non-normal errors, and 0/1 outcomes are
  very non-normal. Clements & Harvey (2010, J. Applied Econometrics 25(6); Warwick WP 774) give encompassing tests built
  for probability forecasts under Brier and log scores, with small-sample Monte Carlo results.
- Fair & Shiller warn that **in-sample forecasts produce a spurious weight**. Every forecast in the test must use only
  information from before it was made, and so must any calibration map applied to it.

Strength: **strong** (established econometrics). The step from continuous outcomes to logistic regression is the
standard analogy, not a separate result.

**F6. Checking "is it working yet?" every week invalidates fixed-sample tests.**
Henzi & Ziegel (2022, Biometrika; arXiv 2103.08402): with three interim looks, a nominal 5% Diebold–Mariano or t-test
rejected falsely 12% of the time, and more often with more looks. E-values built from score differences allow
stopping at any time (stop when E ≥ 20, an error rate of 5% or less). They have less power, and they need a correction
when forecasts overlap in time, as ours do (many markets open at once). For paired-score (Diebold–Mariano) tests,
ForeComp (CRAN) gives finite-sample size and power for a given n. Strength: **strong**.

**F7. Sports betting: information is not profit, and adding the market as an input erodes the edge.**
- Hubáček & Šír (2023, IJF 39(2); arXiv 2010.12508): 9,093 NBA games, 2006–2014. Flat-betting every positive-EV
  disagreement lost at every setting (−5.1% to −0.4%). Only a selective mean–variance strategy made money (best
  +1.74%). The ± values there are seed noise only, and the best setting was picked afterwards.
- Hubáček, Šourek & Železný (2019, IJF 35(2)) trained models to disagree with the bookmaker on purpose.
- Adding the bookmaker odds as an input raised accuracy (68.8% vs 67.6%) and raised correlation with the market from
  0.87 to 0.95. Returns were no better.

Strength: **moderate** (one domain, trained models, not LLMs).

**F8. The one documented profitable rule needed a fixed margin over consensus, not a positive edge.**
Kaunitz, Zhong & Kreiner (2017, arXiv 1710.02824, not peer reviewed): 479,440 football games, 2005–2015. Consensus
closing odds were calibrated to slopes of 1.00–1.08 (R² ≥ 0.995), apart from a constant margin. They bet only when a
price beat the margin-adjusted consensus by α = 0.05: +3.5% in backtest, then profitable with real money until the
bookmakers limited them. α was chosen in-sample, and bookmaker margins (3.4–5.7 points) are smaller than our ~8.4%.
Strength: **moderate**.

**F9. Choosing the biggest disagreements guarantees disappointment unless you shrink first.**
Smith & Winkler (2006, Management Science, "The Optimizer's Curse"), a mathematical result:
- If you pick the best of several unbiased estimates, the pick is overstated. With 10 options of equal true value it
  is overstated by 1.54 standard deviations of the estimate, and correlated errors only partly help.
- The fix is Bayesian shrinkage toward a prior before choosing. The expected overstatement of the chosen option is
  (1 − α)·(estimate − prior mean), so noisy estimates far from the prior shrink the most.

For us the market is the prior, and a scan that bets only the largest model-vs-market gaps is exactly this situation.
This source was extracted but not voted on in verification; the 2006 paper is well known. Strength: **strong** (theorem).

**F10. Letting the forecaster see the price: more accurate forecasts, but less independent information. Blending
in code works better.**
- Schoenegger, Tuminauskaite, Park & Tetlock (2024, arXiv 2402.19379, Science Advances; abstract checked
  2026-10-09): on 31 Metaculus questions, GPT-4 and Claude 2 improved 17–28% after seeing the human median. But their
  updated forecasts were less accurate than a simple average of their blind forecast and the human one. Their
  adjustments tracked the distance to the median, r = 0.88 and 0.87: anchoring or deference. The sample is small.
- Kim et al. (2026, arXiv 2602.21229, "Forecasting Future Language: Context Design for Mention Markets"), 856
  earnings-call mention markets (the venue is Kalshi per the extracted text; not re-checked):
  - pasting the market probability into the prompt did *worse* than the market alone (Brier 0.167 vs 0.140);
  - prompting the LLM to treat the price as a prior and update it came close to the market;
  - a 0.7·market + 0.3·LLM mix was only slightly better than the market (0.139), with no significance test;
  - where the two disagreed, the market won 42 of 70.
- ForecastBench (Karger et al., ICLR 2025, arXiv 2409.19839): the top LLMs were the ones given the crowd forecast
  (Claude 3.5 Sonnet 0.122 with it, 0.136 without). But unresolved questions were scored against the crowd itself,
  which rewards copying it.
- The AIA Forecaster deliberately blocks prediction-market prices from its retrieval, the same design as our
  `news.screen_facts()`.
- Against this: in Dana et al. (F3), beliefs reported after seeing the order book still added information.

Strength: **moderate**. The direction is consistent across studies, but the samples are small. No study measures
whether showing the price shrinks an LLM's incremental weight w, which is the quantity that matters to us.

**F11. Requiring several sources to agree: no direct evidence.**
- No verified study tests an "all sources must agree" rule.
- The theory (encompassing, F5; decorrelation, F7; Smith & Winkler's correlated errors, F9) says a second source adds
  only to the extent its errors differ from the first's.
- Claude direct and Jev + research read the same research, and on 646 markets Jev + research did worse than Claude
  reading it (REBUILD_SCOPE §2). So their agreement probably adds little.

Strength: **weak** (inference only).

## What it means for our trader

These are ranked. Every item that changes code needs Joey's OK. Nothing here touches the price screen.

**1. Replace "forecast − cost ≥ min_edge" with a market-anchored blend and a cost-plus-haircut rule** (the
recommended formula). Expected effect: far fewer bets, and an end to the systematic −13% to −46% from overconfident
disagreements. Whether any bets survive with positive return is unknown, and the honest prior is "few or none".
Confidence: high that it stops the bleeding, low that it makes money.

*The combination formula.* For a market with a two-sided price (both asks quoted, spread ≤ 10¢; otherwise no bet and
no scoring):

- the inputs are:
  - `m` = mid at decision time;
  - `f_k` = source k's probability, clipped to [0.02, 0.98];
  - `Lm = logit(m)` and `D_k = logit(f_k) − Lm`;
- the blend is `z = Lm + a + g·Lm + Σ_k w_k·D_k`, and `q = 1/(1+e^(−z))`.

This is the free stack `a + b·Lm + Σ c_k·logit f_k` rewritten so that "all zeros" means "trust the market": c_k = w_k
and b = 1 + g − Σ w_k. Read it as a Bayesian update with the market as the prior: each source's log-likelihood
ratio against the market is counted at weight w_k.

*The fit.* Maximise the logistic likelihood with Gaussian priors, which is ridge logistic regression with offset Lm:
- a ~ N(0, 0.2²) and g ~ N(0, 0.15²): small corrections to the market's own calibration (favourite/long-shot
  belongs to brief 01);
- w_k ~ N(0, 0.25²).

The priors shrink everything toward the market (F4, F9). With few markets the weights stay near 0 and the blend
stays near the price. These prior widths are a judgment call: they let a well-supported weight reach the 0.3–0.5
seen in the literature. Keep the fitted covariance Σ (the inverse Hessian at the optimum) for the haircut.

*The betting rule.* For each side s (YES uses q, NO uses 1 − q):
1. `cost_s = ask_s + fee(ask_s) + slippage`, the same as `engine.decide` today.
2. `sd_z = sqrt(xᵀ Σ x)`, where x is the market's row (1, Lm, D_1, …), and `q_lo = sigmoid(z − 1.645·sd_z)` on that
   side.
3. Bet only if **all** of these hold:
   - (a) `q_lo − cost_s ≥ h`, with h = 0.03 to start (it covers the optimizer's curse left after shrinkage, F8–F9);
   - (b) the model term points the same way, i.e. `Σ w_k·D_k` pushes toward side s, so a bet that the calibration
     terms a and g alone would make is a brief-01 bet and is logged separately;
   - (c) every source with w_k ≠ 0 has passed the encompassing gate below.

h stays a code-held floor that the loop may raise but not lower below 0.02. That last part is a policy choice, so it
needs Joey's say.

*The encompassing gate.* A source gets a non-zero w_k in the betting blend only once a one-sided likelihood-ratio
test of w_k > 0 passes at 5%, with standard errors clustered by event, on rolling-origin out-of-sample forecasts.
That needs at least 300 settled two-sided markets. The paired log score of the blend must also beat the
market-only calibration (w = 0) with an event-clustered bootstrap 95% CI above zero. Use the sample size fixed in
advance (below), or Henzi–Ziegel e-values if it is checked continuously.

*Fitting and refitting without overfitting:*
1. One row per market, at its first two-sided look, using only the forecast made then.
2. Refit weekly on markets **settled before** the refit date (rolling origin). The weights fitted at refit t are the
   only ones used for decisions until t+1, and those decisions are scored only on markets settling after t
   (Fair & Shiller's out-of-sample rule, F5).
3. Never fit on the markets being scored, and never let the learning loop pick w, a or g by searching for the
   best backtest return. They come only from the likelihood fit. The loop may tune h and market filters, as now.
4. If a source's own calibration map is applied first, it must be out-of-sample too. Simpler: feed raw forecasts and
   let a, g and w do the recalibrating.
5. Publish every refit's weights with their 95% intervals. Flag any week where a weight moves more than one SE
   (a sign of drift, Hendry & Clements 2004 via the review).

**2. Treat the current b ≈ 1.35, c ≈ 0.52 as unexplained until it is checked.** In my scratchpad simulation, a
calibrated market with Brier ~0.17 plus an LLM with independent errors at Brier ~0.21 gave a free fit of about
b ≈ 0.75 and c ≈ 0.12, not 1.35 and 0.52. Making 13% of the market mids uninformative (wide spreads) raised c to 0.21
and *lowered* b. So b + c ≈ 1.87 says both inputs are far too timid on our sample. That could be real (the market
underreacts on short-dated markets), or it could be a leak or a scoring artifact. Taken at face value it says a 70¢
favourite the model agrees with is worth 83%, which our own "always buy the favourite: −2.8% ± 1.7%" contradicts.
Confidence: moderate that something in that fit is off, because this is my simulation, not a paper.

**3. Keep the price screen and blend in code** (no change). F10 supports this, and it keeps the blind forecast as
an independent input, which is what gives it any weight. If Joey ever wants to test a price-aware forecaster, run it
as a separate challenger. Judge it by its w in the encompassing test, not by its Brier, since copying the price
always improves Brier.

**4. Don't add an "all sources agree" gate. Put each source in the stack and test it conditional on the others.**
If Jev + research has w ≈ 0 given Claude direct, drop it from the blend; that frees research budget. Confidence:
moderate.

**5. Expect the model's information to sit in the uncertain middle (market 30–70¢).** Halawi and Kim both found
this. Consider letting the weight vary by price band only if the test below finds it. Confidence: low to moderate.

How big a disagreement pays, under the recommended form. Assumptions: Kalshi, 2¢ spread, slippage 1¢, h = 0.03, no
haircut for fit uncertainty (adding it raises these numbers). The table gives the model probability needed to bet
YES:

| market mid | w = 0.15 | w = 0.30 | w = 0.50 |
|---|---|---|---|
| 0.20 | 0.72 | 0.45 | 0.34 |
| 0.35 | 0.78 | 0.58 | 0.49 |
| 0.50 | 0.86 | 0.71 | 0.63 |
| 0.65 | 0.93 | 0.84 | 0.77 |
| 0.80 | 0.99 | 0.95 | 0.91 |

At Jev-like weights (0.12–0.16) almost nothing qualifies, which matches what the data already showed.

## How to test it on our history

These tests are for the main session to run on the ~1,133 finished markets. Use only first looks with spread ≤ 10¢,
and cluster every standard error and bootstrap by event (markets from one event resolve together).

1. **Refit the stack honestly.** Run rolling-origin weekly refits of the free form `a + b·Lm + c·logit f` and of the
   offset form for each source, with the market input as the mid (not the ask), on two-sided markets only. Report
   a, b, c with clustered 95% CIs, by category and by time-to-close.
   - *Confirms:* c's CI excludes 0 for Claude direct.
   - *Kills the model's role:* c's CI includes 0 on two-sided markets.
   - *Flags a problem:* b + c stays well above 1.3. Then look for leakage, forecasts made after the price snapshot,
     or a sample of short-dated markets settling at extremes.
2. **Nested encompassing.** Fit Claude direct alone, then add Jev + research, Jev alone and self-calibrating Jev one
   at a time, with a likelihood-ratio test of each added w.
   - *Confirms dropping a source:* its added w has a CI that includes 0.
3. **Paired score test.** Compare the out-of-sample log score and Brier of the blend against market-only calibration
   (w = 0), with an event-clustered bootstrap and the Diebold–Mariano statistic with a fixed-b correction (ForeComp).
   - *Confirms:* the CI of the improvement is above 0.
   - Expect this to be small, about 0.002–0.005 Brier per the AIA and Kim papers.
4. **Backtest the betting rule exactly as specified**, with q_lo, h = 0.03 and condition (b), at ask plus fee plus
   slippage. Report the number of bets, the return with a bootstrap CI, and the same rule with w forced to 0
   (market structure only). Also report realized edge against predicted edge for the bets taken; a slope below 1 is
   the optimizer's curse.
   - *Kills it:* fewer than ~100 bets, or a return CI entirely below 0.
   - *Confirms it:* a return CI above 0 that does not depend on one category.
5. **Where the information sits.** Bin markets by mid (≤0.3, 0.3–0.7, ≥0.7) and by |D|, and fit w per bin.
   - *Confirms F10/F11's "middle" pattern:* w is significantly larger in 0.3–0.7.
6. **Agreement rule vs stack.** Compare the return and the number of bets with Claude direct and Jev + research
   both on the bet's side, against the stacked rule.
   - *Expected:* agreement adds nothing once both sources are in the stack.
7. **Closing-line check as an early signal.** For every bet the rule would place, does the mid 6 h, 24 h and at last
   snapshot move toward q (CLV)? This shows signal long before outcomes do.
8. **Sample size.** In my simulation (a model at Brier ~0.21 with errors independent of the market's, at the
   standard 5% significance level), the likelihood-ratio test of w = 0 had 32% power at 300 markets, 50% at 600 and
   73% at 1,100. With noisier models (Brier ~0.27), power was 38% at 1,100. Two consequences:
   - Fix the evaluation point in advance (for example the first 600 new two-sided markets after the change, then
     1,100), or use e-values.
   - Treat "not significant" at a few hundred markets as "not yet known", not "no information".

## Not verified

- The full-text numbers of Kim et al. 2026 (Brier values, 856 markets, Kalshi as the venue); the abstract confirms
  only the method and the direction.
- The Atanasov et al. 2017 effect sizes; only the abstract was read.
- Smith & Winkler's numbers came from extraction and were not run through the three-vote check.
- No study tests a price-blind LLM against a real-money prediction market *with trading costs*.
- No study measures how seeing the price changes an LLM's incremental weight w.
- No study tests a rule that requires several sources to agree.
- The sample-size figures and the b, c sanity check come from my own simulation (generative assumptions: logit truth
  ~ N(0, 1.8²), independent normal errors on the log-odds scale). They are illustrations, not evidence.
- The prior widths (0.2, 0.15, 0.25), h = 0.03 and the 300-market minimum are judgment calls, to be checked by tests
  4 and 8.
