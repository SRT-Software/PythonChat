from bokeh.models import TextInput, Button, CustomJS
import streamlit as st
import streamlit_bokeh_events

# 创建一个文本框
text_input = TextInput(value="默认文本", title="文本框标题")

# 创建一个按钮
button = Button(label="开始语音输入",button_type ='success')



button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en';
    recognition.onresult = function(e){
        var value, value2 = "";
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

    recognition.start();
    }
"""))

result = streamlit_bokeh_events(
    bokeh_plot = button,
    events="GET_TEXT,GET_ONREC,GET_INTRM",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

tr = st.empty()
if result:
    if "GET_INTRM" in result:
        if result.get("GET_INTRM") != '':
            tr.text_area("**Your input**", result.get("GET_INTRM"))

