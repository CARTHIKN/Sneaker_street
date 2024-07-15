FROM python:3.8
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirement.txt /app/
RUN pip install -r requirement.txt
RUN apt-get update \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/
COPY ./entrypoint.sh .

CMD ["sh", "/app/entrypoint.sh"]