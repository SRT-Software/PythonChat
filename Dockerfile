# app/Dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8000"]