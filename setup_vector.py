#AuraDB는 노드의 속성을 임베딩하여 벡터 검색을 지원
#LangChain의 Neo4jVector를 사용해 인덱스를 생성
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector

load_dotenv()

embeddings = OpenAIEmbeddings()

# Exercise 노드의 'description' 텍스트를 임베딩하여 벡터 인덱스 생성
vector_index = Neo4jVector.from_existing_graph(
    embedding=embeddings,
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    database=os.getenv("NEO4J_DATABASE", "neo4j"),
    index_name='exercise_descriptions',
    node_label='Exercise',
    text_node_properties=['description'],
    embedding_node_property='embedding',
)

print("Vector 인덱스 생성이 완료되었습니다.")
