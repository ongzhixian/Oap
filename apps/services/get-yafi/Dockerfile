FROM python:3.7-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ] 
CMD [ "main.py", "/mnt/secrets/cloud-amqp/.cloudampq.json", '/mnt/data/yafi/json' ]