import zhipuai
from query import match_query
import json

QA_TEMPLATE = 'You are a helpful AI assistant. Use the following pieces of context to answer the question at the end.' \
              'If you do not know the answer, just say you do not know. DO NOT try to make up an answer.If the ' \
              'question is not related to the context, politely respond that you are tuned to only answer questions ' \
              'that are related to the context.{}' \
              'Question: {}' \
              'Helpful answer in markdown in Chinese:'

QUES_TEMPLATE = 'make 3 relative questions with {}'\
                'give me the answer in Chinese'\
                'the answer\'s format is [question1@ question2@ question3]'\
                'do not answer the ques, you can only give me [question1@ question2@ question3]'


def chatbot(ques):
    text_list, source_list = match_query(ques, database="milvus")
    response = zhipuai.model_api.sse_invoke(
        model="chatglm_pro",
        prompt=[
            {"role": "user", "content": QA_TEMPLATE.format(text_list, ques)},
        ],
        temperature=0.95,
        top_p=0.7,
        incremental=True
    )
    return response, source_list, text_list

def relative_ques(ques):
    response = zhipuai.model_api.sse_invoke(
        model="chatglm_turbo",
        prompt=[
            {"role": "user", "content": QUES_TEMPLATE.format(ques)},
        ],
        temperature=0.95,
        top_p=0.7,
        incremental=True
    )
    data = ''
    for event in response.events():
        data += event.data
    # print(data)
    datas = data.replace('[', '').replace(']', '').split('@')
    print("relative ques: ", datas)
    return datas


if __name__ == '__main__':
    chatbot()
