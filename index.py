import streamlit as st
from chat import chatbot, relative_ques
from enum import Enum
from config.User import User, default_user
import random

question_list = ['脚手架的操作规范', '矿井内氧气含量过低怎么办', '遭遇恶劣天气应该如何处理']

new_list = []

def random_question():
    st.session_state.lists = random.sample(question_list, 3)


def change_web(attrs1, attrs2):
    if attrs1 == attrs2:
        st.success("登录成功！")
        st.session_state.index = 1
    else:
        st.error("用户名或密码错误")
        st.session_state.index = 0



def login_web():
    st.title("用户登录")
    # 输入用户名和密码
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    user = User(name=username, password=password)
    # 登录按钮
    attrs1 = vars(user)
    attrs2 = vars(default_user)
    print(f"user:{username}, password:{password}")
    st.button("登录", on_click=change_web, args=(attrs1, attrs2))


def chat_web():
    # st.header("Chat",anchor=False)
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            font-size: 80px;
            font-weight:bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="title">Chat</div>', unsafe_allow_html=True)
    with st.sidebar:
        st.title("提示")
        print("buttons: ", st.session_state.lists)
        if st.button(label=st.session_state.lists[0]):
            st.session_state.prompt = st.session_state.lists[0]
        if st.button(label=st.session_state.lists[1]):
            st.session_state.prompt = st.session_state.lists[1]
        if st.button(label=st.session_state.lists[2]):
            st.session_state.prompt = st.session_state.lists[2]


    hello()
    chat()


def hello():
    with st.chat_message("assistant"):
        st.write("你好 👋")


def chat():
    st.markdown(
        """
        <style>
        .tips {
            position: fixed;
            font-size: 20px;
            top: 50px;
            left:5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="tips">TIPS</div>', unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("请输入聊天内容")
    if prompt is not None:
        st.session_state.prompt = prompt
    print(st.session_state.prompt)
    if st.session_state.prompt is not None:
        # Add user message to chat history
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Display assistant response in chat message container
        # with st.chat_message("assistant"):
        #     message_placeholder = st.empty()
        #     full_response = ""
        #     response, sources, texts = chatbot(prompt)
        #     for event in response.events():
        #         full_response += event.data
        #         message_placeholder.markdown(full_response + " ")
        #     message_placeholder.markdown(full_response)
        #     st.session_state.messages.append({"role": "assistant", "content": full_response})
        #     for i in range(len(sources)):
        #         expander_text = 'file: {}, page: {}'.format(sources[i][0], int(sources[i][1]))
        #         with st.expander(expander_text):
        #             st.markdown(texts[i])
            st.session_state.lists = relative_ques(st.session_state.prompt)
            st.session_state.prompt = None
                


pages_name_func = {
    'login': login_web,
    'chat': chat_web
}

pages_name_index = {
    0: 'login',
    1: 'chat',
}

if __name__ == '__main__':
    if 'index' not in st.session_state:
        st.session_state.index = 1

    if 'option' not in st.session_state:
        st.session_state.prompt = None

    if 'lists' not in st.session_state:
        st.session_state.lists =  random.sample(question_list, 3)
    
    print("lists:", st.session_state.lists)
    demo_name = pages_name_index[st.session_state.index]
    pages_name_func[demo_name]()

# D:\Desktop\pythonSRT\venv\Scripts\streamlit.exe run index.py
