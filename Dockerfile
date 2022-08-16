FROM python:3.9

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install --upgrade pip

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
