FROM python:3

ADD /app /web
WORKDIR /web

RUN python3 -m pip install -U pip
RUN pip3 install -r requirements.txt
RUN pip3 install uwsgi

CMD uwsgi --http-socket :$PORT uwsgi.ini

