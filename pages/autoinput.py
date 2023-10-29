import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
st.set_page_config(
    page_title="Streamlit语音输入",
    page_icon="🎤"
)
# # 接收并显示语音输入文本
# text_input = st.text_input("语音输入", value="")
#
# # 在Streamlit中显示语音输入的文本
# def set_text_input(text):
#     text_input.text(text)
#
# # 通过st.components.html加载HTML文件
# def load_html_file(file_path):
#     with open(file_path, "r") as file:
#         st.components.v1.html(file.read(), width=700, height=500)
# # 注册Streamlit应用程序的端点，以接收来自JavaScript的POST请求
#
# load_html_file("audioInput.html")
# # 注册用于接收来自JavaScript的POST请求的处理函数

spk_button = Button(label='SPEAK', button_type='success')


spk_button.js_on_event("button_click", CustomJS(code="""
    var value = "";
    var rand = 0;
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en';

    document.dispatchEvent(new CustomEvent("GET_ONREC", {detail: 'start'}));
    
    recognition.onspeechstart = function () {
        document.dispatchEvent(new CustomEvent("GET_ONREC", {detail: 'running'}));
    }
    recognition.onsoundend = function () {
        document.dispatchEvent(new CustomEvent("GET_ONREC", {detail: 'stop'}));
    }
    recognition.onresult = function (e) {
        var value2 = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
                rand = Math.random();
                
            } else {
                value2 += e.results[i][0].transcript;
            }
        }
        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: {t:value, s:rand}}));
        document.dispatchEvent(new CustomEvent("GET_INTRM", {detail: value2}));

    }
    recognition.onerror = function(e) {
        document.dispatchEvent(new CustomEvent("GET_ONREC", {detail: 'stop'}));
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    bokeh_plot = spk_button,
    events="GET_TEXT,GET_ONREC,GET_INTRM",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

# tr = st.empty()
# if result:
#     if "GET_INTRM" in result:
#         if result.get("GET_INTRM") != '':
#             tr.text_area("**Your input**", result.get("GET_INTRM"))