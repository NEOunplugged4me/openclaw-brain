---
name: task_queue
description: Async task acknowledgment and completion notification pattern. Use when handling tasks that take more than ~30 seconds, involve Claude Code handoffs, or where Spencer might go AFK. Kim acknowledges immediately via message tool FIRST, does the work, then sends a completion message.
metadata:
  openclaw:
    model: haiku
---

# Task Queue

Use this pattern any time Spencer gives you a task that won't finish in the same turn — Claude Code handoffs, API builds, research tasks, or anything he kicks off before going AFK.

## When to use

- Task will take more than ~30 seconds
- Involves a Claude Code handoff
- Spencer says "do this" and then goes quiet (AFK signal)
- You need to ask a clarifying question mid-task without losing context
- Any multi-step task where Spencer shouldn't have to babysit

**Do not use for:** simple lookups, quick bash commands, anything that resolves in the same turn.

## Step order (critical)

### STEP 1: Send acknowledgment via message tool (FIRST, before anything else)

**This must be the very first action in your turn — before any exec, read, write, or sessions_spawn calls.**

Use the `message` tool with your configured delivery channel.

Text format: `Got it. [Specific restatement of exactly what you understood — include the what, the scope, and your plan]. Working on it now.`

**Examples of good acks:**
- "Got it. Pulling Anthropic cost report for today, last 7 days, and last 30 days grouped by API key. On it."
- "Got it. Building the Asana integration skill with getMyTasks, createTask, completeTask, and addComment. Handing to Claude Code now."
- "Got it. Moving all 141 inbox Asana tasks to the parking section. Running it now."

**Examples of bad acks (don't do this):**
- "Got it. Working on it now." (useless — no context)
- "On it." (even worse)
- "Got it, I'll take care of that." (vague)

The ack must be specific enough that Spencer can correct you if you misunderstood, before you waste time going in the wrong direction.

Do not send this as reply text. Reply text only arrives after the full turn completes, which means Spencer sees the ack and the completion at the same time. The `message` tool fires immediately mid-turn, so call it first.

### STEP 2: Do the work

Run the Claude Code handoff, API calls, research, or whatever the task requires.

### STEP 3: Send clarification request if stuck (optional)

When you hit a blocker and need input before continuing, send via `message` tool:

```
Stuck on [task name]. Need to know: [specific question, one sentence]. Reply and I'll continue.
```

Be specific. "I need clarification" is not a question. "Do you want X or Y?" is. One question per message, never bundle blockers.

### STEP 4: Send completion when done

Send via `message` tool:

```
Done: [task name]

[2-3 sentences: what was done, where to find the output]

[Action needed from Spencer — or omit this line if none]
```

## Failure message

If a task fails, send via `message` tool:

```
Failed: [task name]

What went wrong: [1-2 sentences, specific error]

What Spencer needs to do: [concrete next step]
```

Never send a failure message without a concrete next step. "It didn't work" is not useful.

## Sending messages

Use the `message` tool with your configured delivery channel and target.
Check TOOLS.md for the specific channel/target configuration.

## Known Limitation: Ack timing

The acknowledgment message and the response text always arrive at the same time from Spencer's perspective — they both appear after the turn completes. This is a fundamental LLM limitation (the entire turn is atomic). The completion message (sent via message tool after work finishes) does arrive separately and truly async.

## Rules

- Acknowledgment goes via `message` tool FIRST. Not as reply text. Not after the work. First.
- Never say "I'll ping you when done" without actually following through.
- One question per stuck message. Don't bundle multiple blockers.
- For Claude Code tasks: wait for the script to finish, then send the message. Don't send "done" before the work is complete.
