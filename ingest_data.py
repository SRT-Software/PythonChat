from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pinecone import Pinecone
from prepare import PINECONE_ENVIRONMENT, PINECONE_API_KEY, PINECONE_INDEX_NAME, CHATGLM_KEY
import pinecone
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
import zhipuai
from text_splitter.semantic_segmentation import SemanticTextSplitter
from text_splitter.pdf_loader import RapidOCRPDFLoader
from milvus import Milvus, IndexType, MetricType
import numpy as np



filePath = 'docs'
zhipuai.api_key = CHATGLM_KEY


def split_list(long_list, chunk_size):
    return [long_list[i:i + chunk_size] for i in range(0, len(long_list), chunk_size)]


def initPinecone():
    try:
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        return pinecone
    except Exception:
        print(Exception)

def initMilvus():
    milvus = Milvus()
    milvus.connect(host='localhost', port='19530')
    collection = milvus.get_collection_by_name('pdf_collection')
    if collection is None:
        # 向量个数
        num_vec = 10000
        # 向量维度
        vec_dim = 1024
        # metric_type: 向量相似度度量标准, MetricType.IP是向量内积; MetricType.L2是欧式距离
        collection_param = {
            'collection_name': 'pdf_collection', 
            'dimension':vec_dim, 
            'index_file_size':1024, 
            'metric_type':MetricType.IP
        }
        milvus.create_collection(collection_param)  
        return milvus
    else:
        return milvus

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
    index = pineconeStorage.Index(PINECONE_INDEX_NAME)
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
      
        for list in short_lists:
            index.upsert(list)
    elif database == "milvus":  
        milvus = initMilvus()
        # 把向量添加到刚才建立的表格中
        # ids可以为None，使用自动生成的id
        # 转化为numpy vector
        vectors_np = np.array(embedding_list, dtype=np.float64)
        status, ids = milvus.insert(collection_name="pdf_collection",
                                    records=vectors_np,ids=None,
                                    extra_params=metadatas) # 返回这一组向量的ID
        
        # 确保插入操作成功
        if status.OK():
            print('Vectors inserted successfully.')
        else:
            print('Error occurred while inserting vectors:', status)
        

        # 构建索引
        index_param = {
            'nlist': 10,  # 索引聚类中心的数量
            'index_type': IndexType.IVF_FLAT  # 索引类型（这里使用 IVF_FLAT 索引）
        }

        status = milvus.create_index('pdf_collection', index_param)
        if status.OK():
            print('Index created successfully.')
        else:
            print('Error occurred while creating index:', status)





if __name__ == '__main__':
    ingest(database="milvus")
