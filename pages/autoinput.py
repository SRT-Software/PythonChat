from bokeh.models import TextInput, Button, CustomJS
import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events

# 创建一个文本框
text_input = TextInput(value="默认文本", title="文本框标题")

# 创建一个按钮
button = Button(label="开始语音输入",button_type ='success')



button.js_on_event("button_click", CustomJS(code="""
    console.log("js_on_event")
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.start();
    recognition.onresult = function(event) {
        var result = event.results[event.results.length - 1][0].transcript;
        console.log("result:")
        console.log(result)
        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: {t:result, s:1}}));
    };
"""))

result = streamlit_bokeh_events(
    bokeh_plot = button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

tr = st.empty()
if result:
    if "GET_TEXT" in result:
        if result.get("GET_TEXT") != '':
            tr.text_area("**Your input**", result.get("GET_TEXT"))

