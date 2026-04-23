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
- [ ] git commit/push
- [ ] Serena memory 기록
- [ ] Telegram 알림
