# Noise Architecture

## 1. Product definition

Noise의 목적은 사람을 화나게 하는 문장을 찍어내는 것이 아니다.
목표는 다음 3가지를 동시에 만족하는 설계안을 만드는 것이다.

1. 댓글이 주장과 싸우게 만든다.
2. 장면이 캡션보다 더 많은 뜻을 품게 만든다.
3. 작성자 조롱/혐오/성적화 드리프트를 통제한다.

## 2. Pipeline

### A. Deterministic corpus pass
- 입력 코퍼스를 JSONL/JSON/TXT/CSV에서 읽는다.
- whitespace-normalized 기준으로 중복을 계산한다.
- 규칙 기반 키워드 사전으로 아래를 태깅한다.
  - reaction modes
  - emotions
  - defended values
  - targets
  - archetypes
  - conflict axes
  - off-target drift

이 단계 산출물은 `corpus-analysis.json` 으로 저장된다.

### B. Prompt orchestration
- `prompts/` 아래 6개 모듈 프롬프트를 보존한다.
- live 모드에서는 `prompt_bundle_orchestrator.md` 로 1회 infer 한다.
- 브리프와 corpus analysis JSON을 함께 주입한다.
- 출력은 strict JSON으로 강제한다.
- offline 모드에서는 deterministic fallback client가 동일한 bundle schema를 채운다.

### C. Bundle assembly
- 생성 결과를 검증한다.
- `bundle.json`, `bundle.md`, `guivm-response.json`, `prompt.txt`를 저장한다.

## 3. Risk model

off-target drift 카운터:
- `author_attack`
- `sexualization`
- `protected_class_hate`

이 수치 자체는 완전한 moderation이 아니라 early warning이다.

## 4. Current implementation constraints

- 실제 guivm는 분당 1회/최소간격 60초 전제를 가진다.
- 따라서 staged 6-call 대신 batch 1-call orchestration을 기본값으로 사용한다.
- live CLI는 `--wait-timeout-sec` 로 capacity 대기 상한을 줄일 수 있고, 초과 시 명시적 timeout error를 반환한다.
- 필요하면 나중에 staged mode를 추가할 수 있다.

## 5. Validation strategy

- unit test: `python3 -m unittest discover -s tests -v`
- runtime doctor: health/capacity 확인
- end-to-end demo: humanoid-household 샘플 브리프/코퍼스로 실제 bundle 생성
