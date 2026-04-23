# Noise Progress

## Milestone 1: Project scaffold
- [x] `/home/vboxuser/noise` 생성
- [x] `agents.md` 작성
- [x] `pyproject.toml`, `.gitignore`, `README.md`, `docs/architecture.md`, `docs/plans/...` 작성

## Milestone 2: Deterministic analysis layer
- [x] 코퍼스 로더(JSONL/JSON/TXT/CSV)
- [x] 정규화 및 중복 계산
- [x] archetype/axis/risk 규칙 기반 태깅

## Milestone 3: Runtime layer
- [x] guivm client 구현
- [x] batch orchestrator prompt 구현
- [x] CLI `doctor`, `run`, `demo` 구현
- [x] bundle JSON/Markdown/raw response 저장 구현

## Milestone 4: Validation
- [x] unit test 통과
- [x] guivm doctor 실검증
- [x] guivm direct smoke 실검증 (`noise-smoke-20260423-a` -> `{\"ok\": true, \"summary\": \"ping\"}`)
- [x] offline demo end-to-end 실검증 (`/home/vboxuser/noise/runs/demo-offline`)
- [x] live capacity-timeout hardening (`--wait-timeout-sec`, busy slot 시 JSON error 반환)
- [x] git commit/push
- [x] Serena memory 기록
- [x] Telegram 알림

## Milestone 5: Manual X/Grok idea sourcing
- [x] BrowserOS fixed profile / X login 상태에서 홈 피드 수동 점검
- [x] Grok prompt 수동 작성/투입 및 응답 수집
- [x] Grok prompt engineering 보강: 의도/맥락/타임윈도우/검색방향/좋은 예시/나쁜 예시/점수 스키마 포함
- [x] 보강 후 기준 storyboard 후보 3개 추가 저장 (`outputs/storyboards/2026-04-23-post-prompt-engineering/`)
- [x] Grok 응답 parser 시행착오 반영 (`prompt echo`의 빈 `<noise_json>` 스키마를 피하고 non-empty answer 선택)
- [x] 아이디어 11개를 txt 파일로 저장
- [x] `idea-status.tsv` + `idea-log.jsonl` 로 collected/storyboarded 상태 구분
- [x] 스토리보드 3개 버전 저장
- [x] skill 등록 (`noise-x-grok-manual-idea-sourcing`)
- [x] git commit/push

## Milestone 6: Refreshed Grok v3 synthesis + storyboard images
- [x] 최근 Serena memory 및 기존 post-prompt-engineering 후보 확인
- [x] BrowserOS X home 재캡처 (`x-home-capture-v3.json`)
- [x] 업데이트된 engineered prompt로 Grok 재질의 (`grok-prompt-v3-engineered.txt`)
- [x] Grok v3 응답 12개 파싱 (`grok-ideas-v3-parsed.json`)
- [x] 기존 11개 아이디어 + v2 후보 + v3 12개를 종합해 storyboard 후보 3개 작성 (`outputs/storyboards/2026-04-23-all-ideas-v3/`)
- [x] GUIVM 점유 확인; Hermes image tool은 `FAL_KEY environment variable not set` 로 실패
- [x] 이미지 경로 제공을 위해 local storyboard PNG fallback 3개 생성 (`outputs/storyboard-images/2026-04-23-local-storyboard-v3/`)
- [x] 이미지 파일/manifest 및 vision inspection 검증

## Milestone 7: GUIVM Seoul 9-shot storyboard generation
- [x] Storyboard image prompt updated: Korea/contemporary Seoul setting required
- [x] Storyboard format updated from 3x2/6 panels to 3x3/9 numbered shots
- [x] Prompt now asks for professional director-style shooting plan: varied staging, shot sizes, angles, reaction/insert/cutaway shots
- [x] GUIVM capacity retried after previous stockpile stop; live generation succeeded
- [x] GUIVM PNG outputs saved under `outputs/storyboard-images/2026-04-23-guivm-seoul-9shot-v3/`
- [x] Manifest/raw logs saved with signed remote image URLs redacted
- [x] Vision inspection confirmed all 3 generated images are 3x3 / 9-shot sheets with contemporary Korea/Seoul cues

## Milestone 8: Seedance-ready storyboard reference generation
- [x] Runway Seedance 2.0 guide reviewed and distilled into prompt rules
- [x] Storyboard helper updated for Reference-mode use: `use Image 1 as a storyboard to guide the scenes`
- [x] Rigid 3x3 requirement removed; prompt now requests 6-9 clear numbered shots with readability-first layout
- [x] Prompt strengthened for positive/outcome-focused language, visual subject/location continuity, camera/lighting/performance cues, and low text reliance
- [x] GUIVM generated 3 Seedance-ready storyboard reference images in `outputs/storyboard-images/2026-04-23-guivm-seedance-v3/`
- [x] Vision inspection confirmed multi-shot sequence, modern Seoul/Korea cues, and cinematic director-style planning
