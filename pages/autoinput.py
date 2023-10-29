import streamlit as st
st.set_page_config(
    page_title="Streamlit语音输入",
    page_icon="🎤"
)
# 接收并显示语音输入文本
text_input = st.text_input("语音输入", value="")

# 在Streamlit中显示语音输入的文本
def set_text_input(text):
    text_input.text(text)

# 通过st.components.html加载HTML文件
def load_html_file(file_path):
    with open(file_path, "r") as file:
        st.components.v1.html(file.read(), width=700, height=500)
# 注册Streamlit应用程序的端点，以接收来自JavaScript的POST请求

load_html_file("audioInput.html")
# 注册用于接收来自JavaScript的POST请求的处理函数