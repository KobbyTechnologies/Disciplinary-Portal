FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1



RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN mkdir KMPDC

COPY . KMPDC

WORKDIR /KMPDC

CMD [ "python", "manage.py", "runserver" ]
