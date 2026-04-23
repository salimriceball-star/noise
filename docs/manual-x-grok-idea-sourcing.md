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

## Prompt engineering standard

Do not ask Grok a vague prompt like "find ideas for the noise project." Grok does not know the project philosophy, the target comment dynamics, the safety boundaries, or the needed evidence window.

A usable Grok prompt must include:

- intent: `noise` means interpretation-collision design, not rage bait.
- context: comments should emerge from the gap between visible scene and caption claim.
- selection criteria: minimum 4 independent comment axes, rebuttal + self-projection + worldview expansion, low author-attack dependency.
- safety: no protected-class insult, no explicit sexualization, no fabricated claims, no individual harassment.
- time window: primary recent window such as 24h/48h/72h, with fallback to 7d only when needed.
- source confidence: home feed/search/trend/Grok synthesis must be distinguished.
- examples: at least 2-3 good examples and bad examples so Grok can pattern-match the desired output.
- output schema: valid JSON inside `<noise_json>...</noise_json>` with story seed, axes, risk, and scores.

Canonical template:

- `/home/vboxuser/noise/prompts/x_grok_noise_idea_prompt_template.md`

This run's revised concrete prompt:

- `/home/vboxuser/noise/ideas/manual-x-grok/2026-04-23/grok-prompt-v2-engineered.txt`

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

Storyboarded 3 versions before prompt-engineering reinforcement:

1. `/home/vboxuser/noise/outputs/storyboards/2026-04-23/v1-age-verification-platform-safety.txt`
2. `/home/vboxuser/noise/outputs/storyboards/2026-04-23/v2-cangaroo-independence-family-economy.txt`
3. `/home/vboxuser/noise/outputs/storyboards/2026-04-23/v3-lowbirth-wording-language-reality.txt`

After prompt-engineering reinforcement, 3 additional candidates were generated under:

- `/home/vboxuser/noise/outputs/storyboards/2026-04-23-post-prompt-engineering/README.txt`
- `/home/vboxuser/noise/outputs/storyboards/2026-04-23-post-prompt-engineering/v2-001-age-verification-family-privacy.txt`
- `/home/vboxuser/noise/outputs/storyboards/2026-04-23-post-prompt-engineering/v2-002-ai-ad-labor-value.txt`
- `/home/vboxuser/noise/outputs/storyboards/2026-04-23-post-prompt-engineering/v2-003-lowbirth-language-reality.txt`
