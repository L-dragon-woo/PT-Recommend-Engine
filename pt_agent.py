import json
import os

from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

load_dotenv()

DEFAULT_CHAT_MODEL = "gpt-4-turbo"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_INDEX_NAME = "exercise_descriptions"
REQUIRED_ENV_VARS = (
    "OPENAI_API_KEY",
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD",
)


class PTResponse(BaseModel):
    user_message: str = Field(description="고객에게 전달하는 친절하고 쉬운 운동 가이드 및 주의사항")
    trainer_report: str = Field(description="전문 트레이너를 위한 추천 근거, 필터링된 위험 운동, 역학적 소견")


parser = JsonOutputParser(pydantic_object=PTResponse)


def validate_environment() -> None:
    missing_vars = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing_vars:
        missing_list = ", ".join(missing_vars)
        raise RuntimeError(
            "필수 환경변수가 없습니다. "
            f".env 파일에 다음 값을 설정하세요: {missing_list}"
        )


def build_clients():
    validate_environment()

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", DEFAULT_CHAT_MODEL),
        temperature=0,
    )
    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    )
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
    )
    vector_store = Neo4jVector.from_existing_index(
        embedding=embeddings,
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE", "neo4j"),
        index_name=os.getenv("NEO4J_VECTOR_INDEX", VECTOR_INDEX_NAME),
        node_label="Exercise",
        text_node_property="description",
        embedding_node_property="embedding",
    )

    return llm, graph, vector_store


def get_custom_pt_recommendation(target_part: str, user_condition: str):
    llm, graph, vector_store = build_clients()

    cypher_query = f"""
    MATCH (e:Exercise)-[:TARGETS]->(b:BodyPart {{name: '{target_part}'}})
    WHERE NOT (:Condition {{name: '{user_condition}'}})-[:CONTRAINDICATED]->(e)
    RETURN e.name AS safe_exercise
    """
    safe_exercises_result = graph.query(cypher_query)
    safe_exercise_names = [record["safe_exercise"] for record in safe_exercises_result]

    if not safe_exercise_names:
        return {"error": "조건에 맞는 안전한 운동을 찾을 수 없습니다."}

    context_docs = []
    for exercise_name in safe_exercise_names:
        docs = vector_store.similarity_search(exercise_name, k=1)
        context_docs.extend([doc.page_content for doc in docs])

    context_text = "\n".join(context_docs)

    prompt = ChatPromptTemplate.from_template(
        """당신은 전문 PT 트레이너이자 재활 전문가입니다.
아래의 제공된 [안전한 운동 리스트]와 [상세 설명]을 바탕으로 사용자를 위한 가이드를 작성하세요.
반드시 그래프 필터링 결과를 우선시해야 합니다.
아래 [안전한 운동 리스트]에 포함된 운동은 이미 금기 운동이 제외된 결과이므로, 이를 다시 위험하거나 부적합하다고 판단하면 안 됩니다.
답변에는 [안전한 운동 리스트]에 포함된 운동만 사용하세요.
리스트에 있는 운동이 여러 개라면 각 운동을 안전한 선택지로 설명하세요.

사용자 목표 부위: {target_part}
사용자 현재 질환/상태: {user_condition}

[안전한 운동 리스트 (그래프 필터링 됨)]
{safe_exercises}

[운동 상세 설명 (벡터 검색 됨)]
{context}

{format_instructions}
"""
    )

    chain = prompt | llm | parser
    response = chain.invoke(
        {
            "target_part": target_part,
            "user_condition": user_condition,
            "safe_exercises": ", ".join(safe_exercise_names),
            "context": context_text,
            "format_instructions": parser.get_format_instructions(),
        }
    )
    return response


if __name__ == "__main__":
    print("--- 맞춤형 PT 에이전트 실행 ---")
    try:
        result = get_custom_pt_recommendation(
            target_part="하체",
            user_condition="허리통증",
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as exc:
        print(f"실행 실패: {exc}")
