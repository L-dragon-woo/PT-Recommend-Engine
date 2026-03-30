좋습니다. 그럼 목표는 기본 예제는 보존하고, 별도 AuraDB 인스턴스에서 네 그림 전체 흐름을 연습하는 겁니다.

1. 별도 인스턴스 구성
새 AuraDB 인스턴스를 하나 만드세요. 이름은 이렇게 두면 관리가 쉽습니다.

PT-Practice-Graph
PT-RAG-Practice
이 인스턴스는 연습 전용으로 쓰고, 기존 Instance01은 건드리지 않습니다.

준비되면 새 인스턴스 접속정보를 별도 .env.practice 같은 파일로 관리하면 좋습니다.

OPENAI_API_KEY=...
NEO4J_URI=neo4j+s://...
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
NEO4J_DATABASE=neo4j
2. 연습용 데이터 스키마
이 그림 흐름을 연습하려면 최소 스키마는 이 정도면 됩니다.

(:UserProfile {age, gender, pain_level, goal, experience, preferred_place})
(:Exercise {name, description, difficulty, movement_type})
(:BodyPart {name})
(:Condition {name})
(:Goal {name})
(:Equipment {name})
(:CaseNote {title, content, outcome})
관계는 이렇게 두면 충분합니다.

(e:Exercise)-[:TARGETS]->(b:BodyPart)
(c:Condition)-[:CONTRAINDICATED]->(e:Exercise)
(e:Exercise)-[:SUPPORTS]->(g:Goal)
(e:Exercise)-[:NEEDS_EQUIPMENT]->(q:Equipment)
(case:CaseNote)-[:MENTIONS]->(e:Exercise)
(case:CaseNote)-[:RELEVANT_TO]->(c:Condition)
이렇게 하면:

그래프 필터링 연습 가능
유사 사례 검색 연습 가능
하이브리드 추천 가능
3. 벡터 인덱스 대상
벡터 검색은 두 축으로 나누는 게 좋습니다.

운동 설명 검색
대상: Exercise.description
인덱스명: exercise_descriptions
상담 사례 검색
대상: CaseNote.content
인덱스명: case_notes
이렇게 나누면 네 그림의 오른쪽 흐름, 즉:

유사 운동 검색
유사 상담 사례 검색
둘 다 연습할 수 있습니다.
4. 실습 시나리오
네 그림 기준으로 5단계 실습으로 쪼개면 됩니다.

시나리오 A. 규칙 기반 1차 추천
입력:

36세 여성
목표: 하체 근력 강화
상태: 허리통증
운동경험: 초급
실습 목표:

CONTRAINDICATED 운동 제외
하체 타겟 운동만 조회
초급 우선 Top-N 선정
예상 학습 포인트:

그래프 필터링
Cypher 조건 조합
시나리오 B. 벡터 기반 의미 검색
입력 질의:

허리 부담이 적고 초보자가 따라하기 쉬운 하체 운동
둔근 자극이 크고 재활에 가까운 운동
실습 목표:

exercise_descriptions에서 의미 기반 검색
키워드 검색이 아니라 의미 검색 차이 체감
예상 학습 포인트:

ai.text.embed
db.index.vector.queryNodes
시나리오 C. 하이브리드 검색
입력:

허리 부담이 적은 하체 운동을 찾되, 허리통증 금기 운동은 제외
실습 목표:

벡터 검색으로 후보 찾기
그래프로 금기 제거
최종 Top-K 반환
예상 학습 포인트:

RAG + rule-based filtering 결합
시나리오 D. 유사 사례 검색
입력:

허리통증이 있는 초보자가 집에서 할 수 있는 운동 루틴
어깨통증이 있는 사용자 상담 사례
실습 목표:

CaseNote.content 벡터 검색
조건 노드와 사례 연결
비슷한 케이스 근거 제시
예상 학습 포인트:

사례 기반 추천
컨텍스트 구성
시나리오 E. 최종 응답 생성
입력:

프로필 + 그래프 결과 + 벡터 결과
실습 목표:

고객용 결과
전문가용 요약
추가 질문 생성
예상 학습 포인트:

네 그림의 출력1, 출력2 구조 연습
5. 실제 연습 순서
이 순서가 제일 깔끔합니다.

새 AuraDB 인스턴스 생성
연습용 그래프 데이터 적재
Exercise.description 벡터 인덱스 생성
CaseNote.content 벡터 인덱스 생성
Aura Query에서 Cypher 실습
Aura Query에서 임베딩 검색 실습
하이브리드 검색 실습
Aura Agent에서 Text2Cypher 연결
가능하면 Similarity Search도 연결
6. 추천 커밋/작업 단위
코드는 한 번에 크게 하지 말고 이렇게 끊는 게 좋습니다.

feat: add practice AuraDB schema for PT recommendation flow
feat: seed practice graph data for exercise and case retrieval
feat: add vector indexes for exercise descriptions and case notes
docs: add practice scenarios for graph and embedding queries
7. 현실적인 다음 액션
지금 당장 할 일은 이것 하나입니다.

새 AuraDB 인스턴스 생성
그 다음 내가 바로 이어서 해줄 수 있는 건 2가지입니다.

연습용 스키마 + 샘플 데이터 설계
시나리오별 Cypher/임베딩 쿼리
가장 자연스러운 다음 단계는 연습용 스키마 + 샘플 데이터 설계입니다.
원하면 내가 바로 노드/관계 구조 + 샘플 레코드 20개 수준으로 짜드리겠습니다.


---

나는 Neo4j AuraDB로 PT 추천/RAG 파이프라인을 연습하고 싶다.

중요 조건:
- 기존 기본 예제 인스턴스는 절대 건드리지 말 것
- 별도 AuraDB 인스턴스를 전제로 설계할 것
- 목표는 그래프 필터링 + 벡터 검색 + LLM 응답 생성의 전체 흐름을 연습하는 것
- 내가 연습하고 싶은 흐름은 다음과 같다:
  1. 사용자 구조화 프로필 생성
  2. 규칙 기반 1차 추천 후보 생성
  3. Top-N 후보 추출
  4. 벡터 검색으로 유사 운동/유사 사례 검색
  5. 그래프 조건과 결합한 하이브리드 검색
  6. 고객용 결과와 전문가용 결과 분리 생성
  7. 추가 질문 반영 후 재검색
  8. 최종 컨텍스트 조합
  9. 최종 추천 결과 생성

내가 원하는 산출물:
- 별도 AuraDB 인스턴스 기준의 연습용 스키마 설계
- 노드/관계 구조 제안
- PT 도메인 샘플 데이터 설계
- 벡터 인덱스 대상과 인덱스 이름 제안
- 실습 시나리오 단계별 구성
- Aura Query에서 바로 실행 가능한 Cypher 예시
- 임베딩 쿼리 예시
- 하이브리드 검색 예시
- Aura Agent에서 Text2Cypher와 Similarity Search를 어떻게 연결하면 되는지 가이드

추가 조건:
- 기존 데이터와 섞이지 않도록 분리 전략도 설명할 것
- 가능하면 초보자가 따라하기 쉬운 순서로 단계별로 정리할 것
- 필요하면 파일 구조, 시드 데이터 전략, 커밋 단위도 제안할 것
- 설명은 한국어로 해줄 것

먼저 아래 순서로 답해줘:
1. 전체 설계 요약
2. 연습용 AuraDB 스키마
3. 실습 시나리오 3~5개
4. 바로 실행할 첫 번째 단계
