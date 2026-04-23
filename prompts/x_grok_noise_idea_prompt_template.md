# X/Grok Noise Idea Sourcing Prompt Template

아래 프롬프트는 `noise` 프로젝트의 수동 X/Grok 아이디어 수집용이다.
대뜸 "noise project"라고 묻지 말고, 반드시 의도·맥락·판정 기준·예시·타임윈도우를 포함한다.

```text
너는 X/Twitter 트렌드 리서처이자 소셜 콘텐츠 콘셉트 에디터다.

[작업 목적]
나는 "noise"라는 프로젝트를 진행 중이다. 여기서 noise는 단순 어그로나 분노 유발이 아니다.
목표는 "해석 충돌 설계"다. 즉, 사람들이 장면이 보여주는 것과 캡션이 단정하는 것 사이의 틈을 보고, 자기 세계관을 댓글로 드러내게 만드는 콘텐츠 아이디어를 찾는 것이다.

좋은 후보는 다음 조건을 만족한다.
- 기술/사건 자체보다 관계·역할·가치의 숨은 거래조건이 드러난다.
- 댓글이 작성자 조롱이 아니라 주장/장면/암묵 전제와 싸우게 만든다.
- 최소 4개 이상의 독립 댓글축이 생긴다.
- 반박 + 자기경험 + 세계관 확장 댓글이 예상된다.
- 보호집단 비하, 노골적 성적화, 허위 단정, 특정 개인 공격 없이도 작동한다.

[타임윈도우]
- 기준 시각: {RUN_AT_KST}
- 우선 조사 범위: 기준 시각으로부터 최근 {WINDOW_HOURS}시간 이내의 X/Twitter 포스팅, 트렌드, 인용/댓글 흐름.
- 최근 {WINDOW_HOURS}시간 안에서 충분한 신호가 없으면 최근 7일까지 넓혀도 되지만, 각 후보마다 `time_window_used`에 "24h", "48h", "72h", "7d" 중 하나를 명시하라.
- 오래된 밈/상시 논쟁은 `freshness_risk`를 medium/high로 표시하라.

[우선 소스]
- 한국어 X 트렌드와 한국 사용자 반응을 우선한다.
- 필요하면 글로벌 X 포스트를 참고하되, 한국어 맥락으로 번역 가능한 논쟁만 고른다.
- 홈 피드에서 관찰된 신호, X 검색으로 확인한 신호, Grok가 찾은 실시간 신호를 구분한다.
- 링크나 계정명이 확실하지 않으면 지어내지 말고 `source_confidence`를 low로 둔다.

[검색/관찰 방향]
다음 유형의 신호를 찾아라.
1. 편의가 케어/감시/복무/친밀성으로 넘어가는 장면
2. 언어 순화와 현실 회피가 충돌하는 이슈
3. 가족·연애·직장·팬덤·플랫폼에서 암묵적 계약이 드러나는 이슈
4. AI/자동화가 노동·취향·전문성의 가치를 다시 계산하게 만드는 이슈
5. 안전·보호 명분이 사생활·자율성과 충돌하는 이슈
6. 계절/소비/취미처럼 가벼워 보이지만 계급감각이나 자기기만이 묻어나는 이슈

[좋은 예시]
예시 A — 플랫폼 연령 인증
- 관찰 신호: X 홈 피드에서 Discord/플랫폼 연령 인증 관련 반응이 큼.
- 표면 주장: 아이 보호를 위해 플랫폼 연령 인증은 더 촘촘해져야 한다.
- 암묵 전제: 안전을 위해 익명성과 사생활을 조금 포기하는 것이 정상 비용이 된다.
- 장면 훅: 밤 11시, 청소년이 채팅 앱에 들어가려는데 보호자 인증 링크가 가족 단톡방으로 전송된다.
- 댓글축: 청소년 보호 vs 사생활 침해 / 플랫폼 책임 vs 사용자 자유 / 부모 보호 vs 과잉 개입 / 안전 비용 vs 일상 불편
- 좋은 이유: 안전이라는 선한 명분과 감시의 불쾌감이 동시에 살아 있다.

예시 B — 저출산·저출생 용어 논쟁
- 관찰 신호: 용어 변경에 대해 언어 순화 vs 현실 회피 댓글이 붙음.
- 표면 주장: 문제를 바꾸기 어렵다면 먼저 문제를 부르는 말을 바꿀 수 있다.
- 암묵 전제: 사회는 현실을 고치기 전에도 언어를 바꿔 책임감과 불편함을 조절하려 한다.
- 장면 훅: 회의실에서 담당자가 보고서의 "저출산"을 "저출생"으로 일괄 수정하지만 수치 그래프는 그대로다.
- 댓글축: 배려 vs 현실 왜곡 / 표현 개선 vs 정책 부재 / 당사자 감수성 vs 행정 보여주기
- 좋은 이유: 단어 하나가 가치관·정책·체감 현실을 동시에 건드린다.

예시 C — AI 광고 제작
- 관찰 신호: X에서 제품 사진 1장으로 광고 영상을 만드는 AI 워크플로가 확산됨.
- 표면 주장: 제품 사진 한 장이면 광고팀 없이도 광고가 만들어진다.
- 암묵 전제: 창작 결과물의 가치는 팀·경험·취향보다 빠른 도구 조합으로 재계산될 수 있다.
- 장면 훅: 동네 가게 사장이 고양이 사료 사진 하나로 광고 영상을 만들고, 옆의 디자이너가 조용히 본다.
- 댓글축: 민주화 vs 직업 대체 / 속도 vs 감각 / 소상공인 기회 vs 전문성 평가절하
- 좋은 이유: 편의와 노동 가치의 손실이 한 장면에 같이 보인다.

[나쁜 예시]
- "요즘 애들은 문제다"처럼 특정 집단을 비하해야만 반응이 나는 안.
- "정치인/연예인 X는 나쁘다"처럼 특정 개인 공격으로만 작동하는 안.
- "AI가 다 끝낸다"처럼 너무 넓고 이미 닳은 단정.
- 장면과 캡션이 완전히 같은 말을 해서 댓글 여지가 없는 안.

[출력 요구]
- 후보 12개를 제시하라.
- 그중 top_pick 3개를 별도로 고르라.
- 각 후보는 실제 X 신호에서 출발하되, 허위 링크/허위 숫자를 만들지 말라.
- 설명 문장이나 마크다운 없이, 반드시 아래 `<noise_json>` 태그 안에 valid JSON만 넣어라.
- `likely_comment_axes`는 배열로 반환하라.
- `storyboard_seed`는 6컷 배열로 반환하라. 각 컷은 `function`을 utility/care/intimacy/authority/aftermath 중 하나로 분류하라.

<noise_json>{
  "run_context": {
    "run_at_kst": "{RUN_AT_KST}",
    "primary_time_window_hours": {WINDOW_HOURS},
    "market": "Korean X/Twitter first, global X only if Korean-context transferable",
    "project_intent": "interpretation-collision design, not rage bait"
  },
  "suggested_search_queries": [""],
  "ideas": [
    {
      "idea_id": "grok-001",
      "topic": "",
      "time_window_used": "24h|48h|72h|7d",
      "source_type": "x_home_feed|x_search|x_trend|grok_synthesis",
      "source_confidence": "high|medium|low",
      "observed_signal_on_x": "",
      "surface_claim": "",
      "implicit_premise": "",
      "viewer_meta_message": "사람들이 '작성자는 결국 이렇게 보는구나'라고 읽을 부분",
      "scene_caption_gap": "장면이 보여주는 것과 문장이 단정하는 것의 틈",
      "main_axis": "",
      "support_axis": "",
      "background_axis": "",
      "likely_comment_axes": [""],
      "expected_comment_archetypes": ["논리 교정형", "젠더/세대/계급 해석형", "존재론 방어형", "욕망/소비형"],
      "scene_hook": "",
      "storyboard_seed": [
        {"cut": 1, "function": "utility", "scene": "", "expected_comments": [""]},
        {"cut": 2, "function": "utility", "scene": "", "expected_comments": [""]},
        {"cut": 3, "function": "care", "scene": "", "expected_comments": [""]},
        {"cut": 4, "function": "authority", "scene": "", "expected_comments": [""]},
        {"cut": 5, "function": "intimacy", "scene": "", "expected_comments": [""]},
        {"cut": 6, "function": "aftermath", "scene": "", "expected_comments": [""]}
      ],
      "risk_note": "",
      "discard_if": ["작성자 조롱만 남는 경우", "보호집단 비하가 필요한 경우", "허위 사실 단정이 필요한 경우"],
      "freshness_risk": "low|medium|high",
      "why_useful_for_noise_pipeline": "",
      "score": {
        "interpretation_conflict": 1,
        "rebuttal_pull": 1,
        "self_projection_pull": 1,
        "visual_caption_gap": 1,
        "brand_damage_risk": 1
      }
    }
  ],
  "top_picks": [
    {"idea_id": "grok-001", "reason": ""}
  ]
}</noise_json>
```
