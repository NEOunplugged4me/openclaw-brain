#!/usr/bin/env node

import { chromium } from 'playwright';
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { createHash } from 'crypto';
import { join } from 'path';

const args = process.argv.slice(2);
const url = args.find(a => !a.startsWith('--'));
const getFlag = (name) => {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 ? args[idx + 1] : null;
};
const hasFlag = (name) => args.includes(`--${name}`);

if (!url) {
  console.error('Usage: web-fetch.mjs <url> [--mode text|markdown|links|screenshot|raw] [--selector ".css"] [--wait ms] [--no-cache]');
  process.exit(1);
}

const mode = getFlag('mode') || 'text';
const selector = getFlag('selector');
const wait = parseInt(getFlag('wait') || '0');
const noCache = hasFlag('no-cache');

// Cache setup
const cacheDir = join(process.env.HOME, '.openclaw', 'workspace', 'tools', '.cache');
if (!existsSync(cacheDir)) mkdirSync(cacheDir, { recursive: true });

const cacheKey = createHash('md5').update(`${url}:${mode}:${selector || ''}`).digest('hex');
const cachePath = join(cacheDir, `${cacheKey}.txt`);
const TWELVE_HOURS = 12 * 60 * 60 * 1000;

// Check cache
if (!noCache && existsSync(cachePath)) {
  const stat = readFileSync(cachePath);
  const age = Date.now() - require('fs').statSync(cachePath).mtimeMs;
  if (age < TWELVE_HOURS) {
    process.stdout.write(stat.toString());
    process.exit(0);
  }
}

const contextDir = join(process.env.HOME, '.openclaw', 'browser-context');

let browser, context, page;
try {
  browser = await chromium.launch({ headless: true });

  if (existsSync(contextDir)) {
    context = await browser.newContext({ storageState: join(contextDir, 'state.json') }).catch(() => browser.newContext());
  } else {
    context = await browser.newContext();
  }

  page = await context.newPage();
  await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

  if (wait > 0) await page.waitForTimeout(wait);

  let result;
  const target = selector ? await page.$(selector) : page;

  switch (mode) {
    case 'text':
      result = selector
        ? await target?.innerText() || ''
        : await page.innerText('body');
      break;

    case 'markdown': {
      const text = selector
        ? await target?.innerText() || ''
        : await page.innerText('body');
      // Basic text cleanup — not full markdown conversion but good enough
      result = text.replace(/\t/g, '  ').replace(/\n{3,}/g, '\n\n').trim();
      break;
    }

    case 'links': {
      const links = await page.$$eval(
        selector ? `${selector} a[href]` : 'a[href]',
        els => els.map(a => ({ text: a.innerText.trim(), href: a.href }))
      );
      result = JSON.stringify(links, null, 2);
      break;
    }

    case 'screenshot': {
      const screenshotPath = join(process.env.HOME, '.openclaw', 'workspace', 'tools', `screenshot-${Date.now()}.png`);
      if (selector && target) {
        await target.screenshot({ path: screenshotPath });
      } else {
        await page.screenshot({ path: screenshotPath, fullPage: true });
      }
      result = `Screenshot saved: ${screenshotPath}`;
      break;
    }

    case 'raw':
      result = selector
        ? await target?.innerHTML() || ''
        : await page.content();
      break;

    default:
      result = await page.innerText('body');
  }

  // Write cache
  if (mode !== 'screenshot') {
    writeFileSync(cachePath, result);
  }

  process.stdout.write(result);
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
} finally {
  if (browser) await browser.close();
}
