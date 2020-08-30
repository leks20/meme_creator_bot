FROM python:latest

RUN mkdir -p /usr/src/app
WORKDIR /usr/scr/app

COPY requirements.txt /usr/scr/app
RUN pip install -r /usr/scr/app/requirements.txt

COPY . /usr/scr/app

ENV telegram_token 
ENV path_img images
ENV path_collection ./collection.txt

CMD ["python", "meme_creator.py"]
