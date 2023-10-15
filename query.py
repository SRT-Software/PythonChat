import zhipuai
from ingest_data import initPinecone, initMilvus
from prepare import PINECONE_ENVIRONMENT, PINECONE_API_KEY, PINECONE_INDEX_NAME, CHATGLM_KEY
from milvus import Milvus, IndexType, MetricType
import numpy as np


def match_query(ques, database="pinecone"):
    embedding = zhipuai.model_api.invoke(
        model="text_embedding",
        prompt=ques
    )['data']['embedding']
    text_list = []
    source_list = []
    if database == "pinecone":
        p = initPinecone()
        index = p.Index(PINECONE_INDEX_NAME)
        res = index.query(embedding,
                          top_k=4,
                          include_metadata=True,
        )
        text_list = [text['metadata']['text'] for text in query['matches']]
        source_list = [(text['metadata']['source'], text['metadata']['page']) for text in query['matches']]
        return text_list, source_list
    else:
        milvus = initMilvus;
        # 转换查询向量为 NumPy 数组
        query_vector_np = np.array([embedding], dtype=np.float32)

        # 执行搜索
        search_param = {
            'nprobe': 10  # 指定搜索时检查的聚类中心数量
        }
        status, results = milvus.search('pdf_collection', query_vector_np, top_k=5, params=search_param)

        # 确保搜索操作成功
        if status.OK():
            print('Search completed successfully.')
            for result in results[0]:
                print('Vector ID:', result.id, ' Distance:', result.distance)
                metadata = milvus.get_entity_by_id(collection_name='pdf_collection', ids=[result.id])
                text_list.append(metadata['text'])
                source_list.append((metadata['source'], metadata['page']))
        else:
            print('Error occurred while searching:', status)
        
        return text_list, source_list



if __name__ == '__main__':
    print('input query')
    query = input()
    match_query(query)
