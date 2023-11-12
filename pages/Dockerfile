FROM python:3.11-alpine

WORKDIR /database_api

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY api.py .

EXPOSE 8000

CMD [ "python", "api.py" ]