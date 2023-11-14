FROM python:3.11-alpine

WORKDIR /ai_bot

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD [ "python", "main.py" ]