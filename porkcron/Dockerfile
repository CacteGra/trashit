FROM python:3.10-alpine

ARG API_KEY SECRET_KEY API_URL CERTIFICATE_PATH PRIVATE_KEY_PATH

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../porkcron.py /usr/local/bin/porkcron
RUN chmod +x /usr/local/bin/porkcron

COPY crontab /etc/crontabs/root

CMD [ "crond", "-f" ]