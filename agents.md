# Noise Project Agent Rules

이 프로젝트에서는 아래 규칙을 항상 따른다.

## Canonical Context

- 핵심 문서는 아래 파일을 기준으로 유지한다.
- `/home/vboxuser/noise/README.md`
- `/home/vboxuser/noise/docs/architecture.md`
- `/home/vboxuser/noise/progress.md`
- `guivm` 사용 기준 문서는 `/home/vboxuser/Downloads/guivm_API_사용_메뉴얼.md` 와 `/home/vboxuser/ai_persona/agents.md` 의 검증 내용을 함께 따른다.
- GUIVM 실사용 기본 엔드포인트는 `/home/vboxuser/ai_persona/agents.md` 에서 검증된 `http://10.0.2.2:8765` 로 둔다.
- GitHub PAT 로컬 파일 경로는 `/home/vboxuser/ai_persona/.local/github_pat.txt` 를 그대로 재사용한다.

## Scope Discipline

- 이 프로젝트의 범위는 단순 문서화가 아니라 실제 실행 가능한 분석/생성 파이프라인, CLI, 샘플 입력, 검증 로그까지 포함한다.
- 핵심 목적은 `노이즈 생성` 자체가 아니라 댓글을 부르는 `해석 충돌 설계`를 구조화·재현하는 엔진을 만드는 것이다.
- 결과물은 코퍼스 분석, 갈등축 구조화, 장면/카피 설계, 리스크 필터, 운영 가이드를 하나의 번들로 산출해야 한다.

## GUIVM

- 현재 VM 실검증 기준 `guivm` 호출 기본값은 `http://10.0.2.2:8765` 이다.
- `http://127.0.0.1:8765` 는 이 VM 에서 기본값으로 가정하지 않는다.
- 사전 점검 엔드포인트는 `/v1/health`, `/v1/llm-gate/capacity` 이다.
- 실제 요청은 `POST /v1/llm-gate/infer` 를 기준으로 설계한다.
- `request_id`, `stage`, `symbol`, `prompt.compiled_prompt` 를 항상 포함한다.
- GUI 자동화는 직렬 처리와 최소 간격 제한을 전제로 하므로 요청 폭주를 설계하지 않는다.

## GitHub

- 원격 저장소는 GitHub 전용 저장소를 사용한다.
- PAT 값은 문서에 적지 말고 `/home/vboxuser/ai_persona/.local/github_pat.txt` 에서 읽어 사용한다.
- PAT 파일과 기타 비밀 정보는 반드시 gitignore 대상이어야 한다.

## Memory

- memory 루트는 `/home/vboxuser/noise/memory` 로 고정한다.
- Serena memory 저장 경로는 `/home/vboxuser/noise/memory/serena` 로 고정한다.
- 항상 작업 마지막에 Serena memory를 업데이트한다.
- Serena memory 파일명은 `키워드__YYYY-MM-DD-HHmm__상태.md` 형식을 따른다.
- 키워드는 소문자, 숫자, 하이픈만 사용하고 여러 키워드는 `+` 로 연결한다.
- 상태는 `plan`, `wip`, `passed`, `failed`, `blocked`, `rolledback`, `mixed`, `skipped` 중 하나만 사용한다.
- Serena memory는 300토큰 이내 초압축 형식으로만 기록한다.
- Serena memory에는 아래만 기록한다.
- 작업 일시
- 작업 배경 및 목표
- 수정된 파일 목록(절대경로)
- 주요 변경 사항 상세 설명
- 검증 결과(로그, 테스트 결과)
- 참조 문서/memory
- 다음 단계 또는 known issues
