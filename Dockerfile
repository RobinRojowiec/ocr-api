FROM python:3.8-slim

WORKDIR /ocr
COPY requirements.txt .

RUN apt-get update && \
    apt-get -y install --no-install-recommends \ 
                       tesseract-ocr && \
    # Install depencies
    pip --no-cache install \
                pillow \
                pytesseract && \
    # Instal project requirements
    pip --no-cache install -r requirements.txt && \
    # Cleaning
    apt-get clean               && \
    apt-get autoremove          && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/*         && \
    rm -rf /usr/share/doc/*     && \
    rm -rf /usr/share/X11/*     && \
    rm -rf /usr/share/fonts/*

# copy files and install dependencies
COPY . .

EXPOSE 8000
ENTRYPOINT python3 server.py
