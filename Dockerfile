FROM python:3.10.0a4-alpine3.12

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
