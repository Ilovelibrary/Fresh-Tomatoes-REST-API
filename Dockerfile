FROM python:2.7
ADD . /Movie_REST_API
WORKDIR /Movie_REST_API
RUN pip install -r requirements.txt
