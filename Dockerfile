FROM python:3.11-bookworm

WORKDIR /falinn

COPY ./requirements.txt /falinn/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /falinn/requirements.txt

COPY ./src /falinn/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]