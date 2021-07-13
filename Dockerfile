FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
RUN mkdir /LionrocketImgtool
WORKDIR /LionrocketImgtool
ADD requirements.txt /LionrocketImgtool/  
RUN pip install -r requirements.txt
ADD . /LionrocketImgtool/
CMD opyrator launch-ui Imgtool:Lionlocket_Img_tool  
WORKDIR /LionrocketImgtool
EXPOSE 8051