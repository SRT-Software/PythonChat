import os
from dotenv import load_dotenv

# 指定.env文件的路径
dotenv_path = '.env'
load_dotenv(dotenv_path)

# 加载环境变量
load_dotenv(dotenv_path)

PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')

CHATGLM_KEY = os.getenv('CHATGLM_KEY')


if __name__ == '__main__':
    print(PINECONE_ENVIRONMENT)
    print(PINECONE_API_KEY)
    print(PINECONE_INDEX_NAME)
    print(CHATGLM_KEY)