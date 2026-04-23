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
- [x] Grok 응답 parser 시행착오 반영 (`prompt echo`의 빈 `<noise_json>` 스키마를 피하고 non-empty answer 선택)
- [x] 아이디어 11개를 txt 파일로 저장
- [x] `idea-status.tsv` + `idea-log.jsonl` 로 collected/storyboarded 상태 구분
- [x] 스토리보드 3개 버전 저장
- [x] skill 등록 (`noise-x-grok-manual-idea-sourcing`)
- [x] git commit/push
