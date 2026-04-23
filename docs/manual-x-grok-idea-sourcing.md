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

## Follow-up run: v3 refreshed Grok response and image candidates

Run timestamp: 2026-04-23 20:03 KST

Reason:
- The previous post-prompt-engineering candidates were based on the reinforced prompt, but the user requested a fresh Grok response with the updated prompt and image candidate outputs.

Fresh inputs saved:
- X home capture: `/home/vboxuser/noise/ideas/manual-x-grok/2026-04-23/x-home-capture-v3.json`
- Concrete prompt: `/home/vboxuser/noise/ideas/manual-x-grok/2026-04-23/grok-prompt-v3-engineered.txt`
- Grok capture: `/home/vboxuser/noise/ideas/manual-x-grok/2026-04-23/grok-response-v3-capture.json`
- Grok raw text: `/home/vboxuser/noise/ideas/manual-x-grok/2026-04-23/grok-response-v3-raw.txt`
- Parsed JSON: `/home/vboxuser/noise/ideas/manual-x-grok/2026-04-23/grok-ideas-v3-parsed.json`

Observed home-feed signals included Unitree humanoid robot/wheel discussion and GPT image-2 + Seedance storyboard workflow discussion. Grok returned 12 valid ideas; the new idea files were stored as `grok-v3-001` through `grok-v3-012` under the date-stamped `ideas/` directory. `idea-status.tsv` and `idea-log.jsonl` were updated.

All-ideas synthesis outputs:
- `/home/vboxuser/noise/outputs/storyboards/2026-04-23-all-ideas-v3/README.txt`
- `/home/vboxuser/noise/outputs/storyboards/2026-04-23-all-ideas-v3/v3-001-humanoid-wheel-care-labor.txt`
- `/home/vboxuser/noise/outputs/storyboards/2026-04-23-all-ideas-v3/v3-002-ai-storyboard-labor-value.txt`
- `/home/vboxuser/noise/outputs/storyboards/2026-04-23-all-ideas-v3/v3-003-birth-contract-language-reality.txt`

Image generation note:
- GUIVM was still occupied by `/home/vboxuser/ai_persona/.local/stockpile_persona_pipeline.py --days 8`.
- Hermes `image_generate` was attempted as the requested image-tool fallback, but the tool failed with `FAL_KEY environment variable not set`.
- To still produce image artifacts and paths, local storyboard concept-sheet PNG fallbacks were generated from the synthesized candidates:
  - `/home/vboxuser/noise/outputs/storyboard-images/2026-04-23-local-storyboard-v3/v3-001-humanoid-wheel-care-labor.png`
  - `/home/vboxuser/noise/outputs/storyboard-images/2026-04-23-local-storyboard-v3/v3-002-ai-storyboard-labor-value.png`
  - `/home/vboxuser/noise/outputs/storyboard-images/2026-04-23-local-storyboard-v3/v3-003-birth-contract-language-reality.png`
- The image directory also contains GPT image-2 prompt files and `manifest.json` for reproducibility.

## Follow-up run: GUIVM Seoul 9-shot storyboard images

Run timestamp: 2026-04-23 22:40 KST

User prompt update applied to the GUIVM storyboard helper:
- Every storyboard image prompt must state that the scene is set in Korea, in contemporary Seoul.
- The storyboard sheet must be at least a 3x3 grid, here implemented as exactly 9 numbered shots.
- The 9 shots do not need to be separate topics; they may be different staging, camera angles, shot sizes, reaction shots, inserts, close-ups, cutaways, or emotional beats from the same topic.
- The output should feel like an immersive professional director's shooting plan, not a flat six-panel summary.

GUIVM became available after the prior ai_persona stockpile process stopped. The new GUIVM run used:
- helper: `/home/vboxuser/noise/tools/manual/generate_guivm_storyboard_images.py`
- output directory: `/home/vboxuser/noise/outputs/storyboard-images/2026-04-23-guivm-seoul-9shot-v3/`
- source storyboards: `/home/vboxuser/noise/outputs/storyboards/2026-04-23-all-ideas-v3/`

Generated GUIVM images:
- `/home/vboxuser/noise/outputs/storyboard-images/2026-04-23-guivm-seoul-9shot-v3/v3-001-humanoid-wheel-care-labor.png`
- `/home/vboxuser/noise/outputs/storyboard-images/2026-04-23-guivm-seoul-9shot-v3/v3-002-ai-storyboard-labor-value.png`
- `/home/vboxuser/noise/outputs/storyboard-images/2026-04-23-guivm-seoul-9shot-v3/v3-003-birth-contract-language-reality.png`

Verification notes:
- `manifest.json` records HTTP 200 and `output.images >= 1` for all 3 candidates.
- Each generated PNG is 1254x1254.
- Vision inspection confirmed all three are 3x3 / 9-shot storyboard sheets and read as contemporary Korea/Seoul, with usual AI text artifacts noted.
- Signed remote image URLs remain redacted in raw logs and manifest.

## Follow-up run: Seedance 2.0-ready storyboard reference images

Run timestamp: 2026-04-23 23:08 KST

Runway guide reviewed:
- URL: `https://help.runwayml.com/hc/en-us/articles/50488490233363-Creating-with-Seedance-2-0`
- Relevant Seedance 2.0 guidance applied:
  - Seedance can generate video from text, image, video, and audio inputs.
  - Reference mode is best when controlling what gets pulled from each image/video input.
  - Prompts should be positive, unambiguous, and outcome-focused.
  - A storyboard image can be used with a prompt like `use Image 1 as a storyboard to guide the scenes`.
  - The model supports director-level control over camera movement, lighting, and character performance, so storyboard references should show camera/lighting/performance cues visually.
  - Input image requirements are compatible with these PNG outputs: image files are >300 px and <6000 px.

Prompt update:
- The helper no longer forces a rigid 3x3 grid.
- It now asks for a Seedance-ready storyboard/reference board with 6-9 numbered shots, preferring 9 only when readability stays strong.
- It emphasizes modern Seoul continuity, subject/background consistency, shot rhythm, establishing shots, OTS/insert shots, reaction shots, close-ups, blocking, and lingering aftermath frames.
- It minimizes reliance on dense text/UI because video models often distort small text.

Generated GUIVM Seedance-ready images:
- `/home/vboxuser/noise/outputs/storyboard-images/2026-04-23-guivm-seedance-v3/v3-001-humanoid-wheel-care-labor.png`
- `/home/vboxuser/noise/outputs/storyboard-images/2026-04-23-guivm-seedance-v3/v3-002-ai-storyboard-labor-value.png`
- `/home/vboxuser/noise/outputs/storyboard-images/2026-04-23-guivm-seedance-v3/v3-003-birth-contract-language-reality.png`

Verification notes:
- `manifest.json` records HTTP 200 and `output.images >= 1` for all 3 candidates.
- PNG sizes: two 1491x1055 images and one 1448x1086 image, all within Seedance reference image requirements.
- Vision inspection confirmed all three work as multi-shot storyboard/reference boards with modern Korea/Seoul cues and cinematic director-style shot planning.
- Main known issue: AI-generated Korean/UI text may need manual cleanup before final video production.

## Follow-up run: user-supplied autonomous taxi storyboard reference

Run timestamp: 2026-04-24 KST

Prompt practice update:
- Exact-frame inputs should preserve the user-specified frame count; open-ended story inputs can be decomposed into the smallest readable 8-12 shot sequence.
- A reusable user-facing template was saved as `/home/vboxuser/Desktop/storyboard_prompt_template.txt`, with a repo copy at `/home/vboxuser/noise/prompts/user_storyboard_image_prompt_template.txt`.
- The template asks for a single storyboard-reference image, a clear contact-sheet layout, stable character/vehicle/prop/location IDs, tail-frame continuity, varied camera grammar, low text reliance, and no platform syntax in the artwork.

Autonomous taxi concrete prompt:
- `/home/vboxuser/noise/outputs/storyboard-images/2026-04-24-autonomous-car-passive-taxi-income-seedance/autonomous-car-passive-taxi-income.prompt.txt`
- The sequence is decomposed into 12 shots: commute, makeup in driver seat, arrival cue, office drop-off, empty car leaving, empty-driver-seat POV, passenger hail/pickup, passenger ride, payment beat, desk-phone revenue popup, glass-wall reaction, drone-view aftermath.
- GUIVM output directory: `/home/vboxuser/noise/outputs/storyboard-images/2026-04-24-autonomous-car-passive-taxi-income-seedance/`

Generated GUIVM autonomous taxi image:
- `/home/vboxuser/noise/outputs/storyboard-images/2026-04-24-autonomous-car-passive-taxi-income-seedance/autonomous-car-passive-taxi-income.png`
- Manifest: `/home/vboxuser/noise/outputs/storyboard-images/2026-04-24-autonomous-car-passive-taxi-income-seedance/manifest.json`
- PNG: 1448x1086, 2,392,625 bytes, sha256 prefix `ca887053293e12be`.

Verification notes:
- Vision inspection rated the result as a strong match for the requested sequence: 12 clear shots covering autonomous commute, makeup in the driver seat, arrival/drop-off, empty-driver-seat POV, passenger hail/pickup/ride/drop-off, revenue notification, office/glass-wall reaction, and drone-view urban aftermath.
- Minor known issues: AI UI text is readable enough for planning but should be manually cleaned for final video assets; the parking-lot beat reads more like an office pickup/drop-off zone than a fully explicit empty parking lot.
- Validation passed: `python3 -m py_compile tools/manual/generate_prompt_storyboard_image.py`, `python3 -m unittest discover -s tests -v` (17 tests), manifest/hash checks, signed URL/credential-like scan, and `git diff --check`.
