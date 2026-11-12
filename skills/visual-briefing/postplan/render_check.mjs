// Renders the document at 390x844 and reports what only a browser can know:
// how big the components actually come out, whether anything is clipped, and
// how much there is to read. build.py turns this into refusals.
//
// Usage: node render_check.mjs <file.html> [viewportWidth]
// Prints one JSON object on stdout.
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { execSync } from 'node:child_process';

// playwright is installed globally (mise on the laptop), so a bare import does
// not resolve from this folder. Ask npm where the global root is and load it
// from there; POSTPLAN_PLAYWRIGHT overrides for a machine that keeps it
// somewhere else.
async function loadChromium() {
  const tries = [];
  if (process.env.POSTPLAN_PLAYWRIGHT) tries.push(process.env.POSTPLAN_PLAYWRIGHT);
  tries.push('playwright');
  try {
    const root = execSync('npm root -g', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    if (root) tries.push(pathToFileURL(resolve(root, 'playwright', 'index.mjs')).href);
  } catch {}
  tries.push('/home/decruce/.local/share/mise/installs/npm-playwright/latest/node_modules/playwright/index.mjs');
  for (const t of tries) {
    try {
      const mod = await import(t.startsWith('/') ? pathToFileURL(t).href : t);
      return mod.chromium;
    } catch {}
  }
  return null;
}

const chromium = await loadChromium();
if (!chromium) {
  console.log(JSON.stringify({ error: 'playwright not found' }));
  process.exit(0);
}

const file = process.argv[2];
const width = Number(process.argv[3] || 390);
if (!file) {
  console.log(JSON.stringify({ error: 'no file given' }));
  process.exit(0);
}

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width, height: 844 },
  deviceScaleFactor: 2,
  reducedMotion: 'reduce',
});
await page.goto(pathToFileURL(resolve(file)).href, { waitUntil: 'load', timeout: 60000 });
await page.waitForTimeout(400); // the scaler runs on load

const report = await page.evaluate((MIN_PX) => {
  // The rendered size of text: its computed font-size times whatever scale its
  // ancestors apply. A .stage scales the whole component with a transform, so
  // the computed value alone says nothing about what the eye gets.
  const scaleOf = (el) => {
    const natural = el.offsetWidth;
    if (!natural) return 1;
    return el.getBoundingClientRect().width / natural;
  };

  const tiny = [];
  const clipped = [];
  const boxes = [];

  for (const host of document.querySelectorAll('.stage, .viz, .phone')) {
    const k = scaleOf(host.firstElementChild || host);
    boxes.push({
      cls: host.className,
      box: Math.round(host.getBoundingClientRect().width),
      scale: Number(k.toFixed(3)),
    });
    const walker = document.createTreeWalker(host, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walker.nextNode())) {
      const text = n.nodeValue.trim();
      if (!text) continue;
      const el = n.parentElement;
      if (!el || !el.getClientRects().length) continue;
      const fs = parseFloat(getComputedStyle(el).fontSize);
      const rendered = fs * k;
      if (rendered < MIN_PX) {
        tiny.push({
          cls: el.className || el.tagName.toLowerCase(),
          text: text.slice(0, 40),
          px: Math.floor(rendered * 10) / 10,
          host: host.className,
        });
      }
    }
    for (const el of host.querySelectorAll('*')) {
      const st = getComputedStyle(el);
      if (st.overflow === 'visible' && st.overflowX === 'visible') continue;
      if (el.hasAttribute('data-bleeds')) continue;
      if (el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 0) {
        clipped.push({
          cls: el.className || el.tagName.toLowerCase(),
          scrollWidth: el.scrollWidth,
          clientWidth: el.clientWidth,
          text: (el.textContent || '').trim().slice(0, 40),
        });
      }
    }
  }

  // A table of the document itself can lose its last column off the right edge
  // the same way a component can, and it carries the same decisions.
  const wideTables = [];
  for (const t of document.querySelectorAll('table')) {
    const host = t.closest('.tw') || t.parentElement;
    const room = host ? host.clientWidth : document.body.clientWidth;
    if (t.scrollWidth > room + 2 && getComputedStyle(host).overflowX !== 'auto') {
      wideTables.push({ w: t.scrollWidth, room, head: (t.querySelector('th') || {}).textContent || '' });
    }
  }

  const words = (document.body.innerText || '').trim().split(/\s+/).filter(Boolean).length;
  const firstQ = document.querySelector('.q');
  return {
    words,
    heightPx: document.documentElement.scrollHeight,
    screens: Number((document.documentElement.scrollHeight / 844).toFixed(1)),
    firstQuestionAtPx: firstQ ? Math.round(firstQ.getBoundingClientRect().top + window.scrollY) : null,
    questions: document.querySelectorAll('.q').length,
    findings: document.querySelectorAll('.finding').length,
    // A table row carries a fact the same way a finding block does, for a
    // median of 17 words instead of 68, so the ceiling has to see it.
    tableRows: document.querySelectorAll('table tr').length,
    components: boxes.length,
    smallestBox: boxes.length ? Math.min(...boxes.map((b) => b.box)) : null,
    tiny: tiny.slice(0, 12),
    tinyCount: tiny.length,
    clipped: clipped.slice(0, 8),
    clippedCount: clipped.length,
    wideTables,
    // How far the page runs past the screen it is read on, whatever its layout.
    pageOverflowPx: Math.max(0, document.documentElement.scrollWidth - window.innerWidth),
  };
}, 11);

console.log(JSON.stringify(report));
await browser.close();
