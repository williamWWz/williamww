FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY streamlit_app.py .
EXPOSE 8501
ENV APPLICATION_DB=/data/applications.db
VOLUME ["/data"]
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
