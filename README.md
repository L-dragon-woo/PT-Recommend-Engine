# PT-Recommend-Engine

PT 추천 에이전트 예제입니다. Neo4j 그래프 필터링, 벡터 검색, OpenAI LLM 생성을 연결합니다.

## 실행 전 준비

`.env` 파일에 아래 값을 넣어야 합니다.

```env
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
OPENAI_MODEL=gpt-4-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
NEO4J_VECTOR_INDEX=exercise_descriptions
```

## 실행

```powershell
python pt_agent.py
```

## 현재 확인된 실행 실패 원인

`.env`가 비어 있으면 실행되지 않습니다. 현재 코드는 이 경우 아래처럼 바로 안내 메시지를 출력합니다.

```text
실행 실패: 필수 환경변수가 없습니다. .env 파일에 다음 값을 설정하세요: OPENAI_API_KEY, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
```
