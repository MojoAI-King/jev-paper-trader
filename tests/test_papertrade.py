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
from papertrade import dashboard, jev_client, news, review
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


POLY_FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "polymarket_markets.json").read_text())


class PolymarketFetchTests(unittest.TestCase):
    """Replays recorded Gamma API responses; no network."""

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
        d = engine.decide(market(), ans(0.9), POLICY, 100000, 30000, 70000)
        self.assertFalse(d["bet"])

    def test_yes_no_disagreement_blocks(self):
        self.assertTrue(engine.decide(market(), ans(0.60, p_no=0.42), POLICY, 100000, 0, 100000)["bet"])
        d = engine.decide(market(), ans(0.60, p_no=0.70), POLICY, 100000, 0, 100000)  # 0.60 + 0.70 is far from 1
        self.assertFalse(d["bet"])
        self.assertIn("disagree", " ".join(d["reasons"]))

    def test_kalshi_fee_reduces_edge(self):
        poly = engine.decide(market(), ans(0.6), POLICY, 100000, 0, 100000)
        kal = engine.decide(market(src="kalshi"), ans(0.6), POLICY, 100000, 0, 100000)
        self.assertLess(kal["edge"], poly["edge"])


SCAN_NOW = datetime(1999, 12, 25, tzinfo=timezone.utc)  # test markets close 2000-01-01/02: inside the window
STREAM = (Path(__file__).parent / "fixtures" / "claude_stream.jsonl").read_text()  # a real Claude Code run, recorded


def fact(text, kind="event", date_="1999-12-20", source="Reuters", url="https://www.reuters.com/a"):
    return {"kind": kind, "date": date_, "source": source, "url": url, "fact": text}


class FakeResearcher:
    def __init__(self, facts, usd=0.5, urls=("https://www.reuters.com/a",), fail=None):
        self.facts, self.usd, self.urls, self.fail, self.calls = facts, usd, list(urls), fail, []

    def research(self, markets, today):
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
             "SUMMARY", "SITE")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._saved = {n: getattr(engine, n) for n in self.NAMES}
        for n, v in {"DATA": d, "PORTFOLIO": d / "portfolio.json", "PORTFOLIOS": d / "portfolios",
                     "JUDGMENTS": d / "judgments.jsonl", "RESOLUTIONS": d / "resolutions.json",
                     "SCANS": d / "scans.jsonl", "REVIEWS": d / "reviews.jsonl", "RESEARCH": d / "research.jsonl",
                     "SUMMARY": d / "summary.json", "SITE": d / "site"}.items():
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
        self.assertEqual(stats["funnel"]["bets"], {"main": 2, "jev_alone": 0, "claude_direct": 1})
        self.assertFalse(any(seen_prices))

        # a second scan in the same hour judges nothing and asks Claude for nothing
        r2 = FakeResearcher([])
        stats2 = engine.scan(policy, researcher=r2, forecaster=FakeForecaster({}), **kw)
        self.assertEqual((stats2["funnel"]["judged"], r2.calls), (0, []))

        s = engine.settle(policy, resolvers={"polymarket": lambda mid: "yes" if mid in "12" else None},
                          log=lambda *_: None)
        self.assertEqual(s["by_strategy"], {"main": 2, "jev_alone": 0, "claude_direct": 1})
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
        for i in range(30):  # a day that has already used its research allowance
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
            "seven_day": {"utilization": 0.95, "resetsAt": (SCAN_NOW + timedelta(hours=10)).timestamp()}}}
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
        self.assertEqual(stats["funnel"]["bets"], {"main": 1, "jev_alone": 1, "claude_direct": 0})
        j = engine.read_jsonl(engine.JUDGMENTS)[0]
        self.assertEqual((j["decisions"]["main"]["p_yes"], j["decisions"]["jev_alone"]["p_yes"]), (0.70, 0.60))
        # two days later the market is judged again for data, but no strategy adds to a position it holds
        stats2 = self.run_scan([self.lula()], FakeResearcher([]), fc, transport=transport, now=SCAN_NOW + timedelta(days=2))
        self.assertEqual(stats2["funnel"]["judged"], 1)
        self.assertEqual(stats2["funnel"]["bets"]["main"], 0)
        self.assertEqual(len(engine.load_portfolio(POLICY)["open"]), 1)

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
    return {"main": main, "jev_alone": fresh_pf(), "claude_direct": fresh_pf()}


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
        seen = {"polymarket:1": ("2000-01-01T06:00:00Z", 0.40)}
        self.assertTrue(engine.due(m, {}, "2000-01-01T00:00:00Z", 0.05))                      # never judged
        self.assertFalse(engine.due(m, seen, "2000-01-01T00:00:00Z", 0.05))                   # recent, same price
        self.assertTrue(engine.due(m, seen, "2000-01-01T07:00:00Z", 0.05))                    # older than the window
        self.assertTrue(engine.due(dict(m, mid=0.46), seen, "2000-01-01T00:00:00Z", 0.05))    # price moved 6 points


class FakeAnalyst:
    def __init__(self):
        self.cases = []

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
