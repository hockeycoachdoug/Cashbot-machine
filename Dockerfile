FROM python:3.11-alpine
WORKDIR /app
COPY . .
RUN pip install flask openai
RUN apk add --no-cache curl bash
CMD ["python", "app.py"]
