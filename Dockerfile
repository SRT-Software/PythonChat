## app/Dockerfile
#
#FROM python:3.9-slim
#
#WORKDIR /app
#
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    curl \
#    software-properties-common \
#    git \
#    && rm -rf /var/lib/apt/lists/*
#
#RUN git clone https://github.com/SRT-Software/PythonChat.git
#
#RUN pip install -r requirements.txt
#
#EXPOSE 8000
#
#HEALTHCHECK CMD curl --fail http://localhost:8000/_stcore/health
#
#ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8000"]

# 使用基于 Python 的官方镜像作为基础映像
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . /app

# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Streamlit 的默认端口
EXPOSE 8000

# 运行 Streamlit 应用
CMD ["streamlit", "run", "index.py", "--server.port 8000"]