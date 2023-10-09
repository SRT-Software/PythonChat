from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pinecone import Pinecone
from prepare import PINECONE_ENVIRONMENT, PINECONE_API_KEY, PINECONE_INDEX_NAME, CHATGLM_KEY
import pinecone
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
import zhipuai
from text_splitter.semantic_segmentation import SemanticTextSplitter
from text_splitter.pdf_loader import RapidOCRPDFLoader

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


def ingest():
    pineconeStorage = initPinecone()

    directoryLoader = DirectoryLoader('docs', glob='*.pdf', loader_cls=PyPDFLoader)
    d = directoryLoader.load()
    print(len(d))
    rawDocs = []
    for i in range(3):
        rawDocs.append(d[i+10])
    # splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=150)
    # s = splitter.split_documents(rawDocs)
    textSplitter = SemanticTextSplitter(pdf=True)
    docs = textSplitter.split_documents(rawDocs)
    print('docs:\n', docs)
    content_list = [chunk.page_content for chunk in docs]
    print('content', len(content_list))
    print(content_list)
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
    short_lists = split_list(tuple_list, 200)
    for list in short_lists:
        index.upsert(list)
    return index


if __name__ == '__main__':
    ingest()
