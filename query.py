import zhipuai
from ingest_data import initPinecone
from prepare import PINECONE_ENVIRONMENT, PINECONE_API_KEY, PINECONE_INDEX_NAME, CHATGLM_KEY


def match_query(ques):
    embedding = zhipuai.model_api.invoke(
        model="text_embedding",
        prompt=ques
    )['data']['embedding']

    p = initPinecone()
    index = p.Index(PINECONE_INDEX_NAME)
    res = index.query(embedding, top_k=4, include_metadata=True)
    return res

if __name__ == '__main__':
    print('input query')
    query = input()
    match_query(query)
