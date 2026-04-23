# Noise Engine Implementation Plan

> **For Hermes:** implement this plan with strict TDD where code is introduced, validate with real guivm, then commit and push.

**Goal:** Build a runnable project in `/home/vboxuser/noise` that turns an issue brief and comment corpus into a structured interpretation-collision content bundle.

**Architecture:** Use a hybrid pipeline. First, deterministic preprocessing deduplicates and tags comments into reusable axes/risk buckets. Second, a guivm-backed JSON generation layer turns the structured input into concept/storyboard/copy/safety bundles. Third, a CLI saves JSON+Markdown artifacts and runtime logs.

**Tech Stack:** Python 3.11 stdlib + requests, unittest, argparse, GitHub HTTPS remote with reused PAT.

---

### Task 1: Scaffold project docs and metadata
**Objective:** Create the base repository structure and canonical docs.
**Files:**
- Create: `/home/vboxuser/noise/agents.md`
- Create: `/home/vboxuser/noise/README.md`
- Create: `/home/vboxuser/noise/docs/architecture.md`
- Create: `/home/vboxuser/noise/progress.md`
- Create: `/home/vboxuser/noise/pyproject.toml`
- Create: `/home/vboxuser/noise/.gitignore`

### Task 2: Write failing tests for corpus loading and tagging
**Objective:** Define expected behavior for comment ingestion, dedupe, axis tagging, and drift detection.
**Files:**
- Create: `/home/vboxuser/noise/tests/test_corpus.py`
- Create: `/home/vboxuser/noise/tests/test_pipeline.py`

### Task 3: Implement deterministic corpus analysis
**Objective:** Add loaders, normalizers, keyword-based taggers, archetype aggregation, and risk summaries.
**Files:**
- Create: `/home/vboxuser/noise/src/noise_engine/corpus.py`
- Create: `/home/vboxuser/noise/src/noise_engine/models.py`
- Create: `/home/vboxuser/noise/src/noise_engine/__init__.py`

### Task 4: Write failing tests for guivm prompt assembly and bundle compilation
**Objective:** Lock down prompt contents, JSON schema expectations, and file outputs before implementation.
**Files:**
- Modify: `/home/vboxuser/noise/tests/test_pipeline.py`
- Create: `/home/vboxuser/noise/tests/test_cli.py`

### Task 5: Implement guivm client, prompt templates, pipeline, and CLI
**Objective:** Build the runtime that calls guivm, validates JSON, and emits bundle artifacts.
**Files:**
- Create: `/home/vboxuser/noise/src/noise_engine/guivm.py`
- Create: `/home/vboxuser/noise/src/noise_engine/prompting.py`
- Create: `/home/vboxuser/noise/src/noise_engine/pipeline.py`
- Create: `/home/vboxuser/noise/src/noise_engine/cli.py`
- Create: `/home/vboxuser/noise/prompts/prompt_1_tension_analyzer.md`
- Create: `/home/vboxuser/noise/prompts/prompt_2_comment_simulator.md`
- Create: `/home/vboxuser/noise/prompts/prompt_3_angle_selector.md`
- Create: `/home/vboxuser/noise/prompts/prompt_4_storyboard_director.md`
- Create: `/home/vboxuser/noise/prompts/prompt_5_copy_director.md`
- Create: `/home/vboxuser/noise/prompts/prompt_6_safety_editor.md`
- Create: `/home/vboxuser/noise/prompts/prompt_bundle_orchestrator.md`

### Task 6: Add sample brief and corpus fixtures
**Objective:** Provide a realistic demo input based on the humanoid household-care case.
**Files:**
- Create: `/home/vboxuser/noise/examples/humanoid-household/brief.md`
- Create: `/home/vboxuser/noise/examples/humanoid-household/comments.jsonl`

### Task 7: Validate locally and against real guivm
**Objective:** Run unit tests, guivm health/capacity checks, and an end-to-end sample bundle generation.
**Files:**
- Runtime output: `/home/vboxuser/noise/runs/...`

### Task 8: Finalize docs, progress log, Serena memory, git push, Telegram notification
**Objective:** Record implementation details, create the remote repo, push commits, and send completion notice.
**Files:**
- Create: `/home/vboxuser/noise/memory/serena/noise-engine__YYYY-MM-DD-HHmm__passed.md`
- Modify: `/home/vboxuser/noise/README.md`
- Modify: `/home/vboxuser/noise/docs/architecture.md`
- Modify: `/home/vboxuser/noise/progress.md`
