// Responsive audit via the Chrome DevTools Protocol (Node 22+, no dependencies).
//
// For 10 viewport widths (320-1440px) it checks: horizontal overflow, tap targets
// under 24x24px (WCAG 2.2 AA; stretched links are measured by real hit-testing),
// the smallest rendered font, that every hero phrase fits on one line, and that
// the mobile menu opens, stays on screen and closes after choosing a link.
//
// Usage (with the dev server running):
//   node tools/responsive_audit.mjs <chrome-binary> http://127.0.0.1:8000/ <screenshot-dir>
//
// Exit codes: 0 = no issues, 1 = layout issues found, 2 = usage error or the audit
// could not run. Chrome is always shut down and its temporary profile removed,
// even when the audit fails partway.
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const USAGE = "Usage: node tools/responsive_audit.mjs <chrome-binary> <url> <screenshot-dir>";
const WIDTHS = [320, 360, 375, 390, 414, 768, 820, 1024, 1280, 1440];

// --- Validate arguments before starting anything -----------------------------------
const [chromeBin, url, outDir] = process.argv.slice(2);
const usageError = (message) => {
  console.error(`Error: ${message}\n${USAGE}`);
  process.exit(2);
};
if (!chromeBin || !url || !outDir) usageError("missing arguments.");
if (!existsSync(chromeBin) || !statSync(chromeBin).isFile()) usageError(`Chrome binary not found: ${chromeBin}`);
try {
  new URL(url);
} catch {
  usageError(`not a valid URL: ${url}`);
}
mkdirSync(outDir, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const profile = mkdtempSync(join(tmpdir(), "audit-profile-"));
let chrome;
let ws;

async function main() {
  // Port 0 lets Chrome pick a free port, so parallel or leftover runs never collide.
  // Chrome writes the chosen port to <profile>/DevToolsActivePort.
  chrome = spawn(chromeBin, [
    "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
    "--remote-debugging-port=0", `--user-data-dir=${profile}`, "about:blank",
  ], { stdio: "ignore" });
  const chromeExited = new Promise((_, reject) => {
    chrome.once("error", (err) => reject(new Error(`could not start Chrome: ${err.message}`)));
    chrome.once("exit", (code) => reject(new Error(`Chrome exited early (code ${code})`)));
  });

  const findPage = async () => {
    for (let i = 0; i < 75; i++) {
      try {
        const port = readFileSync(join(profile, "DevToolsActivePort"), "utf8").split("\n")[0].trim();
        const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
        const page = targets.find((t) => t.type === "page");
        if (page) return page;
      } catch {
        // Not ready yet.
      }
      await sleep(200);
    }
    throw new Error("Chrome did not expose a DevTools page within 15s");
  };
  const page = await Promise.race([findPage(), chromeExited]);
  // Chrome exiting is only an error during startup; we kill it ourselves at the end.
  chromeExited.catch(() => {});
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve, { once: true });
    ws.addEventListener("error", () => reject(new Error("could not connect to Chrome DevTools")), { once: true });
  });

  let seq = 0;
  const pending = new Map();
  const events = [];
  ws.addEventListener("message", (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
    else if (msg.method) events.push(msg);
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    if (ws.readyState !== WebSocket.OPEN) return reject(new Error(`${method}: DevTools connection closed`));
    const id = ++seq;
    pending.set(id, (m) => (m.error ? reject(new Error(`${method}: ${m.error.message}`)) : resolve(m.result)));
    ws.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async (expression) => {
    const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || "eval error");
    return r.result.value;
  };

  await send("Page.enable");
  await send("Runtime.enable");

  const MEASURE = `(() => {
    const vw = document.documentElement.clientWidth;
    const docOverflow = document.documentElement.scrollWidth - vw;
    const isClipped = (el) => {
      for (let p = el.parentElement; p; p = p.parentElement) {
        const cs = getComputedStyle(p);
        if (cs.overflowX !== "visible" || cs.overflow === "hidden") return true;
      }
      return false;
    };
    const visible = (el) => {
      const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none";
    };
    const overflowing = [...document.querySelectorAll("body *")]
      .filter((el) => visible(el) && el.getBoundingClientRect().right > vw + 1 && !isClipped(el))
      .slice(0, 8).map((el) => el.tagName.toLowerCase() + "." + [...el.classList].join(".") + " right=" + Math.round(el.getBoundingClientRect().right));
    const smallTargets = [...document.querySelectorAll("a, button")]
      .filter((el) => visible(el) && !el.classList.contains("skip-link"))
      .map((el) => {
        // A "stretched link" (::after absolutely positioned) is tappable over its containing block.
        let r = el.getBoundingClientRect();
        const after = getComputedStyle(el, "::after");
        if (after.content !== "none" && after.position === "absolute" && el.offsetParent) {
          const box = el.offsetParent.getBoundingClientRect();
          el.scrollIntoView({ block: "center", behavior: "instant" });
          const b = el.offsetParent.getBoundingClientRect();
          const probes = [[b.left + 4, b.top + 4], [b.right - 4, b.bottom - 4], [b.left + b.width / 2, b.top + 4]];
          const hitsLink = probes.every(([x, y]) => { const hit = document.elementFromPoint(x, y); return hit && (hit === el || el.contains(hit)); });
          if (hitsLink) r = box;
        }
        return { el, r };
      })
      .filter(({ r }) => r.height < 24 || r.width < 24)
      .map(({ el, r }) => (el.className || el.tagName) + " " + Math.round(r.width) + "x" + Math.round(r.height) + " '" + el.textContent.trim().slice(0, 30) + "'");
    let minFont = 99, minFontText = "";
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n; (n = walker.nextNode()); ) {
      if (!n.textContent.trim() || !n.parentElement || !visible(n.parentElement)) continue;
      if (n.parentElement.closest(".visually-hidden, script, noscript")) continue;
      const fs = parseFloat(getComputedStyle(n.parentElement).fontSize);
      if (fs < minFont) { minFont = fs; minFontText = n.textContent.trim().slice(0, 40); }
    }
    // Every hero phrase must fit on one line (where nowrap applies).
    const phraseEl = document.querySelector("[data-rotate]");
    const phrases = JSON.parse(document.getElementById("hero-phrases").textContent);
    const original = phraseEl.textContent;
    const phraseFit = phrases.map((p) => {
      phraseEl.textContent = p;
      return { p, fits: phraseEl.scrollWidth <= phraseEl.parentElement.clientWidth + 1 && phraseEl.getBoundingClientRect().right <= vw };
    });
    phraseEl.textContent = original;
    const header = document.querySelector(".site-header").getBoundingClientRect().height;
    return { vw, docOverflow, overflowing, smallTargets, minFont, minFontText, phraseFit, header: Math.round(header) };
  })()`;

  const MENU = `(async () => {
    const toggle = document.querySelector("[data-nav-toggle]");
    if (getComputedStyle(toggle).display === "none") return { applicable: false };
    toggle.click();
    await new Promise((r) => setTimeout(r, 50));
    const nav = document.querySelector("[data-nav]");
    const open = getComputedStyle(nav).display !== "none" && toggle.getAttribute("aria-expanded") === "true";
    const links = [...nav.querySelectorAll("a")].map((a) => Math.round(a.getBoundingClientRect().height));
    const navRect = nav.getBoundingClientRect();
    nav.querySelector("a").click();
    await new Promise((r) => setTimeout(r, 50));
    const closedAfterClick = toggle.getAttribute("aria-expanded") === "false";
    return { applicable: true, open, linkHeights: links, navInViewport: navRect.right <= innerWidth + 1, closedAfterClick };
  })()`;

  const results = [];
  for (const width of WIDTHS) {
    await send("Emulation.setDeviceMetricsOverride", { width, height: 860, deviceScaleFactor: 1, mobile: width < 800 });
    events.length = 0;
    const nav = await send("Page.navigate", { url });
    if (nav.errorText) throw new Error(`could not load ${url} (${nav.errorText}). Is the dev server running?`);
    for (let i = 0; i < 100 && !events.some((e) => e.method === "Page.loadEventFired"); i++) await sleep(50);
    await sleep(300);
    const m = await evaluate(MEASURE);
    const menu = await evaluate(MENU);
    if ([320, 390, 768, 1024].includes(width)) {
      await send("Page.navigate", { url });
      await sleep(800);
      const shot = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true,
        clip: { x: 0, y: 0, width, height: 1400, scale: 1 } });
      writeFileSync(join(outDir, `w${width}.png`), Buffer.from(shot.data, "base64"));
    }
    results.push({ width, ...m, menu });
  }

  let widthsWithIssues = 0;
  for (const r of results) {
    const problems = [];
    if (r.docOverflow > 0) problems.push(`page scrolls sideways by ${r.docOverflow}px`);
    if (r.overflowing.length) problems.push(`overflowing: ${r.overflowing.join(", ")}`);
    if (r.smallTargets.length) problems.push(`small tap targets: ${r.smallTargets.join(" | ")}`);
    const badPhrases = r.phraseFit.filter((p) => !p.fits).map((p) => p.p);
    if (badPhrases.length) problems.push(`phrase wraps/overflows: ${badPhrases.join(", ")}`);
    if (r.menu.applicable && !(r.menu.open && r.menu.navInViewport && r.menu.closedAfterClick)) problems.push(`menu: ${JSON.stringify(r.menu)}`);
    if (r.menu.applicable && r.menu.linkHeights.some((h) => h < 44)) problems.push(`menu links < 44px: ${r.menu.linkHeights}`);
    console.log(`${String(r.width).padStart(4)}px  header=${r.header}px  minFont=${r.minFont}px ('${r.minFontText}')  menu=${r.menu.applicable ? "ok" : "n/a"}`);
    console.log(problems.length ? problems.map((p) => "      ✗ " + p).join("\n") : "      ✓ no issues");
    if (problems.length) widthsWithIssues++;
  }

  return widthsWithIssues;
}

// --- Run, always cleaning up -------------------------------------------------------
try {
  const widthsWithIssues = await main();
  console.log(widthsWithIssues ? `\n${widthsWithIssues} width(s) with issues.` : "\nAll widths passed.");
  process.exitCode = widthsWithIssues ? 1 : 0;
} catch (err) {
  console.error(`Audit failed: ${err.message}`);
  process.exitCode = 2;
} finally {
  try { ws?.close(); } catch { /* already closed */ }
  if (chrome && chrome.exitCode === null && chrome.signalCode === null) {
    // kill() only sends the signal. Wait for Chrome to actually exit (max 5s) before
    // deleting its profile, or it may still be writing files there (ENOTEMPTY).
    const exited = new Promise((resolve) => chrome.once("exit", resolve));
    chrome.kill();
    await Promise.race([exited, sleep(5000)]);
  }
  try {
    rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  } catch (err) {
    console.error(`Warning: could not remove temporary profile ${profile}: ${err.message}`);
  }
}
