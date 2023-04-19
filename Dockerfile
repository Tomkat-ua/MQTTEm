FROM python:3-slim
#alpine
RUN pip install --upgrade pip
WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./main.py /usr/src/app/main.py

CMD ["python","-u","main.py","prod"]
