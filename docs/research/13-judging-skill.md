# 13: Telling skill from luck quickly

Researched 2026-10-09 for `docs/research/briefs/13-judging-skill.md`.

Method: the deep-research workflow (5 search angles, 22 sources fetched, 107 claims extracted, the top 25 put to a
3-vote adversarial check: 23 confirmed, 2 refuted), then a second pass that read the primary papers for the topics the
first pass dropped for budget (deflated Sharpe, backtest overfitting, false discovery, closing-line value). Sample-size
numbers are my own arithmetic from the standard formulas, marked as such. No `papertrade_data/` was analysed; the
spreads used below come from the ± figures already published in `docs/REBUILD_SCOPE.md`.

## Answer in five lines

1. **Judge forecasters, not bets.** A paired Brier comparison against the market on every finished market (about 85 a
   day) settles a 0.02 gap in a few hundred markets. Profit and loss needs 800 to 7,000 bets for a 5–10% edge, which
   is months at our volume, and longer still once a dozen variants share the history.
2. **Closing-line value (CLV) is the fast signal for bets.** Score each bet by where the mid price stood some hours
   later, never by the final price. It needs about 20 to 80 times fewer bets than profit and loss. It shows only that
   the market later agreed with us, not that we beat costs, so it supplements profit and loss rather than replacing it.
3. **Peeking and picking break ordinary tests.** Checking a 5% test at four looks gives a 12% false-alarm rate, and
   picking the best of 12 variants needs a z of about 2.9, not 1.96. Use always-valid tests (confidence sequences or
   e-values) for monitoring, and count every variant ever tried.
4. **One history can't both pick and prove a strategy.** A split of the 1,100 markets can itself be mined. The proof
   must come from markets that finish *after* the rule is frozen and written down, a forward test fixed in advance.
5. **Our learning loop changes rules far faster than our data can justify.** Rules change every 1–2 days, on tens of
   bets per version (±20–30% standard error on return). The calibration map starts at 30 markets. Both are tuning on
   noise.

## Findings

### A. Comparing a forecaster with the market (Brier)

**A1. The right test is a paired one: the per-market score difference, tested with Diebold-Mariano.**
Take d_i = (f_i − y_i)² − (m_i − y_i)² on each market i (our forecast f, market price m, outcome y), then test whether
mean(d) = 0 with DM = d̄ / se(d̄), which is approximately N(0,1). The DM test takes forecasts, not models, as its input,
and Diebold names "forecasts obtained from explicit prediction markets" as a use. It needs a variance that is robust to
dependence: clustered by event when several markets share one event.
Evidence: Diebold, *Comparing Predictive Accuracy, Twenty Years Later*, NBER WP 18391 (2012; JBES 33(1), 2015), §2.1,
https://www.nber.org/papers/w18391.pdf. Strength: **strong** (3–0 vote; a standard method).

**A2. In small or dependent samples, plain DM with 1.96 calls a winner too often. Use a t-reference correction.**
In a Monte Carlo study (10,000 replications, nominal 5%), the real false-positive rate was 7.7% (MA(1)) to 19.6%
(MA(5)) at T = 40, and 5.8–8.6% at T = 120. Fixed-m (Daniell kernel, t with 2m degrees of freedom) or fixed-b
(Bartlett, M = T^½) corrections brought it back to 4.0–5.0%. The Harvey-Leybourne-Newbold correction is formally
justified only for independent loss differences.
Evidence: Coroneo & Iacone, York DP 15/15 (2015; J. Applied Econometrics 2020),
https://www.york.ac.uk/media/economics/documents/discussionpapers/2015/1515.pdf. Strength: **moderate**: one source,
and it simulates Gaussian errors, not bounded Brier differences. The direction carries over to our case; the exact
sizes may not.

**A3. Classical binned calibration plots and the binned Murphy decomposition mislead at our sample sizes.**
On n = 86 forecasts, 9, 10 or 11 equal bins gave "drastically distinct reliability diagrams". Binned calibration error
moves with the bin count, so it can be "fudged (whether purposefully or unintentionally)". In finite samples the binned
decomposition overstates reliability (the forecaster looks worse calibrated than it is), understates uncertainty, and
biases resolution in either direction (Ferro & Fricker). The bias can be reduced but not removed.
Evidence: Dimitriadis, Gneiting & Jordan, *Stable reliability diagrams*, PNAS 118(8) 2021,
https://arxiv.org/pdf/2008.03033. Dimitriadis, Gneiting, Jordan & Vogel, *Triptych*, 2023,
https://arxiv.org/pdf/2301.10803. Bröcker & Smith, Weather and Forecasting 2007. Ferro & Fricker, QJRMS 138 (2012),
doi 10.1002/qj.1924 (verified from the abstract only). Strength: **strong** (3–0, four sources).

**A4. CORP reliability diagrams with consistency bands are the replacement, and they give an exact decomposition.**
CORP fits an isotonic regression with the PAV algorithm, which picks the number and position of bins itself, with no
tuning. In simulations (n = 128 to 8,192, 1,000 replicates each) it beat 5, 10 and 50 fixed bins and quantile bins at
every sample size. Its decomposition is exact: **Brier = MCB − DSC + UNC**, where

- MCB = S − S_C (miscalibration, ≥ 0);
- DSC = S_R − S_C (discrimination, ≥ 0);
- UNC = S_R = ȳ(1 − ȳ);
- S_C is the score of the PAV-recalibrated forecast, and S_R the score of always forecasting the base rate.

For binary Brier, MCB and DSC equal Murphy's REL and RES only when the conditional event frequencies don't decrease
across the forecast values. A claim that they always equal them was refuted 0–3.

A 90% consistency band, made by resampling under perfect calibration, shows which parts of the curve could be noise.
The band is pointwise and is not a formal test, and the paper recommends resampling bands for n ≤ 1,000.

Evidence: same PNAS 2021 and Triptych 2023 papers; Bröcker & Smith 2007 for consistency resampling. Strength:
**strong**, though the evidence that CORP resists overfitting comes from its own authors.

**A5. Skill against the market is a skill score, and UNC cancels in a paired comparison.**
BSS = 1 − BS_ours / BS_market. Population identity (Murphy 1973): E[(X−Y)²] = Var(Y) − Var(E[Y|X]) + E[(X − E[Y|X])²].
On the same markets UNC is shared, so the comparison is (MCB_ours − MCB_mkt) − (DSC_ours − DSC_mkt): did we lose on
calibration, on discrimination, or both?
Evidence: Pohle 2020, https://arxiv.org/pdf/2005.01835. Strength: **strong** (a textbook identity).

### B. Watching results as they come in

**B1. Peeking inflates false positives.** A one-sided 5% t-test of the mean Brier difference, checked at 150, 300, 450
and 600 markets and stopped at the first significant look, rejected 12% of the time when there was no difference.
With five looks the figure reaches about 15%.
Evidence: Henzi & Ziegel, *Valid sequential inference on probability forecast performance*, arXiv 2103.08402 (2021,
rev. 2022), §4.1. This matches the classical result (Armitage, McPherson & Rowe 1969). Strength: **strong** (3–0).

**B2. Always-valid alternatives exist for exactly our comparison.**

- **E-values for "forecast p beats forecast q":** valid for any proper score, in finite samples, with no model
  assumptions. Multiply them as results arrive, and reject when the running product exceeds 1/α (20 at α = 0.05).
  The cost is less power than DM, and a stronger null. Staggered resolution dates (lag > 1) need care.
  Source: Henzi & Ziegel, Theorem 3.1. Strength: **strong** (3–0).
- **Confidence sequences:** Choe & Ramdas, *Comparing sequential forecasters* (arXiv 2110.00115, Operations
  Research), give empirical-Bernstein confidence sequences for the running mean score difference. They hold "at
  arbitrary data-dependent stopping times" and need only bounded scores.
  - Worked example: FiveThirtyEight against Vegas closing odds on 25,165 MLB games (2010–2019). The Brier interval was
    (−0.00265, −0.00062), so the betting market was marginally better than the expert model.
  - Weather examples run T = 1,128 to 1,809.
  - Such a sequence is wider than a fixed-time interval at any single moment. That width is the price of being able
    to look every hour.

  Strength: **strong** (the paper's own statements, confirmed in the second pass). Background: Ramdas et al.,
  Statistical Science 38(4) 2023; Waudby-Smith & Ramdas, JRSS-B 2024.

### C. Closing-line value

**C1. CLV is far less noisy than profit and loss, by about 80× in the best documented example. But that example is a
vendor article about one bettor.**
Buchdahl (Pinnacle, 4 Apr 2019) reviewed one bettor's 1,214 bets at average odds of 2.065. Beating the no-margin
closing price by 2.19% was about 18.5 standard errors from chance (sd of the price-to-close ratio 0.114). The same
record judged by profit could have come from luck "about once in 200 bettors". Squaring the standard deviations
(1.03 for profit, 0.114 for CLV) gives a variance ratio of about 82.
https://www.pinnacle.com/betting-resources/en/betting-strategy/using-the-closing-line-to-test-your-skill-in-betting/7e6jwjm5ykejuwkq.
Strength: **anecdotal** (vendor, one bettor). The second pass found no peer-reviewed study that ties a bettor's CLV
to later profit.

**C2. Why the gain is real, and how big it is for us (my derivation).**
If the price is a martingale, the noise in profit splits cleanly: Var(Y − p) = Var(c − p) + E[c(1 − c)], where p is
our entry, c the later price and Y the outcome. CLV keeps only the first term. The bets saved are therefore
p(1−p) / Var(c − p):

| Price move from bet to measuring point (sd) | Factor fewer bets |
|---|---|
| 5¢ | about 100× |
| 10¢ | about 25× |
| 20¢ | about 6× |

The factor shrinks the later the price is read, because a late read includes most of the outcome noise. A simulation
(300 runs of 200 bets with a true 2¢ edge) gave a mean t of 5.7 on CLV against 0.6 on profit and loss when moves had
sd 5¢; at 10¢ it gave 2.9 against 0.5. Strength: **moderate**. The algebra is standard, but it assumes the later
price is efficient, which is exactly the thing in question.

**C3. Never use the final price as the "close".** Near resolution a binary price runs to 0 or 100 and order flow
becomes mechanically one-sided. Bartlett & O'Hara (41.6 million Kalshi trades) restrict their analysis to prices of
30–70¢ for this reason. Measuring each market over its whole life instead of its first 80% roughly halved the
calibration gap they found (4.5 to 2.3 points). A "close" taken after the answer is known is just the outcome, so
CLV against it collapses back into profit and loss.
Evidence: *Adverse Selection in Prediction Markets: Evidence from Kalshi*, NBER conference paper, July 2026,
https://conference.nber.org/conf_papers/f243677.pdf. Strength: **moderate** (2–1 vote; the paper is about flow, not
CLV, so applying it to CLV is an inference). A related claim, that Kalshi price impact is "almost entirely permanent",
was **refuted 1–2**, so we cannot assume a move after our bet is information rather than noise.

**C4. Positive CLV does not mean profit.** On 3,670 NBA games (2022/23 to 2024/25, about 10 books), bets were sorted
into ten groups by CLV. The second-best group averaged 5% CLV but only +0.2% profit, against a margin of about 4.5%.
Only the top group made a meaningful profit (+11.4%). CLV can also be gained mechanically, for example by betting
heavy underdogs early in thin markets.
Evidence: Karl Whelan, *The Truth about Closing Line Value*, 12 Aug 2026, https://www.karlwhelan.com/?p=2595.
Strength: **anecdotal/moderate** (an economist's blog with a stated dataset). For us: CLV must clear our ~8.4% cost,
not zero.

**C5. A beat-the-consensus strategy can show a real edge in a backtest and still be marginal live.**
Kaunitz, Zhong & Kreiner (arXiv 1710.02824, 2017) bet whenever a bookmaker's odds beat the consensus by a margin.

- Backtest on closing odds: 56,435 bets, +3.5%.
- At odds 1–5 hours before kickoff: 6,994 bets, +9.9%.
- Live (paper plus real money): 672 bets, +6.2%, p = 0.089 against random betting, so not significant.
- The margin was chosen in-sample, and bookmakers limited their accounts.

Strength: **moderate** (not peer-reviewed). It is a clean real-world example of everything in this brief: one setting
picked in-sample, a strong backtest, and too few live bets to confirm the edge.

### D. Testing many variants on one history

**D1. Holding out part of one history isn't enough.** The split point can itself be mined. Protection across many
variants needs simulation-based tests over the whole set tried (White's Reality Check, Hansen's SPA, the
Hansen-Lunde-Nason model confidence set), or new data.
Evidence: Diebold 2012/2015, §4.1. Bailey & López de Prado (2014) put it the same way: run a holdout "say 20 times
for a 95% confidence level" and "false positives are no longer unlikely: They are expected." Strength: **strong** (3–0).

**D2. Probabilistic and deflated Sharpe ratio, and minimum track record.** All three are formulas in observations, so
they work per bet.

- **PSR(SR\*) = Φ[(SR̂ − SR\*)·√(n−1) / √(1 − γ₃·SR̂ + (γ₄−1)/4·SR̂²)]**. SR̂ is the per-bet mean return over its sd,
  γ₃ is skew and γ₄ is kurtosis (3 for a normal).
- **DSR** is PSR with SR\* raised to **SR₀ = √V[SR_n]·((1−γ)Φ⁻¹(1−1/N) + γΦ⁻¹(1−1/(Ne)))**, where N is the number of
  trials and γ ≈ 0.5772. In the paper's example the same result fails at N = 100 trials (DSR 0.90) but would have
  passed at N = 46.
- **MinTRL = 1 + (1 − γ₃·SR̂ + (γ₄−1)/4·SR̂²)·(Φ⁻¹(1−α)/(SR̂ − SR\*))²** observations. Trust it only above about 30.

Evidence: Bailey & López de Prado, *The Sharpe Ratio Efficient Frontier*, J. Risk 15(2) 2012, and *The Deflated Sharpe
Ratio*, JPM 40(5) 2014 (authors' PDFs at davidhbailey.com). Strength: **strong** for the formulas (read from the
primary papers). The second pass did not put them to a vote.

**D3. Probability of backtest overfitting (PBO, by CSCV).** Arrange the results as one row per time block and one
column per variant (all N variants). Split the rows into S blocks (S = 16 suggested). Take every half of the blocks as
the training set and the other half as the test set. PBO is the share of splits in which the variant that did best
on the training half lands below the median on the test half. The authors suggest rejecting a selection process when
PBO > 0.05.

- N must be "≫ 10" to resolve small PBOs.
- Hiding failed variants biases PBO down.
- A high PBO doesn't prove that no variant has skill.
- It cannot catch wrong costs or look-ahead.

Evidence: Bailey, Borwein, López de Prado & Zhu, J. Computational Finance 20(4) 2017. Strength: **strong** (primary
paper; not voted).

**D4. False discovery control and the t > 3 bar.**

- **Benjamini-Hochberg (BH):** find the largest k with p₍k₎ ≤ (k/m)·α and reject the first k. It is valid under
  independence or positive dependence.
- **Benjamini-Yekutieli (BY), for arbitrary dependence:** p₍k₎ ≤ k·α / (m·Σᵢ₌₁ᵐ 1/i).
- Harvey, Liu & Zhu (RFS 29(1) 2016; NBER w20592) argue that a new finance factor needs t > 3.0, and that "most
  claimed research findings in financial economics are likely false".
- Harvey & Liu (JPM 2015) recommend BHY for choosing among strategies. They show the haircut is nonlinear: over 50%
  for weak Sharpe ratios, at most 25% above 1.0.
- Correlated variants shrink the effective number of tests.

Strength: **strong** (standard results; formulas confirmed in the second pass).

**D5. Purging and embargo.** When labels overlap in time, drop from training every observation whose label overlaps
the test period (purging). Also drop the observations just after each test block (embargo). Source: López de Prado,
*Advances in Financial Machine Learning* (Wiley 2018), ch. 7 and 12, via the skfolio documentation; the book text
itself was not reachable. For us the "label" is a market's resolution, so a market that is still open at the cutoff
belongs to neither side. Strength: **moderate**.

## Formulas and minimum samples

Notation: α = 0.05 two-sided and 80% power, so K = (1.96 + 0.84)² = 7.85. All counts below are **my arithmetic**.
They assume independent markets; divide n by the design effect 1 + (m−1)ρ when m markets share an event with
correlation ρ (for example 1.6 for m = 3 and ρ = 0.3).

**Return on stake from realized profit and loss.** A binary bet at price p has return sd ≈ √((1−p)/p): 1.53 at 30¢,
1.00 at 50¢, 0.65 at 70¢. Then n = K·sd²/edge², and one standard error after n bets is sd/√n (±20% at 24 bets,
±8.5% at 137, ±4% at 600, at 50¢).

| Price | 2% edge | 5% edge | 10% edge |
|---|---|---|---|
| 30¢ | 46,300 | 7,500 | 1,930 |
| 50¢ | 19,600 | 3,130 | 780 |
| 70¢ | 8,200 | 1,250 | 280 |

These are bets, for the *net* edge after the 8.4% cost.

**Paired Brier gap against the market.** n = K·sd(d)²/gap². The published ± figures imply sd(d) ≈ 0.16–0.18 for our
forecasters on general markets, and 0.07 for Claude on real-priced sports, where it sits closer to the price. A
forecaster that stays near the price has a smaller sd(d), so it is cheaper to test.

| sd(d) | gap 0.005 | gap 0.01 | gap 0.02 |
|---|---|---|---|
| 0.07 | 1,540 | 385 | 100 |
| 0.10 | 3,140 | 785 | 200 |
| 0.16 | 8,040 | 2,010 | 500 |

Today's gaps (0.035 to 0.073) need only 50 to 170 markets. That is why they are already settled at 4–7 standard
errors.

**Closing-line value per bet.** n = K·sd(move)²/CLV². sd(move) is the spread of the later mid minus our fill, in
probability points, and must be measured.

| sd(move) | CLV 1¢ | CLV 2¢ | CLV 5¢ |
|---|---|---|---|
| 0.05 | 200 | 50 | 8 |
| 0.10 | 785 | 200 | 32 |
| 0.15 | 1,770 | 440 | 71 |

**Picking the best of N variants.** The required z rises from 1.96 to 2.87 (N = 12), 3.08 (N = 24) and 3.29
(N = 50). That multiplies every n above by 1.75, 1.96 and 2.18. DSR's version of the same bar for N = 12 independent
variants, at 50¢:

| Bets | Per-bet Sharpe needed | Return needed |
|---|---|---|
| 300 | 0.19 | 19% |
| 1,000 | 0.105 | 10.5% |
| 3,000 | 0.06 | 6% |

**Minimum sample for each kind of decision** (my recommendation, built from the tables above):

| Decision | What to measure | Minimum before acting |
|---|---|---|
| Drop or bench a forecaster that looks worse than the market | Paired Brier, DM with event-clustered se, or a confidence sequence | 200 real-priced markets, *or* earlier if an always-valid sequence excludes zero |
| Claim a forecaster beats the market | Paired Brier, plus a correction for every forecaster tried | 400 (sd 0.07) to 2,000 (sd 0.16) markets for a 0.01 gap, times about 1.75 for 12 tried, on markets that finish after the claim is written down |
| Trust a calibration map | CORP plus a consistency band | 300 or more; never 30 |
| Promote a strategy to real-money-style trust | CLV at a fixed interior horizon, net of the spread, and then profit and loss as a veto | 200–500 bets of CLV clear of zero after multiple-testing correction, *and* profit and loss not significantly negative |
| Change a betting rule (gate, filter, price band) | Replay old and new rules on the same finished markets, paired; then a forward check | The paired difference beyond 2.9 se across all variants tried, then 200+ forward markets |
| Retire a challenger | The same as dropping a forecaster, or CLV significantly below zero | An always-valid sequence below zero; no fixed count |
| Say anything at all | Every number with ± and n | Nothing under about 100 markets gets a verdict |

## What it means for our trader

Ranked by expected effect. Every code change waits for Joey's OK.

1. **Make the paired Brier comparison against the market on real-priced markets the main forecaster scoreboard.**
   Report d̄ ± clustered se, n, and the CORP split (MCB, DSC). At about 85 finished markets a day, that answers in
   days what profit and loss answers in months. Effect: large (the decisions become trustworthy). Confidence: high.
   This overlaps BACKLOG B25 (scoring the market on its mid in wide-spread markets).
2. **Slow the daily review to the speed of its evidence.** Rules currently may change daily
   (`learning.min_days_between_changes: 1`, although its note says every 2 days). At 20–35 bets a day across a dozen
   strategies, each version is judged on tens of bets, a ±20–30% standard error on return. A rule should change only
   when a paired replay shows the new rule beats the old one on the same markets beyond the multiple-testing bar, not
   on recent profit and loss. The same goes for `calibration_min_resolved: 30`: CORP evidence says that is far too
   few to fit a map. Effect: large (it stops chasing noise). Confidence: high.
3. **Add CLV to every bet record:**
   - the mid at +6h, +24h and at 80% of the market's life (whichever comes first before resolution), each minus the
     ask we paid, in cents and log-odds;
   - only from snapshots with a spread of 10¢ or less and a mid between 5¢ and 95¢.

   Paper bets have no price impact of our own, which removes one standard CLV pitfall. Effect: medium (it gives an
   early read on strategies). Confidence: medium, because nobody has validated CLV against profit on these venues.
4. **Keep a trials ledger.** Count every variant, challenger and back-tested idea ever tried, including research
   sessions like this one, and use that N in a DSR, Bonferroni or BY bar. `docs/EXPERIMENTS.md` already registers
   strategies before results come in; extend it to count back-tests. Effect: medium. Confidence: high.
5. **Freeze before you prove.** Treat the ~1,100-market history as the place where ideas are *found*. Every idea
   must then pass a forward test, registered in advance, on markets that finish after the freeze date: about 2–3 days
   for 200 markets, 12 days for 1,000. Effect: large against the two reversals we already had. Confidence: high.
6. **Monitor with always-valid tests.** Use confidence sequences (Choe & Ramdas) or e-values for the dashboard's "is X
   better than the market" line, so hourly looks don't inflate false alarms. Effect: small to medium. Confidence:
   medium (it costs power at our sample sizes; see "Not verified").
7. **Use profit and loss only as a veto.** It confirms, slowly, that costs are covered; it is the wrong tool to pick
   between variants.

## How to test it on our history

For the main session to run on `papertrade_data/` (real-priced first looks only, spread ≤ 10¢):

1. **sd(d) and clustering.** For each forecaster, compute d_i against the market, its sd, and the intra-event
   correlation ρ, with markets grouped by event. That replaces the placeholder sd(d) values in the tables.
   *Confirms*: sd(d) of about 0.07–0.18, which keeps the minimums above. *Changes the plan*: ρ > 0.3, which raises
   every minimum by the design effect.
2. **CLV noise.** For every settled bet, compute c − ask with c the mid at +6h, +24h and at 80% of the market's life,
   using the interior-price filter. Report sd(c − ask) and the variance ratio p(1−p) / Var(c − p).
   *Confirms CLV as a fast signal*: a ratio of 10 or more at +24h. *Kills it*: a ratio under 3, or a mean CLV that
   disagrees in sign with realized return on 137+ bets.
3. **Does CLV predict outcome?** Sort bets into groups by CLV at +24h and check realized return per group (the
   Whelan test).
   *Confirms*: return rises across the groups. *Kills it*: no slope (ρ ≈ 0 with its ± range).
4. **Peeking replay.** Re-run the 2026-10-02 claims ("Jev + research best", 112 markets; "19 of 24") as if
   monitored with a 95% confidence sequence.
   *Confirms the method*: the sequence would not have called either one a winner.
5. **Rule-change noise.** For the last 20 rule changes the daily review made, compute each version's settled-bet
   count and the ± on its return. *Confirms recommendation 2*: the median ± exceeds the change the review acted on.
6. **PBO on the strategy set.** Build a day × strategy matrix of per-day return across all strategies ever run
   (retired ones included), with S = 8 or 16 blocks, and compute PBO.
   *Confirms an overfitting problem*: PBO > 0.5. *Says selection is working*: PBO < 0.1.

## Data sources

No external data is needed. All the tests run on our own snapshots and outcomes. Software, all free:

- CORP reliability diagrams and decompositions: R package `reliabilitydiag`.
- Brier score with the Ferro-Fricker correction: R `s2dv::BrierScore`.
- Confidence sequences: the Choe & Ramdas code linked from arXiv 2110.00115, and Python `confseq`.
- Purged cross-validation: `skfolio` `CombinatorialPurgedCV`.

Package names come from the papers and the docs; I did not install or run them.

## Not verified

- **How much sooner CLV shows skill than profit and loss on Kalshi or Polymarket.** No peer-reviewed source; the
  ~80× figure is one vendor example, and the 6–100× range is my derivation. Test 2 above settles it for us.
- **Whether a move after our bet is information or noise on these venues.** The supporting claim (permanent price
  impact on Kalshi) was refuted 1–2.
- **How much power always-valid tests lose against fixed-sample DM at n = 200–1,000.** The papers give no single
  ratio; Henzi & Ziegel and Choe & Ramdas say only that the tests are less powerful or wider.
- The DM small-sample size distortions were simulated with Gaussian errors, not binary Brier differences.
- **Never put to a 3-vote check:** the DSR, PSR, MinTRL and PBO formulas, the BH and BY formulas, and the
  Harvey-Liu-Zhu t > 3. They were read from the primary papers in a second pass but not adversarially voted.
- Ferro & Fricker was checked from the abstract only. The book chapters for purging, embargo and CPCV were confirmed
  through secondary documentation, not the book.
- **All sample-size tables are my arithmetic.** They use a normal approximation and assume independence. Binary
  returns at 30¢ are skewed, which matters below about 100 bets.
- "About 85 finished markets a day" is an estimate (1,133 finished markets between the first live cycle on 2026-09-27 and 2026-10-09), not a measured rate.
