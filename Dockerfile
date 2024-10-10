FROM python:3.11.9

WORKDIR /home

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "__main__.py"]
