FROM tesseractshadow/tesseract4re

# install python 3
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# copy files and install dependencies
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000
ENTRYPOINT python3 server.py