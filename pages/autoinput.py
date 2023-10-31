import streamlit as st
import speech_recognition as sr

# 创建一个语音识别器实例
recognizer = sr.Recognizer()

# 设置Streamlit页面的标题和说明
st.title("实时语音识别")
st.write("点击下方按钮开始录音，并实时显示识别结果：")



# 定义回调函数处理按钮点击事件
if st.button("audio"):
        # 使用麦克风进行语音输入
        with sr.Microphone(device_index=0) as source:
            st.write("开始录音...")
            r.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

            try:
                # 将语音转换为文本
                text = recognizer.recognize_google(audio, language='zh-CN')
                result_text.text(text)
            except sr.UnknownValueError:
                st.write("无法识别语音")
            except sr.RequestError as e:
                st.write("请求出错：", str(e))
# 创建一个文本框用于显示识别结果
result_text = st.empty()