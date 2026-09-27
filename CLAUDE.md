# Notes for AI agents working in this repo

- This is a **paper-trading** experiment: fake money only. Never add code that places real orders,
  connects to a trading account, or handles exchange credentials, unless Joey explicitly asks.
- `.env` holds `TYPESAFE_AI_API_KEY`. Never print it, log it, or commit it.
- Jev must **not** see market prices in its state. The test `test_scan_settle_report` checks this.
- Any change to question wording in `papertrade/judge.py` requires bumping `QUESTION_SET_VERSION`,
  because calibration data from old wording doesn't carry over.
- Tune behavior in `policy.json`, not in code. Keep hard limits (stake caps, exposure caps) in code-enforced policy.
- Run the offline tests before and after changes: `python3 -m unittest discover -s tests -t .`
- For Jev/TypeSafe API details, use the TypeSafe skill and the live docs at https://docs.typesafe.ai/llms.txt.
