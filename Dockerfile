# define base image as python slim-buster.
FROM python:3.9-slim as base

## start builder stage.

# this is the first stage of the build.
# it will install all requirements.
FROM base as builder

# install all packages for chromedriver: https://gist.github.com/varyonic/dea40abcf3dd891d204ef235c6e8dd79
RUN apt-get update -y
RUN apt-get install -y firefox-esr=115.4.0esr-1~deb12u1 xvfb gnupg wget curl unzip --no-install-recommends
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux-aarch64.tar.gz -P /tmp
RUN tar -xf /tmp/geckodriver-v0.33.0-linux-aarch64.tar.gz -C /usr/bin
RUN chmod +x /usr/bin/geckodriver

# copy any python requirements file into the install directory and install all python requirements.
COPY requirements.txt /requirements.txt
RUN pip install --upgrade --no-cache-dir -r /requirements.txt
RUN rm /requirements.txt

COPY src /src

FROM builder

CMD ["python3", "-m", "src.test"]