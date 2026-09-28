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

POLICY = engine.load_policy()


def ans(p, clear=0.9, info=0.8, p_no=None):
    """A Jev reply answering every question in judge.QUESTIONS (the client rejects partial replies)."""
    return {"p_yes": {"noul": p}, "p_no": {"noul": round(1 - p, 4) if p_no is None else p_no},
            "rules_clear": {"noul": clear}, "info_sufficient": {"noul": info}, "already_decided": {"noul": 0.1}}


def market(src="polymarket", mid="1", yes_ask=0.40, no_ask=0.62, m=0.39, close="2099-01-01T00:00:00Z"):
    return {"source": src, "market_id": mid, "question": f"Q{mid}", "rules": "r", "close_time": close,
            "yes_ask": yes_ask, "no_ask": no_ask, "mid": m, "volume": 50000, "url": "u"}


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
        with mock.patch("urllib.request.urlopen", fake):
            self.assertEqual(mk.fetch_kalshi(30, 10000, 60), [])
        self.assertEqual(len(calls), mk.MAX_PAGES)

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
    def test_main_keeps_its_pre_registered_gates(self):  # PLAN.md fixes these before results come in
        self.assertEqual({k: v for k, v in POLICY["gates"].items() if not k.startswith("_")},
                         {"min_edge": 0.08, "min_rules_clear": 0.75, "min_info_sufficient": 0.5, "max_framing_gap": 0.15})
        self.assertNotIn("gate_overrides", POLICY["strategies"]["main"])
        self.assertIs(engine.strategy_policy(POLICY, POLICY["strategies"]["main"]), POLICY)

    def test_bold_differs_from_main_only_in_the_info_bar(self):
        bold = engine.strategy_policy(POLICY, POLICY["strategies"]["bold"])
        self.assertEqual(bold["gates"], dict(POLICY["gates"], min_info_sufficient=0.2))
        self.assertEqual((bold["sizing"], bold["fees"]), (POLICY["sizing"], POLICY["fees"]))
        a = ans(0.60, info=0.3)
        self.assertFalse(engine.decide(market(), a, POLICY, 100000, 0, 100000)["bet"])
        self.assertTrue(engine.decide(market(), a, bold, 100000, 0, 100000)["bet"])
        self.assertFalse(engine.decide(market(), ans(0.60, info=0.1), bold, 100000, 0, 100000)["bet"])

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
    NAMES = ("DATA", "PORTFOLIO", "PORTFOLIOS", "JUDGMENTS", "RESOLUTIONS", "SCANS", "REVIEWS", "RESEARCH",
             "SUMMARY", "SITE", "PLAYBOOK", "PLAYBOOK_LOG", "RETROS", "PROPOSALS")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._saved = {n: getattr(engine, n) for n in self.NAMES}
        for n, v in {"DATA": d, "PORTFOLIO": d / "portfolio.json", "PORTFOLIOS": d / "portfolios",
                     "JUDGMENTS": d / "judgments.jsonl", "RESOLUTIONS": d / "resolutions.json",
                     "SCANS": d / "scans.jsonl", "REVIEWS": d / "reviews.jsonl", "RESEARCH": d / "research.jsonl",
                     "SUMMARY": d / "summary.json", "SITE": d / "site", "PLAYBOOK": d / "playbook.json",
                     "PLAYBOOK_LOG": d / "playbook_history.jsonl", "RETROS": d / "retros.jsonl",
                     "PROPOSALS": d / "proposals.json"}.items():
            setattr(engine, n, v)

    def tearDown(self):
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
        self.assertEqual(stats["funnel"]["bets"], {"main": 2, "jev_alone": 0, "claude_direct": 1, "bold": 2, "calibrated": 0})
        self.assertFalse(any(seen_prices))

        # a second scan in the same hour judges nothing and asks Claude for nothing
        r2 = FakeResearcher([])
        stats2 = engine.scan(policy, researcher=r2, forecaster=FakeForecaster({}), **kw)
        self.assertEqual((stats2["funnel"]["judged"], r2.calls), (0, []))

        s = engine.settle(policy, resolvers={"polymarket": lambda mid: "yes" if mid in "12" else None},
                          log=lambda *_: None)
        self.assertEqual(s["by_strategy"], {"main": 2, "jev_alone": 0, "claude_direct": 1, "bold": 2, "calibrated": 0})
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
        ms = [self.lula(str(i), event=f"polymarket:e{i}") for i in range(6)]
        r = FakeResearcher([])
        self.run_scan(ms, r)
        self.assertEqual(len(r.calls), POLICY["research"]["max_research_per_cycle"])
        for i in range(POLICY["research"]["max_research_per_day"]):  # a day that has already used its research allowance
            engine.append_jsonl(engine.RESEARCH, {"ts": "1999-12-25T01:00:00Z", "event": f"old{i}", "mids": {}})
        r2 = FakeResearcher([])
        self.run_scan([self.lula("N", event="polymarket:new")], r2, now=SCAN_NOW + timedelta(hours=2))
        self.assertEqual(r2.calls, [])

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
        self.assertEqual((len(r.calls), stats["funnel"]["judged"], stats["funnel"]["with_research"], stats["errors"]),
                         (3, 3, 0, 3))
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
        runs = []

        def runner(args, env, cwd, timeout):
            runs.append(args)
            return 0, STREAM, ""
        rc = POLICY["research"]
        busy = {"status": "allowed_warning", "unifiedWindows": {
            "seven_day": {"utilization": rc["max_week_used"], "resetsAt": (SCAN_NOW + timedelta(hours=10)).timestamp()}}}
        engine.append_jsonl(engine.SCANS, {"ts": "1999-12-24T23:00:00Z", "claude": {"rate": busy}})
        cc = news.ClaudeCode(rc, runner=runner)
        stats = self.run_scan([self.lula()], news.Researcher(rc, cc), news.DirectForecaster(rc, cc), claude=cc)
        self.assertEqual((runs, stats["claude"]["limited"], stats["funnel"]["judged"]), ([], True, 1))
        # after the weekly window resets, research runs again
        cc2 = news.ClaudeCode(rc, runner=runner)
        self.run_scan([self.lula()], news.Researcher(rc, cc2), news.DirectForecaster(rc, cc2), claude=cc2,
                      now=SCAN_NOW + timedelta(hours=11))
        self.assertGreaterEqual(len(runs), 1)

    def test_each_strategy_uses_its_own_probability_and_never_doubles_up(self):
        def transport(url, body, key, timeout):
            return {"model": "jev-test", "answers": ans(0.70 if "recent_facts" in body["state"] else 0.60)}
        fc = FakeForecaster({"Will Lula win the election? (L)": 0.45})
        stats = self.run_scan([self.lula()], FakeResearcher([fact(CLEAN[0])]), fc, transport=transport)
        self.assertEqual(stats["funnel"]["bets"], {"main": 1, "jev_alone": 1, "claude_direct": 0, "bold": 1, "calibrated": 0})
        j = engine.read_jsonl(engine.JUDGMENTS)[0]
        self.assertEqual((j["decisions"]["main"]["p_yes"], j["decisions"]["jev_alone"]["p_yes"]), (0.70, 0.60))
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
        self.run_scan([self.lula()], FakeResearcher([fact(CLEAN[1])]), transport=transport)
        j = engine.read_jsonl(engine.JUDGMENTS)[-1]
        self.assertIsNone(j["jev_calibrated"])
        self.assertIn("still learning", j["decisions"]["calibrated"]["reasons"][0])
        # 40 resolved markets where Jev said 80% and only half came true: Jev is overconfident
        for i in range(40):
            engine.append_jsonl(engine.REVIEWS, {"key": f"k{i}", "ts": "1999-12-01T00:00:00Z",
                                                 "probs": {"jev_research": 0.8}, "outcome": "yes" if i % 2 else "no"})
        self.run_scan([self.lula("M")], FakeResearcher([fact(CLEAN[1])]), transport=transport)
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
             "strategy": {"label": "Edge 1", "probability": "jev_research", "gates": "jev_research",
                          "gate_overrides": {"min_edge": 0.01}}},
            {"id": "ch3", "kind": "challenger", "status": "running", "title": "t",  # tries to change sizing
             "strategy": {"label": "Big", "probability": "jev_research", "gates": "jev_research",
                          "sizing": {"max_stake_pct": 0.5}}},
            {"id": "ch4", "kind": "challenger", "status": "proposed", "title": "t",  # not approved yet
             "strategy": {"label": "Later", "probability": "jev_plain", "gates": "jev_plain"}}]})
        names = set(engine.strategies(POLICY))
        self.assertIn("ch1", names)
        self.assertFalse(names & {"ch2", "ch3", "ch4"})
        self.run_scan([self.lula()], FakeResearcher([fact(CLEAN[1])]))
        self.assertIn("ch1", engine.read_jsonl(engine.JUDGMENTS)[0]["decisions"])
        self.assertTrue(engine.portfolio_path("ch1").exists())

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
    BAD = dict(GOOD, title="Bigger bets", strategy=dict(GOOD["strategy"], gate_overrides={"min_edge": 0.0}))

    def setUp(self):
        super().setUp()
        for i in range(POLICY["learning"]["retro_min_reviews"]):
            engine.append_jsonl(engine.REVIEWS, reviewed(f"k{i}"))

    def test_with_auto_start_off_nothing_starts_until_approved(self):
        off = dict(POLICY, learning=dict(POLICY["learning"], auto_start_challengers=False))
        w = FakeRetro([self.GOOD, self.BAD, dict(self.GOOD, title="third")])
        r = coach.retro(off, writer=w, log=lambda *_: None, now=self.NOW)
        self.assertEqual((r["ran"], r["proposals"]), (True, 2))  # at most two a week
        props = {p["title"]: p for p in coach.load_proposals()["proposals"]}
        self.assertEqual(props["Lower edge bar"]["status"], "proposed")
        self.assertEqual(props["Bigger bets"]["status"], "invalid")
        self.assertNotIn(props["Lower edge bar"]["id"], engine.strategies(POLICY))
        self.assertIn("gate_ledger", w.numbers)  # Claude interprets numbers computed in code
        self.assertFalse(coach.retro(off, writer=w, log=lambda *_: None, now=self.NOW + timedelta(days=3))["ran"])
        # Joey approves: it runs as its own strategy from the next cycle
        pid = props["Lower edge bar"]["id"]
        self.assertIn("running", coach.set_status(pid, "running", off))
        self.assertIn(pid, engine.strategies(off))
        self.assertIn("Can't start", coach.set_status(props["Bigger bets"]["id"], "running", off))

    def test_challengers_start_by_themselves_but_only_within_bounds_and_slots(self):
        self.assertTrue(POLICY["learning"]["auto_start_challengers"])  # Joey's choice, 2026-09-27
        coach.retro(POLICY, writer=FakeRetro([self.GOOD, self.BAD]), log=lambda *_: None, now=self.NOW)
        status = {p["title"]: p["status"] for p in coach.load_proposals()["proposals"]}
        self.assertEqual(status, {"Lower edge bar": "running", "Bigger bets": "invalid"})
        self.assertIn(next(p["id"] for p in coach.load_proposals()["proposals"] if p["status"] == "running"),
                      engine.strategies(POLICY))
        # a week later, more valid challengers than free slots: the extra one waits
        two = [dict(self.GOOD, title="A", strategy=dict(self.GOOD["strategy"], gate_overrides={"min_edge": 0.07})),
               dict(self.GOOD, title="B", strategy=dict(self.GOOD["strategy"], gate_overrides={"min_edge": 0.10}))]
        coach.retro(POLICY, writer=FakeRetro(two), log=lambda *_: None, now=self.NOW + timedelta(days=8))
        status = {p["title"]: p["status"] for p in coach.load_proposals()["proposals"]}
        self.assertEqual((status["A"], status["B"]), ("running", "proposed"))
        self.assertIn("free slot", next(p for p in coach.load_proposals()["proposals"] if p["title"] == "B")["status_reason"])


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
