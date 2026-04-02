---
name: btw
description: Capture a quick side thought, idea, or note from Spencer without derailing the current conversation. Logs it to brain/IDEAS.md with a timestamp.
metadata:
  openclaw:
    emoji: "💡"
---

# BTW

Use this skill when Spencer wants to quickly log a thought, idea, or note while in the middle of something else. The goal is zero friction: capture it, confirm it, move on.

## When to use

Trigger phrases:
- `/btw [thought]`
- `btw: [thought]`
- `btw -- [thought]`
- "side note: [thought]"
- "note to self: [thought]"
- "log this: [thought]"
- "jot this down: [thought]"

## Behavior

1. Extract the note content (everything after the trigger phrase)
2. Append to `~/workspace/brain/IDEAS.md` with a timestamp
3. Acknowledge with a single short line, then stop. Do NOT ask follow-up questions. Do NOT elaborate. Do NOT derail the current task.
4. If there was an active conversation or task before the /btw, continue it naturally after acknowledging.

## Format to append to IDEAS.md

```
- [YYYY-MM-DD HH:MM] [note content]
```

Use the current date and time. Append to the bottom of the file.

## Example

Spencer: `/btw look into whether Base44 supports webhooks natively`

Kim appends to IDEAS.md:
```
- 2026-03-25 14:32 look into whether Base44 supports webhooks natively
```

Kim replies: `Logged.`

That's it. No summary, no "great idea!", no elaboration.

## Implementation

```bash
echo "- $(date '+%Y-%m-%d %H:%M') [note content]" >> ~/.openclaw/workspace/brain/IDEAS.md
```

Then commit if a git push is scheduled, or leave for the next session push. Do not commit mid-session just for a btw entry.

## Notes

- This is a capture tool, not an action trigger. Log it and move on.
- If Spencer says `/btw` with no content, ask once: "What did you want to log?"
- Entries are reviewed during session wrap-up or when Spencer asks to see recent ideas.
