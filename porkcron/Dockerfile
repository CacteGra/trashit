FROM python:3.10-alpine

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY porkcron.py /usr/local/bin/porkcron
RUN --mount=type=secret,id=.env target=$HOME/trashit/.env > /tmp/secret_output
RUN chmod +x /usr/local/bin/porkcron

COPY crontab /etc/crontabs/root

CMD [ "crond", "-f" ]