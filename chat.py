import zhipuai
from query import match_query
import json

QA_TEMPLATE = 'You are a helpful AI assistant. Use the following pieces of context to answer the question at the end.' \
              'If you do not know the answer, just say you do not know. DO NOT try to make up an answer.If the ' \
              'question is not related to the context, politely respond that you are tuned to only answer questions ' \
              'that are related to the context.' \
              '{context}' \
              'Question: {question}' \
              'Helpful answer in markdown:'

Message = {
    'text': ''
}

def chatbot(ques):
    print(ques)
    query = match_query(ques)
    text_list = [text['metadata']['text'] for text in query['matches']]
    response = zhipuai.model_api.sse_invoke(
        model="chatglm_pro",
        prompt=[
            {"role": "user", "content": 'please help me summary the {}'.format(text_list)},
        ],
        temperature=0.95,
        top_p=0.7,
        incremental=True
    )
    return response

if __name__ == '__main__':
    chatbot()
