#LangChain의 Neo4jGraph를 이용해 운동, 타겟 부위, 그리고 질환에 따른 금기(주의) 규칙을 그래프로 만든다.

import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph

load_dotenv()

# 1. Neo4j AuraDB 연결
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# 2. 초기 데이터 (노드 및 관계) 세팅 (Cypher 쿼리)
# 구조: (운동)-[:TARGETS]->(부위), (질환)-[:CONTRAINDICATED]->(운동)
# 설명(description)은 나중에 벡터 검색에 활용됩니다.
setup_query = """
// 1. 노드 생성
MERGE (lower:BodyPart {name: '하체'})
MERGE (waist_pain:Condition {name: '허리통증'})

MERGE (squat:Exercise {name: '스쿼트', description: '바벨을 짊어지거나 맨몸으로 앉았다 일어서는 전신 하체 운동. 코어와 척추에 강한 압력이 가해집니다.'})
MERGE (deadlift:Exercise {name: '데드리프트', description: '바닥에 있는 무거운 바벨을 들어 올리는 전신 후면 사슬 운동. 척추 기립근에 매우 큰 부하가 걸립니다.'})
MERGE (bridge:Exercise {name: '글루트 브릿지', description: '바닥에 누워 골반을 들어올려 둔근과 햄스트링을 수축시키는 운동. 척추를 바닥에 대고 하므로 허리 부담이 매우 적습니다.'})
MERGE (lunge:Exercise {name: '런지', description: '한 발을 앞으로 내밀고 무릎을 굽히는 하체 운동. 코어 안정성이 필요하지만 척추 압박은 스쿼트보다 덜합니다.'})

// 2. 타겟 부위 관계 설정
MERGE (squat)-[:TARGETS]->(lower)
MERGE (deadlift)-[:TARGETS]->(lower)
MERGE (bridge)-[:TARGETS]->(lower)
MERGE (lunge)-[:TARGETS]->(lower)

// 3. 전문가 규칙 (금기/주의사항) 관계 설정 -> 핵심 포인트!
MERGE (waist_pain)-[:CONTRAINDICATED]->(deadlift)
MERGE (waist_pain)-[:CONTRAINDICATED]->(squat)
"""

graph.query(setup_query)
print("Graph 데이터 세팅이 완료되었습니다.")