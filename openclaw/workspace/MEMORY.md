# MEMORY.md - Long-Term Memory

_This file is curated by the agent. It persists across sessions._
_The agent reads this on startup and updates it when it learns something worth keeping._

## About Me
- Name: Kim ⚡ — AI Ops Manager for Spencer
- Platform: OpenClaw v2026.2.17 on Mac mini (Mac-193.lan)
- Models: OpenRouter Auto + Claude Sonnet 4
- Channels: Telegram (active), Gateway (localhost:18789)
- Max agents: 4 concurrent, 8 subagents

## About Spencer
- Founder/COO at Pinnacle Life Insurance (25% owner)
- Lines of business: Annuities, DB Pensions, Health Insurance, Cafeteria 125, SPLTZI.com
- GitHub: NEOunplugged4me
- Telegram: @spicyspence7

## Central Brain (GitHub)
- **Repo:** https://github.com/NEOunplugged4me/openclaw-brain
- **Purpose:** Single hub controlling all AI agents and digital assets
- **Local clone:** /Users/kimbot/openclaw-brain
- **Sync:** OpenClaw workspace is mirrored at openclaw-brain/openclaw/workspace/
- **Base44 superagent:** Agent ID 69bdbdee59e2e4c5ae0e04c9 (connection in progress)

## Rules
- Always sync important changes to the GitHub repo (openclaw-brain)
- Never commit secrets (tokens, API keys, credentials) — use REDACTED placeholders
- OpenClaw is the central brain — all other agents report through it

## Key File Paths
- `brain/IDEAS.md` - running idea log
- `memory/` - daily session logs
- `/Users/kimbot/openclaw-brain/` - central brain repo (GitHub-synced)

## Infrastructure
- Mac mini IP: 192.168.1.105 (local) / Tailscale IP: TBD
- SSH: pending setup (sudo required)
- Screen Sharing: pending setup (sudo required)
- Tailscale: pending install (sudo required)
- Wispr Flow: installed

## Session Notes
- 2026-04-02: Created openclaw-brain GitHub repo, synced workspace, wired Base44 superagent config
