# Noise

Noise는 `어그로 생성기`가 아니라 댓글을 부르는 `해석 충돌 설계 엔진`이다.

핵심 아이디어:
- 댓글 데이터부터 구조화한다.
- 장면과 문장 사이의 틈을 설계한다.
- 주장보다 암묵 전제와 시청자 메타해석을 다룬다.
- 작성자 조롱/성적화/혐오로 흐르는 안은 걸러낸다.

## What it does

입력:
- 이슈 브리프 1개
- 댓글 코퍼스 1개

출력:
- concept sheet
- storyboard sheet
- copy sheet
- risk sheet
- evaluation sheet
- operating sheet
- corpus analysis JSON
- guivm raw response log

## Project layout

- `src/noise_engine/`: 코어 로직
- `prompts/`: 6개 모듈 프롬프트 + 일괄 오케스트레이터
- `examples/humanoid-household/`: 샘플 브리프와 코퍼스
- `docs/architecture.md`: 구조 설명
- `progress.md`: 구현/검증 기록
- `memory/serena/`: 초압축 작업 메모

## Commands

테스트:
- `python3 -m unittest discover -s tests -v`

GUIVM 상태 점검:
- `PYTHONPATH=src python3 -m noise_engine.cli doctor --base-url http://10.0.2.2:8765`

GUIVM live smoke:
- `PYTHONPATH=src python3 -m noise_engine.cli smoke --base-url http://10.0.2.2:8765`

샘플 번들 생성:
- offline deterministic fallback: `PYTHONPATH=src python3 -m noise_engine.cli demo --offline --output-dir /home/vboxuser/noise/runs/demo`
- live guivm mode: `PYTHONPATH=src python3 -m noise_engine.cli demo --base-url http://10.0.2.2:8765 --output-dir /home/vboxuser/noise/runs/demo-live`

직접 실행:
- live: `PYTHONPATH=src python3 -m noise_engine.cli run --brief /path/to/brief.md --comments /path/to/comments.jsonl --output-dir /path/to/out`
- offline: `PYTHONPATH=src python3 -m noise_engine.cli run --offline --brief /path/to/brief.md --comments /path/to/comments.jsonl --output-dir /path/to/out`

## Design choices

1. 코퍼스 분석은 규칙 기반으로 먼저 구조화한다.
2. 최종 번들은 guivm text infer 1회로 생성한다.
3. 모듈 프롬프트 6종은 파일로 별도 보존해 추후 staged mode로 확장할 수 있다.
4. 기본 base URL은 ai_persona에서 실검증된 `http://10.0.2.2:8765` 를 재사용한다.
