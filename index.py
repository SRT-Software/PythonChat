import streamlit as st
from chat import chatbot
from enum import Enum
from config.User import User, default_user


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
    hello()
    chat()


def hello():
    with st.chat_message("assistant"):
        st.write("Hello 👋")


def chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("say something"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            response, sources, texts = chatbot(prompt)
            for event in response.events():
                full_response += event.data
                message_placeholder.markdown(full_response + " ")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            for i in range(len(sources)):
                expander_text = 'file: {}, page: {}'.format(sources[i][0], int(sources[i][1]))
                with st.expander(expander_text):
                    st.markdown(texts[i])


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
        st.session_state.index = 0
    demo_name = pages_name_index[st.session_state.index]
    pages_name_func[demo_name]()

# D:\Desktop\pythonSRT\venv\Scripts\streamlit.exe run index.py
