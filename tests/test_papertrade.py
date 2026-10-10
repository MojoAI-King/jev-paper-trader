"""Offline tests for the paper trader. Run: python3 -m unittest discover -s tests -t ."""
import io
import json
import tempfile
from datetime import datetime, timedelta, timezone
import unittest
import urllib.error
import urllib.parse
from pathlib import Path
from unittest import mock

from papertrade.jev_client import JevClient
import random

from papertrade import coach, dashboard, jev_client, learn, news, review
from papertrade import engine
from papertrade import markets as mk
from papertrade import odds

POLICY = engine.load_policy()


def ans(p, clear=0.9, info=0.8, p_no=None):
    """A Jev reply answering every question in judge.QUESTIONS (the client rejects partial replies)."""
    return {"p_yes": {"noul": p}, "p_no": {"noul": round(1 - p, 4) if p_no is None else p_no},
            "rules_clear": {"noul": clear}, "info_sufficient": {"noul": info}, "already_decided": {"noul": 0.1}}


def market(src="polymarket", mid="1", yes_ask=0.40, no_ask=0.62, m=0.39, close="2099-01-01T00:00:00Z", fee_rate=0.0):
    # fee-free by default, so the arithmetic in tests about other things stays edge = p - ask - slippage;
    # FeeTests covers the fees themselves
    return {"source": src, "market_id": mid, "question": f"Q{mid}", "rules": "r", "close_time": close,
            "yes_ask": yes_ask, "no_ask": no_ask, "mid": m, "volume": 50000, "url": "u", "fee_rate": fee_rate}


class FeeTests(unittest.TestCase):
    def test_each_polymarket_market_pays_its_own_published_rate(self):
        fee = lambda src, p, m=None: engine.fee_per_contract(src, p, POLICY, m)
        self.assertAlmostEqual(fee("polymarket", 0.5, {"fee_rate": 0.04}), 0.01)     # politics: 0.04 x 0.5 x 0.5
        self.assertAlmostEqual(fee("polymarket", 0.9, {"fee_rate": 0.07}), 0.0063)   # crypto, cheap near the ends
        self.assertEqual(fee("polymarket", 0.5, {"fee_rate": 0.0}), 0.0)              # fee-free (geopolitics)
        self.assertAlmostEqual(fee("polymarket", 0.5, {"fee_rate": None}), 0.0125)   # unpublished: the default 0.05
        self.assertAlmostEqual(fee("polymarket", 0.5), 0.0125)                       # an old saved market, no field
        self.assertAlmostEqual(fee("kalshi", 0.5, {"fee_rate": 0.0}), 0.0175)        # Kalshi ignores it: 0.07 x p x (1-p)

    def test_kalshi_charges_each_series_published_multiplier(self):
        fee = lambda m: engine.fee_per_contract("kalshi", 0.5, POLICY, m)
        self.assertAlmostEqual(fee({"fee_multiplier": 0.5}), 0.00875)  # MLB games: half the 0.07 rate
        self.assertEqual(fee({"fee_multiplier": 0.0}), 0.0)             # a free series
        self.assertAlmostEqual(fee({"fee_multiplier": None}), 0.0175)  # unknown: the full rate
        self.assertAlmostEqual(fee({}), 0.0175)                         # saved before 2026-10-09
        mk._SERIES_FEE.clear()
        calls = []
        def get(url, params=None, timeout=20):
            calls.append(url)
            if url.endswith("/KXMLBGAME"):
                return {"series": {"fee_type": "quadratic_with_maker_fees", "fee_multiplier": 0.5}}
            raise RuntimeError("down")
        with mock.patch.object(mk, "_get", side_effect=get), mock.patch.object(mk, "_sleep", lambda s: None):
            self.assertEqual(mk.kalshi_fee_multiplier("KXMLBGAME"), 0.5)
            self.assertEqual(mk.kalshi_fee_multiplier("KXMLBGAME"), 0.5)   # cached: one call
            self.assertIsNone(mk.kalshi_fee_multiplier("KXBROKEN"))      # a failed lookup pays the full rate
            ms = [{"source": "kalshi", "event": "kalshi:KXMLBGAME-26OCT10NYYBOS"}, {"source": "polymarket", "event": "p:1"}]
            mk.add_kalshi_fees(ms)                                       # the scan's step, for judged markets
        self.assertEqual((ms[0]["fee_multiplier"], "fee_multiplier" in ms[1]), (0.5, False))
        self.assertEqual(len(calls), 2)                                  # still cached: no third call
        mk._SERIES_FEE.clear()

    def test_the_rate_comes_from_the_markets_fee_schedule(self):
        base = {"id": 1, "question": "Q?", "outcomes": '["Yes","No"]', "outcomePrices": '["0.5","0.5"]'}
        on = dict(base, feesEnabled=True, feeType="crypto_fees", feeSchedule={"exponent": 1, "rate": 0.07, "takerOnly": True})
        self.assertEqual(mk.normalize_polymarket(on)["fee_rate"], 0.07)
        self.assertEqual(mk.normalize_polymarket(dict(base, feesEnabled=False, feeType=None))["fee_rate"], 0.0)
        self.assertIsNone(mk.normalize_polymarket(base)["fee_rate"])                       # says nothing
        self.assertIsNone(mk.normalize_polymarket(dict(on, feeSchedule={"rate": "x"}))["fee_rate"])
        self.assertIsNone(mk.normalize_polymarket(dict(on, feeSchedule={"rate": -1}))["fee_rate"])

    def test_the_fee_is_in_the_bet_decision(self):
        pol = json.loads(json.dumps(POLICY)); pol["gates"]["min_edge"] = 0.05
        # p 0.47 against a 40c ask plus 1c slippage: a 6c edge when fee-free, 4.3c after a 0.07 rate (0.0168)
        self.assertTrue(engine.decide(market(fee_rate=0.0), ans(0.47), pol, 100000, 0, 100000)["bet"])
        self.assertFalse(engine.decide(market(fee_rate=0.07), ans(0.47), pol, 100000, 0, 100000)["bet"])
        self.assertFalse(engine.decide(market(fee_rate=None), ans(0.47), pol, 100000, 0, 100000)["bet"])  # default 0.05


NOW_ODDS = datetime(1999, 12, 25, tzinfo=timezone.utc)


def game(prices=None, last_update="1999-12-24T23:50:00Z", commence="2000-01-01T23:00:00Z", book="pinnacle"):
    """One NFL game as papertrade/odds.py keeps it (odds.compact): Pittsburgh at Cincinnati."""
    prices = prices or {"Pittsburgh Steelers": 2.0, "Cincinnati Bengals": 1.85}
    return {"id": "g1", "sport": "americanfootball_nfl", "commence": commence, "home": "Cincinnati Bengals",
            "away": "Pittsburgh Steelers", "books": {book: {"last_update": last_update, "prices": prices},
                                                     "kalshi": {"last_update": last_update, "prices": {"Pittsburgh Steelers": 2.3}}}}


def kalshi_game(**kw):
    return dict({"source": "kalshi", "market_id": "KXNFLGAME-26OCT11PITCIN-PIT", "event": "kalshi:KXNFLGAME-26OCT11PITCIN",
                 "question": "Pittsburgh at Cincinnati Winner?", "rules": "r", "close_time": "2000-01-15T00:00:00Z",
                 "expected_expiration": "2000-01-02T03:00:00Z", "yes_side": "Pittsburgh", "yes_ask": 0.40,
                 "no_ask": 0.62, "mid": 0.39, "volume": 50000, "url": "u"}, **kw)


class OddsTests(unittest.TestCase):
    """The sharp-line strategy's data: Pinnacle's price without its margin, matched to our game markets."""
    CFG = {"sports": ["americanfootball_nfl"], "refresh_minutes": 360, "reserve": 25, "max_line_age_minutes": 45,
           "max_margin": 0.06, "kickoff_window_hours": 8}

    def test_the_margin_comes_out_and_the_favourite_stays_the_favourite(self):
        p = odds.devig_power([1.9, 1.9])
        self.assertAlmostEqual(p[0], 0.5)
        self.assertAlmostEqual(sum(p), 1.0)
        p = odds.devig_power([1.5, 2.8])
        self.assertAlmostEqual(sum(p), 1.0, places=6)
        self.assertGreater(p[0], 1 / 1.5 / (1 / 1.5 + 1 / 2.8))  # power method: the favourite keeps a bit more
        self.assertIsNone(odds.devig_power([1.9]))
        self.assertIsNone(odds.devig_power([1.9, None]))
        self.assertIsNone(odds.devig_power([1.9, 1.0]))

    def test_only_a_fresh_sharp_line_with_a_small_margin_counts(self):
        f = odds.fair(game(), self.CFG, NOW_ODDS)
        self.assertEqual((f["book"], f["age_min"]), ("pinnacle", 10.0))
        self.assertAlmostEqual(sum(f["probs"].values()), 1.0, places=6)
        self.assertIsNone(odds.fair(game(last_update="1999-12-24T22:00:00Z"), self.CFG, NOW_ODDS))   # 2 hours old
        self.assertIsNone(odds.fair(game(prices={"Pittsburgh Steelers": 1.7, "Cincinnati Bengals": 1.7}), self.CFG, NOW_ODDS))
        self.assertIsNone(odds.fair(game(book="draftkings"), self.CFG, NOW_ODDS))  # a soft book is never the reference
        self.assertEqual(odds.fair(game(book="betfair_ex_eu"), self.CFG, NOW_ODDS)["book"], "betfair_ex_eu")

    def test_a_kalshi_game_market_matches_its_game_and_side(self):
        got = odds.match([game()], [kalshi_game()], self.CFG, NOW_ODDS)
        rec = got["kalshi:KXNFLGAME-26OCT11PITCIN-PIT"]
        self.assertEqual((rec["outcome"], rec["book"], rec["sport"]), ("Pittsburgh Steelers", "pinnacle", "americanfootball_nfl"))
        self.assertAlmostEqual(rec["p_yes"], odds.fair(game(), self.CFG, NOW_ODDS)["probs"]["Pittsburgh Steelers"], places=4)
        cin = odds.match([game()], [kalshi_game(market_id="X-CIN", yes_side="Cincinnati")], self.CFG, NOW_ODDS)
        self.assertEqual(cin["kalshi:X-CIN"]["outcome"], "Cincinnati Bengals")
        # Kalshi's titles since October 2026 name one team; both teams are in the rules
        now_style = kalshi_game(market_id="X-NEW", question="Pittsburgh wins", rules=(
            "If Pittsburgh wins the PIT Steelers vs CIN Bengals Pro Football game originally scheduled for "
            "Jan 1, 2000, then the market resolves to Yes."))
        self.assertEqual(odds.match([game()], [now_style], self.CFG, NOW_ODDS)["kalshi:X-NEW"]["outcome"], "Pittsburgh Steelers")
        spread = dict(now_style, market_id="X-SPR", question="Pittsburgh wins by over 2.5 points")
        self.assertEqual(odds.match([game()], [spread], self.CFG, NOW_ODDS), {})  # the rules don't rescue a spread

    def test_anything_unclear_is_left_out(self):
        m = lambda **kw: odds.match([game()], [kalshi_game(**kw)], self.CFG, NOW_ODDS)
        self.assertEqual(m(question="Pittsburgh wins by over 2.5 points"), {})            # a spread, not who wins
        self.assertEqual(m(question="Pittsburgh at Cincinnati: total points over 44.5?"), {})
        self.assertEqual(m(expected_expiration="2000-01-05T03:00:00Z"), {})              # decided days after the game
        self.assertEqual(m(question="Pittsburgh at Baltimore Winner?"), {})              # another game
        self.assertEqual(m(yes_side="Somebody"), {})                                    # can't tell which side YES is
        self.assertEqual(odds.match([game(commence="1999-12-24T23:00:00Z")], [kalshi_game()], self.CFG, NOW_ODDS), {})  # started
        twin = dict(game(), id="g2")
        self.assertEqual(odds.match([game(), twin], [kalshi_game()], self.CFG, NOW_ODDS), {})  # two games fit: no guess

    def test_a_polymarket_team_market_matches_on_the_date(self):
        poly = {"source": "polymarket", "market_id": "77", "event": "polymarket:9", "question": "Will Pittsburgh win on 2000-01-01?",
                "rules": "r", "close_time": "2000-01-08T00:00:00Z", "starts": None, "yes_ask": 0.4, "no_ask": 0.62, "mid": 0.39}
        got = odds.match([game()], [poly], self.CFG, NOW_ODDS)
        self.assertEqual(got["polymarket:77"]["outcome"], "Pittsburgh Steelers")
        self.assertEqual(odds.match([game()], [dict(poly, question="Will Pittsburgh win on 2000-01-09?")], self.CFG, NOW_ODDS), {})

    def test_the_cache_refreshes_within_the_quota_and_errors_never_show_the_key(self):
        calls = []

        class Reply(io.BytesIO):
            def __init__(self, body, left):
                super().__init__(json.dumps(body).encode())
                self.headers = {"x-requests-remaining": str(left), "x-requests-used": "1", "x-requests-last": "1"}

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        left = {"n": 30}

        def opener(req, timeout):
            calls.append(req.full_url)
            if "/sports?" in req.full_url:
                return Reply([{"key": "americanfootball_nfl", "active": True}, {"key": "baseball_mlb", "active": False}], left["n"])
            return Reply([{"id": "g1", "sport_key": "americanfootball_nfl", "commence_time": "2000-01-01T23:00:00Z",
                           "home_team": "Cincinnati Bengals", "away_team": "Pittsburgh Steelers",
                           "bookmakers": [{"key": "pinnacle", "last_update": "1999-12-24T23:59:00Z", "markets": [
                               {"key": "h2h", "outcomes": [{"name": "Cincinnati Bengals", "price": 1.85},
                                                           {"name": "Pittsburgh Steelers", "price": 2.0}]}]}]}], 29)
        cfg = dict(self.CFG, sports=["americanfootball_nfl", "baseball_mlb"])
        odds.LAST.clear()
        cache = odds.load_events(cfg, "SECRETKEY", {}, NOW_ODDS, opener=opener, warn=lambda *_: None)
        self.assertEqual(list(cache), ["americanfootball_nfl"])  # the out-of-season sport isn't fetched
        self.assertEqual(cache["americanfootball_nfl"]["events"][0]["books"]["pinnacle"]["prices"]["Pittsburgh Steelers"], 2.0)
        self.assertEqual(odds.LAST["remaining"], "29")
        n = len(calls)
        odds.load_events(cfg, "SECRETKEY", cache, NOW_ODDS + timedelta(hours=1), opener=opener, warn=lambda *_: None)
        self.assertEqual(len(calls), n + 1)  # only the free sports list: the line is under 6 hours old
        warned, n = [], len(calls)
        left["n"] = 20  # the quota left is at or below the reserve (25): keep what we have
        kept = odds.load_events(cfg, "SECRETKEY", {}, NOW_ODDS, opener=opener, warn=warned.append)
        self.assertIn("quota down to 20", warned[-1])
        self.assertEqual((kept, len(calls)), ({}, n + 1))  # only the free sports list was called

        def broken(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, None)
        with self.assertRaises(odds.OddsError) as e:
            odds.fetch_odds("americanfootball_nfl", "SECRETKEY", opener=broken)
        self.assertNotIn("SECRETKEY", str(e.exception))
        self.assertIn("HTTP 401", str(e.exception))
        odds.LAST.clear()


class SkillSizingTests(unittest.TestCase):
    """docs/REBUILD_PLAN.md phase 1: bets are sized by each forecaster's measured edge over the market (lambda)."""

    def judged(self, n, informative, spread=(0.51, 0.51), source="claude_direct", seed=1):
        """n resolved markets at mid 0.5; an informative forecaster leans toward the outcome, the other is noise."""
        rnd, js, res = random.Random(seed), [], {}
        for i in range(n):
            y = rnd.random() < 0.5
            q = (0.7 if y else 0.3) if informative else rnd.choice([0.3, 0.7])
            j = {"key": f"m{i}", "ts": "1", "question_set": review.QUESTION_SET_VERSION,
                 "market": {"mid": 0.5, "yes_ask": spread[0], "no_ask": spread[1], "event": f"e{i}"},
                 "answers_no_news": {"p_yes": {"noul": 0.5}}}
            if source == "claude_direct":
                j["claude_direct"] = {"p_yes": q}
            js.append(j); res[f"m{i}"] = "yes" if y else "no"
        return js, res

    def test_lambda_is_measured_only_where_it_is_real(self):
        js, res = self.judged(400, informative=True)
        sk = engine.skill(js, res)["claude_direct"]
        self.assertEqual(sk["n"], 400)
        self.assertGreater(sk["lambda"], 0.8)       # 0.2 of every 0.2 the forecast leans comes true
        self.assertLessEqual(sk["lambda"], 1.0)
        noise = engine.skill(*self.judged(400, informative=False))["claude_direct"]
        self.assertEqual(noise["lambda"], 0.0)       # no edge: raw about 0, shrunk or floored to 0
        few = engine.skill(*self.judged(299, informative=True))["claude_direct"]
        self.assertEqual((few["n"], few["lambda"]), (299, 0.0))  # under 300 markets: not measured yet
        wide = engine.skill(*self.judged(400, informative=True, spread=(0.99, 0.92)))["claude_direct"]
        self.assertEqual((wide["n"], wide["lambda"]), (0, 0.0))  # fake mids never count
        self.assertEqual(engine.skill(js, {})["claude_direct"]["n"], 0)  # unresolved never count

    def sized(self, lam=0.0, event_cost=0.0, probes=0, peak=100000.0):
        return {"lambda": lam, "event_cost": event_cost, "probes_today": probes, "peak": peak}

    def test_no_measured_edge_means_a_small_probe_not_a_kelly_bet(self):
        d = engine.decide(market(), ans(0.6), POLICY, 100000, 0, 100000, self.sized())
        self.assertTrue(d["bet"] and d["probe"])
        self.assertEqual(d["sizing"], "probe")
        self.assertAlmostEqual(d["total_cost"], 250, delta=1)  # 0.25% of equity, not the 2% Kelly cap
        self.assertTrue(d["reasons"][-1].startswith("PROBE YES"))
        capped = engine.decide(market(), ans(0.6), POLICY, 100000, 0, 100000, self.sized(probes=5))
        self.assertFalse(capped["bet"])
        self.assertIn("probe limit reached", capped["reasons"][-1])
        old = engine.decide(market(), ans(0.6), POLICY, 100000, 0, 100000)  # the frozen yardstick's sizing
        self.assertAlmostEqual(old["total_cost"], 2000, delta=1)

    def test_a_measured_edge_bets_kelly_on_the_forecast_shrunk_toward_the_market(self):
        d = engine.decide(market(yes_ask=0.40, no_ask=0.62, m=0.39), ans(0.6), POLICY, 100000, 0, 100000,
                          self.sized(lam=0.5))
        self.assertEqual((d["sizing"], d["probe"]), ("kelly", False))
        self.assertAlmostEqual(d["q_shrunk"], 0.495)  # 0.39 + 0.5 x (0.60 - 0.39)
        self.assertAlmostEqual(d["kelly"], (0.495 - 0.41) / 0.59, places=3)
        self.assertAlmostEqual(d["total_cost"], min(0.25 * d["kelly"] * 100000, 2000), delta=1)  # quarter-Kelly, capped at 2%
        self.assertAlmostEqual(d["total_cost"], 2000, delta=1)
        # clears the 8c edge bar raw, but shrunk by a small lambda (0.39 + 0.05 x 0.21 = 0.40) it no longer beats
        # the 0.41 cost: a probe, not a Kelly bet
        lean = engine.decide(market(), ans(0.6), POLICY, 100000, 0, 100000, self.sized(lam=0.05))
        self.assertEqual((lean["sizing"], lean["probe"]), ("probe", True))
        # equity 20% below its peak: the cushion (equity - 0.7 x peak) / 0.3 leaves a third of the stake
        down = engine.decide(market(), ans(0.6), POLICY, 80000, 0, 80000, self.sized(lam=0.5, peak=100000))
        self.assertAlmostEqual(down["total_cost"], 0.25 * down["kelly"] * (80000 - 70000) / 0.3, delta=1)
        out = engine.decide(market(), ans(0.6), POLICY, 70000, 0, 70000, self.sized(lam=0.5, peak=100000))
        self.assertFalse(out["bet"])
        self.assertIn("drawdown cushion used up", out["reasons"][-1])

    def test_one_stake_budget_per_event_and_a_real_price_required(self):
        full = engine.decide(market(), ans(0.6), POLICY, 100000, 2000, 100000, self.sized(event_cost=2000))
        self.assertFalse(full["bet"])
        self.assertIn("this event already has a full stake", full["reasons"][-1])
        part = engine.decide(market(), ans(0.6), POLICY, 100000, 1900, 100000, self.sized(event_cost=1900))
        self.assertAlmostEqual(part["total_cost"], 100, delta=1)  # only what's left of the event's 2%
        wide = engine.decide(market(yes_ask=0.97, no_ask=0.92, m=0.53), ans(0.99), POLICY, 100000, 0, 100000, self.sized())
        self.assertFalse(wide["bet"] or wide["cleared_gates"])
        self.assertIn("no real price", wide["reasons"][-1])

    def test_the_book_supplies_peak_event_cost_and_todays_probes(self):
        pf = fresh_pf()
        pf["open"] = [{"key": "polymarket:a", "total_cost": 300, "event": "polymarket:E", "opened": "2000-01-01T01:00:00Z",
                       "probe": True},
                      {"key": "polymarket:b", "total_cost": 200, "opened": "1999-12-31T01:00:00Z"}]  # saved before events
        pf["closed"] = [{"key": "polymarket:c", "total_cost": 100, "probe": True, "opened": "2000-01-01T00:30:00Z"}]
        pf["cash"] = 100000 - 500
        m = dict(market(), event="polymarket:E")
        sz = engine.skill_sizing(pf, m, 0.0, "2000-01-01T05:00:00Z", {"polymarket:b": "polymarket:E"})
        self.assertEqual((sz["event_cost"], sz["probes_today"], sz["lambda"]), (500, 2, 0.0))
        self.assertEqual(pf["peak_equity"], 100000)


class NormalizeTests(unittest.TestCase):
    def test_polymarket_json_strings(self):
        n = mk.normalize_polymarket({"id": 7, "question": "Will X?", "description": "rules",
                                     "outcomes": '["Yes","No"]', "outcomePrices": '["0.3","0.7"]',
                                     "bestBid": "0.29", "bestAsk": "0.31", "endDate": "2026-10-01T00:00:00Z",
                                     "volumeNum": 12345, "slug": "x"})
        self.assertEqual((n["yes_ask"], n["no_ask"], n["mid"]), (0.31, 0.71, 0.3))

    def test_polymarket_skips_non_binary(self):
        self.assertIsNone(mk.normalize_polymarket({"outcomes": '["A","B","C"]', "outcomePrices": '["0.2","0.3","0.5"]'}))

    def test_kalshi_dollars_and_cents(self):
        a = mk.normalize_kalshi({"ticker": "T", "title": "t", "yes_ask_dollars": "0.4500",
                                 "no_ask_dollars": "0.5700", "yes_bid_dollars": "0.4300", "volume_fp": "900"})
        b = mk.normalize_kalshi({"ticker": "T", "title": "t", "yes_ask": 45, "no_ask": 57, "yes_bid": 43, "volume": 900})
        self.assertEqual((a["yes_ask"], a["no_ask"], a["mid"]), (b["yes_ask"], b["no_ask"], b["mid"]))
        self.assertEqual(a["mid"], 0.44)
        # the size on offer at each ask; buying NO fills against YES bids, so the NO ask's size is the YES bid's
        c = mk.normalize_kalshi({"ticker": "T", "title": "Philadelphia wins", "yes_sub_title": "Philadelphia",
                                 "yes_ask_dollars": "0.23", "no_ask_dollars": "0.79", "yes_bid_dollars": "0.21",
                                 "yes_ask_size_fp": "14.00", "yes_bid_size_fp": "2.00", "volume_fp": "900"})
        self.assertEqual((c["yes_ask_size"], c["no_ask_size"], c["yes_side"]), (14.0, 2.0, "Philadelphia"))
        self.assertEqual((b["yes_ask_size"], b["no_ask_size"]), (None, None))  # not given: no cap

    def test_kalshi_skips_parlays(self):
        self.assertIsNone(mk.normalize_kalshi({"ticker": "KXMVEFOO", "yes_ask": 40, "no_ask": 62}))

    def test_kalshi_links_open_the_event_page(self):
        # kalshi.com/markets/<EVENT> is Kalshi's "Page not found"; /markets/<series>/<slug>/<event> opens the event
        m = mk.normalize_kalshi({"ticker": "KXNBAGAME-26OCT20BOSDET-DET", "event_ticker": "KXNBAGAME-26OCT20BOSDET",
                                 "title": "Boston vs Detroit Winner?", "yes_ask": 45, "no_ask": 57, "volume": 900})
        self.assertEqual(m["url"], "https://kalshi.com/markets/kxnbagame/boston-vs-detroit-winner/kxnbagame-26oct20bosdet")
        # links saved in old ledgers are repaired on the way to the page; other links pass through untouched
        self.assertEqual(mk.fix_url("https://kalshi.com/markets/KXNBAGAME-26OCT20BOSDET"),
                         "https://kalshi.com/markets/kxnbagame/market/kxnbagame-26oct20bosdet")
        for fine in ("https://polymarket.com/market/abc", m["url"], None):
            self.assertEqual(mk.fix_url(fine), fine)


POLY_FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "polymarket_markets.json").read_text())


class PolymarketFetchTests(unittest.TestCase):
    """Replays recorded Gamma API responses; no network."""

    def setUp(self):
        self.waits = []
        p = mock.patch.object(mk, "_sleep", self.waits.append)  # no real waiting between pages or retries
        p.start()
        self.addCleanup(p.stop)

    def fake_urlopen(self, req, timeout):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(req.full_url).query)
        # Sort fields the live API accepted on 2026-09-26; anything else gets the recorded 422.
        if q.get("order", [""])[0] not in ("volume24hr", "volumeNum", "volume"):
            body = json.dumps(POLY_FIXTURE["bad_order_body"]).encode()
            raise urllib.error.HTTPError(req.full_url, 422, "Unprocessable Entity", {}, io.BytesIO(body))
        return io.BytesIO(json.dumps(POLY_FIXTURE["ok_body"]).encode())

    def test_fetch_uses_a_sort_field_the_api_accepts(self):
        # Regression: order=volume_24hr got HTTP 422, so Polymarket returned nothing.
        with mock.patch("urllib.request.urlopen", self.fake_urlopen):
            ms = mk.fetch_polymarket(30, 10000, 60)
        self.assertEqual(len(ms), 3)  # the team-vs-team market is not Yes/No, so it's skipped
        self.assertTrue(all(m["source"] == "polymarket" and m["question"] for m in ms))

    def paged(self, page_fn):
        """Fake urlopen serving page_fn(i) for offset i * POLY_PAGE; records the pages asked for."""
        self.pages_asked = []

        def fake(req, timeout):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(req.full_url).query)
            i = int(q["offset"][0]) // mk.POLY_PAGE
            self.pages_asked.append(i)
            return io.BytesIO(json.dumps(page_fn(i)).encode())
        return fake

    @staticmethod
    def full_page(template_idx, prefix):
        base = POLY_FIXTURE["ok_body"][template_idx]  # 0 = Yes/No market, 3 = team-vs-team
        return [dict(base, id=f"{prefix}-{k}") for k in range(mk.POLY_PAGE)]

    def test_paginates_until_limit(self):
        # Page 0 is all team-vs-team markets (skipped); Yes/No markets start on page 1.
        page_fn = lambda i: self.full_page(3, "team") if i == 0 else self.full_page(0, i)
        with mock.patch("urllib.request.urlopen", self.paged(page_fn)):
            ms = mk.fetch_polymarket(30, 10000, 150)
        self.assertEqual(len(ms), 150)
        self.assertEqual(self.pages_asked, [0, 1, 2])

    def test_page_limit_stops_a_feed_that_never_runs_dry(self):
        with mock.patch("urllib.request.urlopen", self.paged(lambda i: self.full_page(3, i))):
            ms = mk.fetch_polymarket(30, 10000, 60)
        self.assertEqual((ms, len(self.pages_asked)), ([], mk.MAX_PAGES))

    def test_repeated_market_counted_once(self):
        with mock.patch("urllib.request.urlopen", self.paged(lambda i: self.full_page(0, "same"))):
            ms = mk.fetch_polymarket(30, 10000, 150)
        self.assertEqual(len(ms), len({m["market_id"] for m in ms}))
        self.assertEqual(len(ms), mk.POLY_PAGE)

    def test_kalshi_page_limit(self):
        calls = []

        def fake(req, timeout):  # a cursor that never runs out, and nothing with enough volume
            calls.append(req.full_url)
            return io.BytesIO(json.dumps({"markets": [{"ticker": "T", "yes_ask": 40, "no_ask": 62,
                                                       "volume": 5}], "cursor": "more"}).encode())
        with mock.patch("urllib.request.urlopen", fake), mock.patch.object(mk, "_sleep", lambda s: None):
            self.assertEqual(mk.fetch_kalshi(30, 10000, 60), [])
        self.assertEqual(len(calls), mk.KALSHI_MAX_PAGES)
        self.assertTrue(mk.LAST_FETCH["kalshi"]["cut_short"])  # the scan logs it as a problem

    @staticmethod
    def kalshi_raw(ticker, volume):
        return {"ticker": ticker, "event_ticker": ticker.split("-")[0] + "-E", "title": ticker, "yes_ask": 40,
                "no_ask": 62, "yes_bid": 38, "volume": volume}

    def test_kalshi_walks_the_window_soonest_first_and_ranks_all_of_it(self):
        # Kalshi lists latest-closing first; the biggest market sits in the far-dated slice, and a
        # market the free filters reject never takes a slot
        asked, slices, edges = [], {}, []

        def fake_get(url, params=None, timeout=20):
            asked.append(params["min_close_ts"])
            edges.append((params["min_close_ts"], params["max_close_ts"]))
            i = slices.setdefault(params["min_close_ts"], len(slices))
            markets = [self.kalshi_raw(f"S{i}-M", [20000, 30000, 90000][i])]
            if i == 0:
                markets.append(self.kalshi_raw("BAD-M", 500000))
            return {"markets": markets, "cursor": None}
        with mock.patch.object(mk, "_get", fake_get):
            ms = mk.fetch_kalshi(30, 10000, 2, lambda m: m["market_id"] != "BAD-M")
        self.assertEqual(asked, sorted(asked))  # soonest slice first
        self.assertEqual([hi for _, hi in edges[:-1]], [lo for lo, _ in edges[1:]])  # no gaps between slices
        self.assertEqual(len(slices), 3)
        self.assertEqual([m["market_id"] for m in ms], ["S2-M", "S1-M"])
        self.assertEqual(mk.LAST_FETCH["kalshi"]["pages"], 3)

    def test_kalshi_keeps_what_it_fetched_when_a_later_page_fails(self):
        calls = []

        def fake_get(url, params=None, timeout=20):
            calls.append(1)
            if len(calls) > 1:
                raise RuntimeError("HTTP 429 from kalshi")
            return {"markets": [self.kalshi_raw("S0-M", 20000)], "cursor": None}
        with mock.patch.object(mk, "_get", fake_get):
            ms = mk.fetch_kalshi(30, 10000, 60)
        self.assertEqual([m["market_id"] for m in ms], ["S0-M"])  # the soonest slice survived
        self.assertIn("429", mk.LAST_FETCH["kalshi"]["error"])
        with mock.patch.object(mk, "_get", mock.Mock(side_effect=RuntimeError("down"))):
            with self.assertRaises(RuntimeError):  # nothing fetched at all: the scan reports the source as down
                mk.fetch_kalshi(30, 10000, 60)

    def test_polymarket_filters_before_taking_the_top(self):
        with mock.patch("urllib.request.urlopen", self.fake_urlopen):
            self.assertEqual(mk.fetch_polymarket(30, 10000, 60, lambda m: False), [])
            self.assertEqual(len(mk.fetch_polymarket(30, 10000, 60, lambda m: True)), 3)

    def test_kalshi_results_are_checked_in_batches_and_scalar_is_void(self):
        seen = []

        def fake_get(url, params=None, timeout=20):
            seen.append(params["tickers"].split(","))
            return {"markets": [
                {"ticker": "A", "status": "finalized", "result": "yes"},
                {"ticker": "B", "status": "active", "result": ""},
                {"ticker": "C", "status": "finalized", "result": "scalar", "settlement_value_dollars": "0.5000"},
                {"ticker": "D", "status": "determined", "result": "no"}]}  # not final: can still be disputed
        with mock.patch.object(mk, "_get", fake_get):
            out = mk.check_kalshi([f"T{i}" for i in range(mk.KALSHI_BATCH + 1)])
        self.assertEqual([len(s) for s in seen], [mk.KALSHI_BATCH, 1])  # one request per batch
        self.assertEqual(out, {"A": "yes", "C": ("void", 0.5)})

    def test_a_failed_result_batch_loses_only_itself(self):
        calls = []

        def fake_get(url, params=None, timeout=20):
            calls.append(1)
            if len(calls) == 1:
                raise TimeoutError("timed out")
            return {"markets": [{"ticker": "B", "status": "finalized", "result": "no"}]}
        with mock.patch.object(mk, "_get", fake_get):
            out = mk.check_kalshi([f"T{i}" for i in range(mk.KALSHI_BATCH + 1)])
        self.assertEqual(out, {"B": "no"})  # the second batch still counts
        self.assertEqual(len(mk.LAST_FETCH["kalshi_check"]["errors"]), 1)
        with mock.patch.object(mk, "_get", mock.Mock(side_effect=TimeoutError("down"))):
            with self.assertRaises(RuntimeError):  # every batch failed: settle logs it
                mk.check_kalshi(["T1"])

    def test_normalized_markets_carry_when_the_event_happens(self):
        k = mk.normalize_kalshi(dict(self.kalshi_raw("KX-1", 20000), expected_expiration_time="2026-10-01T14:00:00Z"))
        self.assertEqual(k["expected_expiration"], "2026-10-01T14:00:00Z")
        base = POLY_FIXTURE["ok_body"][0]
        sports = mk.normalize_polymarket(dict(base, sportsMarketType="moneyline", gameStartTime="2026-09-28 19:25:00+00"))
        counting = mk.normalize_polymarket(dict(base, gameStartTime="2026-09-22 16:00:00+00"))  # a tweet-count period
        self.assertEqual((sports["starts"], counting["starts"]), ("2026-09-28T19:25:00Z", None))

    def test_rate_limit_is_retried_then_reported(self):
        def limited(n):
            calls = []

            def fake(req, timeout):
                calls.append(1)
                if len(calls) <= n:
                    raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests",
                                                 {"Retry-After": "3"} if len(calls) == 1 else {},
                                                 io.BytesIO(b'{"error":{"code":"too_many_requests"}}'))
                return io.BytesIO(b'{"markets": []}')
            return fake, calls
        fake, calls = limited(2)  # two 429s, then an answer: GitHub's runners hit Kalshi's limit on 2026-09-27
        with mock.patch("urllib.request.urlopen", fake):
            self.assertEqual(mk._get(f"{mk.KALSHI}/markets"), {"markets": []})
        self.assertEqual((len(calls), self.waits), (3, [3.0, 6.0]))  # honors Retry-After, else backs off
        fake, calls = limited(99)
        with mock.patch("urllib.request.urlopen", fake):
            with self.assertRaisesRegex(RuntimeError, "HTTP 429.*too_many_requests"):
                mk._get(f"{mk.KALSHI}/markets")
        self.assertEqual(len(calls), mk.RETRIES)

    def test_http_error_keeps_api_reason(self):
        with mock.patch("urllib.request.urlopen", self.fake_urlopen):
            with self.assertRaisesRegex(RuntimeError, "422.*order fields are not valid"):
                mk._get(f"{mk.POLY}/markets", {"order": "volume_24hr"})


class DecideTests(unittest.TestCase):
    def test_bets_yes_when_edge_and_gates_pass(self):
        d = engine.decide(market(), ans(0.60), POLICY, 100000, 0, 100000)
        self.assertTrue(d["bet"]); self.assertEqual(d["side"], "yes")
        self.assertLessEqual(d["total_cost"], 2000.0)  # 2% cap

    def test_bets_no_side(self):
        d = engine.decide(market(yes_ask=0.70, no_ask=0.32, m=0.69), ans(0.40), POLICY, 100000, 0, 100000)
        self.assertTrue(d["bet"]); self.assertEqual(d["side"], "no")

    def test_small_edge_skipped(self):
        self.assertFalse(engine.decide(market(), ans(0.45), POLICY, 100000, 0, 100000)["bet"])

    def test_gates_block(self):
        self.assertFalse(engine.decide(market(), ans(0.9, clear=0.5), POLICY, 100000, 0, 100000)["bet"])
        self.assertFalse(engine.decide(market(), ans(0.9, info=0.2), POLICY, 100000, 0, 100000)["bet"])

    def test_exposure_cap(self):
        full = POLICY["sizing"]["max_total_exposure_pct"] * 100000  # open bets already at the cap
        d = engine.decide(market(), ans(0.9), POLICY, 100000, full, 100000 - full)
        self.assertFalse(d["bet"])
        self.assertIn("no room", d["reasons"][0])
        self.assertTrue(engine.decide(market(), ans(0.9), POLICY, 100000, full - 5000, 100000 - full + 5000)["bet"])

    def test_yes_no_disagreement_blocks(self):
        self.assertTrue(engine.decide(market(), ans(0.60, p_no=0.42), POLICY, 100000, 0, 100000)["bet"])
        d = engine.decide(market(), ans(0.60, p_no=0.70), POLICY, 100000, 0, 100000)  # 0.60 + 0.70 is far from 1
        self.assertFalse(d["bet"])
        self.assertIn("disagree", " ".join(d["reasons"]))

    def test_kalshi_fee_reduces_edge(self):
        poly = engine.decide(market(), ans(0.6), POLICY, 100000, 0, 100000)
        kal = engine.decide(market(src="kalshi"), ans(0.6), POLICY, 100000, 0, 100000)
        self.assertLess(kal["edge"], poly["edge"])


class StrategyGateTests(unittest.TestCase):
    def test_main_starts_from_its_pre_registered_gates_and_only_original_stays_on_them(self):
        # Reversed 2026-09-28 (Joey chose "free rein over the rules"): main's gates were pinned here so they
        # could never change; now the daily review may tune main like any strategy. What stays pinned: main
        # STARTS from the pre-registered gates, and "original" keeps them for good as the yardstick.
        self.assertEqual({k: v for k, v in POLICY["gates"].items() if not k.startswith("_")},
                         {"min_edge": 0.08, "min_rules_clear": 0.75, "min_info_sufficient": 0.5, "max_framing_gap": 0.15})
        main, orig = POLICY["strategies"]["main"], POLICY["strategies"]["original"]
        self.assertNotIn("gate_overrides", main)
        self.assertNotIn("gate_overrides", orig)
        self.assertEqual((orig["probability"], orig["gates"]), (main["probability"], main["gates"]))
        self.assertIs(engine.strategy_policy(POLICY, orig), POLICY)
        self.assertEqual(POLICY["learning"]["frozen_strategies"], ["original"])
        self.assertTrue(POLICY["learning"]["auto_tune"])
        self.assertNotIn("main", POLICY["learning"]["frozen_strategies"])

    def test_a_strategy_can_skip_categories_and_prices(self):
        pol = engine.strategy_policy(POLICY, {"label": "x", "tuned": {"skip_categories": ["crypto"],
                                                                      "min_ask": 0.2, "max_ask": 0.5}})
        self.assertTrue(engine.decide(market(), ans(0.6), pol, 100000, 0, 100000)["bet"])  # control: an ordinary bet passes
        crypto = dict(market(), question="Will bitcoin close above $100k?")
        self.assertTrue(engine.decide(crypto, ans(0.6), POLICY, 100000, 0, 100000)["bet"])  # control: main takes it
        d = engine.decide(crypto, ans(0.6), pol, 100000, 0, 100000)
        self.assertFalse(d["bet"])
        self.assertIn("skips crypto markets", d["reasons"])
        self.assertEqual(learn._blocked_by(d), "filter")
        cheap, dear = market(yes_ask=0.10, no_ask=0.92), market(yes_ask=0.45, no_ask=0.57)
        self.assertTrue(engine.decide(cheap, ans(0.4), POLICY, 100000, 0, 100000)["bet"])
        self.assertIn("skips prices under", " ".join(engine.decide(cheap, ans(0.4), pol, 100000, 0, 100000)["reasons"]))
        self.assertTrue(engine.decide(dear, ans(0.1), POLICY, 100000, 0, 100000)["bet"])  # buys NO at 0.57
        self.assertIn("skips prices over", " ".join(engine.decide(dear, ans(0.1), pol, 100000, 0, 100000)["reasons"]))

    def test_bold_differs_from_main_only_in_the_info_bar(self):
        bold = engine.strategy_policy(POLICY, POLICY["strategies"]["bold"])
        self.assertEqual(bold["gates"], dict(POLICY["gates"], min_info_sufficient=0.2))
        self.assertEqual((bold["sizing"], bold["fees"]), (POLICY["sizing"], POLICY["fees"]))
        a = ans(0.60, info=0.3)
        self.assertFalse(engine.decide(market(), a, POLICY, 100000, 0, 100000)["bet"])
        self.assertTrue(engine.decide(market(), a, bold, 100000, 0, 100000)["bet"])
        self.assertFalse(engine.decide(market(), ans(0.60, info=0.1), bold, 100000, 0, 100000)["bet"])

    def test_jev_alone_bold_differs_from_jev_alone_only_in_the_info_bar(self):
        s = POLICY["strategies"]["jev_alone_bold"]
        self.assertEqual((s["probability"], s["gates"]), ("jev_plain", "jev_plain"))  # no research, like jev_alone
        pol = engine.strategy_policy(POLICY, s)
        self.assertEqual(pol["gates"], dict(POLICY["gates"], min_info_sufficient=0.2))  # Bold's bar
        self.assertEqual((pol["sizing"], pol["fees"]), (POLICY["sizing"], POLICY["fees"]))
        self.assertIsNone(learn.challenger_problem(dict({k: s[k] for k in ("probability", "gates", "gate_overrides")},
                                                        label="A copy"), POLICY))  # inside the bounds a challenger could reach

    def test_an_override_of_a_gate_that_does_not_exist_is_refused(self):
        with self.assertRaises(ValueError):
            engine.strategy_policy(POLICY, {"label": "typo", "gate_overrides": {"min_info_sufficent": 0.1}})


SCAN_NOW = datetime(1999, 12, 25, tzinfo=timezone.utc)  # test markets close 2000-01-01/02: inside the window
STREAM = (Path(__file__).parent / "fixtures" / "claude_stream.jsonl").read_text()  # a real Claude Code run, recorded


def fact(text, kind="event", date_="1999-12-20", source="Reuters", url="https://www.reuters.com/a"):
    return {"kind": kind, "date": date_, "source": source, "url": url, "fact": text}


class FakeResearcher:
    def __init__(self, facts, usd=0.5, urls=("https://www.reuters.com/a",), fail=None):
        self.facts, self.usd, self.urls, self.fail, self.calls = facts, usd, list(urls), fail, []

    def research(self, markets, today, lessons=None):
        self.lessons = lessons
        self.calls.append([m["question"] for m in markets])
        if self.fail:
            raise self.fail
        return {"raw_facts": self.facts, "source_urls": self.urls, "meta": {"api_equivalent_usd": self.usd}}


class FakeForecaster:
    def __init__(self, probs):
        self.probs, self.states = probs, []

    def forecast(self, state):
        self.states.append(state)
        return {"p_yes": self.probs.get(state["market"]["question"], 0.5), "meta": {"api_equivalent_usd": 0.01}}


class DataDirTest(unittest.TestCase):
    """Points every engine path at a temp folder so tests never touch real data."""
    NAMES = ("DATA", "PORTFOLIO", "PORTFOLIOS", "JUDGMENTS", "RESOLUTIONS", "VOIDS", "SCANS", "REVIEWS", "RESEARCH",
             "SUMMARY", "SITE", "PLAYBOOK", "PLAYBOOK_LOG", "RETROS", "PROPOSALS", "TUNED", "TUNED_LOG", "ODDS", "MENTIONS")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._saved = {n: getattr(engine, n) for n in self.NAMES}
        for n, v in {"DATA": d, "PORTFOLIO": d / "portfolio.json", "PORTFOLIOS": d / "portfolios",
                     "JUDGMENTS": d / "judgments.jsonl", "RESOLUTIONS": d / "resolutions.json", "VOIDS": d / "voids.json",
                     "SCANS": d / "scans.jsonl", "REVIEWS": d / "reviews.jsonl", "RESEARCH": d / "research.jsonl",
                     "SUMMARY": d / "summary.json", "SITE": d / "site", "PLAYBOOK": d / "playbook.json",
                     "PLAYBOOK_LOG": d / "playbook_history.jsonl", "RETROS": d / "retros.jsonl",
                     "PROPOSALS": d / "proposals.json", "TUNED": d / "rules.json",
                     "TUNED_LOG": d / "rules_history.jsonl", "ODDS": d / "odds.json",
                     "MENTIONS": d / "mentions.jsonl"}.items():
            setattr(engine, n, v)
        # A real ODDS_API_KEY in .env or the CI environment must never reach a test: on 2026-10-10 the scans in
        # these tests spent about 100 of the free tier's 500 requests in one run. No key, and any call fails loudly.
        self._no_odds = [mock.patch.object(odds, "api_key", return_value=None),
                         mock.patch.object(odds, "_get", side_effect=AssertionError("a test called The Odds API"))]
        for p in self._no_odds:
            p.start()

    def tearDown(self):
        for p in self._no_odds:
            p.stop()
        for n, v in self._saved.items():
            setattr(engine, n, v)
        self.tmp.cleanup()


class EndToEndTests(DataDirTest):
    def test_scan_settle_report(self):
        ms = [market(mid="1", close="2000-01-01T00:00:00Z"),            # YES bet, resolves yes
              market(mid="2", yes_ask=0.70, no_ask=0.32, m=0.69, close="2000-01-01T00:00:00Z"),  # NO bet, resolves yes -> loss
              market(mid="3", close="2000-01-02T00:00:00Z")]             # no edge
        probs = {"Q1": 0.62, "Q2": 0.40, "Q3": 0.41}
        plain_probs = {"Q1": 0.41, "Q2": 0.68, "Q3": 0.41}  # without research: no edge anywhere
        seen_prices = []

        def transport(url, body, key, timeout):
            state = body["state"]
            seen_prices.append("0.4" in json.dumps(state) or "0.69" in json.dumps(state))  # Jev must not see prices
            p = (probs if "recent_facts" in state else plain_probs)[state["market"]["question"]]
            return {"model": "jev-test", "answers": ans(p)}

        policy = dict(POLICY, sources=["polymarket"])
        kw = dict(client=JevClient(transport=transport), fetchers={"polymarket": lambda *a: ms},
                  log=lambda *_: None, now=SCAN_NOW)
        stats = engine.scan(policy, researcher=FakeResearcher([fact("A clean fact.")]),
                            forecaster=FakeForecaster({"Q1": 0.62, "Q2": 0.68, "Q3": 0.41}), **kw)
        self.assertEqual((stats["funnel"]["judged"], stats["funnel"]["with_research"]), (3, 3))
        self.assertEqual(stats["funnel"]["bets"], {"main": 2, "claude_direct": 1, "bold": 2, "calibrated": 0,
                                                   "original": 2, "sharp": 0, "mention_no": 0})  # the yardstick bets as main started
        self.assertFalse(any(seen_prices))

        # a second scan in the same hour judges nothing and asks Claude for nothing
        r2 = FakeResearcher([])
        stats2 = engine.scan(policy, researcher=r2, forecaster=FakeForecaster({}), **kw)
        self.assertEqual((stats2["funnel"]["judged"], r2.calls), (0, []))

        s = engine.settle(policy, resolvers={"polymarket": lambda mid: "yes" if mid in "12" else None},
                          log=lambda *_: None)
        # settling covers every ledger, the retired Jev alone's too
        self.assertEqual(s["by_strategy"], {"main": 2, "jev_alone": 0, "claude_direct": 1, "bold": 2, "calibrated": 0,
                                            "jev_alone_bold": 0, "original": 2, "sharp": 0, "mention_no": 0})
        pf = engine.load_portfolio(policy)
        self.assertEqual(len(pf["open"]), 0)
        self.assertEqual(sorted(p["outcome"] for p in pf["closed"]), ["yes", "yes"])
        r = engine.report(policy)
        self.assertIn("Brier", r)
        self.assertIn("Claude direct", r)
        self.assertAlmostEqual(pf["cash"], 100000 + sum(p["pnl"] for p in pf["closed"]), places=2)
        out = dashboard.write_dashboard(policy)
        self.assertEqual(out.parent, engine.DATA)  # written next to the data, not into the real folder
        self.assertIn('"settled": 2', out.read_text())

    def test_v1_ledger_moves_to_main_untouched(self):
        engine.save_json(engine.PORTFOLIO, {"created": "x", "starting_bankroll": 100000, "cash": 99000.0,
                                            "open": [], "closed": []})
        pf = engine.load_portfolio(POLICY)
        self.assertEqual(pf["cash"], 99000.0)
        self.assertFalse(engine.PORTFOLIO.exists())
        self.assertTrue(engine.portfolio_path("main").exists())


class SettleAndStorageTests(DataDirTest):
    def test_kalshi_results_count_before_the_stored_close_and_a_scalar_pays_its_value(self):
        far = "2099-01-01T00:00:00Z"  # Kalshi's close_time is a late upper bound; the result is in already
        bet = {"key": "kalshi:K1", "source": "kalshi", "market_id": "K1", "question": "Decided early", "url": "u",
               "close_time": far, "side": "yes", "contracts": 100, "cost_per": 0.4, "total_cost": 40.0,
               "p_side": 0.6, "market_ask": 0.39, "edge": 0.1, "opened": "2026-09-20T00:00:00Z"}
        void_bet = dict(bet, key="kalshi:K2", market_id="K2", question="Settled at a value", side="no")
        engine.save_portfolio("main", dict(fresh_pf(), cash=100000 - 80.0, open=[bet, void_bet]))
        engine.append_jsonl(engine.JUDGMENTS, {"key": "kalshi:K3", "market": {"close_time": far}})  # judged, no bet
        asked = []

        def check(ids):
            asked.append(sorted(ids))
            return {"K1": "yes", "K2": ("void", 0.25), "K3": "no"}
        engine.settle(POLICY, resolvers={}, batch={"kalshi": check}, log=lambda *_: None)
        self.assertEqual(asked, [["K1", "K2", "K3"]])
        self.assertEqual(engine.load_json(engine.RESOLUTIONS, {}), {"kalshi:K1": "yes", "kalshi:K3": "no"})  # never scored
        self.assertEqual(engine.load_json(engine.VOIDS, {}), {"kalshi:K2": 0.25})
        pf = engine.load_portfolio(POLICY)
        closed = {p["key"]: p for p in pf["closed"]}
        self.assertEqual((closed["kalshi:K1"]["payout"], closed["kalshi:K2"]["outcome"], closed["kalshi:K2"]["payout"]),
                         (100.0, "void", 75.0))  # NO is paid 1 - value per contract
        self.assertAlmostEqual(pf["cash"], 100000 - 80.0 + 175.0)
        engine.settle(POLICY, resolvers={}, batch={"kalshi": check}, log=lambda *_: None)
        self.assertEqual(len(asked), 1)  # settled markets aren't asked about again

    def test_a_kalshi_event_under_way_is_filtered_by_its_expected_expiration(self):
        m = dict(market(src="kalshi", close="1999-12-28T00:00:00Z"), expected_expiration="1999-12-25T02:00:00Z")
        self.assertEqual(engine.passes_free_filters(m, POLICY["market_filters"], SCAN_NOW), "close date")
        m["expected_expiration"] = "1999-12-26T02:00:00Z"
        self.assertIsNone(engine.passes_free_filters(m, POLICY["market_filters"], SCAN_NOW))

    def test_logs_rotate_into_archives_and_are_still_read_whole(self):
        for i in range(50):
            engine.append_jsonl(engine.JUDGMENTS, {"ts": f"1999-12-25T00:{i:02d}:00Z", "key": f"k{i}", "pad": "x" * 200})
        self.assertIsNone(engine.rotate_log(engine.JUDGMENTS, 1))  # under the limit: left alone
        target = engine.rotate_log(engine.JUDGMENTS, 0.005)
        self.assertEqual(target.name, "judgments-19991225T000000Z.jsonl.gz")
        self.assertEqual(engine.JUDGMENTS.read_text(), "")
        engine.append_jsonl(engine.JUDGMENTS, {"ts": "1999-12-25T01:00:00Z", "key": "new"})
        self.assertEqual([r["key"] for r in engine.read_jsonl(engine.JUDGMENTS)], [f"k{i}" for i in range(50)] + ["new"])

    def test_the_scan_hands_the_free_filters_to_the_fetcher_and_logs_a_fetch_cut_short(self):
        got = []

        def fetch(*a):
            got.append(a)
            mk.LAST_FETCH["polymarket"] = {"pages": 3, "seconds": 1.0, "cut_short": False, "error": "HTTP 429", "passing": 0}
            return []
        stats = engine.scan(dict(POLICY, sources=["polymarket"]), client=JevClient(transport=lambda *a: None),
                            fetchers={"polymarket": fetch}, log=lambda *_: None, now=SCAN_NOW)
        keep = got[0][3]
        self.assertFalse(keep(dict(market(close="2000-01-01T00:00:00Z"), mid=0.02)))  # outside the price range
        self.assertTrue(keep(market(close="2000-01-01T00:00:00Z")))
        self.assertTrue(any("429" in p for p in stats["problems"]))
        self.assertEqual(stats["funnel"]["fetch"]["polymarket"]["pages"], 3)

        def cut(*a):
            mk.LAST_FETCH["polymarket"] = {"pages": 60, "seconds": 90.0, "cut_short": True, "error": None, "passing": 0}
            return []
        stats = engine.scan(dict(POLICY, sources=["polymarket"]), client=JevClient(transport=lambda *a: None),
                            fetchers={"polymarket": cut}, log=lambda *_: None, now=SCAN_NOW)
        self.assertTrue(any("page limit" in p for p in stats["problems"]))

    def test_settle_checks_kalshi_every_cycle_by_default(self):
        engine.append_jsonl(engine.JUDGMENTS, {"key": "kalshi:K9", "market": {"close_time": "2099-01-01T00:00:00Z"}})
        check = mock.Mock(return_value={"K9": "yes"})
        with mock.patch.dict(mk.BATCH_RESOLVERS, {"kalshi": check}), \
             mock.patch.dict(mk.RESOLVERS, {"polymarket": mock.Mock(return_value=None)}):
            engine.settle(POLICY, log=lambda *_: None)
        check.assert_called_once_with(["K9"])
        self.assertEqual(engine.load_json(engine.RESOLUTIONS, {}), {"kalshi:K9": "yes"})

    def test_a_match_is_skipped_from_an_hour_before_it_starts_and_checked_soon_after(self):
        mf = POLICY["market_filters"]
        m = dict(market(close="2000-01-01T00:00:00Z"), starts="1999-12-25T00:30:00Z")
        self.assertEqual(engine.passes_free_filters(m, mf, SCAN_NOW), "started")
        m["starts"] = "1999-12-25T03:00:00Z"
        self.assertIsNone(engine.passes_free_filters(m, mf, SCAN_NOW))
        # listed to close in 2099, but the match started long ago: its result is checked now
        engine.append_jsonl(engine.JUDGMENTS, {"key": "polymarket:P1", "market": {"close_time": "2099-01-01T00:00:00Z",
                                                                                   "starts": "2020-01-01T00:00:00Z"}})
        asked = []
        engine.settle(POLICY, resolvers={"polymarket": lambda mid: asked.append(mid) or "no"}, log=lambda *_: None)
        self.assertEqual(asked, ["P1"])

    def test_research_stops_starting_when_the_cycle_is_out_of_time(self):
        ticks = iter([0, 0, 10 ** 6, 10 ** 6, 10 ** 6, 10 ** 6, 10 ** 6, 10 ** 6, 10 ** 6, 10 ** 6])
        ms = [dict(market(mid=str(i), close="2000-01-01T00:00:00Z"), event=f"polymarket:e{i}") for i in range(3)]
        r = FakeResearcher([])
        with mock.patch.object(engine, "_clock", lambda: next(ticks, 10 ** 6)):
            engine.scan(dict(POLICY, sources=["polymarket"]), client=JevClient(transport=lambda *a: {"model": "t", "answers": ans(0.5)}),
                        fetchers={"polymarket": lambda *a: ms}, log=lambda *_: None, now=SCAN_NOW + timedelta(hours=12),
                        researcher=r, forecaster=FakeForecaster({}))
        self.assertEqual(len(r.calls), 1)  # the first started in time; the rest wait for a later cycle
        later = [j for j in engine.read_jsonl(engine.JUDGMENTS) if j["key"] == "polymarket:2"][0]
        self.assertIn("research time for this cycle used up", later["decisions"]["main"]["reasons"][0])


LEAKY = [
    "Polymarket traders give Lula a 43% chance of winning.",
    "Lula is the 4/6 favourite with bookmakers.",
    "FiveThirtyEight's forecast model gives Lula a 61 in 100 shot.",
    "Lula stands at 43% in the latest tally.",          # the market's own price, unlabeled
    "Yes shares for Lula trade at 57 cents.",
    "The implied probability of a Lula win is 55%.",
    "Analysts say Lula is expected to win the runoff.",
    "Lula has a 38% chance according to one model.",
]
CLEAN = [
    "A Datafolha poll of 2,004 voters released 1999-12-20 shows Lula at 47% and Bolsonaro at 39%.",
    "The runoff vote is scheduled for 2000-01-01.",
    "Lula won 48.4% of the first-round vote, per the electoral court.",
    "Bolsonaro's coalition gained two senators in the last week.",
]


class ResearchPipelineTests(DataDirTest):
    def lula(self, mid="L", event="polymarket:e1", **kw):
        m = market(mid=mid, yes_ask=0.43, no_ask=0.58, m=0.43, close="2000-01-01T00:00:00Z", **kw)
        return dict(m, question=f"Will Lula win the election? ({mid})", event=event)

    def run_scan(self, ms, researcher, forecaster=None, policy=None, transport=None, now=SCAN_NOW, **kw):
        self.states = []

        def default_transport(url, body, key, timeout):
            self.states.append(body["state"])
            return {"model": "jev-test", "answers": ans(0.5)}
        policy = policy or dict(POLICY, sources=["polymarket"])
        return engine.scan(policy, client=JevClient(transport=transport or default_transport),
                           fetchers={"polymarket": lambda *a: ms}, log=lambda *_: None, now=now,
                           researcher=researcher, forecaster=forecaster or FakeForecaster({}), **kw)

    def test_price_never_reaches_jev_or_claude_through_research(self):
        facts = [fact(t) for t in LEAKY + CLEAN]
        facts.append(fact("Official turnout data was published today.", url="https://kalshi.com/markets/x"))
        fc = FakeForecaster({})
        researcher = FakeResearcher(facts, urls=["https://www.reuters.com/a", "https://kalshi.com/markets/x"])
        self.run_scan([self.lula()], researcher, fc)

        seen = [json.dumps(s) for s in self.states + fc.states]  # everything Jev and Claude direct were given
        self.assertEqual(len(self.states), 2)
        for blob in seen:
            for leak in LEAKY + ["kalshi.com", "0.43", "0.58"]:
                self.assertNotIn(leak, blob)
        rich = [s for s in self.states if "recent_facts" in s]
        self.assertEqual(len(rich), 1)
        self.assertEqual([f["fact"] for f in rich[0]["recent_facts"]], CLEAN)

        j = engine.read_jsonl(engine.JUDGMENTS)[0]
        self.assertEqual(j["recent_facts"], rich[0]["recent_facts"])  # the log holds exactly what Jev saw
        self.assertEqual(len(j["facts_dropped"]), len(LEAKY) + 1)
        self.assertIsNotNone(j["answers_no_news"])

    def test_one_research_call_per_event(self):
        r = FakeResearcher([fact(CLEAN[1])])
        self.run_scan([self.lula("A"), self.lula("B"), self.lula("C", event="polymarket:e2")], r)
        self.assertEqual(sorted(len(c) for c in r.calls), [1, 2])

    def test_free_filters_rechecked_before_paying(self):
        r = FakeResearcher([])
        thin = dict(self.lula("T"), volume=10)                                 # below min_volume
        far = dict(self.lula("F"), close_time="2000-06-01T00:00:00Z")          # closes too late
        cheap = dict(self.lula("C"), mid=0.02)                                 # outside the price range
        stats = self.run_scan([thin, far, cheap], r)
        self.assertEqual((r.calls, stats["funnel"]["passed_filters"]), ([], 0))

    def test_research_only_where_jev_finds_the_rules_clear(self):
        def transport(url, body, key, timeout):
            vague = "(V)" in body["state"]["market"]["question"]
            return {"model": "jev-test", "answers": ans(0.5, clear=0.4 if vague else 0.9)}
        r = FakeResearcher([])
        stats = self.run_scan([self.lula("V", event="polymarket:ev"), self.lula("K", event="polymarket:ek")], r,
                              transport=transport)
        self.assertEqual(r.calls, [["Will Lula win the election? (K)"]])
        self.assertEqual(stats["funnel"]["judged"], 2)  # Jev still judged both (Jev alone decides on both)
        vague = [j for j in engine.read_jsonl(engine.JUDGMENTS) if "(V)" in j["market"]["question"]][0]
        self.assertIn("rules unclear", vague["decisions"]["main"]["reasons"][0])

    def test_research_caps_per_cycle_and_per_day(self):
        cap = POLICY["research"]["max_research_per_cycle"]
        ms = [self.lula(str(i), event=f"polymarket:e{i}") for i in range(cap + 3)]
        r = FakeResearcher([])
        unpaced = dict(POLICY, sources=["polymarket"], research=dict(POLICY["research"], pace_through_day=False))
        self.run_scan(ms, r, policy=unpaced)
        self.assertEqual(len(r.calls), POLICY["research"]["max_research_per_cycle"])
        for i in range(POLICY["research"]["max_research_per_day"]):  # a day that has already used its research allowance
            engine.append_jsonl(engine.RESEARCH, {"ts": "1999-12-25T01:00:00Z", "event": f"old{i}", "mids": {}})
        r2 = FakeResearcher([])
        self.run_scan([self.lula("N", event="polymarket:new")], r2, policy=unpaced, now=SCAN_NOW + timedelta(hours=2))
        self.assertEqual(r2.calls, [])

    def test_research_is_paced_through_the_day_and_soonest_first(self):
        # the mechanism at the 2026-09-28 numbers (60 a day, 6 a cycle): policy.json's numbers change, the pacing doesn't
        rc = dict(POLICY["research"], max_research_per_day=60, max_research_per_cycle=6)
        self.assertTrue(rc["pace_through_day"])
        policy = dict(POLICY, research=rc, sources=["polymarket"])
        ms = [dict(self.lula(str(i), event=f"polymarket:e{i}"), close_time=f"2000-01-0{9 - i}T00:00:00Z") for i in range(8)]
        r = FakeResearcher([])
        self.run_scan(ms, r, policy=policy)  # 00:00 UTC, nothing used yet: only the first hour's share of the day
        first_hour = -(-rc["max_research_per_day"] * 1 // 24)
        self.assertEqual(len(r.calls), min(first_hour, rc["max_research_per_cycle"]))
        # the events decided soonest were researched first (e7 closes Jan 2, e0 Jan 9)
        self.assertEqual([c[0] for c in r.calls], [f"Will Lula win the election? ({i})" for i in (7, 6, 5)][:len(r.calls)])
        for i in range(20):  # by noon 20 have run: the day's pace allows up to 60 x 13/24 = 33, capped per cycle
            engine.append_jsonl(engine.RESEARCH, {"ts": "1999-12-25T11:00:00Z", "event": f"old{i}", "mids": {}})
        r2 = FakeResearcher([])
        more = [self.lula(f"n{i}", event=f"polymarket:n{i}") for i in range(8)]
        self.run_scan(more, r2, policy=policy, now=SCAN_NOW + timedelta(hours=12))
        self.assertEqual(len(r2.calls), rc["max_research_per_cycle"])
        for i in range(4):  # 3 + 20 + 6 + 4 = 33 used by 12:30; the pace allows 34 (60 x 13.5/24, rounded up)
            engine.append_jsonl(engine.RESEARCH, {"ts": "1999-12-25T12:10:00Z", "event": f"x{i}", "mids": {}})
        r3 = FakeResearcher([])
        self.run_scan([self.lula(f"m{i}", event=f"polymarket:m{i}") for i in range(8)], r3, policy=policy,
                      now=SCAN_NOW + timedelta(hours=12, minutes=30))
        self.assertEqual(len(r3.calls), 1)  # one more, not a whole cycle's worth

    def test_research_is_reused_until_stale_or_the_price_moves(self):
        r = FakeResearcher([fact(CLEAN[1])])
        self.run_scan([self.lula()], r)
        self.assertEqual(len(r.calls), 1)
        fc = FakeForecaster({})
        stats = self.run_scan([self.lula()], r, fc, now=SCAN_NOW + timedelta(hours=7))   # due again, research fresh
        self.assertEqual((len(r.calls), stats["funnel"]["research_reused"], stats["funnel"]["with_research"]), (1, 1, 1))
        self.assertEqual(fc.states, [])  # Claude direct only runs on fresh research
        moved = dict(self.lula(), mid=0.60)
        self.run_scan([moved], r, now=SCAN_NOW + timedelta(hours=14))                   # price moved 17 points
        self.assertEqual(len(r.calls), 2)
        self.run_scan([moved], r, now=SCAN_NOW + timedelta(hours=40))                   # older than 24 hours
        self.assertEqual(len(r.calls), 3)

    def test_research_failure_leaves_jev_alone_running_and_fatal_stops_research(self):
        ms = [self.lula(str(i), event=f"polymarket:e{i}") for i in range(3)]
        r = FakeResearcher([], fail=news.NewsError("bad reply"))
        stats = self.run_scan(ms, r)
        # two failures in a row end research for the cycle; Jev alone still judges every market
        self.assertEqual((len(r.calls), stats["funnel"]["judged"], stats["funnel"]["with_research"], stats["errors"]),
                         (2, 3, 0, 2))
        third = [j for j in engine.read_jsonl(engine.JUDGMENTS) if j["market"]["question"].endswith("(2)")][0]
        self.assertIn("research failing this cycle", third["decisions"]["main"]["reasons"][0])
        r2 = FakeResearcher([], fail=news.NewsError("not installed", fatal=True))
        self.run_scan([dict(m, market_id=m["market_id"] + "x") for m in ms], r2)
        self.assertEqual(len(r2.calls), 1)

    def test_an_api_key_in_the_environment_stops_research_not_jev(self):
        with mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
            stats = engine.scan(dict(POLICY, sources=["polymarket"]),
                                client=JevClient(transport=lambda *a: {"model": "t", "answers": ans(0.5)}),
                                fetchers={"polymarket": lambda *a: [self.lula()]}, log=lambda *_: None, now=SCAN_NOW)
        self.assertEqual((stats["funnel"]["judged"], stats["funnel"]["with_research"], stats["errors"]), (1, 0, 1))
        self.assertIn("API account", stats["claude"]["note"])
        j = engine.read_jsonl(engine.JUDGMENTS)[0]
        self.assertIn("research unavailable", j["decisions"]["main"]["reasons"][0])

    def test_plan_usage_guard_waits_for_the_window_to_reset(self):
        rc = POLICY["research"]
        runs = []

        def runner_with(week):
            def runner(args, env, cwd, timeout):
                runs.append(args)
                return 0, stream("[]", week=week), ""
            return runner
        busy = {"status": "allowed_warning", "unifiedWindows": {
            "seven_day": {"utilization": rc["max_week_used"], "resetsAt": (SCAN_NOW + timedelta(hours=10)).timestamp()}}}
        engine.append_jsonl(engine.SCANS, {"ts": "1999-12-24T23:00:00Z", "claude": {"rate": busy}})
        # the plan really is full: one probe call gets a fresh (full) reading, and research stops there
        cc = news.ClaudeCode(rc, runner=runner_with(rc["max_week_used"]))
        stats = self.run_scan([self.lula(), self.lula("M", event="polymarket:e2")], news.Researcher(rc, cc),
                              news.DirectForecaster(rc, cc), claude=cc)
        self.assertEqual((len(runs), stats["claude"]["limited"], stats["claude"]["probe"]), (1, True, True))
        # half an hour later the stored reading still says full and a probe ran recently: no call at all
        cc2 = news.ClaudeCode(rc, runner=runner_with(rc["max_week_used"]))
        self.run_scan([self.lula("N", event="polymarket:e3")], news.Researcher(rc, cc2), news.DirectForecaster(rc, cc2),
                      claude=cc2, now=SCAN_NOW + timedelta(minutes=30))
        self.assertEqual(len(runs), 1)
        # after the weekly window resets, research runs again
        cc3 = news.ClaudeCode(rc, runner=runner_with(0.3))
        self.run_scan([self.lula("P", event="polymarket:e4")], news.Researcher(rc, cc3), news.DirectForecaster(rc, cc3),
                      claude=cc3, now=SCAN_NOW + timedelta(hours=11))
        self.assertGreater(len(runs), 1)

    def test_a_stale_busy_reading_from_another_account_does_not_block_research(self):
        rc = POLICY["research"]
        runs = []

        def runner(args, env, cwd, timeout):
            runs.append(args)
            return 0, stream("[]", week=0.2), ""  # the new token's account has room
        full = {"unifiedWindows": {"seven_day": {"utilization": 1.0, "resetsAt": (SCAN_NOW + timedelta(days=4)).timestamp()}}}
        engine.append_jsonl(engine.SCANS, {"ts": "1999-12-24T23:30:00Z", "claude": {"rate": full}})
        cc = news.ClaudeCode(rc, runner=runner)
        self.run_scan([self.lula(), self.lula("M", event="polymarket:e2")], news.Researcher(rc, cc),
                      news.DirectForecaster(rc, cc), claude=cc)
        self.assertGreaterEqual(len(runs), 2)  # the probe found room, so research carried on

    def test_the_sharp_line_bets_a_matched_game_and_the_line_never_reaches_jev(self):
        mk._SERIES_FEE["KXNFLGAME"] = 1.0  # the series' fee multiplier, known: no network in tests
        states = []

        def transport(url, body, key, timeout):
            states.append(body["state"])
            return {"model": "jev-test", "answers": ans(0.5)}
        cache = {"americanfootball_nfl": {"fetched": "1999-12-24T23:55:00Z", "events": [game()]}}
        try:
            with mock.patch.object(odds, "api_key", return_value="k"), \
                    mock.patch.object(odds, "load_events", return_value=cache):
                stats = engine.scan(dict(POLICY, sources=["kalshi"]), client=JevClient(transport=transport),
                                    fetchers={"kalshi": lambda *a: [kalshi_game()]}, log=lambda *_: None, now=SCAN_NOW,
                                    researcher=FakeResearcher([fact(CLEAN[1])]))
        finally:
            mk._SERIES_FEE.pop("KXNFLGAME", None)
        self.assertEqual((stats["sharp"]["matched"], stats["funnel"]["bets"]["sharp"]), (1, 1))
        bet = engine.load_portfolio(POLICY, "sharp")["open"][0]
        self.assertEqual((bet["sizing"], bet["probe"], bet["side"], bet["event"]),
                         ("probe", True, "yes", "kalshi:KXNFLGAME-26OCT11PITCIN"))  # no measured edge yet: a probe
        self.assertAlmostEqual(bet["total_cost"], 250, delta=1)
        j = engine.read_jsonl(engine.JUDGMENTS)[-1]
        p = j["sharp"]["p_yes"]
        self.assertEqual((j["sharp"]["outcome"], j["decisions"]["sharp"]["p_yes"]), ("Pittsburgh Steelers", p))
        self.assertEqual(engine._prob(j, "sharp"), p)  # scored and measured like any forecaster
        sent = json.dumps(states)
        self.assertNotIn(str(p), sent)       # Pinnacle's price never goes to Jev
        self.assertNotIn("Steelers", sent)   # nor anything else from the odds feed
        self.assertTrue(engine.ODDS.exists())  # kept for the next cycle

    def mention(self, **kw):
        return dict({"source": "kalshi", "market_id": "KXEARNINGSMENTIONDAL-26OCT09-TARIFF", "event": "kalshi:KXEARNINGSMENTIONDAL-26OCT09",
                     "question": "Will Delta say Tariff during its earnings call?", "rules": "r", "close_time": "1999-12-28T00:00:00Z",
                     "expected_expiration": "1999-12-27T15:00:00Z", "yes_ask": 0.56, "no_ask": 0.46, "mid": 0.55,
                     "volume": 300, "url": "u", "yes_ask_size": 400.0, "no_ask_size": 900.0}, **kw)

    def scan_mentions(self, ms, now=SCAN_NOW):
        mk.LAST_MENTIONS[:] = ms
        try:
            return engine.scan(dict(POLICY, sources=["kalshi"]), client=JevClient(transport=lambda *a: {"model": "t", "answers": ans(0.5)}),
                               fetchers={"kalshi": lambda *a: []}, log=lambda *_: None, now=now)
        finally:
            mk.LAST_MENTIONS.clear()

    def test_the_mention_strategy_buys_no_before_the_event_within_what_the_ask_offers(self):
        stats = self.scan_mentions([self.mention()])
        self.assertEqual((stats["funnel"]["bets"]["mention_no"], stats["mentions"]), (1, {"seen": 1, "looked": 1}))
        bet = engine.load_portfolio(POLICY, "mention_no")["open"][0]
        # mid 0.55 -> P(YES) 0.43 -> P(NO) 0.57 against a 46c NO ask plus fee and slippage: a NO probe
        self.assertEqual((bet["side"], bet["sizing"], bet["probe"]), ("no", "probe", True))
        self.assertAlmostEqual(bet["p_side"], 0.57)
        self.assertAlmostEqual(bet["total_cost"], 250, delta=1)
        rec = engine.read_jsonl(engine.MENTIONS)[0]
        self.assertEqual((rec["mention_prior"]["p_yes"], engine._prob(rec, "mention_prior")), (0.43, 0.43))
        self.assertEqual(engine.read_jsonl(engine.JUDGMENTS), [])  # no Jev call, and the Jev log stays clean
        # looked at again only after rejudge_after_hours: the same market an hour later isn't logged twice
        self.scan_mentions([self.mention()], now=SCAN_NOW + timedelta(hours=1))
        self.assertEqual(len(engine.read_jsonl(engine.MENTIONS)), 1)

    def test_mention_markets_outside_the_band_near_the_event_or_thin_get_no_full_bet(self):
        self.scan_mentions([self.mention(market_id="A", mid=0.85, yes_ask=0.86, no_ask=0.16)])  # outside the band: the mid
        self.assertEqual(engine.read_jsonl(engine.MENTIONS)[0]["mention_prior"]["p_yes"], 0.85)
        self.assertEqual(engine.load_portfolio(POLICY, "mention_no")["open"], [])
        self.scan_mentions([self.mention(market_id="B", expected_expiration="1999-12-25T00:30:00Z")])  # 30 min to go
        self.assertNotIn("kalshi:B", {r["key"] for r in engine.read_jsonl(engine.MENTIONS)})
        self.scan_mentions([self.mention(market_id="C", no_ask_size=40.0)])  # only 40 contracts offered at the ask
        bet = next(b for b in engine.load_portfolio(POLICY, "mention_no")["open"] if b["market_id"] == "C")
        self.assertEqual(bet["contracts"], 40)

    def test_one_mention_bet_per_event_soonest_first(self):
        later = self.mention(market_id="L1", event="kalshi:LATE", expected_expiration="1999-12-30T15:00:00Z")
        soon = [self.mention(market_id=f"S{i}", event="kalshi:SOON") for i in range(3)]
        self.scan_mentions([later] + soon)
        held = engine.load_portfolio(POLICY, "mention_no")["open"]
        self.assertEqual(sorted(b["event"] for b in held), ["kalshi:LATE", "kalshi:SOON"])  # one per event
        recs = engine.read_jsonl(engine.MENTIONS)
        self.assertEqual(recs[0]["key"], "kalshi:S0")  # the soonest-ending market was looked at first
        self.assertIn("already holds a bet on this event", recs[1]["decisions"]["mention_no"]["reasons"][0])

    def test_settling_scores_mention_markets_that_were_only_looked_at(self):
        engine.append_jsonl(engine.MENTIONS, {"ts": "1999-12-25T00:00:00Z", "key": "kalshi:X", "question_set": review.QUESTION_SET_VERSION,
                                              "market": dict(self.mention(market_id="X"), close_time="1999-12-26T00:00:00Z"),
                                              "mention_prior": {"p_yes": 0.43}, "decisions": {}})
        engine.settle(POLICY, resolvers={}, batch={"kalshi": lambda ids: {i: "no" for i in ids}}, log=lambda *_: None)
        self.assertEqual(engine.load_json(engine.RESOLUTIONS, {})["kalshi:X"], "no")

    def test_each_strategy_uses_its_own_probability_and_never_doubles_up(self):
        def transport(url, body, key, timeout):
            return {"model": "jev-test", "answers": ans(0.70 if "recent_facts" in body["state"] else 0.60)}
        fc = FakeForecaster({"Will Lula win the election? (L)": 0.45})
        stats = self.run_scan([self.lula()], FakeResearcher([fact(CLEAN[0])]), fc, transport=transport)
        self.assertEqual(stats["funnel"]["bets"], {"main": 1, "claude_direct": 0, "bold": 1, "calibrated": 0,
                                                   "original": 1, "sharp": 0, "mention_no": 0})
        j = engine.read_jsonl(engine.JUDGMENTS)[0]
        self.assertEqual((j["decisions"]["main"]["p_yes"], j["answers_no_news"]["p_yes"]["noul"]), (0.70, 0.60))
        self.assertFalse({"jev_alone", "jev_alone_bold"} & set(j["decisions"]))  # retired: they no longer bet
        self.assertIn("ODDS_API_KEY", j["decisions"]["sharp"]["reasons"][0])  # no key in tests: says what it waits for
        # two days later the market is judged again for data, but no strategy adds to a position it holds
        stats2 = self.run_scan([self.lula()], FakeResearcher([]), fc, transport=transport, now=SCAN_NOW + timedelta(days=2))
        self.assertEqual(stats2["funnel"]["judged"], 1)
        self.assertEqual(stats2["funnel"]["bets"]["main"], 0)
        self.assertEqual(len(engine.load_portfolio(POLICY)["open"]), 1)

    def test_a_new_strategy_gets_a_first_look_without_new_research(self):
        without_bold = dict(POLICY, sources=["polymarket"],
                            strategies={k: v for k, v in POLICY["strategies"].items() if k != "bold"})
        r = FakeResearcher([fact(CLEAN[1])])
        self.run_scan([self.lula()], r, policy=without_bold)
        stats = self.run_scan([self.lula()], r, now=SCAN_NOW + timedelta(hours=1))  # bold added an hour later
        self.assertEqual((stats["funnel"]["judged"], stats["funnel"]["research_reused"], len(r.calls)), (1, 1, 1))
        self.assertIn("bold", engine.read_jsonl(engine.JUDGMENTS)[-1]["decisions"])
        stats = self.run_scan([self.lula()], r, now=SCAN_NOW + timedelta(hours=2))  # everyone has decided now
        self.assertEqual(stats["funnel"]["judged"], 0)

    def test_playbook_lessons_reach_research_screened_and_logged(self):
        engine.save_json(engine.PLAYBOOK, {"version": 4, "rules": [
            {"id": "R1", "category": "politics", "rule": "Read the electoral court's official results page first."},
            {"id": "R2", "category": "sports", "rule": "Read the league's official standings table first."},
            {"id": "R3", "category": "general", "rule": "Note the exact time zone the resolution source uses."},
            {"id": "R4", "category": "general", "rule": "Check what bookmakers and Polymarket traders expect first."}]})
        r = FakeResearcher([fact(CLEAN[1])])
        self.run_scan([self.lula()], r)  # a politics market
        self.assertEqual([x["id"] for x in r.lessons], ["R1", "R3"])  # its category + general; R4 fails the screen
        rec = engine.read_jsonl(engine.RESEARCH)[0]
        self.assertEqual((rec["playbook_version"], rec["lessons"]), (4, ["R1", "R3"]))
        self.assertEqual(engine.read_jsonl(engine.JUDGMENTS)[0]["research"]["playbook"], 4)

    def test_calibrated_strategy_waits_then_bets_with_the_learned_map(self):
        def transport(url, body, key, timeout):
            return {"model": "jev-test", "answers": ans(0.80 if "recent_facts" in body["state"] else 0.5)}
        pol = dict(POLICY, sources=["polymarket"], learning=dict(POLICY["learning"], calibration_min_resolved=40))
        self.run_scan([self.lula()], FakeResearcher([fact(CLEAN[1])]), transport=transport, policy=pol)
        j = engine.read_jsonl(engine.JUDGMENTS)[-1]
        self.assertIsNone(j["jev_calibrated"])
        self.assertIn("still learning", j["decisions"]["calibrated"]["reasons"][0])
        # 40 resolved markets where Jev said 80% and only half came true: Jev is overconfident
        for i in range(40):
            engine.append_jsonl(engine.REVIEWS, {"key": f"k{i}", "ts": "1999-12-01T00:00:00Z",
                                                 "probs": {"jev_research": 0.8}, "outcome": "yes" if i % 2 else "no"})
        self.run_scan([self.lula("M")], FakeResearcher([fact(CLEAN[1])]), transport=transport, policy=pol)
        j = engine.read_jsonl(engine.JUDGMENTS)[-1]
        self.assertLess(j["jev_calibrated"], 0.75)  # pulled from 0.80 toward what actually happened
        self.assertGreater(j["jev_calibrated"], 0.5)  # but the prior keeps 40 results from erasing Jev's view
        self.assertEqual(j["decisions"]["calibrated"]["p_yes"], j["jev_calibrated"])
        self.assertEqual(j["calibration_map"]["n"], 40)

    def test_running_challengers_trade_their_own_bankroll_and_bad_ones_never_load(self):
        engine.save_json(engine.PROPOSALS, {"proposals": [
            {"id": "ch1", "kind": "challenger", "status": "running", "title": "t",
             "strategy": {"label": "Edge 5", "probability": "jev_research", "gates": "jev_research",
                          "gate_overrides": {"min_edge": 0.05}}},
            {"id": "ch2", "kind": "challenger", "status": "running", "title": "t",  # hand-edited past the bounds
             "strategy": {"label": "Edge 70", "probability": "jev_research", "gates": "jev_research",
                          "gate_overrides": {"min_edge": 0.7}}},
            {"id": "ch3", "kind": "challenger", "status": "running", "title": "t",  # tries to change fees
             "strategy": {"label": "Free", "probability": "jev_research", "gates": "jev_research",
                          "rules": {"slippage": 0.0}}},
            {"id": "ch4", "kind": "challenger", "status": "proposed", "title": "t",  # not approved yet
             "strategy": {"label": "Later", "probability": "jev_plain", "gates": "jev_plain"}}]})
        book = engine.load_json(engine.PROPOSALS, {})
        book["proposals"].append({"id": "ch5", "kind": "challenger", "status": "running", "title": "t",  # sizing is allowed
                                  "strategy": {"label": "Big", "probability": "jev_research", "gates": "jev_research",
                                               "rules": {"max_stake_pct": 0.03, "kelly_fraction": 0.5}}})
        engine.save_json(engine.PROPOSALS, book)
        names = set(engine.strategies(POLICY))
        self.assertTrue({"ch1", "ch5"} <= names)
        self.assertFalse(names & {"ch2", "ch3", "ch4"})
        self.assertEqual(engine.strategy_policy(POLICY, engine.strategies(POLICY)["ch5"])["sizing"]["max_stake_pct"], 0.03)
        self.run_scan([self.lula()], FakeResearcher([fact(CLEAN[1])]))
        self.assertIn("ch1", engine.read_jsonl(engine.JUDGMENTS)[0]["decisions"])
        self.assertTrue(engine.portfolio_path("ch1").exists())

    def test_each_bet_records_the_rules_version_it_was_placed_under(self):
        now = datetime(1999, 12, 20, tzinfo=timezone.utc)
        self.assertEqual(coach.tune(POLICY, "main", {"max_stake_pct": 0.03}, now, why="w")[0], "applied")

        def transport(url, body, key, timeout):
            return {"model": "jev-test", "answers": ans(0.75)}
        self.run_scan([self.lula()], FakeResearcher([fact(CLEAN[1])]), transport=transport)
        main, orig = engine.load_portfolio(POLICY, "main")["open"][0], engine.load_portfolio(POLICY, "original")["open"][0]
        self.assertEqual((main["rules_version"], orig["rules_version"]), (2, 1))
        # no forecaster has a measured edge, so main places a probe (0.25% of equity); the frozen yardstick keeps
        # the old Kelly sizing, capped at 2%
        self.assertEqual((main["sizing"], main["probe"], main["lambda"]), ("probe", True, 0.0))
        self.assertAlmostEqual(main["total_cost"], 250, delta=1.0)
        self.assertEqual((orig["sizing"], orig["probe"]), ("kelly (old rules)", False))
        self.assertAlmostEqual(orig["total_cost"], 2000, delta=1.0)
        self.assertEqual(main["event"], orig["event"])

    def test_scan_logs_its_funnel(self):
        self.run_scan([self.lula()], FakeResearcher([fact(CLEAN[1])]))
        s = engine.read_jsonl(engine.SCANS)[-1]
        f = s["funnel"]
        self.assertEqual((f["fetched"], f["judged"], f["researched_new"], f["with_research"]), (1, 1, 1, 1))
        self.assertEqual(s["claude"]["api_equivalent_usd"], 0.51)


class ScreenFactsTests(unittest.TestCase):
    M = [dict(market(mid="L", yes_ask=0.43, no_ask=0.58, m=0.43))]
    URLS = ["https://www.reuters.com/world/x"]

    def screen(self, facts, max_facts=20):
        return news.screen_facts(facts, self.M, "1999-12-25", self.URLS, max_facts)

    def test_drops_every_leak_with_a_reason(self):
        kept, dropped = self.screen([fact(t) for t in LEAKY])
        self.assertEqual(kept, [])
        self.assertTrue(all(d["reason"] for d in dropped))

    def test_keeps_clean_facts(self):  # the negative control: the screen must not eat ordinary evidence
        kept, dropped = self.screen([fact(t) for t in CLEAN])
        self.assertEqual(([k["fact"] for k in kept], dropped), (CLEAN, []))

    def test_requires_a_date_a_source_and_a_page_the_call_saw(self):
        facts = [fact("Future.", date_="1999-12-26"), fact("No date.", date_="soon"), fact("No source.", source=""),
                 fact("Unseen page.", url="https://example.org/x"), fact("Good one.", url="https://reuters.com/y")]
        kept, dropped = self.screen(facts)
        self.assertEqual([k["fact"] for k in kept], ["Good one."])
        self.assertEqual(len(dropped), 4)

    def test_web_addresses_are_checked_for_market_sites_only(self):
        # Jev never sees a fact's web address, so a word like "prediction" in a news page's address is
        # harmless; a prediction-market or betting site is still refused by its name (Joey, 2026-09-27).
        urls = ["https://www.sportsmole.co.uk/football/preview/belgium-vs-france-prediction-team-news_1.html",
                "https://www.oddschecker.com/football/france", "https://sportsbook.fanduel.com/x"]
        facts = [fact("Mbappe will miss the match with a calf injury.", url=urls[0]),
                 fact("France play Belgium on Monday.", url=urls[1]),
                 fact("Kickoff is at 8:45 pm local time.", url=urls[2])]
        kept, dropped = news.screen_facts(facts, self.M, "1999-12-25", urls, 20)
        self.assertEqual([k["fact"] for k in kept], ["Mbappe will miss the match with a calf injury."])
        self.assertEqual(len(dropped), 2)

    def test_caps_dedupes_and_normalizes(self):
        facts = [fact(f"Fact {i}.") for i in range(5)] + [fact("Fact 0."), dict(fact("Odd kind."), kind="rumor")]
        kept, dropped = self.screen(facts, max_facts=3)
        self.assertEqual(len(kept), 3)
        self.assertEqual({d["reason"] for d in dropped}, {"over the fact cap", "duplicate"})
        kept2, _ = self.screen([dict(fact("Odd kind."), kind="rumor")])
        self.assertEqual(kept2[0]["kind"], "event")


def stream(text, is_error=False, rate_status="allowed", week=0.3):
    """A Claude Code stream-json reply in the recorded shape."""
    lines = [{"type": "rate_limit_event", "rate_limit_info": {"status": rate_status, "unifiedWindows": {
                 "seven_day": {"utilization": week, "resetsAt": 4102444800}, "five_hour": {"utilization": 0.1, "resetsAt": 4102444800}}}},
             {"type": "user", "message": {"content": [{"type": "tool_result", "content": "Links: https://www.reuters.com/a"}]}},
             {"type": "result", "subtype": "success", "is_error": is_error, "result": text, "num_turns": 2,
              "total_cost_usd": 0.12}]
    return "\n".join(json.dumps(x) for x in lines)


class ClaudeCodeTests(unittest.TestCase):
    CFG = POLICY["research"]

    def claude(self, replies, calls):
        it = iter(replies)

        def runner(args, env, cwd, timeout):
            calls.append({"args": args, "env": env, "cwd": cwd})
            r = next(it)
            return r if isinstance(r, tuple) else (0, r, "")
        with mock.patch.dict("os.environ", {}, clear=False):
            return news.ClaudeCode(self.CFG, runner=runner)

    def test_parses_a_real_recorded_run(self):
        s = news.parse_stream(STREAM)
        self.assertFalse(s["result"]["is_error"])
        self.assertEqual((s["searches"], s["fetches"]), (1, 0))
        self.assertIn("https://en.wikipedia.org/wiki/Columbus_Day", s["urls"])
        self.assertIn("seven_day", s["rate"]["unifiedWindows"])

    def test_refuses_to_run_with_an_api_key_set(self):
        for var in news.BILLING_VARS:
            with mock.patch.dict("os.environ", {var: "x"}):
                with self.assertRaises(news.NewsError) as cm:
                    news.ClaudeCode(self.CFG, runner=lambda *a: (0, "", ""))
                self.assertTrue(cm.exception.fatal)

    def test_runs_on_the_plan_with_only_web_tools_and_no_market_sites(self):
        calls = []
        cc = self.claude([stream(json.dumps([fact("A.")]))], calls)
        out = news.Researcher(self.CFG, cc).research([market(yes_ask=0.4321, no_ask=0.5876, m=0.4312)], "1999-12-25")
        a, env = calls[0]["args"], calls[0]["env"]
        self.assertEqual(a[:2], ["claude", "-p"])
        self.assertEqual(a[a.index("--tools") + 1], "WebSearch,WebFetch")
        self.assertEqual(a[a.index("--permission-mode") + 1], "dontAsk")
        self.assertEqual(a[a.index("--setting-sources") + 1], "")
        self.assertEqual(a[a.index("--model") + 1], "claude-opus-5-5")
        self.assertIn("WebFetch(domain:kalshi.com)", a)
        self.assertNotIn("--bare", a)  # bare mode would require an API key
        self.assertFalse(set(news.BILLING_VARS) & set(env))
        self.assertNotIn("jev-paper-trader", calls[0]["cwd"])  # runs outside the repo: no CLAUDE.md, no hooks
        blob = json.dumps(a)
        for price in ("0.4321", "0.5876", "0.4312", "43.2"):
            self.assertNotIn(price, blob)
        self.assertEqual((out["raw_facts"][0]["fact"], out["source_urls"]), ("A.", ["https://www.reuters.com/a"]))
        self.assertEqual(out["meta"]["billing"], "claude_plan")

    def test_forecast_has_no_tools_and_validates(self):
        calls = []
        cc = self.claude([stream('{"p_yes": 0.37}'), stream('{"p_yes": 1.7}')], calls)
        f = news.DirectForecaster(self.CFG, cc)
        self.assertEqual(f.forecast({"market": {}})["p_yes"], 0.37)
        self.assertEqual(calls[0]["args"][calls[0]["args"].index("--tools") + 1], "")
        with self.assertRaises(news.NewsError):
            f.forecast({"market": {}})

    def test_limits_errors_and_usage_share(self):
        calls = []
        cc = self.claude([stream("You've hit your session limit · resets 3am", is_error=True),
                          stream("", rate_status="rejected"), (1, "", "boom"), stream("no json")], calls)
        r = news.Researcher(self.CFG, cc)
        for expect_limited in (True, True):
            with self.assertRaises(news.NewsError) as cm:
                r.research([market()], "1999-12-25")
            self.assertEqual((cm.exception.limited, cm.exception.fatal), (expect_limited, True))
        cc.last_rate = None
        with self.assertRaises(news.NewsError) as cm:
            r.research([market()], "1999-12-25")
        self.assertFalse(cm.exception.limited)
        with self.assertRaises(news.NewsError):
            r.research([market()], "1999-12-25")  # no JSON list in the reply
        cc.last_rate = {"unifiedWindows": {"seven_day": {"utilization": self.CFG["max_week_used"]}}}
        self.assertFalse(cc.usage_ok())
        cc.last_rate = {"unifiedWindows": {"five_hour": {"utilization": self.CFG["max_five_hour_used"] - 0.01}}}
        self.assertTrue(cc.usage_ok())

    def test_research_keeps_pace_with_the_week_but_the_learning_steps_do_not_wait(self):
        cc = self.claude([], [])
        now, day = 1_000_000.0, 86400
        rate = lambda used, days_left: {"unifiedWindows": {"seven_day": {"utilization": used, "resetsAt": now + days_left * day}}}
        self.assertEqual(self.CFG["week_pace_margin"], 0.15)
        cc.last_rate = rate(0.40, 5)  # 2 of 7 days gone (29%): 40% is within 29% + 15%
        self.assertTrue(cc.usage_ok(now=now))
        cc.last_rate = rate(0.50, 5)  # more than 15 points ahead of pace: research waits
        self.assertFalse(cc.usage_ok(now=now))
        self.assertTrue(cc.usage_ok(paced=False, now=now))  # the daily review and the coach still run
        cc.last_rate = rate(0.80, 1)  # 6 days gone: 80% is on pace
        self.assertTrue(cc.usage_ok(now=now))
        cc.last_rate = rate(0.50, 30)  # a reset time that can't be this week's is not paced against
        self.assertTrue(cc.usage_ok(now=now))


def fresh_pf():
    return {"created": "2026-09-27T00:00:00Z", "starting_bankroll": 100000, "cash": 100000.0, "open": [], "closed": []}


def books(main):
    return {name: main if name == "main" else fresh_pf() for name in engine.strategies(POLICY)}


class DashboardTests(DataDirTest):
    def pf(self):
        opened = {"key": "kalshi:A", "source": "kalshi", "market_id": "A", "question": "Open one", "url": "https://kalshi.com/x",
                  "close_time": "2099-01-01T00:00:00Z", "side": "yes", "contracts": 100, "cost_per": 0.41,
                  "total_cost": 41.0, "p_side": 0.55, "market_ask": 0.40, "edge": 0.14, "opened": "2026-09-20T00:00:00Z"}
        won = dict(opened, key="polymarket:B", source="polymarket", question="Won one", total_cost=50.0, contracts=100,
                   outcome="yes", payout=100.0, pnl=50.0, settled="2026-09-22T00:00:00Z")
        lost = dict(opened, key="kalshi:C", question="Lost one", total_cost=30.0, outcome="no", payout=0.0, pnl=-30.0,
                    settled="2026-09-21T00:00:00Z")
        return {"created": "2026-09-19T00:00:00Z", "starting_bankroll": 100000,
                "cash": 100000 - 41.0 + 20.0, "open": [opened], "closed": [won, lost]}

    def test_summary_numbers(self):
        s = dashboard.summarize(POLICY, books(self.pf()), [], {}, "2026-09-27T00:00:00Z")
        self.assertEqual((s["equity"], s["open_cost"], s["realized"]), (100020.0, 41.0, 20.0))
        self.assertEqual((s["wins"], s["settled"]), (1, 2))
        self.assertAlmostEqual(s["roi_settled"], 20.0 / 80.0)
        # curve: start, then each settlement oldest first, then now
        self.assertEqual([p["equity"] for p in s["curve"]], [100000, 99970.0, 100020.0, 100020.0])
        self.assertEqual(s["by_source"], {"kalshi": 41.0})
        self.assertEqual([c["question"] for c in s["closed"]], ["Won one", "Lost one"])  # newest first
        # the page's lifetime record: wins and losses counted, and the money won and lost kept apart
        main = next(r for r in s["strategies"] if r["name"] == "main")
        self.assertEqual((main["wins"], main["losses"], main["won_amt"], main["lost_amt"], main["realized"]),
                         (1, 1, 50.0, -30.0, 20.0))
        self.assertEqual(s["research_per_day"], POLICY["research"]["max_research_per_day"])

    def test_empty_portfolio(self):
        s = dashboard.summarize(POLICY, books(fresh_pf()), [], {}, "2026-09-27T01:00:00Z")
        self.assertEqual((s["equity"], s["settled"], s["roi_settled"], s["last_scan"]), (100000.0, 0, None, None))
        html = dashboard.build_html(s)
        self.assertNotIn("__DASHBOARD_DATA__", html)

    def test_market_text_cannot_break_out_of_the_page(self):
        pf = self.pf()
        evil = "</script><script>alert(1)</script>"
        pf["open"][0]["question"] = evil
        html = dashboard.build_html(dashboard.summarize(POLICY, books(pf), [], {}, "2026-09-27T00:00:00Z"))
        self.assertNotIn(evil, html)
        blob = html.split('<script type="application/json" id="data">', 1)[1].split("</script>", 1)[0]
        self.assertEqual(json.loads(blob)["open"][0]["question"], evil)  # still shown, as plain text

    def test_last_scan_counts_gates(self):
        j = {"ts": "2026-09-27T03:50:00Z", "market": {"source": "kalshi"},
             "decision": {"bet": False, "info_sufficient": 0.2, "rules_clear": 0.5, "edge": 0.3}}
        ls = dashboard.last_scan(POLICY, [dict(j, ts="2026-09-26T03:00:00Z"), j])
        self.assertEqual((ls["date"], ls["judged"], ls["fail_info"], ls["fail_rules"], ls["fail_edge"]),
                         ("2026-09-27", 1, 1, 1, 0))

    def test_last_scan_counts_only_the_latest_scan(self):
        old = {"ts": "2026-09-27T03:50:00Z", "question_set": "papertrade-v1", "market": {"source": "kalshi"},
               "decision": {"bet": False}}
        new = dict(old, ts="2026-09-27T07:25:00Z", question_set=review.QUESTION_SET_VERSION)
        ls = dashboard.last_scan(POLICY, [old] * 32 + [new] * 29)
        self.assertEqual(ls["judged"], 29)

    def test_forecasters_are_scored_head_to_head_on_the_same_markets(self):
        def look(key, ts, plain=0.5, rich=0.7, direct=0.8, mid=0.6, qs=review.QUESTION_SET_VERSION, asks=(0.61, 0.41)):
            ans = lambda p: {"p_yes": {"noul": p}} if p is not None else None
            return {"key": key, "ts": ts, "question_set": qs, "market": {"mid": mid, "yes_ask": asks[0], "no_ask": asks[1]},
                    "answers_no_news": ans(plain), "answers": ans(rich),
                    "claude_direct": {"p_yes": direct} if direct is not None else None}
        js = [look("a", "1", plain=0.1),          # superseded by a's later look
              look("a", "2"),                     # a: all four, latest -> counted
              look("b", "1", direct=None),        # b: Claude never forecast it -> b left out for everyone
              look("c", "1", mid=0.9, qs="papertrade-v1"),  # old wording -> left out
              look("d", "1"),                     # d: not resolved -> left out
              look("e", "1", asks=(0.99, 0.92)),  # e: no bids, a fake mid -> left out, and counted as such
              look("f", "1", asks=(0.99, 0.92)), look("f", "2")]  # f: its latest real-priced look counts
        res = {"a": "yes", "b": "no", "c": "yes", "e": "yes", "f": "yes"}
        pr = engine.paired(js, res)
        self.assertEqual((pr["n"], pr["left_out"]), (2, 1))
        got = {s["name"]: round(s["brier"], 4) for s in pr["sources"]}  # a and f score the same: 4 identical looks
        self.assertEqual(got, {"jev_plain": 0.25, "jev_research": 0.09, "claude_direct": 0.04, "market": 0.16})
        cal = engine.calibration(js, res)  # what the page and the daily review read
        self.assertEqual(cal["paired"], pr)
        # the per-source scores still cover each source's own markets, wide spreads included (a, b, e, f for Jev alone)
        self.assertEqual(next(x for x in cal["sources"] if x["name"] == "jev_plain")["n"], 4)
        s = dashboard.summarize(POLICY, books(self.pf()), [], {}, "2026-09-27T00:00:00Z")
        self.assertEqual(s["calibration"]["paired"], {"n": 0, "left_out": 0, "sources": [{"name": n, "label": l, "brier": None}
                         for n, l in (("market", "Market price"), ("jev_research", "Jev + research"),
                                      ("claude_direct", "Claude direct"), ("jev_plain", "Jev alone"))]})
        self.assertIn('id="p-score"', dashboard.build_html(s))

    def test_plan_usage_comes_from_the_latest_report(self):
        rate = {"unifiedWindows": {"seven_day": {"utilization": 0.4, "resetsAt": 1}, "five_hour": {"utilization": 0.2}}}
        u = dashboard.plan_usage([{"ts": "a", "claude": {"rate": rate}}, {"ts": "b", "kind": "review"}])
        self.assertEqual((u["week"], u["five_hour"]), (0.4, 0.2))


class IntradayTests(DataDirTest):
    def test_due_after_time_or_a_price_move(self):
        m = dict(market(mid="1", m=0.40))
        seen = {"polymarket:1": ("2000-01-01T06:00:00Z", 0.40, frozenset({"main"}))}
        self.assertTrue(engine.due(m, {}, "2000-01-01T00:00:00Z", 0.05))                      # never judged
        self.assertFalse(engine.due(m, seen, "2000-01-01T00:00:00Z", 0.05))                   # recent, same price
        self.assertTrue(engine.due(m, seen, "2000-01-01T07:00:00Z", 0.05))                    # older than the window
        self.assertTrue(engine.due(dict(m, mid=0.46), seen, "2000-01-01T00:00:00Z", 0.05))    # price moved 6 points
        self.assertFalse(engine.due(m, seen, "2000-01-01T00:00:00Z", 0.05, ["main"]))         # every strategy has decided
        self.assertTrue(engine.due(m, seen, "2000-01-01T00:00:00Z", 0.05, ["main", "bold"]))  # a new strategy gets a look


class FakeAnalyst:
    def __init__(self):
        self.cases, self.wins = [], []

    def explain_win(self, case):
        self.wins.append(case)
        return {"root_cause": "research_found_it", "what_happened": "It happened.", "what_worked": "The standings.",
                "lesson": "Read the standings early.", "suggested_change": {"area": "none", "change": ""},
                "meta": {"api_equivalent_usd": 0.1}, "kind": "win"}

    def explain(self, case):
        self.cases.append(case)
        return {"root_cause": "missing_info", "what_happened": "It happened.", "what_we_missed": "The standings.",
                "lesson": "Read the standings.", "suggested_change": {"area": "research", "change": "Read the table."},
                "meta": {"api_equivalent_usd": 0.2}}


class ReviewTests(DataDirTest):
    def judged(self, mid, p, plain=0.5, direct=0.5, researched=True):
        m = dict(market(mid=mid, m=0.60), url="https://kalshi.com/markets/x")
        engine.append_jsonl(engine.JUDGMENTS, {"ts": "1999-12-25T00:00:00Z", "key": f"polymarket:{mid}", "question_set": review.QUESTION_SET_VERSION,
                                               "market": m, "recent_facts": [fact("A.")] if researched else None,
                                               "answers": ans(p) if researched else None,
                                               "answers_no_news": ans(plain), "claude_direct": {"p_yes": direct} if researched else None})

    def test_scores_every_resolved_market_once_and_explains_misses(self):
        self.judged("1", 0.90)   # resolves NO: confidently wrong -> post-mortem
        self.judged("2", 0.70)   # resolves YES: fine -> scored only
        self.judged("3", 0.50)   # unresolved -> not reviewed yet
        self.judged("4", 0.50, researched=False)  # resolved, never researched -> scored on Jev alone, no post-mortem
        engine.save_json(engine.RESOLUTIONS, {"polymarket:1": "no", "polymarket:2": "yes", "polymarket:4": "no"})
        analyst = FakeAnalyst()
        s = review.review(POLICY, analyst=analyst, log=lambda *_: None, now_stamp="1999-12-26T00:00:00Z")
        self.assertEqual((s["reviewed"], s["post_mortems"], s["api_equivalent_usd"]), (3, 1, 0.2))
        self.assertEqual(analyst.cases[0]["actual_outcome"], "no")
        rows = {r["key"]: r for r in engine.read_jsonl(engine.REVIEWS)}
        self.assertEqual(rows["polymarket:1"]["errors"]["jev_research"], 0.9)
        self.assertIsNone(rows["polymarket:2"]["post_mortem"])
        self.assertNotIn("jev_research", rows["polymarket:4"]["errors"])
        self.assertEqual(review.review(POLICY, analyst=analyst, log=lambda *_: None)["reviewed"], 0)  # once only

        L = review.learning(engine.read_jsonl(engine.REVIEWS))
        self.assertEqual((L["reviewed"], L["post_mortems"], L["root_causes"], L["proposals"]),
                         (3, 1, {"missing_info": 1}, {"research": 1}))
        self.assertEqual(L["recent"][0]["lesson"], "Read the standings.")

    def test_wins_get_a_why_were_we_right_review(self):
        self.judged("1", 0.90)  # market said 60%, Jev with research said 90%, it resolved YES
        self.judged("2", 0.65)  # right, but not by a wide margin over the market: scored only
        engine.save_json(engine.RESOLUTIONS, {"polymarket:1": "yes", "polymarket:2": "yes"})
        analyst = FakeAnalyst()
        s = review.review(POLICY, analyst=analyst, log=lambda *_: None, now_stamp="1999-12-26T00:00:00Z")
        self.assertEqual((s["reviewed"], s["post_mortems"], s["win_reviews"]), (2, 0, 1))
        L = review.learning(engine.read_jsonl(engine.REVIEWS))
        self.assertEqual((L["win_reviews"], L["credits"]), (1, {"research_found_it": 1}))
        self.assertEqual(L["recent_wins"][0]["what_worked"], "The standings.")

    def test_a_losing_bet_by_any_strategy_gets_a_postmortem(self):
        self.judged("1", 0.55)  # not confidently wrong...
        engine.save_portfolio("bold", dict(fresh_pf(), closed=[{"key": "polymarket:1", "pnl": -40.0}]))
        engine.save_json(engine.RESOLUTIONS, {"polymarket:1": "no"})
        analyst = FakeAnalyst()
        s = review.review(POLICY, analyst=analyst, log=lambda *_: None, now_stamp="1999-12-26T00:00:00Z")
        self.assertEqual(s["post_mortems"], 1)  # ...but the bold strategy lost money on it
        self.assertEqual(analyst.cases[0]["bets_by_strategy"], {"bold": -40.0})

    def test_postmortems_have_a_daily_cap(self):
        for i in range(8):
            self.judged(str(i), 0.95)
        engine.save_json(engine.RESOLUTIONS, {f"polymarket:{i}": "no" for i in range(8)})
        s = review.review(POLICY, analyst=FakeAnalyst(), log=lambda *_: None, now_stamp="1999-12-26T00:00:00Z")
        self.assertEqual((s["reviewed"], s["post_mortems"]), (8, POLICY["review"]["max_postmortems_per_day"]))

    def test_postmortem_parses_and_rejects_bad_replies(self):
        good = {"root_cause": "overconfident", "what_happened": "x", "what_we_missed": "", "lesson": "y",
                "suggested_change": {"area": "gates", "change": "z"}}
        replies = iter([stream(json.dumps(good)), stream('{"root_cause": "vibes"}')])
        cc = news.ClaudeCode(POLICY["research"], runner=lambda *a: (0, next(replies), ""))
        pm = review.PostMortem(POLICY["research"], POLICY["review"], cc)
        out = pm.explain({"question": "Q"})
        self.assertEqual((out["root_cause"], out["suggested_change"]["area"]), ("overconfident", "gates"))
        with self.assertRaises(news.NewsError):
            pm.explain({"question": "Q"})


class LearnTests(DataDirTest):
    def test_categories(self):
        cases = {"Will Bitcoin reach $90,000 in September?": "crypto", "San Antonio wins": "sports",
                 "Will Lula win the 2026 Brazilian presidential election?": "politics",
                 "Sense and Sensibility Rotten Tomatoes score? (Above 70)": "culture",
                 "Saudi Oil Pipeline (East-West) restarts by October 15?": "world", "Will Pluto be a planet?": "other"}
        self.assertEqual({q: learn.category({"question": q}) for q in cases}, cases)

    def test_calibration_recovers_overconfidence(self):
        rng, pairs = random.Random(7), []
        for _ in range(3000):  # Jev says p, but the truth is only half as extreme (a = 0.5)
            p = rng.uniform(0.05, 0.95)
            pairs.append((p, 1.0 if rng.random() < learn._sigmoid(0.5 * learn._logit(p)) else 0.0))
        fit = learn.fit_calibration(pairs, prior=5)
        self.assertAlmostEqual(fit["a"], 0.5, delta=0.1)
        self.assertAlmostEqual(fit["b"], 0.0, delta=0.1)
        self.assertEqual(learn.fit_calibration([], prior=5), {"a": 1.0, "b": 0.0, "n": 0})  # nothing learned: identity

    def test_gate_ledger_scores_what_each_gate_stopped(self):
        def j(k, ts, d):
            return {"ts": ts, "key": k, "question_set": review.QUESTION_SET_VERSION, "decisions": {"main": d}}
        js = [j("a", "t1", {"bet": True, "side": "yes", "cost": 0.40, "edge": 0.2, "reasons": ["BET"]}),
              j("b", "t1", {"bet": False, "side": "no", "cost": 0.50, "edge": 0.1, "reasons": ["needs recent info (0.2 < 0.5)"]}),
              j("b", "t2", {"bet": False, "side": "no", "cost": 0.20, "edge": 0.3, "reasons": ["needs recent info (0.2 < 0.5)"]}),
              j("c", "t1", {"bet": False, "side": "yes", "cost": 0.50, "edge": 0.02, "reasons": ["edge"]}),  # no edge: not counted
              j("d", "t1", {"bet": False, "side": "yes", "cost": 0.50, "edge": 0.1,
                            "reasons": ["rules_clear 0.5 < 0.75", "needs recent info (0.2 < 0.5)"]})]
        led = learn.gate_ledger(POLICY, js, {"a": "yes", "b": "yes", "c": "yes", "d": "no"}, {"main": POLICY})
        rows = {r["group"]: r for r in led["main"]}
        self.assertEqual(rows["bet"]["pnl_per_100"], 150.0)          # $100 at 40c on a YES that came in
        self.assertEqual((rows["info"]["n"], rows["info"]["pnl_per_100"]), (1, -100.0))  # first sight: NO at 50c, lost
        self.assertEqual((rows["several"]["n"], rows["several"]["wins"]), (1, 0))
        self.assertNotIn("c", [r["group"] for r in led["main"]])


class FakeCoach:
    def __init__(self, rules, changes=("added R1",)):
        self.rules, self.changes, self.seen = rules, list(changes), []

    def propose(self, playbook, reviews, max_rules):
        self.seen.append([r["key"] for r in reviews])
        return {"rules": self.rules, "changes": self.changes, "meta": {"api_equivalent_usd": 0.3}}


class FakeRetro:
    def __init__(self, proposals):
        self.proposals, self.numbers = proposals, None

    def write(self, numbers, bounds):
        self.numbers = numbers
        return {"headline": "A quiet week.", "went_well": ["x"], "went_badly": ["y"], "proposals": self.proposals,
                "meta": {"api_equivalent_usd": 0.4}}


def reviewed(key, kind="miss", ts="1999-12-26T00:00:00Z"):
    return {"key": key, "ts": ts, "question": key, "outcome": "no", "category": "sports",
            "probs": {"jev_research": 0.9, "market": 0.5}, "post_mortem": {
                "kind": kind, "root_cause": "missing_info", "what_happened": "h", "what_we_missed": "m",
                "lesson": "l", "suggested_change": {"area": "research", "change": "c"}}}


class CoachTests(DataDirTest):
    DAY1 = datetime(1999, 12, 26, 12, tzinfo=timezone.utc)

    def test_coach_checks_every_rule_in_code_and_versions_the_playbook(self):
        for k in ("a", "b", "c"):
            engine.append_jsonl(engine.REVIEWS, reviewed(k))
        good = {"id": "new", "category": "sports", "rule": "Read the league's official standings table before anything else.",
                "evidence": ["a"]}
        bad = [dict(good, rule="Check the betting odds at the big sportsbooks before anything else."),   # the screen
               dict(good, rule="Read what the forecast models say about who will win the title."),     # a forecast
               dict(good, rule="Read the league's official injury report before anything else.", evidence=["zzz"]),  # no such review
               dict(good, rule="Read the league's official injury report, " + "and more " * 40),        # too long
               dict(good, category="astrology", rule="Read the official schedule before anything else.")]
        c = coach.coach(POLICY, coach_=FakeCoach([good] + bad), log=lambda *_: None, now=self.DAY1)
        self.assertEqual((c["ran"], c["version"], c["added"], c["dropped"]), (True, 1, 1, 5))
        pb = coach.load_playbook()
        self.assertEqual([(r["id"], r["rule"]) for r in pb["rules"]], [("R1", good["rule"])])
        hist = engine.read_jsonl(engine.PLAYBOOK_LOG)[-1]
        self.assertEqual(len(hist["dropped"]), 5)
        self.assertIn("names a prediction market or sportsbook", {d["reason"] for d in hist["dropped"]})
        # the same day: not again; the next day with no new reviews: not again
        f2 = FakeCoach([good])
        self.assertFalse(coach.coach(POLICY, coach_=f2, log=lambda *_: None, now=self.DAY1)["ran"])
        self.assertFalse(coach.coach(POLICY, coach_=f2, log=lambda *_: None, now=self.DAY1 + timedelta(days=1))["ran"])
        # three more reviews: R1 is sharpened (keeps its id), one rule is added, nothing it saw is re-used
        for k in ("d", "e", "f"):
            engine.append_jsonl(engine.REVIEWS, reviewed(k, kind="win"))
        sharper = dict(good, id="R1", rule="Read the league's official standings table, and check its update time.", evidence=["d"])
        added = dict(good, rule="For a player's next team, read the team's official transactions page.", evidence=["e"])
        f3 = FakeCoach([sharper, added])
        c = coach.coach(POLICY, coach_=f3, log=lambda *_: None, now=self.DAY1 + timedelta(days=2))
        self.assertEqual((c["version"], c["revised"], c["added"]), (2, 1, 1))
        self.assertEqual(f3.seen, [["d", "e", "f"]])
        self.assertEqual([r["id"] for r in coach.load_playbook()["rules"]], ["R1", "R2"])

    def test_a_failed_coach_waits_a_day_instead_of_retrying_hourly(self):
        for k in ("a", "b", "c"):
            engine.append_jsonl(engine.REVIEWS, reviewed(k))

        class Broken:
            calls = 0

            def propose(self, *a):
                Broken.calls += 1
                raise news.NewsError("bad reply")
        coach.coach(POLICY, coach_=Broken(), log=lambda *_: None, now=self.DAY1)
        coach.coach(POLICY, coach_=Broken(), log=lambda *_: None, now=self.DAY1 + timedelta(hours=1))
        self.assertEqual(Broken.calls, 1)


class RetroTests(DataDirTest):
    NOW = datetime(1999, 12, 27, tzinfo=timezone.utc)
    GOOD = {"title": "Lower edge bar", "why": "w", "kind": "challenger", "judge_by": "Brier after 50", "min_resolved": 50,
            "strategy": {"label": "Edge 6", "probability": "jev_research", "gates": "jev_research",
                         "gate_overrides": {"min_edge": 0.06}}}
    BAD = dict(GOOD, title="No fees", strategy=dict(GOOD["strategy"], rules={"slippage": 0.0}))

    def setUp(self):
        super().setUp()
        for i in range(POLICY["learning"]["retro_min_reviews"]):
            engine.append_jsonl(engine.REVIEWS, reviewed(f"k{i}"))

    def test_with_auto_start_off_nothing_starts_until_approved(self):
        off = dict(POLICY, learning=dict(POLICY["learning"], auto_start_challengers=False))
        w = FakeRetro([self.GOOD, self.BAD] + [dict(self.GOOD, title=t) for t in ("third", "fourth", "fifth")])
        r = coach.retro(off, writer=w, log=lambda *_: None, now=self.NOW)
        self.assertEqual((r["ran"], r["proposals"]), (True, POLICY["learning"]["max_proposals_per_retro"]))  # 4 a day
        props = {p["title"]: p for p in coach.load_proposals()["proposals"]}
        self.assertNotIn("fifth", props)
        self.assertEqual(props["Lower edge bar"]["status"], "proposed")
        self.assertEqual(props["No fees"]["status"], "invalid")
        self.assertNotIn(props["Lower edge bar"]["id"], engine.strategies(POLICY))
        self.assertIn("gate_ledger", w.numbers)  # Claude interprets numbers computed in code
        every = timedelta(days=POLICY["learning"]["retro_every_days"])  # twice a day since 2026-10-01
        self.assertFalse(coach.retro(off, writer=w, log=lambda *_: None, now=self.NOW + every / 2)["ran"])
        self.assertTrue(coach.retro(off, writer=FakeRetro([]), log=lambda *_: None, now=self.NOW + every)["ran"])
        # Joey approves: it runs as its own strategy from the next cycle
        pid = props["Lower edge bar"]["id"]
        self.assertIn("running", coach.set_status(pid, "running", off))
        self.assertIn(pid, engine.strategies(off))
        self.assertIn("Can't start", coach.set_status(props["No fees"]["id"], "running", off))

    def test_challengers_start_by_themselves_but_only_within_bounds_and_slots(self):
        self.assertTrue(POLICY["learning"]["auto_start_challengers"])  # Joey's choice, 2026-09-27
        coach.retro(POLICY, writer=FakeRetro([self.GOOD, self.BAD]), log=lambda *_: None, now=self.NOW)
        status = {p["title"]: p["status"] for p in coach.load_proposals()["proposals"]}
        self.assertEqual(status, {"Lower edge bar": "running", "No fees": "invalid"})
        self.assertIn(next(p["id"] for p in coach.load_proposals()["proposals"] if p["status"] == "running"),
                      engine.strategies(POLICY))
        # a week later, more valid challengers than free slots: the extra one waits
        two = [dict(self.GOOD, title="A", strategy=dict(self.GOOD["strategy"], label="Edge 7", gate_overrides={"min_edge": 0.07})),
               dict(self.GOOD, title="B", strategy=dict(self.GOOD["strategy"], label="Edge 10", gate_overrides={"min_edge": 0.10}))]
        coach.retro(POLICY, writer=FakeRetro(two), log=lambda *_: None, now=self.NOW + timedelta(days=8))
        status = {p["title"]: p["status"] for p in coach.load_proposals()["proposals"]}
        self.assertEqual((status["A"], status["B"]), ("running", "proposed"))
        self.assertIn("free slot", next(p for p in coach.load_proposals()["proposals"] if p["title"] == "B")["status_reason"])


class TuningTests(DataDirTest):
    """The daily review may change any strategy's rules by itself (Joey, 2026-09-28), inside checks made in code."""
    NOW = datetime(1999, 12, 27, tzinfo=timezone.utc)
    TUNE = {"kind": "tune", "strategy": "main", "rules": {"min_edge": 0.05, "max_stake_pct": 0.03}, "title": "Looser main",
            "why": "w", "judge_by": "P&L vs original after 30 settled", "min_resolved": 30}

    def setUp(self):
        super().setUp()
        for i in range(POLICY["learning"]["retro_min_reviews"]):
            engine.append_jsonl(engine.REVIEWS, reviewed(f"k{i}"))

    def retro(self, proposals, policy=POLICY, days=0):
        return coach.retro(policy, writer=FakeRetro(proposals), log=lambda *_: None, now=self.NOW + timedelta(days=days))

    def test_only_the_rules_the_loop_owns_pass_and_every_bad_spelling_is_refused(self):
        good = [{"min_edge": 0}, {"min_edge": 0.5}, {"kelly_fraction": 0.5}, {"max_stake_pct": 0.03, "max_total_exposure_pct": 0.5},
                {"skip_categories": ["crypto", "weather"]}, {"skip_categories": []}, {"min_ask": 0.1, "max_ask": 0.9},
                {"min_edge": None}, {"min_rules_clear": 0.0, "min_info_sufficient": 1.0, "max_framing_gap": 1.0}]
        for r in good:  # the control: each check below fails for its own reason, not because nothing passes
            self.assertIsNone(learn.rules_problem(r, POLICY), r)
        bad = [{"fees": 0}, {"slippage": 0.0}, {"kalshi_taker_coef": 0}, {"polymarket_default_rate": 0},
               {"max_research_per_day": 500}, {"probability": "claude_direct"}, {"gates": "jev_plain"},
               {"starting_bankroll": 1e9}, {"_min_edge": 0.0}, {"MIN_EDGE": 0.1}, {" min_edge": 0.1},
               {"min_edge": True}, {"min_edge": "0.1"}, {"min_edge": float("nan")}, {"min_edge": float("inf")},
               {"min_edge": -0.01}, {"min_edge": 0.51}, {"kelly_fraction": 1.5}, {"max_stake_pct": -0.1},
               {"max_total_exposure_pct": 1.01}, {"min_ask": 0}, {"max_ask": 1.0}, {"min_ask": 0.6, "max_ask": 0.4},
               {"kelly_fraction": 0.51}, {"max_stake_pct": 0.031}, {"max_total_exposure_pct": 0.51},  # the 2026-10-09 caps
               {"skip_categories": "crypto"}, {"skip_categories": ["astrology"]}, {"skip_categories": [1]},
               {"min_edge": [0.1]}, {"min_edge": {"v": 0.1}}]
        for r in bad:
            self.assertIsNotNone(learn.rules_problem(r, POLICY), r)
        for r in ([("min_edge", 0.1)], "min_edge=0.1", None, 7):
            self.assertIsNotNone(learn.rules_problem(r, POLICY), r)

    def test_the_review_tunes_main_by_itself_and_the_new_rules_bet(self):
        r = self.retro([self.TUNE])
        self.assertEqual((r["ran"], r["tuned"]), (True, ["main"]))
        p = coach.load_proposals()["proposals"][-1]
        self.assertEqual((p["kind"], p["status"]), ("tune", "applied"))
        self.assertIn("main rules v2: edge bar 8% → 5%; max bet 2% → 3%", p["status_reason"])
        s = engine.strategies(POLICY)
        self.assertEqual((s["main"]["rules_version"], s["main"]["tuned"]), (2, self.TUNE["rules"]))
        main, orig = engine.strategy_policy(POLICY, s["main"]), engine.strategy_policy(POLICY, s["original"])
        self.assertEqual((main["gates"]["min_edge"], main["sizing"]["max_stake_pct"]), (0.05, 0.03))
        self.assertIs(orig, POLICY)  # the yardstick is untouched
        self.assertEqual(main["fees"], POLICY["fees"])
        # an edge of 0.06: tuned main bets, the original rules don't
        self.assertTrue(engine.decide(market(), ans(0.47), main, 100000, 0, 100000)["bet"])
        self.assertFalse(engine.decide(market(), ans(0.47), orig, 100000, 0, 100000)["bet"])
        # a big edge: main's bet is capped at 3% of equity instead of 2%
        big, small = (engine.decide(market(), ans(0.6), pol, 100000, 0, 100000) for pol in (main, orig))
        self.assertEqual((round(big["total_cost"], -1), round(small["total_cost"], -1)), (3000, 2000))
        c = engine.read_jsonl(engine.TUNED_LOG)[-1]
        self.assertEqual((c["strategy"], c["version"], c["by"]), ("main", 2, "the daily review"))
        self.assertEqual(c["changed"], {"min_edge": [0.08, 0.05], "max_stake_pct": [0.02, 0.03]})
        self.assertEqual(c["judge_by"], self.TUNE["judge_by"])
        # the next review sees main's new rules, when it may next change, and its record since the change
        nums = coach.week_numbers(POLICY, self.NOW + timedelta(hours=12))
        m = next(x for x in nums["strategies"] if x["name"] == "main")
        self.assertEqual((m["rules_version"], m["rules"]["min_edge"], m["starting_rules"]["min_edge"]), (2, 0.05, 0.08))
        self.assertEqual(m["can_change_from"], "2000-01-03T00:00:00Z")  # min_days_between_changes: 7
        self.assertEqual(m["since_change"]["bets"], 0)
        self.assertTrue(next(x for x in nums["strategies"] if x["name"] == "original")["frozen"])
        self.assertEqual(nums["recent_rule_changes"][-1]["strategy"], "main")

    def test_too_soon_frozen_unknown_and_out_of_range_changes_are_refused(self):
        now = self.NOW
        self.assertEqual(coach.tune(POLICY, "original", {"min_edge": 0.05}, now)[0], "invalid")
        self.assertEqual(coach.tune(POLICY, "nope", {"min_edge": 0.05}, now)[0], "invalid")
        self.assertEqual(coach.tune(POLICY, "main", {"slippage": 0.0}, now)[0], "invalid")
        self.assertEqual(coach.tune(POLICY, "main", {}, now)[0], "invalid")
        self.assertEqual(coach.tune(POLICY, "main", {"min_edge": 0.08}, now), ("skipped", "changes nothing"))
        self.assertEqual(coach.tune(POLICY, "main", {"min_edge": 0.06}, now)[0], "applied")  # control
        st, why = coach.tune(POLICY, "main", {"min_edge": 0.07}, now + timedelta(hours=12))
        self.assertEqual(st, "skipped")
        self.assertIn("next change is allowed from 2000-01-03", why)
        self.assertEqual(coach.tune(POLICY, "main", {"min_edge": 0.07}, now + timedelta(days=6))[0], "skipped")
        self.assertEqual(coach.tune(POLICY, "main", {"min_edge": 0.07}, now + timedelta(days=8))[0], "applied")
        self.assertEqual(engine.strategies(POLICY)["main"]["rules_version"], 3)
        self.assertEqual(engine.strategies(POLICY)["main"]["tuned"], {"min_edge": 0.07})
        # null puts a rule back to the strategy's own starting value: Bold's info bar returns to 0.2, not 0.5
        self.assertEqual(coach.tune(POLICY, "bold", {"min_info_sufficient": 0.4}, now)[0], "applied")
        self.assertEqual(coach.tune(POLICY, "bold", {"min_info_sufficient": None}, now + timedelta(days=8))[0], "applied")
        bold = engine.strategies(POLICY)["bold"]
        self.assertEqual(engine.strategy_policy(POLICY, bold)["gates"]["min_info_sufficient"], 0.2)
        self.assertEqual(bold["rules_version"], 3)

    def test_hand_edits_to_the_rules_file_are_checked_on_every_load(self):
        engine.save_json(engine.TUNED, {"strategies": {
            "original": {"version": 2, "rules": {"min_edge": 0.0}},           # the frozen yardstick
            "main": {"version": 2, "rules": {"slippage": 0.0}},               # not a rule the loop owns
            "sharp": {"version": True, "rules": {"min_edge": 0.05}},          # a bool is not a version
            "claude_direct": {"version": 2, "rules": {"min_edge": None}},     # stored values are never null
            "calibrated": {"version": 2, "rules": {"min_ask": 0.9, "max_ask": 0.2}},
            "bold": {"version": 2, "rules": {"min_edge": 0.05}, "since": "1999-12-01T00:00:00Z"}}})  # the control
        s = engine.strategies(POLICY)
        for name in ("original", "main", "sharp", "claude_direct", "calibrated"):
            self.assertEqual((s[name]["rules_version"], s[name].get("tuned")), (1, None), name)
        self.assertEqual((s["bold"]["rules_version"], s["bold"]["tuned"]), (2, {"min_edge": 0.05}))
        engine.save_json(engine.TUNED, {"strategies": ["not", "a", "dict"]})
        self.assertEqual(engine.strategies(POLICY)["bold"]["rules_version"], 1)

    def test_with_auto_tune_off_a_change_waits_for_joey(self):
        off = dict(POLICY, learning=dict(POLICY["learning"], auto_tune=False))
        self.retro([self.TUNE, dict(self.TUNE, strategy="original")], policy=off)
        tune, frozen = coach.load_proposals()["proposals"][-2:]
        self.assertEqual((tune["status"], frozen["status"]), ("proposed", "invalid"))
        self.assertEqual(engine.strategies(off)["main"]["rules_version"], 1)
        self.assertIn("applied", coach.set_status(tune["id"], "running", off, now=self.NOW))
        self.assertEqual(engine.strategies(off)["main"]["rules_version"], 2)
        self.assertIn("only a proposed rule change", coach.set_status(tune["id"], "running", off, now=self.NOW))
        self.assertIn("already applied", coach.set_status(tune["id"], "rejected", off, now=self.NOW))

    def test_code_ideas_wait_for_joey_and_show_on_the_page(self):
        idea = {"kind": "code", "title": "Add a sportsbook source", "why": "Sports are half our bets"}
        self.retro([idea, dict(idea, title="Second idea")])
        a, b = coach.load_proposals()["proposals"][-2:]
        self.assertEqual((a["status"], a["status_reason"]), ("proposed", "waiting for Joey"))
        self.assertFalse(engine.TUNED.exists())  # an idea changes nothing by itself
        s = dashboard.summarize(POLICY, books(fresh_pf()), [], {}, "2000-01-01T00:00:00Z")
        self.assertEqual([i["title"] for i in s["learning"]["ideas_for_joey"]], ["Add a sportsbook source", "Second idea"])
        self.assertIn(("idea", "Add a sportsbook source"), [(e["type"], e.get("text")) for e in s["feed"]])
        coach.set_status(a["id"], "running", POLICY, now=self.NOW)
        self.assertIn("needs a code session", {x["id"]: x for x in coach.load_proposals()["proposals"]}[a["id"]]["status_reason"])
        coach.set_status(b["id"], "rejected", POLICY, now=self.NOW)
        s = dashboard.summarize(POLICY, books(fresh_pf()), [], {}, "2000-01-01T00:00:00Z")
        self.assertEqual(s["learning"]["ideas_for_joey"], [])
        self.assertEqual({e["text"]: e["status"] for e in s["feed"] if e["type"] == "idea"},
                         {"Add a sportsbook source": "approved", "Second idea": "rejected"})  # the page shows the decision

    def test_the_page_shows_each_change_and_main_s_tuned_limits(self):
        self.retro([dict(self.TUNE, rules={"max_total_exposure_pct": 0.4, "max_stake_pct": 0.03})])
        s = dashboard.summarize(POLICY, books(fresh_pf()), [], {}, "2000-01-01T00:00:00Z")
        self.assertEqual((s["exposure_cap_pct"], s["max_stake_pct"]), (0.4, 0.03))
        row = next(r for r in s["strategies"] if r["name"] == "main")
        self.assertEqual((row["rules_version"], row["tuned_at"]), (2, "1999-12-27T00:00:00Z"))
        self.assertTrue(next(r for r in s["strategies"] if r["name"] == "original")["frozen"])
        t = next(e for e in s["feed"] if e["type"] == "tune")
        self.assertEqual((t["strategy"], t["version"], t["text"]), ("main", 2, "max bet 2% → 3%; open-bet limit 50% → 40%"))
        self.assertEqual(s["learning"]["rule_changes"][0]["strategy"], "main")

    def test_a_retired_challenger_stops_betting_but_its_open_bets_still_settle(self):
        engine.save_json(engine.PROPOSALS, {"proposals": [
            {"id": "ch1", "kind": "challenger", "status": "running", "title": "t",
             "strategy": {"label": "Edge 5", "probability": "jev_research", "gates": "jev_research"}}]})
        pf = fresh_pf()
        pf["open"].append({"key": "polymarket:9", "source": "polymarket", "market_id": "9", "question": "Q9", "url": "u",
                           "close_time": "1999-12-01T00:00:00Z", "side": "yes", "contracts": 100, "cost_per": 0.4,
                           "total_cost": 40.0, "p_side": 0.6, "market_ask": 0.39, "edge": 0.2, "opened": "1999-11-30T00:00:00Z"})
        pf["cash"] -= 40.0
        engine.save_portfolio("ch1", pf)
        self.retro([{"kind": "retire", "strategy": "ch1", "why": "losing"}, {"kind": "retire", "strategy": "main", "why": "x"}])
        props = {p["id"]: p for p in coach.load_proposals()["proposals"]}
        self.assertEqual(props["ch1"]["status"], "retired")
        self.assertEqual([p["status"] for p in props.values() if p["kind"] == "retire"], ["applied", "invalid"])
        self.assertNotIn("ch1", engine.strategies(POLICY))
        st = engine.settle(POLICY, resolvers={"polymarket": lambda mid: "yes"}, batch={}, log=lambda *_: None)
        self.assertEqual(st["by_strategy"]["ch1"], 1)
        self.assertEqual(engine.load_portfolio(POLICY, "ch1")["cash"], fresh_pf()["cash"] + 60.0)

    def test_true_false_huge_and_infinite_values_are_refused_by_their_own_checks(self):
        for r in ({"max_stake_pct": True}, {"kelly_fraction": True}, {"max_total_exposure_pct": False},
                  {"min_rules_clear": True}, {"min_edge": 10 ** 400}, {"kelly_fraction": 0.0}, {"max_stake_pct": 0}):
            self.assertIsNotNone(learn.rules_problem(r, POLICY), r)  # true is 1 and 1 is inside these ranges
        wide = dict(POLICY, learning=dict(POLICY["learning"], bounds=dict(
            POLICY["learning"]["bounds"], min_edge=[float("-inf"), float("inf")], slippage=[0, 0.02],
            max_research_per_day=[0, 500])))
        self.assertIsNone(learn.rules_problem({"min_edge": 0.3}, wide))  # control
        for r in ({"min_edge": float("inf")}, {"min_edge": float("nan")}):
            self.assertIn("finite", learn.rules_problem(r, wide), r)  # the range can't catch these here
        for r in ({"slippage": 0.0}, {"max_research_per_day": 500}):  # a range in policy.json doesn't make it a rule
            self.assertIn("isn't a rule", learn.rules_problem(r, wide), r)

    def test_a_challenger_may_not_take_another_strategy_s_name(self):
        base = {"probability": "jev_research", "gates": "jev_research"}
        self.assertIsNone(learn.challenger_problem(dict(base, label="Edge 5"), POLICY))  # control
        for label in ("Original rules", "jev + claude", "MAIN", "Jev + Claude research ", "x" * 61, 7, ["a"], ""):
            self.assertIsNotNone(learn.challenger_problem(dict(base, label=label), POLICY), label)

    def test_a_malformed_proposal_is_marked_invalid_and_the_rest_still_apply(self):
        r = self.retro([dict(self.TUNE, rules={"min_edge": 10 ** 400}), dict(self.TUNE, strategy="bold")])
        self.assertEqual((r["ran"], r["tuned"]), (True, ["bold"]))
        with mock.patch.object(coach, "tune", side_effect=KeyError("boom")):
            r = self.retro([dict(self.TUNE, strategy="calibrated")], days=1)
        self.assertTrue(r["ran"])
        self.assertEqual(coach.load_proposals()["proposals"][-1]["status_reason"], "could not be read: KeyError")

    def test_a_change_that_bets_the_same_way_is_not_a_new_version(self):
        self.assertEqual(coach.tune(POLICY, "main", {"skip_categories": []}, self.NOW), ("skipped", "changes nothing"))
        self.assertEqual(coach.tune(POLICY, "calibrated", {"skip_categories": ["sports", "crypto"]}, self.NOW)[0], "applied")
        self.assertEqual(engine.strategies(POLICY)["calibrated"]["tuned"], {"skip_categories": ["crypto", "sports"]})
        later = self.NOW + timedelta(days=8)
        self.assertEqual(coach.tune(POLICY, "calibrated", {"skip_categories": ["crypto", "sports", "crypto"]}, later),
                         ("skipped", "changes nothing"))
        for retired in ("jev_alone", "jev_alone_bold"):
            self.assertEqual(coach.tune(POLICY, retired, {"min_edge": 0.1}, later)[0], "invalid")  # retired: not tuned

    def test_undoing_a_change_by_hand_never_reuses_a_version_or_skips_the_wait(self):
        self.assertEqual(coach.tune(POLICY, "main", {"min_edge": 0.05}, self.NOW)[0], "applied")
        self.assertEqual(coach.tune(POLICY, "main", {"min_edge": 0.06}, self.NOW + timedelta(days=8))[0], "applied")
        engine.save_json(engine.TUNED, {"strategies": {}})  # the documented undo: main's entry removed
        self.assertEqual(engine.strategies(POLICY)["main"]["rules_version"], 1)
        st, why = coach.tune(POLICY, "main", {"min_edge": 0.03}, self.NOW + timedelta(days=8, hours=12))
        self.assertEqual(st, "skipped")  # the wait runs from the last logged change
        self.assertEqual(coach.tune(POLICY, "main", {"min_edge": 0.03}, self.NOW + timedelta(days=16))[0], "applied")
        self.assertEqual([c["version"] for c in coach.history("main")], [2, 3, 4])

    def test_the_review_judges_current_rules_on_their_own_bets_and_main_against_the_yardstick(self):
        coach.tune(POLICY, "main", {"min_edge": 0.05}, self.NOW)
        bet = {"key": "k", "source": "polymarket", "market_id": "1", "question": "Q", "url": "u", "close_time": "x",
               "side": "yes", "contracts": 10, "cost_per": 0.5, "total_cost": 5.0, "p_side": 0.6, "market_ask": 0.49,
               "edge": 0.1}
        main = fresh_pf()
        main["closed"] = [dict(bet, key="old", opened="1999-12-20T00:00:00Z", rules_version=1, settled="1999-12-21T00:00:00Z", pnl=10.0),
                          dict(bet, key="k2", opened="1999-12-27T01:00:00Z", rules_version=2, settled="1999-12-28T00:00:00Z", pnl=-5.0)]
        main["open"] = [dict(bet, key="k3", opened="1999-12-27T02:00:00Z", rules_version=2),
                        dict(bet, key="held", opened="1999-12-25T00:00:00Z", rules_version=1)]  # held before original began
        engine.save_portfolio("main", main)
        engine.save_portfolio("original", dict(fresh_pf(), created="1999-12-26T00:00:00Z", closed=[
            dict(bet, key="k2", opened="1999-12-27T01:00:00Z", settled="1999-12-28T00:00:00Z", pnl=4.0),
            dict(bet, key="held", opened="1999-12-27T01:00:00Z", settled="1999-12-28T00:00:00Z", pnl=99.0)]))
        nums = coach.week_numbers(POLICY, self.NOW + timedelta(days=1))
        m = next(x for x in nums["strategies"] if x["name"] == "main")
        self.assertEqual((m["all_time"]["bets"], m["all_time"]["pnl"]), (4, 5.0))
        self.assertEqual((m["since_change"]["bets"], m["since_change"]["settled"], m["since_change"]["pnl"]), (2, 1, -5.0))
        y = nums["yardstick"]["original"]
        # no head start for main, and no free pass for original on a market main couldn't bet again
        self.assertEqual((y["main"]["bets"], y["main"]["pnl"], y["original"]["bets"], y["original"]["pnl"]), (2, -5.0, 1, 4.0))
        row = next(r for r in dashboard.strategy_rows(POLICY, engine.all_books(POLICY)) if r["name"] == "original")
        self.assertIn("Since 1999-12-26, on markets both could bet: main -5 on 1 settled bets, this +4 on 1.", row["blurb"])

    def test_the_gate_ledger_scores_each_decision_by_the_edge_bar_it_was_made_under(self):
        from papertrade.judge import QUESTION_SET_VERSION as QSV
        placed = {"bet": True, "edge": 0.09, "min_edge": 0.08, "side": "yes", "cost": 0.5, "reasons": []}
        legacy = {"bet": False, "edge": 0.06, "side": "yes", "cost": 0.5, "reasons": ["edge +0.060 < 0.08"]}
        tuned_bet = dict(placed, edge=0.06, min_edge=0.05)  # placed under a tuned 0.05 bar
        js = [{"question_set": QSV, "key": "a", "decisions": {"main": placed}},
              {"question_set": QSV, "key": "b", "decisions": {"main": legacy}},
              {"question_set": QSV, "key": "c", "decisions": {"main": tuned_bet}}]
        coach.tune(POLICY, "main", {"min_edge": 0.05}, self.NOW)
        coach.tune(POLICY, "main", {"min_edge": 0.12}, self.NOW + timedelta(days=2))
        strats = engine.strategies(POLICY)
        ledger = learn.gate_ledger(POLICY, js, {"a": "yes", "b": "yes", "c": "yes"}, coach.starting_policies(POLICY, strats))
        # both bets count at the bar each was placed under (not today's 0.12, not the starting 0.08); the legacy
        # decision, made before bars were recorded, is judged by the starting bar it was made under
        self.assertEqual([(g["group"], g["n"]) for g in ledger["main"]], [("bet", 2)])
        self.assertEqual(engine.decide(market(), ans(0.6), POLICY, 100000, 0, 100000)["min_edge"], 0.08)

    def test_no_room_says_which_limit_stopped_the_bet(self):
        d = engine.decide(market(), ans(0.6), POLICY, 100000, 50000, 50000)
        self.assertIn("no room: open-bet limit reached", d["reasons"])
        self.assertIn("no room: out of cash", engine.decide(market(), ans(0.6), POLICY, 100000, 0, 0.1)["reasons"])

    def test_a_null_rule_in_a_challenger_means_the_shared_value(self):
        engine.save_json(engine.PROPOSALS, {"proposals": [{"id": "ch1", "kind": "challenger", "status": "running",
            "strategy": {"label": "Nulls", "probability": "jev_research", "gates": "jev_research",
                         "rules": {"min_edge": None}}}]})
        pol = engine.strategy_policy(POLICY, engine.strategies(POLICY)["ch1"])
        self.assertEqual(pol["gates"]["min_edge"], 0.08)
        self.assertTrue(engine.decide(market(), ans(0.6), pol, 100000, 0, 100000)["bet"])

    def test_a_tuned_value_can_t_contradict_a_challenger_s_starting_rules(self):
        engine.save_json(engine.PROPOSALS, {"proposals": [{"id": "ch1", "kind": "challenger", "status": "running",
            "strategy": {"label": "Dear", "probability": "jev_research", "gates": "jev_research", "rules": {"min_ask": 0.6}}}]})
        self.assertEqual(coach.tune(POLICY, "ch1", {"max_ask": 0.8}, self.NOW)[0], "applied")  # control
        self.assertEqual(coach.tune(POLICY, "ch1", {"max_ask": 0.4}, self.NOW + timedelta(days=8)),
                         ("invalid", "min_ask 0.6 is above max_ask 0.4"))
        engine.save_json(engine.TUNED, {"strategies": {"ch1": {"version": 3, "rules": {"max_ask": 0.4}}}})
        self.assertEqual(engine.strategies(POLICY)["ch1"]["rules_version"], 1)  # a hand edit that contradicts is ignored

    def test_retiring_frees_a_slot_and_a_waiting_challenger_takes_it(self):
        ch = lambda i, label: {"id": f"ch{i}", "kind": "challenger", "status": "running", "slot": 6 + i, "started": "x",
                               "strategy": {"label": label, "probability": "jev_research", "gates": "jev_research"}}
        engine.save_json(engine.PROPOSALS, {"proposals": [ch(1, "A"), ch(2, "B"), dict(ch(3, "C"), status="proposed",
                         status_reason="waiting for a free slot (2 challengers already running)", slot=None)]})
        new = {"kind": "challenger", "title": "D", "strategy": {"label": "D", "probability": "jev_plain", "gates": "jev_plain"}}
        self.retro([new, {"kind": "retire", "strategy": "ch1", "why": "losing"}])  # the retire is handled first,
        props = {p["strategy"]["label"]: p for p in coach.load_proposals()["proposals"] if p["kind"] == "challenger"}
        self.assertEqual({k: (p["status"], p.get("slot")) for k, p in props.items()},  # and C, waiting longest, gets it
                         {"A": ("retired", 7), "B": ("running", 8), "C": ("running", 7), "D": ("proposed", None)})
        self.assertIn("free slot", props["D"]["status_reason"])
        self.retro([{"kind": "retire", "strategy": "ch2", "why": "x"}], days=1)  # another slot opens: D starts
        props = {p["strategy"]["label"]: p for p in coach.load_proposals()["proposals"] if p["kind"] == "challenger"}
        self.assertEqual((props["D"]["status"], props["D"]["slot"]), ("running", 8))
        self.retro([dict(new, title="D again")], days=2)  # the same experiment twice is refused
        self.assertIn("already running or waiting", coach.load_proposals()["proposals"][-1]["status_reason"])
        for bad in ("ch3", "ch1", "main"):  # running, already retired, not a challenger
            self.assertEqual(coach._retire(coach.load_proposals(), bad if bad != "ch3" else "nope", "t", "w")[0], "invalid")

    def test_a_retired_challenger_keeps_its_record_on_the_page(self):
        engine.save_json(engine.PROPOSALS, {"proposals": [{"id": "ch1", "kind": "challenger", "status": "running",
            "started": "1999-12-01T00:00:00Z", "slot": 7,
            "strategy": {"label": "Loser", "probability": "jev_research", "gates": "jev_research"}}]})
        pf = fresh_pf()
        pf["closed"] = [{"key": "polymarket:9", "source": "polymarket", "market_id": "9", "question": "Q9", "url": "u",
                         "close_time": "x", "side": "yes", "contracts": 100, "cost_per": 0.4, "total_cost": 40.0,
                         "p_side": 0.6, "market_ask": 0.39, "edge": 0.2, "opened": "1999-12-02T00:00:00Z",
                         "outcome": "no", "payout": 0.0, "pnl": -40.0, "settled": "1999-12-03T00:00:00Z"}]
        pf["cash"] -= 40.0
        engine.save_portfolio("ch1", pf)
        coach.set_status("ch1", "retired", POLICY, now=self.NOW)  # by hand: the same as the review's retire
        ch1 = coach.load_proposals()["proposals"][0]
        self.assertEqual((ch1["status"], ch1["retired"]), ("retired", "1999-12-27T00:00:00Z"))
        self.assertNotIn("ch1", engine.strategies(POLICY))  # it no longer bets
        s = dashboard.current_summary(POLICY)
        row = next(r for r in s["strategies"] if r["name"] == "ch1")
        self.assertEqual((row["badge"], row["slot"], row["realized"], row["losses"]), ("Retired", 0, -40.0, 1))
        self.assertIn(("loss", "ch1"), [(e["type"], e.get("strategy")) for e in s["feed"]])
        self.assertIn("Challenger retired: Loser", [e.get("text") for e in s["feed"]])
        self.assertIn("is retired", coach.set_status("ch1", "retired", POLICY, now=self.NOW))

    def test_joey_s_approve_and_reject_keep_challengers_honest(self):
        ch = lambda i, st, slot: {"id": f"ch{i}", "kind": "challenger", "status": st, "slot": slot, "started": "x",
                                  "status_reason": "waiting for a free slot (2 challengers already running)",
                                  "strategy": {"label": f"C{i}", "probability": "jev_research", "gates": "jev_research"}}
        engine.save_json(engine.PROPOSALS, {"proposals": [ch(1, "running", 7), ch(2, "running", 8), ch(3, "proposed", None)]})
        self.assertIn("already running", coach.set_status("ch1", "running", POLICY, now=self.NOW))
        self.assertIn("retire one first", coach.set_status("ch3", "running", POLICY, now=self.NOW))  # the cap holds by hand too
        coach.set_status("ch1", "rejected", POLICY, now=self.NOW)  # rejecting a running one retires it: nothing hidden
        props = {x["id"]: x for x in coach.load_proposals()["proposals"]}
        self.assertEqual((props["ch1"]["status"], props["ch1"]["slot"]), ("retired", 7))
        self.assertEqual((props["ch3"]["status"], props["ch3"]["slot"]), ("running", 7))  # the waiting one took the slot
        self.assertIn("ch1", engine.strategies(POLICY, retired=True))

    def test_a_retired_challenger_stays_retired_and_names_stay_unique_by_hand_too(self):
        ch = lambda i, st, label: {"id": f"ch{i}", "kind": "challenger", "status": st, "slot": 6 + i, "started": "x",
                                   "retired": "y" if st == "retired" else None, "status_reason": "r",
                                   "strategy": {"label": label, "probability": "jev_research", "gates": "jev_research"}}
        engine.save_json(engine.PROPOSALS, {"proposals": [ch(1, "retired", "Edge 6"), ch(2, "running", "Edge 7"),
                                                          ch(3, "invalid", "edge 7 ")]})
        for verb in ("rejected", "retired", "running"):
            self.assertIn("is retired", coach.set_status("ch1", verb, POLICY, now=self.NOW))
        self.assertEqual(coach.load_proposals()["proposals"][0]["status"], "retired")
        self.assertIn("has that name", coach.set_status("ch3", "running", POLICY, now=self.NOW))

    def test_a_waiting_challenger_goes_before_a_new_one_even_without_a_retire(self):
        three = dict(POLICY, learning=dict(POLICY["learning"], max_running_challengers=3))
        engine.save_json(engine.PROPOSALS, {"proposals": [
            {"id": "ch1", "kind": "challenger", "status": "running", "slot": 7, "started": "x",
             "strategy": {"label": "A", "probability": "jev_research", "gates": "jev_research"}},
            {"id": "ch2", "kind": "challenger", "status": "running", "slot": 8, "started": "x",
             "strategy": {"label": "B", "probability": "jev_research", "gates": "jev_research"}},
            {"id": "ch3", "kind": "challenger", "status": "proposed", "status_reason": "waiting for a free slot (2 running)",
             "strategy": {"label": "C", "probability": "jev_research", "gates": "jev_research"}}]})
        self.retro([{"kind": "challenger", "title": "D", "strategy": {"label": "D", "probability": "jev_plain", "gates": "jev_plain"}}],
                   policy=three)
        status = {p["strategy"]["label"]: p["status"] for p in coach.load_proposals()["proposals"]}
        self.assertEqual((status["C"], status["D"]), ("running", "proposed"))

    def test_joey_s_own_change_skips_the_wait_but_never_the_checks(self):
        self.assertEqual(coach.tune(POLICY, "main", {"min_edge": 0.05}, self.NOW)[0], "applied")
        soon = self.NOW + timedelta(hours=1)
        self.assertEqual(coach.tune(POLICY, "main", {"min_ask": 0.3}, soon)[0], "skipped")  # the loop waits
        self.assertEqual(coach.tune(POLICY, "main", {"min_ask": 0.3}, soon, by="Joey", wait=False)[0], "applied")
        self.assertEqual(coach.tune(POLICY, "original", {"min_ask": 0.3}, soon, wait=False)[0], "invalid")
        self.assertEqual(coach.tune(POLICY, "main", {"slippage": 0}, soon, wait=False)[0], "invalid")
        self.assertEqual(coach.history("main")[-1]["by"], "Joey")

    def test_the_review_sees_results_by_price_paid(self):
        bet = {"key": "k", "source": "polymarket", "market_id": "1", "question": "Q", "url": "u", "close_time": "x",
               "side": "yes", "contracts": 10, "total_cost": 5.0, "p_side": 0.6, "market_ask": 0.49, "edge": 0.1,
               "opened": "1999-12-20T00:00:00Z", "settled": "x"}
        main = dict(fresh_pf(), closed=[dict(bet, cost_per=0.15, pnl=-5.0), dict(bet, cost_per=0.15, pnl=-5.0),
                                        dict(bet, cost_per=0.45, pnl=6.0), dict(bet, cost_per=0.8, pnl=1.0)])
        engine.save_portfolio("main", main)
        m = next(x for x in coach.week_numbers(POLICY, self.NOW)["strategies"] if x["name"] == "main")
        self.assertEqual({k: (v["settled"], v["pnl"]) for k, v in m["by_price_paid"].items()},
                         {"under 30c": (2, -10.0), "30-60c": (1, 6.0), "60c and up": (1, 1.0)})

    def test_an_empty_skip_list_clears_a_starting_one(self):
        engine.save_json(engine.PROPOSALS, {"proposals": [{"id": "ch1", "kind": "challenger", "status": "running", "slot": 7,
            "strategy": {"label": "No sports", "probability": "jev_research", "gates": "jev_research",
                         "rules": {"skip_categories": ["sports"]}}}]})
        game = dict(market(), question="Will France win on 2026-09-28?")
        pol = lambda: engine.strategy_policy(POLICY, engine.strategies(POLICY)["ch1"])
        self.assertFalse(engine.decide(game, ans(0.6), pol(), 100000, 0, 100000)["bet"])
        self.assertEqual(coach.tune(POLICY, "ch1", {"skip_categories": []}, self.NOW)[0], "applied")
        self.assertTrue(engine.decide(game, ans(0.6), pol(), 100000, 0, 100000)["bet"])
        self.assertEqual(coach.tune(POLICY, "ch1", {"skip_categories": None}, self.NOW + timedelta(days=8))[0], "applied")
        self.assertFalse(engine.decide(game, ans(0.6), pol(), 100000, 0, 100000)["bet"])  # null: the starting list again

    def test_the_last_scan_counts_what_that_scan_decided_not_today_s_bars(self):
        d = engine.decide(market(), ans(0.6, info=0.4), POLICY, 100000, 0, 100000)  # stopped by the 0.5 info bar
        j = {"ts": "1999-12-27T00:00:00Z", "market": {"source": "polymarket"}, "decision": d}
        self.assertEqual(dashboard.last_scan(POLICY, [j])["fail_info"], 1)
        coach.tune(POLICY, "main", {"min_info_sufficient": 0.3}, self.NOW)  # tuned after the scan
        self.assertEqual(dashboard.last_scan(POLICY, [j])["fail_info"], 1)

    def test_every_ledger_has_a_row_and_every_running_challenger_a_colour(self):
        engine.save_json(engine.PROPOSALS, {"proposals": [{"id": "ch1", "kind": "challenger", "status": "running",
            "strategy": {"label": "Old one", "probability": "jev_research", "gates": "jev_research"}}]})  # from before slots
        engine.save_portfolio("gone", dict(fresh_pf(), cash=99000.0, closed=[{"key": "z", "source": "polymarket",
            "market_id": "z", "question": "Qz", "url": "u", "close_time": "x", "side": "yes", "contracts": 10, "cost_per": 0.5,
            "total_cost": 1000.0, "p_side": 0.6, "market_ask": 0.49, "edge": 0.1, "opened": "1999-12-01T00:00:00Z",
            "outcome": "no", "payout": 0.0, "pnl": -1000.0, "settled": "1999-12-02T00:00:00Z"}]))
        rows = {r["name"]: r for r in dashboard.current_summary(POLICY)["strategies"]}
        self.assertEqual(rows["ch1"]["slot"], 7)
        self.assertEqual((rows["gone"]["badge"], rows["gone"]["slot"], rows["gone"]["realized"]), ("Stopped", 0, -1000.0))

    def test_the_review_prompt_names_every_limit(self):
        class Claude:
            def ask(self, system, user, web, timeout, paced=True):
                self.system = system
                return {"text": json.dumps({"headline": "h"}), "meta": {}}
        c = Claude()
        coach.Retro(POLICY["research"], claude=c).write({}, coach.limits(POLICY))
        for k in ("{bounds}", "{categories}", "{frozen}", "{max_proposals}", "{max_challengers}"):
            self.assertNotIn(k, c.system)
        for word in ('"max_total_exposure_pct": [0.05, 0.5]', "original", '"crypto"', "at most 4 changes", "At most 2 run",
                     '"yardstick"'):
            self.assertIn(word, c.system)


class SchedulerGateTests(DataDirTest):
    def due(self):
        from papertrade import __main__ as cli
        out = io.StringIO()
        with mock.patch("sys.stdout", out), mock.patch("sys.stderr", io.StringIO()):
            cli.cmd_due(25)
        return out.getvalue().strip()

    def test_runs_when_no_cycle_or_the_last_one_is_old_and_skips_when_recent(self):
        self.assertEqual(self.due(), "run=true")  # never ran
        engine.append_jsonl(engine.SCANS, {"ts": (datetime.now(timezone.utc) - timedelta(minutes=40)).strftime(engine.TS), "funnel": {}})
        self.assertEqual(self.due(), "run=true")
        engine.append_jsonl(engine.SCANS, {"ts": (datetime.now(timezone.utc) - timedelta(minutes=5)).strftime(engine.TS), "funnel": {}})
        engine.append_jsonl(engine.SCANS, {"ts": engine.now_iso(), "kind": "review"})  # not a cycle
        self.assertEqual(self.due(), "run=false")


class ExperimentsRegistryTests(unittest.TestCase):
    """docs/EXPERIMENTS.md and policy.json describe the same strategies (each file reads fine alone)."""

    def test_every_strategy_has_a_registry_row_and_every_row_a_strategy(self):
        import re
        text = (Path(__file__).parent.parent / "docs" / "EXPERIMENTS.md").read_text()
        rows = set(re.findall(r"^\| `([a-z0-9_]+)` \|", text, re.M))
        configured = {k for k in POLICY["strategies"] if not k.startswith("_")}
        self.assertEqual(configured - rows, set(), "strategies in policy.json with no row in docs/EXPERIMENTS.md")
        self.assertEqual({r for r in rows - configured if not re.fullmatch(r"ch\d+", r)}, set(),
                         "rows in docs/EXPERIMENTS.md for strategies that don't exist")


class PublishTests(DataDirTest):
    def test_page_shell_loads_live_data_from_the_public_repo(self):
        engine.save_portfolio("main", fresh_pf())
        out = dashboard.build_site(POLICY)
        files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
        self.assertEqual(files, ["index.html"])
        html = (out / "index.html").read_text()
        self.assertIn("America/New_York", html)
        blob = json.loads(html.split('<script type="application/json" id="data">', 1)[1].split("</script>", 1)[0])
        self.assertEqual(blob["data_url"],
                         "https://raw.githubusercontent.com/MojoAI-King/jev-paper-trader/master/papertrade_data/summary.json")
        self.assertFalse(blob["example"])

    def test_summary_json_is_real_data_with_ledger_links(self):
        engine.save_portfolio("main", fresh_pf())
        s = json.loads(dashboard.write_summary(POLICY).read_text())
        self.assertFalse(s["example"])
        self.assertTrue(s["ledger_base"].endswith("/papertrade_data/"))

    def test_refuses_to_publish_example_data(self):
        s = dashboard.summarize(POLICY, books(fresh_pf()), [], {}, "2026-09-27T00:00:00Z", example=True)
        with self.assertRaises(RuntimeError):
            dashboard.build_site(POLICY, summary=s)
        self.assertFalse(engine.SITE.exists())


if __name__ == "__main__":
    unittest.main()
