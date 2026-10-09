# 12: Bet sizing when our probabilities are uncertain

Researched 2026-10-09 for `docs/research/briefs/12-bet-sizing.md`.

## Answer in five lines

1. Quarter-Kelly on a forecast that overstates its edge is not quarter-Kelly. If the real edge is a fraction λ of
   what the forecast claims, a Kelly fraction k bets k/λ of the true Kelly stake. Our 137 post-floor bets claimed
   about +0.25 per bet and delivered about −0.03 ± 0.04, so λ ≈ 0 and every positive stake over-bets.
2. On a binary contract, fractional Kelly is *exactly* full Kelly on a forecast pulled toward the market price
   (p' = m + λ(p − m)). So the Kelly fraction should be measured, not chosen: the slope of (outcome − price) on
   (forecast − price) from our own settled markets, shrunk again by its own standard error. Today that is 0.
3. A ladder of thresholds on one price, or YES on one fighter plus NO on the other, is one bet. Perfectly
   correlated bets should together get one bet's stake (Thorp), and Kelly never holds both sides of one outcome.
4. Drawdown risk under c-fractional Kelly is P(ever falling to x of the bankroll) = x^(2/c − 1), and only for c
   measured against the true edge. Quarter-Kelly on a correct edge gives about an 8% chance of ever losing 30%.
5. Put in code: market-anchored shrinkage, one stake budget per event and per underlying-date, no opposite sides,
   a drawdown cushion that scales stakes down to zero at −30% from peak, and tighter hard bounds (the daily
   review can currently raise the Kelly fraction, the bet cap and the open-bet cap all the way to 100%).

## Findings

### F1. Plug-in Kelly over-bets when the probability is estimated; the fix is to shrink

- **Claim.** Plugging an estimated probability into Kelly does worse out of sample than in sample, and the
  growth-optimal stake is the plug-in stake shrunk by a factor below 1. The mechanism matters for us:
  "outcomes with overestimated values will consistently look more favourable than in reality, with larger
  wagers placed on them" (Metel). A bot that bets only where it sees an edge picks exactly the over-estimates.
- **Evidence.**
  - Baker & McHale, "Optimal betting under parameter uncertainty", *Decision Analysis* 10(3):189–199 (2013),
    https://pubsonline.informs.org/doi/10.1287/deca.2013.0271. Abstract only (paywalled): the bet "should be
    shrunk in the presence of this parameter uncertainty". In a simulation and on tennis betting data, shrunk
    Kelly beat raw Kelly. Their formula and effect sizes were not retrieved.
  - Metel, arXiv 1701.02814 (2017), https://arxiv.org/abs/1701.02814. Publication in *Decision Analysis*
    15(1) (2018) is not verified.
  - MacLean, Thorp & Ziemba, "Good and bad properties of the Kelly criterion", *Quantitative Finance*
    10(7):681–687 (2010); draft read in full at https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf.
    Quote: "Given the extreme sensitivity of E log calculations to errors in mean estimates … the size of the
    wagers should be reduced."
  - Thorp (2006), §7.3 (full text, link under F5). If the true edge is half the estimate, betting the estimated
    Kelly gives "g = 0 and we suffer increasingly wild oscillations." Choosing "f in the range .5fe* ⩽ f < fe*
    offers protection against g ⩽ 0".
- **Caveat.** For one binary bet that is always placed, Kelly is linear in p, so an *unbiased* p gives an
  unbiased stake. The damage comes from selection (betting only on large estimated edges) and from bias
  (overconfidence). We have both.
- **Strength:** strong. These are peer-reviewed results that agree on the direction, though Baker & McHale's
  formula itself was not read.

### F2. Kelly on a $1 binary contract, and it never holds both sides

- **Claim.** At price m with belief p > m, full Kelly spends f* = (p − m)/(1 − m) of wealth on YES. When p < m,
  it spends (m − p)/m on NO. There is one signed optimum, so Kelly never holds both sides of the same outcome.
  YES and NO together cost 1 and pay 1, so the pair does nothing before fees and strictly loses after them.
- **Evidence.** Beygelzimer, Langford & Pennock, "Learning performance of prediction markets with Kelly
  bettors", AAMAS 2012, https://arxiv.org/abs/1201.6655. The verifiers rechecked the algebra.
- **Our code already does this per market.** `papertrade/engine.py:264` computes
  `kelly = (q − c)/(1 − c)` with c = ask + fee + slippage. What it lacks is a check *across* markets, so YES on
  fighter A plus NO on fighter B is two "different" bets on one outcome (BACKLOG B17).
- **Strength:** strong.

### F3. Fractional Kelly is the same as shrinking the forecast toward the market

- **Claim.** On one binary contract, λ-fractional Kelly is *exactly* full Kelly on the revised belief
  p' = λp + (1 − λ)m. The Bayesian reading is λ = t/(t + t₀): our forecast's worth in independent observations
  over the total of ours and the market's.
- **Evidence.**
  - Beygelzimer et al. 2012, §6: "λ-fractional Kelly is precisely equivalent to full Kelly with revised belief
    λp+(1−λ)pm".
  - Rising & Wyner, IEEE ISIT 2012, Theorem V.1 (the same identity for the Gaussian approximation of Kelly),
    https://faculty.wharton.upenn.edu/wp-content/uploads/2013/05/Wyner_2012_Partial_3.pdf.
- **What it means.** Choosing a Kelly fraction *is* choosing how much to trust our forecast over the price. Brief
  05 found the market's weight is 1.12 and our forecasters' weights are indistinguishable from 0 on about 1,000
  real-priced markets (`docs/REBUILD_SCOPE.md` item 6). In this frame, the stake those numbers justify is 0.
- **Limits.** The identity is exact only for one contract with no fees. With fees, shrink toward the market mid
  and *then* compare against the all-in cost, as the formula in the next section does.
- **Strength:** strong. The identity is exact algebra; how to estimate λ is inference (next finding).

### F4. How much to shrink: measured, and it depends on sample size

- **Claim.** The data-dependent shrink is λ ≈ edge² / (edge² + variance of the edge estimate). It is small
  when the edge is new or noisy, and grows toward 1 as evidence accumulates. Bayesian Kelly is ordinary Kelly at
  the posterior mean of p. With a Beta prior, worked examples ranged from 0.075 to 0.75 of naive Kelly,
  depending on prior strength and sample size.
- **Evidence.**
  - Rising & Wyner 2012, Theorem V.2: 1 − α* = ‖edge‖²/(‖edge‖² + tr Var(edge estimate)). This is a 4-page
    conference paper in continuous returns, so applying it to binary bets is an analogy.
  - Chu, Wu & Swartz, "Modified Kelly criteria", *J. Quantitative Analysis in Sports* 14(1):1–11 (2018),
    https://www.degruyterbrill.com/journal/key/jqas/14/1/html. Full text checked. Examples:
    - a 100/180 record at odds 1.952: naive Kelly 8.9%, Bayes 4.8%;
    - a tighter prior: 0.5% (0.075 of Kelly);
    - real NBA data, 271/484: 5.4% vs 7.6%.
    Their prior is centred on 0.5, not on the market; centring it on the price is our adaptation.
- **Applied to our forecasters (our inference, not a source).** If E[y | p, m] = m + λ(p − m), then full Kelly on
  that conditional mean is exactly λ-Kelly. λ can be estimated as the through-origin slope
  λ̂ = Σ(y − m)(p − m) / Σ(p − m)².
- **A rough version from published totals.** On the 137 post-floor bets (`REBUILD_SCOPE.md` item 4), forecasts
  claimed 99.8 − 65.7 = 34.1 extra wins over the market and delivered 62 − 65.7 = −3.7. That gives
  λ ≈ −0.11 ± 0.17 (one SE, treating bets as independent), with a 95% upper bound of about 0.23.
- **Strength:** moderate. The formulas are peer-reviewed; mapping them to an LLM forecaster against a market is
  our inference.

### F5. Drawdown and growth under fractional Kelly

- **Claim.** With c-fractional Kelly in the continuous approximation:
  - P(ever falling to x of the starting bankroll) = x^(2/c − 1);
  - growth relative to full Kelly = c(2 − c), and the standard deviation scales with c;
  - betting 2× Kelly gives zero growth.

  | c (share of true Kelly) | Growth vs full | P(ever −30%) | P(ever −50%) |
  |---|---|---|---|
  | 1 | 100% | 70% | 50% |
  | 0.5 | 75% | 34% | 12.5% |
  | 0.25 | 44% | 8.2% | 0.8% |
  | 0.1 | 19% | 0.1% | ~0% |

- **Evidence.**
  - Thorp, "The Kelly criterion in blackjack, sports betting and the stock market", *Handbook of Asset and
    Liability Management* Vol. 1, ch. 9 (2006), read in full at
    https://www.gwern.net/doc/statistics/decision/2006-thorp.pdf.
    - Eq. 7.13 (p. 415): "Prob(V(t, cf*)/V0 ⩽ x for some t) = x ∧ (2/c − 1)".
    - §7.1 (p. 409): "g∞(cf*)/g∞(f*) = c(2 − c)".
    - Thorp notes that earlier versions of the chapter had this exponent off by a factor of 2.
  - MacLean, Thorp & Ziemba 2010 (p. 3): growth "becomes zero … when one bets exactly twice the Kelly wager".
  - **Our check.** We simulated 4,000 paths of 20,000 even-money bets at p = 0.53. The simulated probabilities
    were within 0.03 of the formula at c = 1, 0.5 and 0.25, slightly below it because the horizon is finite.
- **The catch for us.** c is measured against the *true* edge. If the forecast's edge is λ times too large,
  c = k/λ.
  - Quarter-Kelly (k = 0.25) with λ = 0.25 is full Kelly: a 50% chance of ever halving.
  - With λ ≤ 0.125 it is 2× Kelly or more, so growth is zero or negative before costs.
- **Strength:** strong. The formulas are primary and matched our simulation; the continuous approximation is
  close for small bets.

### F6. Risk-constrained Kelly reduces to fractional Kelly for one binary bet

- **Claim.** The constraint "Prob(W_min < α) < β" is implied by E[(r·b)^(−λ)] ≤ 1 with λ = log β / log α.
  - For a single binary bet there is no closed form, only a one-dimensional root-find. The answer is a
    fractional Kelly bet.
  - Matching it to Thorp's formula gives c = 2/(λ + 1). For "at most a 10% chance of ever falling to 70%", that
    is c ≈ 0.27, essentially our quarter-Kelly, *if the edge were measured correctly*.
  - It beats fractional Kelly only when several bets are sized jointly. In their 19-asset example it had growth
    0.047 against 0.035 for fractional Kelly, at the same 10% risk.
- **Evidence.** Busseti, Ryu & Boyd, "Risk-constrained Kelly gambling", *J. Investing* 25(3):118–134 (2016),
  read in full at https://arxiv.org/pdf/1603.06183 (§3–5, Table 1). The printed eq. 10 has typos; use −λ as
  derived in §4. The c = 2/(λ + 1) matching is our derivation.
- **Strength:** strong for the theory; the mapping to quarter-Kelly is our derivation.

### F7. Drawdown control by a cushion above a trailing floor

- **Claim.** If wealth must stay above a fraction α of its running peak M (W ≥ αM), the optimal policy for
  constant-relative-risk-aversion utility invests in proportion to the surplus W − αM. Fixed-fraction sizing
  already shrinks stakes after losses ("The absolute amount bet is monotone increasing in wealth"), but only in
  proportion to wealth, not to the drawdown.
- **Evidence.**
  - Grossman & Zhou, "Optimal investment strategies for controlling drawdowns", *Mathematical Finance*
    3(3):241–276 (1993), https://ideas.repec.org/a/bla/mathfi/v3y1993i3p241-276.html. Abstract only; the
    multiplier was not verified.
  - MacLean, Thorp & Ziemba 2010 (p. 5).
  - The same paper says practitioners "sharply reduce risk as their drawdown increases" (p. 8). That is stated
    without data, so it is anecdotal.
- **Strength:** moderate. The form is from a peer-reviewed abstract; the multiplier is not verified.

### F8. Correlated and simultaneous bets

- **Claim.** Perfectly correlated bets should together get the stake of one bet. Independent simultaneous bets
  need only slightly smaller stakes at our sizes. Several outcomes of one event should be sized as one race.
  A ladder of thresholds decomposes into price buckets, which turns it into exactly that kind of race.
- **Evidence.**
  - **Correlation.** Thorp 2006, Example 6.2, Table 5: at correlation 1 the Kelly bet per coin is m/2, so the
    pair equals one single Kelly bet. At correlation 0 it is m/(1 + m²), "only moderately less" than betting
    singly.
    - §8.4: the multi-asset form is F* = C⁻¹[M − R].
    - For near-duplicate assets "det C = 0 and C⁻¹ does not exist". A covariance-matrix Kelly breaks on a ladder.
    - For blackjack hands at one table, "a pairwise correlation … estimated at .5 … should substantially reduce
      the Kelly fraction per hand".
  - **One event, several outcomes.** Kelly, "A new interpretation of information rate", *Bell System Technical
    Journal* (1956), pp. 923–925, read at https://homepage.sns.it/marmi/esameIUE/kelly.pdf. This is the
    horse-race algorithm.
    - In contract terms, sort outcomes by p/c, then stake p_s − b·c_s on each outcome in the bet set.
    - Whelan, "On optimal betting strategies with multiple mutually exclusive outcomes", *Bulletin of Economic
      Research* (2025), https://www.karlwhelan.com/Papers/BER.pdf, eq. 19:
      x_i = π_i/p_i − Σ_{k∉S} π_k / (1 − Σ_{k∈S} p_k).
    - Whelan also warns that if prices include a margin and are otherwise right, the more aggressive
      multi-outcome bet loses more.
  - **Ladders as buckets.** Gürkaynak & Wolfers, "Macroeconomic derivatives", NBER ISOM 2005 (2007),
    https://www.nber.org/chapters/c0355.pdf. Digital calls and puts "can be expressed as portfolios of digital
    ranges", and buying a range "can be thought of as shorting all other outcomes".
    - Sizing a strike ladder as one race end to end is our inference; no paper found does it.
  - **Simultaneous independent bets.** A log-wealth optimisation run by a research agent, for n identical
    independent 50¢ contracts at p = 0.55:
    - each stake stays at 96% of its single Kelly at n = 5 and 90% at n = 10;
    - it shrinks hard only when n × single Kelly nears 100% of wealth.
    - At our 2% caps this effect is negligible; correlation is what matters.
  - **Concentration limits in regulation.** Basel Committee, BCBS 283 (2014),
    https://www.bis.org/publ/bcbs283.htm. Large-exposure limits apply to "groups of connected counterparties
    (ie counterparties that are interdependent and likely to fail simultaneously)". This is a regulatory
    analogue to "one underlying, one limit", not betting evidence.
- **Strength:** strong for the correlation-1 rule and the race algorithm; moderate for ladder decomposition.

### F9. Sizing and stopping a strategy whose edge is unproven

- **Claim.** A strategy's paper wealth against the market price is a test martingale if the market is fair.
  Ville's inequality, P(sup W_t ≥ 1/α) ≤ α, then lets us check it after every settlement without inflating
  false "edge proven" calls. The betting score for a forecast q against market m is the likelihood ratio, and
  a shrunk version q' = m + λ(q − m) keeps it robust.
- **Evidence.**
  - Shafer, "Testing by betting", *JRSS-A* 184:407–431 (2021), full text. "A betting score is a likelihood
    ratio." "Multiplying our money by 5 might merit attention; multiplying it by 100 or by 1000 might be
    considered conclusive."
  - Waudby-Smith & Ramdas, "Estimating means of bounded random variables by betting", *JRSS-B* (2024),
    https://arxiv.org/pdf/2010.09686 (Prop. 2, eq. 23, 26; betting fraction truncated at 1/2 or 3/4).
  - Henzi & Ziegel, "Valid sequential inference on probability forecast performance", *Biometrika* (2022),
    https://arxiv.org/abs/2103.08402, Theorem 3.3. The growth-optimal e-value for a point null is exactly the
    likelihood ratio. Robustness comes from mixing toward the null.
  - Choe & Ramdas, "Comparing sequential forecasters", *Operations Research* 72(4) (2024),
    https://arxiv.org/abs/2110.00115. One of their forecasters is betting odds.
  - Caveat: products of e-values from simultaneous, correlated markets are not valid in general. Use one factor
    per event cluster.
  - Wald's SPRT is optimal for a fixed alternative, but no peer-reviewed application to trading strategies was
    found. It also needs an assumed edge size, which the e-process does not.
  - This overlaps brief 13 (telling skill from luck), which should own the test itself.
- **For sizing.** A Bayesian stake with a prior centred on zero edge starts near 0 and grows only as evidence
  comes in. Browne & Whitt, *Adv. Appl. Probab.* 28(4) (1996), abstract only: bet "a fraction … equal to a linear
  function of the posterior mean increment". λ from F4 does exactly this.
- **Strength:** strong for e-process validity; moderate for applying it to our strategies.

### F10. LLM forecasters specifically (one preprint)

- **Claim.** Full Kelly is "particularly unstable" with LLM probabilities, and "Kelly can lose" even when the
  forecaster beats the market on Brier score. A "proper betting" rule, stake ∝ 2(p − m) under Brier, beat full
  Kelly in 3 of 5 model setups. Forecasters worse than the market lost 30–77% under every rule.
- **Evidence.** Gu, Kagan, Sun, Wu & Xu, "When do prophets profit in prediction markets?", arXiv 2607.06166 v3
  (23 Sep 2026), not peer-reviewed. 94,453 forecasts from 18 models. They compare only *full* Kelly, so it says
  nothing about shrunk Kelly. Their main theorem's "reliably profitable" claim was refuted 1–2 by our verifiers
  as overstated.
- **Strength:** weak. It is a single recent preprint, but it agrees with F1 and F5.

### F11. Our own simulation (illustration, not evidence about markets)

**Setup.**
- 2,000 paths of 1,000 sequential bets each.
- Market price uniform on 30–80¢; all-in cost = price × 1.084 (our 8.4% trading cost); YES only.
- The forecaster sees the market price and claims edges in three scenarios:
  - **A:** no true edge, noise SD 0.15. This is roughly where we are.
  - **B:** a small true edge (SD 0.04), overclaimed 3× plus noise 0.10; true λ = 0.20.
  - **C:** a real edge (SD 0.06), honestly estimated with noise 0.04; λ = 0.69.
- Ladders are 4 legs settling on one outcome, which simplifies real nested strikes.
- Code is in the session scratchpad, not the repo.

**Results.** Each cell is median wealth after 1,000 bets, then the share of paths that ever fell 30% and 50%
below their peak.

| Sizing | A: no edge | B: 3× overclaimed | C: honest edge |
|---|---|---|---|
| Quarter-Kelly on raw forecast, 2% cap (today) | ×0.56; 93% / 52% | ×0.84; 70% / 16% | ×1.18; 11% / 0% |
| Quarter-Kelly raw, 3% cap | ×0.42; 99% / 85% | ×0.75; 90% / 45% | ×1.25; 28% / 1% |
| Quarter-Kelly raw, no cap | ×0.05; 100% / 100% | ×0.30; 100% / 99% | ×1.48; 62% / 12% |
| Half-Kelly on λ-shrunk forecast, 2% cap | ×1.00; 0% / 0% | ×1.03; 0% / 0% | ×1.18; 6% / 0% |
| Half-Kelly on λ-shrunk, 3% cap | ×1.00; 0% / 0% | ×1.04; 2% / 0% | ×1.28; 19% / 0% |
| Half-Kelly on λ-shrunk, 5% cap | ×1.00; 0% / 0% | ×1.05; 3% / 0% | ×1.38; 41% / 4% |
| Full Kelly on λ-shrunk, no cap | ×1.00; 0% / 0% | ×1.07; 41% / 4% | ×1.83; 99% / 74% |
| Ladder of 4, quarter-Kelly raw, 2% per leg, B | | ×0.72; 97% / 67% | |
| Same ladder, one 2% budget for the group, B | | ×0.94; 12% / 0% | |
| Ladder of 4, half λ-shrunk, 2% per leg, C | | | ×1.09; 59% / 11% |
| Same ladder, one 2% budget for the group, C | | | ×1.05; 0% / 0% |

**What it shows.**
- Shrinking toward the market stops the bleed when there is no edge, because it stops the bets.
- Half of the shrunk Kelly, capped at 2–3%, keeps drawdowns small in every scenario.
- A ladder sized leg by leg is the single biggest drawdown risk, and one budget per group removes it.
- Full Kelly even on a correctly shrunk forecast has a 74% chance of a 50% drawdown, so an extra fraction on top
  of the shrink is still needed.

**Strength:** illustration only. The numbers depend on the assumed scenarios.

## What it means for our trader

These are ranked. Every item is a code change, so each needs Joey's approval (CLAUDE.md); none is a
`policy.json` tweak the daily review could make by itself.

1. **One stake budget per event and per underlying-date, and no opposite sides.** Expected effect: removes the
   largest drawdown source we can name.
   - Group key: the venue's event id (Kalshi event ticker, Polymarket event) **and** (underlying, settlement
     date) for threshold markets on prices.
   - Total open cost in a group ≤ `max_stake_pct × equity`.
   - Refuse any bet whose outcome set overlaps an open position's on the other side. Within one event, YES on
     A and NO on B are the same side when A and B are the only outcomes.
   - This fixes B17 and the four-threshold oil case inside one strategy.
   - Basis: Thorp corr = 1 → one stake; Kelly never holds both sides; simulation F11 (P(−50%) from 67% → 0%).
   - Confidence: high.
2. **Size on a forecast shrunk toward the market, with the weight measured from our record.** Expected effect: no
   Kelly bets while the forecaster is worse than the price, which is now, and stakes that grow only as a
   measured edge appears.
   - Formula below. Basis: F3, F4, F5.
   - Confidence: high on direction. Medium on the exact λ estimator, which our history test should settle
     (test 1).
3. **Tighten the hard bounds the daily review can tune within.** `learning.bounds` currently allows
   `kelly_fraction`, `max_stake_pct` and `max_total_exposure_pct` up to 1.0. A loop chasing a lucky week could
   set a strategy to full Kelly at 100% per bet.
   - The bounds live in `policy.json`. Per CLAUDE.md ("Keep hard limits … in code-enforced policy") the ceilings
     should be constants in code, checked in `learn.rules_problem`.
   - Numbers below. Confidence: high that a ceiling is needed; medium on the exact numbers.
4. **A drawdown cushion.** Scale each stake by the cushion above a trailing floor of 70% of peak equity. Stakes
   fall smoothly to zero as a strategy approaches −30% from its peak. They recover as it recovers, or as λ is
   re-estimated.
   - Expected effect: caps any strategy's drawdown near 30%, at the cost of slow recovery.
   - Basis: F7 (form verified, multiplier not), with α from F6. Confidence: medium.
5. **No Kelly stakes for an unproven forecaster; optional fixed "probe" stakes for visibility.** Forecasts on
   every finished market measure skill whether or not we bet, so bets aren't needed to learn λ. Probe stakes
   exist only to keep the page showing trades and to measure real execution costs (brief 11).
   - Expected bleed at 8.4% cost: about 0.1% of equity a day per strategy at 5 probes a day.
   - Confidence: high.
6. **Do not adopt covariance-matrix Kelly or ladder-as-race sizing yet.** The covariance form breaks on
   near-duplicates (Thorp). The race form (Kelly 1956, Whelan eq. 19) is the right long-term tool for ladders
   and multi-outcome events, but it only pays once λ > 0. Revisit if test 1 finds an edge.
7. **Cross-strategy exposure is a measurement issue, not a bankroll one.** The WTI call hit four strategies, but
   each has its own paper bankroll. The problem is that those four results are one observation, not four, when
   comparing strategies. Brief 13 should cluster by event when counting evidence.

### Formulas and limits to put in code

```
# Inputs: q = forecaster's P(YES); m = market mid at decision time; E = strategy equity;
#         P = strategy's peak equity; cost = ask + fee + slippage for the chosen side (as now).

if spread > 0.10: no bet                         # mid is not a price (REBUILD_SCOPE item 7)
q_s   = m + λ_s · (q − m)                         # shrink toward the market   (F3)
side  = YES if q_s > m else NO;  q_side = q_s or 1 − q_s
f     = (q_side − cost) / (1 − cost)              # Kelly on the shrunk forecast, as engine.py:264
if f <= 0: no bet
cush  = max(0, E − 0.7·P) / 0.3                   # equals E at a new peak, 0 at −30% from peak   (F7)
stake = k · f · cush
stake = min(stake,
            max_stake_pct · E,
            max_stake_pct · E − open_cost_in_group,   # group = event id, and (underlying, date)  (F8)
            max_total_exposure_pct · E − open_cost,
            cash)
refuse if an open position in the same event is on the opposite outcome            (F2)

# λ_s, recomputed daily per forecaster from settled markets with spread ≤ 0.10 at first look:
n     = number of such markets
λ̂     = Σ (y − m)(q − m) / Σ (q − m)²
se    = cluster-bootstrap SE of λ̂, clustered by event and by (underlying, date)
λ_s   = 0                                  if n < 300 or λ̂ ≤ 0
λ_s   = λ̂ · λ̂² / (λ̂² + se²)               otherwise, capped at 1                    (F4)
```

Why each number:

| Setting | Default | Hard ceiling in code (floor) | Reasoning |
|---|---|---|---|
| λ_s | measured | 1 (0) | The fraction of our forecast's distance from the price that actually comes true (F3). The extra factor λ̂²/(λ̂² + se²) is the Rising–Wyner shrink for estimation noise (F4), so a barely measured edge gets almost nothing. Combining the two factors is our synthesis, not a published formula. |
| n ≥ 300 before λ_s > 0 | 300 | — | `REBUILD_SCOPE.md` item 8: no conclusions below a few hundred markets. At n = 300 the SE of a Brier difference is about ±0.01, the same scale as the gaps we measured. |
| k (`kelly_fraction`) | 0.25 | 0.5 (0.05) | It now multiplies a *calibrated* edge, so the drawdown table (F5) applies honestly. k = 0.25 gives about an 8% chance of ever losing 30% and 44% of max growth. It matches risk-constrained Kelly at α = 0.7, β = 0.1 (c ≈ 0.27, F6). Ceiling 0.5: Thorp's range for protection against estimation error; above it the chance of a −30% drawdown passes 34%. |
| `max_stake_pct` | 0.02 | 0.03 (0.0025) | In F11, scenario C, going from 2% to 3% raised P(−30%) from 6% to 19%, and 5% raised it to 41%. 2% already binds in most simulated bets. |
| Group cap (event, underlying-date) | = `max_stake_pct` | same | Correlation 1 means the group together gets one bet's stake (Thorp, Table 5). The simulated ladder went from P(−50%) 67% to 0%. |
| `max_total_exposure_pct` | 0.5 | 0.5 (0.05) | No source gives a number. With 2% groups, 50% means at least 25 separate groups, which is enough spread for mostly independent events. Joey set 50% on 2026-09-28; a ceiling above it adds risk without evidence. Judgement. |
| Floor α | 0.7 | fixed in code | Busseti's worked example uses α = 0.7. A −30% drawdown is also where a strategy has clearly stopped working on this scale. Judgement; the Grossman–Zhou multiplier was not verified. |
| Probe stake (λ_s = 0) | 0.25% of E, ≤ 5 a day, flagged as probes | 0.5% | Learning λ needs forecasts, not bets. Probes are for the page and for measuring real fills; at 8.4% cost they bleed about 0.1% a day. Judgement. |

## How to test it on our history

All tests use finished markets with a real price (spread ≤ 10¢ at first look), about 1,000 as of 2026-10-09.
Report every number with its ± from a bootstrap clustered by event and by (underlying, settlement date).

1. **Measure λ̂ per forecaster.** Compute the through-origin slope of (outcome − mid) on (forecast − mid) for
   each forecaster on all markets, and again on the bets placed.
   - Also split it by price band (30–50¢, 50–70¢) and by category.
   - **Confirms the idea:** λ̂'s 95% upper bound is below 0.25. Then today's quarter-Kelly is betting more than
     full Kelly on the true edge, and λ-shrinkage would have stopped those bets.
   - **Kills it:** λ̂ ≥ 0.5 with a CI clear of 0.25. Then quarter-Kelly was already conservative, and the
     losses came from costs, not sizing.
   - Brief 05's refit suggests λ̂ ≈ 0. This test should agree with it in sign.
2. **Size of the correlation problem.** For each strategy, group its settled bets by event and by
   (underlying, date).
   - Report the share of total stake and of P&L variance that came from groups of 2 or more bets, and the
     number of events where it held both sides.
   - **Confirms** the group cap matters: more than 20% of stake sits in multi-bet groups, or any both-sides
     events exist.
   - **Kills** it as a priority: under 5% of stake in multi-bet groups.
3. **Walk-forward replay of sizing rules.** Replay every settled bet with stakes recomputed under each rule:
   - (a) current sizing;
   - (b) + group cap and no opposite sides;
   - (c) + λ-shrunk Kelly, with λ estimated *only from markets that settled before the bet* (no look-ahead);
   - (d) + the 70% cushion.

   Keep fill prices as recorded. Report return, maximum drawdown and the number of bets, with block-bootstrap
   ± by day.
   - **Confirms:** (c) and (d) cut max drawdown by more than half without a lower return.
   - **Kills:** (b)–(d) are indistinguishable from (a). That would mean sizing isn't where the losses come from,
     and the rebuild should look elsewhere.
4. **Drawdown formula on our bet stream.** Compare each strategy's realised maximum drawdown with what
   x^(2/c − 1) predicts, using c = k/λ̂. A large mismatch means correlation or fat tails beyond the model, and
   argues for the cushion over the formula.

## Data sources

None external. Every test above uses `papertrade_data/`.

## Not verified

- Baker & McHale (2013): the shrinkage formula and effect sizes (paywalled; abstract only).
- Grossman & Zhou (1993): the investment multiplier (abstract only). The CPPI rule "exposure = m × (W − floor)"
  from a primary source (Black & Perold 1992 and Perold & Sharpe 1988 were not retrievable).
- Smoczynski & Tomkins (2010): full text not read. Their formula is known here only through Whelan's restatement.
- Metel (2017): whether the *Decision Analysis* version matches the arXiv numbers. Our verifiers disagreed on its
  publication status, so its simulation table is not quoted here.
- Wald (1945): full text (paywalled). The SPRT formulas came from lecture notes (secondary).
- Browne & Whitt (1996), Whitrow (2007, *JRSS-C* 56(5):607–623, many simultaneous bets), Medo et al. (2008),
  Long (arXiv 2604.11577, 2026): abstracts only.
- Kalshi per-strike position limits ($25,000 in older contract terms): search snippets only.
- Gu et al. (2026) is an unreviewed preprint. Its headline theorem's practical claim was refuted 1–2 by our
  verifiers as overstated.
- Our synthesis, not from any one source: the combined λ_s formula, c = 2/(λ + 1), the ladder-as-race sizing, the
  α = 0.7 floor, the 0.03 and 0.5 ceilings, the probe stake, and every F11 simulation number.
- The λ ≈ −0.11 ± 0.17 estimate uses published totals and treats bets as independent. Test 1 replaces it.
