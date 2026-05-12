# pull official base image
FROM python:3.12@sha256:d824f747699b6a0f1ebbee9289018c1e484c808e0d928a27be5f3ed7c5f15e4b

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY ./project ./project
# COPY ./main_test.py .
