---
name: model-switch
description: Switch Kim's model between opus/sonnet/haiku via slash commands
metadata:
  openclaw:
    emoji: "🔄"
---

# Model Switch

Switch the active model via slash commands.

## When to use

Trigger commands:
- `/opus` - Switch to Claude Opus
- `/sonnet` - Switch to Claude Sonnet
- `/haiku` - Switch to Claude Haiku
- `/model` or `/status` - Show current model

## Model Mappings

| Command   | Model ID                        |
|-----------|---------------------------------|
| `/opus`   | `anthropic/claude-opus-4-6`     |
| `/sonnet` | `anthropic/claude-sonnet-4-6`   |
| `/haiku`  | `anthropic/claude-haiku-4-5`    |

## Behavior

1. Detect the trigger command
2. Call `session_status` with the `model` parameter set to the mapped model ID
3. Reply with a single confirmation line. Nothing else.

### Switch examples

Spencer: `/opus`
Kim calls: `session_status({ model: "anthropic/claude-opus-4-6" })`
Kim replies: `Switched to Opus.`

Spencer: `/haiku`
Kim calls: `session_status({ model: "anthropic/claude-haiku-4-5" })`
Kim replies: `Now on Haiku.`

### Status example

Spencer: `/model`
Kim calls: `session_status({})` (no model param, just reads current state)
Kim replies: `Currently on Sonnet.`

## Notes

- No follow-up questions. Switch and confirm, that's it.
- If the session_status call fails, say so: "Model switch failed. Try again."
- Do not restart or reset the conversation when switching models.
