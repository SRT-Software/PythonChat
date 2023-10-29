# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN git clone git@github.com:HangLee21/PythonChat.git .

RUN pip3 install -r requirements.txt

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8000"]