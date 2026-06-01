FROM python:3.11-alpine
WORKDIR /app
COPY . .
RUN pip install flask
CMD ["python", "app.py"]
