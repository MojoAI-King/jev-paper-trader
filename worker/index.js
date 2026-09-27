// The public page's Worker. It serves the page (site/, built by `python3 -m papertrade publish`) and, on a
// Cloudflare cron trigger, asks GitHub to start a trading cycle. GitHub's own scheduler skips slots under
// load (five in a row on 2026-09-27); Cloudflare's triggers fire on time.
//
// The trigger needs GITHUB_DISPATCH_TOKEN, a fine-grained GitHub token limited to this one repository with
// "Actions: read and write", stored as a Worker secret (`npx wrangler secret put GITHUB_DISPATCH_TOKEN`).
// Without it the trigger does nothing. The cycle itself still runs on GitHub, the only writer of the
// ledgers, and its "due" step skips it if a cycle ran in the last 25 minutes.
const REPO = "MojoAI-King/jev-paper-trader";
const WORKFLOW = "trade.yml";

export default {
  async fetch(request, env) {
    return env.ASSETS.fetch(request);
  },

  async scheduled(event, env, ctx) {
    if (!env.GITHUB_DISPATCH_TOKEN) {
      console.log("GITHUB_DISPATCH_TOKEN is not set; no trading cycle requested");
      return;
    }
    ctx.waitUntil((async () => {
      const r = await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.GITHUB_DISPATCH_TOKEN}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "jev-paper-trader-cron",
        },
        body: JSON.stringify({ ref: "master", inputs: { force: "false" } }),
      });
      // 204 means GitHub queued the run. Anything else is logged (visible with `npx wrangler tail`).
      console.log(`dispatch ${event.cron}: HTTP ${r.status}${r.status === 204 ? "" : " " + (await r.text()).slice(0, 300)}`);
    })());
  },
};
