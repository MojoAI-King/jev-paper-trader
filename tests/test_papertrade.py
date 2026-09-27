"""Offline tests for the paper trader. Run: python3 -m unittest discover -s tests -t ."""
import io
import json
import tempfile
import unittest
import urllib.error
import urllib.parse
from pathlib import Path
from unittest import mock

from papertrade.jev_client import JevClient
from papertrade import engine
from papertrade import markets as mk

POLICY = engine.load_policy()


def ans(p, clear=0.9, info=0.8):
    return {"p_yes": {"noul": p}, "rules_clear": {"noul": clear}, "info_sufficient": {"noul": info}}


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

    def test_kalshi_fee_reduces_edge(self):
        poly = engine.decide(market(), ans(0.6), POLICY, 100000, 0, 100000)
        kal = engine.decide(market(src="kalshi"), ans(0.6), POLICY, 100000, 0, 100000)
        self.assertLess(kal["edge"], poly["edge"])


class EndToEndTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self._saved = (engine.DATA, engine.PORTFOLIO, engine.JUDGMENTS, engine.RESOLUTIONS)
        engine.DATA, engine.PORTFOLIO = d, d / "portfolio.json"
        engine.JUDGMENTS, engine.RESOLUTIONS = d / "judgments.jsonl", d / "resolutions.json"

    def tearDown(self):
        engine.DATA, engine.PORTFOLIO, engine.JUDGMENTS, engine.RESOLUTIONS = self._saved
        self.tmp.cleanup()

    def test_scan_settle_report(self):
        ms = [market(mid="1", close="2000-01-01T00:00:00Z"),            # YES bet, resolves yes
              market(mid="2", yes_ask=0.70, no_ask=0.32, m=0.69, close="2000-01-01T00:00:00Z"),  # NO bet, resolves yes -> loss
              market(mid="3")]                                            # no edge
        probs = {"Q1": 0.62, "Q2": 0.40, "Q3": 0.41}
        seen_prices = []

        def transport(url, body, key, timeout):
            seen_prices.append("0.4" in json.dumps(body["state"]))  # Jev must not see prices
            return {"model": "jev-test", "answers": ans(probs[body["state"]["market"]["question"]])}

        policy = dict(POLICY, sources=["polymarket"])
        stats = engine.scan(policy, client=JevClient(transport=transport),
                            fetchers={"polymarket": lambda *a: ms}, log=lambda *_: None)
        self.assertEqual((stats["judged"], stats["bets"]), (3, 2))
        self.assertFalse(any(seen_prices))

        # second scan within 24h must not re-judge
        stats2 = engine.scan(policy, client=JevClient(transport=transport),
                             fetchers={"polymarket": lambda *a: ms}, log=lambda *_: None)
        self.assertEqual(stats2["judged"], 0)

        s = engine.settle(policy, resolvers={"polymarket": lambda mid: "yes" if mid in "12" else None},
                          log=lambda *_: None)
        self.assertEqual(s["settled_bets"], 2)
        pf = engine.load_portfolio(policy)
        self.assertEqual(len(pf["open"]), 0)
        self.assertEqual(sorted(p["outcome"] for p in pf["closed"]), ["yes", "yes"])
        r = engine.report(policy)
        self.assertIn("Brier", r)
        self.assertAlmostEqual(pf["cash"], 100000 + sum(p["pnl"] for p in pf["closed"]), places=2)


if __name__ == "__main__":
    unittest.main()
