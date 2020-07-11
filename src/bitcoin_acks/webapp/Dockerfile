FROM tiangolo/meinheld-gunicorn:python3.8

#RUN apk add --no-cache --virtual .build-deps g++ python3-dev libffi-dev openssl-dev

#RUN apk add --no-cache --update python3 zsh linux-headers postgresql-dev

RUN apt-get update && apt-get install -y cron zsh nano sudo libssl-dev

WORKDIR app

EXPOSE 5000

COPY ./requirements.txt .
COPY ./.env .

RUN touch /var/log/cron.log
ADD ./src/bitcoin_acks/webapp/data-cron /etc/cron.d/data-cron
RUN chmod 0644 /etc/cron.d/data-cron

ARG YOUR_ENV

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN sudo -H pip3.8 install --upgrade --no-cache-dir pip -r requirements.txt
