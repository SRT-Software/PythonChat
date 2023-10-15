from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pinecone import Pinecone
from prepare import PINECONE_ENVIRONMENT, PINECONE_API_KEY, PINECONE_INDEX_NAME, CHATGLM_KEY
import pinecone
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
import zhipuai
from text_splitter.semantic_segmentation import SemanticTextSplitter
from text_splitter.pdf_loader import RapidOCRPDFLoader
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
  
import numpy as np
import json



filePath = 'docs'
zhipuai.api_key = CHATGLM_KEY

milvus_collection_name = "pdf_milvus"


def split_list(long_list, chunk_size):
    return [long_list[i:i + chunk_size] for i in range(0, len(long_list), chunk_size)]


def initPinecone():
    try:
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        return pinecone
    except Exception:
        print(Exception)

def initMilvus():
    connections.connect("default", host="localhost", port="19530")
    if not utility.has_collection(milvus_collection_name):
        # 向量个数
        num_vec = 10000
        # 向量维度
        vec_dim = 1024
        # metric_type: 向量相似度度量标准, MetricType.IP是向量内积; MetricType.L2是欧式距离
        fields = [
            FieldSchema(name="index", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=vec_dim),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        schema = CollectionSchema(fields, milvus_collection_name)
        pdf_milvus = Collection(milvus_collection_name, schema)
    else:
        pdf_milvus = Collection(milvus_collection_name)
        return pdf_milvus

def getDocs(model="normal"):
    directoryLoader = DirectoryLoader('docs', glob='*.pdf', loader_cls=PyPDFLoader)
    rawDocs = directoryLoader.load()
    if model == "normal":
      textSplitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=150)
    # print(len(d))
    # rawDocs = []
    # for i in range(3):
    #     rawDocs.append(d[i+10])
    # splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=150)
    # s = splitter.split_documents(rawDocs)
    elif model == 'ali':
        textSplitter = SemanticTextSplitter(pdf=True)
    docs = textSplitter.split_documents(rawDocs)
    return docs


def ingest(database="pinecone"):
    # prepare basic vector
    docs = getDocs()

    print('docs:\n', docs)
    content_list = [chunk.page_content for chunk in docs]
    print('content', len(content_list))
    print(content_list)
    # 字符embedding后 1024维向量
    embedding_list = []
    for content in content_list:
        response = zhipuai.model_api.invoke(
            model="text_embedding",
            prompt=content
        )
        if 'data' in response:
            embedding_list.append(response['data']['embedding'])
            print(len(embedding_list))
    tuple_list = []
    print(len(embedding_list[0]))
    print(docs[0])
    metadatas = []
    for i in range(len(embedding_list)):
        metadata = {
            'text': docs[i].page_content,
            'page': docs[i].metadata['page'],
            'source': docs[i].metadata['source']
        }
        d = {
            'id': 'vec' + str(i),
            'values': embedding_list[i],
            'metadata': metadata
        }
        tuple_list.append(d)
        metadatas.append(metadata)
    # 截短 防止太长一次不能插入
    short_lists = split_list(tuple_list, 200)
        

    if database == "pinecone":
        pineconeStorage = initPinecone()
        index = pineconeStorage.Index(PINECONE_INDEX_NAME)
        for list in short_lists:
            index.upsert(list)
    elif database == "milvus":  
        milvus = initMilvus()
        # 把向量添加到刚才建立的表格中
        # ids可以为None，使用自动生成的id
        json_list = [json.dumps(item) for item in metadatas]
        entities = [
          [i for i in range(len(embedding_list))],  # field index
          [embedding_list], # field embeddings
          [json_list],  # field metadata
        ]
        
        # 确保插入操作成功
        insert_result = milvus.insert(entities)
        # After final entity is inserted, it is best to call flush to have no growing segments left in memory
        milvus.flush() 
        

        # 构建索引
        index = {
          "index_type": "IVF_FLAT",
          "metric_type": "L2",
          "params": {"nlist": 128},
        }
        milvus.create_index("embeddings", index)





if __name__ == '__main__':
    # connections.connect("default", host="localhost", port="19530")
    ingest(database="milvus")
