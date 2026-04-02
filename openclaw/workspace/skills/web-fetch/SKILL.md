---
name: web_fetch
description: Fetch and extract content from web pages using Playwright. Use for scraping, research, reading pages that require JS rendering.
metadata:
  openclaw:
    requires:
      bins: ["node"]
---

# Web Fetch

Use this when you need to read content from a URL — articles, docs, pricing pages, anything on the web.

**When to use this vs other tools:**
- Use `web_fetch` for reading/extracting content from a specific URL you already have
- Use `browser_*` (Playwright MCP) when you need to interact with a page — click, log in, fill forms
- Use `duckduckgo_search` when you need to find URLs first, then web_fetch to read them

## Command

```bash
node ~/.openclaw/workspace/tools/web-fetch.mjs <url> [options]
```

## Options

| Flag | Description |
|------|-------------|
| `--mode text` | Plain text (default) |
| `--mode markdown` | Markdown-formatted output |
| `--mode links` | All links as JSON |
| `--mode screenshot` | Save a screenshot |
| `--mode raw` | Raw HTML |
| `--selector ".css"` | Target a specific element |
| `--wait 5000` | Extra wait time in ms (for slow/JS-heavy pages) |
| `--no-cache` | Bypass 12-hour cache |
| `--file urls.txt` | Batch process a list of URLs |

## Examples

```bash
# Read an article
node ~/.openclaw/workspace/tools/web-fetch.mjs https://example.com --mode markdown

# Extract all links from a page
node ~/.openclaw/workspace/tools/web-fetch.mjs https://example.com --mode links

# Slow-loading page (like Skool)
node ~/.openclaw/workspace/tools/web-fetch.mjs https://skool.com/some-page --wait 6000

# Target a specific section
node ~/.openclaw/workspace/tools/web-fetch.mjs https://example.com --selector ".main-content"
```

## Notes
- Results are cached for 12 hours automatically
- Uses the persistent browser context at `~/.openclaw/browser-context/` — so it's already logged in to sites Dylan has visited
- For Skool, use `--wait 5000` or more since it's JS-heavy
