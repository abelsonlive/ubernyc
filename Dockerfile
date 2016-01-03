FROM ubuntu:latest
RUN echo 'setting up image'

# install base libraries
RUN apt-get update && apt-get install -y \
    git \
    libxml2-dev \
    python \
    build-essential \
    make \
    gcc \
    python-dev \
    locales \
    python-pip

# setup scraper
RUN echo 'installing scraper'
RUN cd /home/ && git clone https://github.com/abelsonlive/ubernyc.git
ADD .config.yml /home/ubernyc/.config.yml
RUN cd /home/ubernyc && python setup.py install
