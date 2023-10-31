# from bokeh.io import curdoc
# from bokeh.layouts import column
# from bokeh.models import TextInput, Button, CustomJS
# import streamlit as st
# import streamlit_bokeh_events
#
# # 创建一个文本框
# text_input = TextInput(value="默认文本", title="文本框标题")
#
# # 创建一个按钮
# button = Button(label="开始语音输入")
#
# # 定义回调函数
# text_input_callback = CustomJS(args=dict(text_input=text_input), code="""
#     var recognition = new webkitSpeechRecognition();
#     recognition.continuous = true;
#     recognition.interimResults = true;
#     recognition.start();
#     recognition.onresult = function(event) {
#         var result = event.results[event.results.length - 1][0].transcript;
#         text_input.value = result;
#     };
# """)
#
# # 将回调函数绑定到按钮的 onclick 事件上
# button.js_on_event("button_click", text_input_callback)
#
# # 创建布局
# layout = column(text_input, button)
#
# # 将布局添加到文档中
# curdoc().add_root(layout)

import streamlit as st
from bokeh.models import CustomJS, Button, TextInput
from bokeh.layouts import layout, column
from streamlit_bokeh_events import streamlit_bokeh_events
callback = CustomJS(args=dict(text_input=text_input), code="""
      var recognition = new webkitSpeechRecognition();
      recognition.lang = "en-US";
      recognition.start();
    var transcript = "";
      recognition.onresult = function(event) {
        for (var i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
      }
    text_input.value = transcript
""")


