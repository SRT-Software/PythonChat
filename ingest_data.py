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
import os
import ast
import json
import subprocess

filePath = 'docs'
zhipuai.api_key = CHATGLM_KEY

milvus_collection_name = "pdf_milvus"

data_path = "data.txt"
meta_path = "meta_path"

chunk_index = 0

def split_list(long_list, chunk_size):
    return [long_list[i:i + chunk_size] for i in range(0, len(long_list), chunk_size)]


def initPinecone():

    try:
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        return pinecone
    except Exception:
        print(Exception)


def initMilvus():
    while True:
        try:
            connections.connect("default", host="localhost", port="19530")
            break
        except Exception as e:
            cmd_command = 'docker-compose down'  # 替换为您要执行的实际CMD命令
            subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            cmd_command = 'docker-compose up -d'  # 替换为您要执行的实际CMD命令
            subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
    if not utility.has_collection(milvus_collection_name):
        # 向量个数
        num_vec = 10000
        # 向量维度
        vec_dim = 1024
        # metric_type: 向量相似度度量标准, MetricType.IP是向量内积; MetricType.L2是欧式距离
        fields = [
            FieldSchema(name="index", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=vec_dim),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=1024)
        ]

        schema = CollectionSchema(fields, milvus_collection_name)
        pdf_milvus = Collection(milvus_collection_name, schema)
        return pdf_milvus
    else:
        pdf_milvus = Collection(milvus_collection_name)
        return pdf_milvus

def get_files_in_directory(directory_path):
    file_list = []
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_list.append(file_path)
    return file_list

def get_single_file_doc(path, model="normal"):
    rawDocs = []
    pdfLoader = PyPDFLoader(file_path=path)
    doc = pdfLoader.load()
    for d in doc:
        rawDocs.append(d)

    if model == 'ali':
        textSplitter = SemanticTextSplitter(pdf=True)
    else:
        textSplitter = RecursiveCharacterTextSplitter(chunk_size=120, chunk_overlap=80)
    docs = textSplitter.split_documents(rawDocs)
    return docs
def getDocs(model="normal"):
    files_list = get_files_in_directory("docs")
    rawDocs = []
    for file in files_list:
        pdfLoader = PyPDFLoader(file_path=file)
        doc = pdfLoader.load()
        for d in doc:
            rawDocs.append(d)

    # directoryLoader = DirectoryLoader('docs', glob='*.pdf', loader_cls=PyPDFLoader)
    # rawDocs = directoryLoader.load()
    # rawDocs = rawDocs[10:20]

    # print(len(d))
    # rawDocs = []
    # for i in range(3):
    #     rawDocs.append(d[i+10])
    # splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=150)
    # s = splitter.split_documents(rawDocs)
    if model == 'ali':
        textSplitter = SemanticTextSplitter(pdf=True)
    else:
        textSplitter = RecursiveCharacterTextSplitter(chunk_size=120, chunk_overlap=80)
    docs = textSplitter.split_documents(rawDocs)
    return docs


def ingest(docs, database="pinecone"):
    # if not os.path.exists(data_path):
        # prepare basic vector
        # print('docs:\n', docs)
    global chunk_index
    content_list = [chunk.page_content for chunk in docs]
    # print('content', len(content_list))
    # print()
    # 字符embedding后 1024维向量
    embedding_list = []
    for i in range(len(content_list)):
        content = content_list[i]
        try:
            response = zhipuai.model_api.invoke(
                model="text_embedding",
                prompt=content
            )
            if 'data' in response:
                embedding_list.append(response['data']['embedding'])
                index = int(len(embedding_list) * 100 / len(content_list))
                progress = '[' + '=' * index + ' ' * (100 - index) + ']'
                print('\r', progress, f'{index}%', end='', flush=True)
        except Exception as e:
            print(e)
            i -= 1
    with open(data_path, 'a') as file:
        for embedding in embedding_list:
            file.write(f"{embedding}\n")

    # print("start read")
    # embedding_list = []
    # str_list = []
    # with open(data_path, 'r') as file:
    #     content = file.read()
    #     str_list = content.split('\n')
    # print("end read")
    # si = 0
    # for s in str_list:
    #     try:
    #         float_vector = ast.literal_eval(s)
    #         embedding_list.append(float_vector)
    #     except Exception as e:
    #         print(f"{str(e)}")
    #         print(si)
    #     si += 1
    #
    # print(len(embedding_list))
    tuple_list = []
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
    short_lists = split_list(tuple_list, 1000)

    if database == "pinecone":
        pineconeStorage = initPinecone()
        index = pineconeStorage.Index(PINECONE_INDEX_NAME)
        for list in short_lists:
            index.upsert(list)
    elif database == "milvus":
        milvus = initMilvus()
        # 把向量添加到刚才建立的表格中
        # ids可以为None，使用自动生成的id
        json_list = [json.dumps(item)for item in metadatas]
        # for jsons in json_list:
        #     print(len(jsons))
        # json_shorts = split_list(json_list, 1000)
        try:
            entities = [
                [i + globals()["chunk_index"] for i in range(len(embedding_list))],
                embedding_list,  # field embeddings
                json_list,  # field metadata
            ]

            # 确保插入操作成功
            insert_result = milvus.insert(entities)
            print(f"result: {insert_result}")
            # After final entity is inserted, it is best to call flush to have no growing segments left in memory
            milvus.flush()

            # 构建索引
            index = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": 128},
            }
            milvus.create_index("embeddings", index)
            globals()["chunk_index"] += len(embedding_list)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # connections.connect("default", host="localhost", port="19530")
    files = get_files_in_directory('docs')
    print('start')
    index = 0
    globals()["chunk_index"] = 0
    for file in files:
        if file.endswith('.pdf') and index > 44:
            print(f"file{index}: {file}, total: {len(files)}")
            doc = get_single_file_doc(file)
            ingest(docs=doc, database="milvus")
        index += 1
