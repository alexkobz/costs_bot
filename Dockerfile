FROM python:3.11.9

WORKDIR /home

COPY . .

RUN python -m pip install -U pip
RUN python -m pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "__main__.py"]
