# Manual X/Grok Idea Sourcing

This workflow is intentionally manual. Do not schedule it as a cron job and do not make it a background routine. The agent should manually inspect X, ask Grok, parse the result, and decide which ideas become storyboard candidates.

## Purpose

Collect input ideas for the noise pipeline from:

1. X home feed posts/trends visible in the logged-in BrowserOS profile.
2. Grok answers at `https://x.com/i/grok` using a prompt targeted at comment-driving interpretation conflicts.

## Output directories

Current run:

- source bundle: `/home/vboxuser/noise/ideas/manual-x-grok/2026-04-23/`
- individual idea txt files: `/home/vboxuser/noise/ideas/manual-x-grok/2026-04-23/ideas/`
- status ledger: `/home/vboxuser/noise/ideas/manual-x-grok/2026-04-23/idea-status.tsv`
- JSONL log: `/home/vboxuser/noise/ideas/manual-x-grok/2026-04-23/idea-log.jsonl`
- storyboards: `/home/vboxuser/noise/outputs/storyboards/2026-04-23/`

## Manual BrowserOS notes from this run

- BrowserOS fixed profile was reused.
- CDP endpoint was available on `127.0.0.1:9100`.
- BrowserOS health on `127.0.0.1:9200` was not consistently available after restart, but CDP worked.
- X home tab: `https://x.com/home`.
- Grok tab: `https://x.com/i/grok`.
- Grok prompt submission succeeded after manual CDP trial/error:
  - find `textarea[placeholder="무엇이든 물어보세요"]`
  - set textarea with native `HTMLTextAreaElement.prototype.value` setter
  - dispatch `InputEvent('input')` and `change`
  - click the button whose `aria-label` includes `Grok`
  - capture `primaryColumn.innerText`

## Parser note

Grok echoes the prompt, including the empty schema tag:

`<noise_json>{"ideas":[]}</noise_json>`

Therefore parser logic must inspect all `<noise_json>...</noise_json>` blocks and choose the last/non-empty `ideas` payload, not the first tag.

Implemented parser:

- `/home/vboxuser/noise/src/noise_engine/grok_parser.py`
- tests: `/home/vboxuser/noise/tests/test_grok_parser.py`

## Current run outputs

Collected 11 idea files:

- 3 manually interpreted from X home feed
- 8 parsed from Grok/X-search response

Storyboarded 3 versions:

1. `/home/vboxuser/noise/outputs/storyboards/2026-04-23/v1-age-verification-platform-safety.txt`
2. `/home/vboxuser/noise/outputs/storyboards/2026-04-23/v2-cangaroo-independence-family-economy.txt`
3. `/home/vboxuser/noise/outputs/storyboards/2026-04-23/v3-lowbirth-wording-language-reality.txt`
