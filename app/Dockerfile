FROM python:3.11-slim

#this is for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

#doesn't download gui
ENV MPLBACKEND=Agg

WORKDIR /app

#installing python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

#copy the rest
COPY . . 
