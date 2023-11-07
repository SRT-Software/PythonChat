import streamlit as st
from streamlit_elements import elements, mui, html
import random

question_list = ['1', '2', '3']
new_list = []
def random_question():
    globals()["new_list"] = random.sample(question_list, 3)


with st.sidebar:
    random_question()
    st.title("提示")
    option = st.selectbox(
        'How would you like to be contacted?',
        (globals()["new_list"][0], globals()["new_list"][1], globals()["new_list"][2]))

st.markdown(
    """
        <style>
        .tips {
        position: fixed;
        font-size: 20px;
        top: 50px;
        left:5px;
        writing-mode: vertical-rl;
        }
        </style>
    """,
    unsafe_allow_html=True
    )

st.markdown('<div class="tips">提示</div>', unsafe_allow_html=True)

st.title('Fixed Position Title')


def cook_breakfast():
    msg = st.toast('Gathering ingredients...')
    msg.toast('Cooking...')
    msg.toast('Ready!', icon = "🥞")

if st.button('Cook breakfast'):
    cook_breakfast()


with elements("callbacks_retrieve_data"):
    with mui.Paper(elevation=3, variant="outlined", square=True):
            mui.TextField(
                label="My text input",
                defaultValue="Type here",
                variant="outlined",
            )


col1, e = st.columns([1, 100])


if "my_text" not in st.session_state:
    st.session_state.anchorEl = None

def handleMenu(event):
    print('here')
    st.session_state.anchorEl = event.currentTarget
    print(st.session_state.anchorEl)

def handleClose(event):
     st.session_state.anchorEl = None
    
    # with mui.Menu(id="simple-menu", keepMounted=True, anchorEl=st.session_state.anchorEl,
    #     open=True, onClose=handleClose):
    #     mui.MenuItem('Profile', onClick=handleClose)
    #     mui.MenuItem('My account', onClick=handleClose)
    #     mui.MenuItem('Logout', onClick=handleClose)
    # mui.Box(
    #         sx={
    #             "bgcolor": "red",
    #             "boxShadow": 1,
    #             "borderRadius": 2,
    #             "p": 2,
    #             'minHeight': 100,
    #         }
    #     )
    # with mui.Menu(id="simple-menu", keepMounted=True, anchorEl=st.session_state.anchorEl,
    #     open=True, onClose=handleClose):
    #     mui.MenuItem('Profile', onClick=handleClose)
    #     mui.MenuItem('My account', onClick=handleClose)
    #     mui.MenuItem('Logout', onClick=handleClose)


def chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with e.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("say something"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with e.chat_message("user"):
            st.markdown(prompt)
        # Display assistant response in chat message container
        with e.chat_message("assistant"):
            st.session_state.messages.append({"role": "assistant", "content": 'hi'})
            st.write('hi')


chat()

                    


# D:\Desktop\pythonSRT\venv\Scripts\streamlit.exe run index.py

