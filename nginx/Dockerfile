FROM nginx:1.19.6-alpine

RUN mkdir /etc/nginx/ssl
RUN mkdir /etc/nginx/ssl/live
RUN mkdir /etc/nginx/ssl/live/$env:DOMAIN

EXPOSE 80
EXPOSE 443

RUN mkdir /etc/nginx/templates
COPY default.conf.template /etc/nginx/templates

COPY wait-for-ssl.sh /docker-entrypoint.d/
RUN --mount=type=secret,id=.env target=$HOME/trashit/.env > /tmp/secret_output
RUN chmod +x /docker-entrypoint.d/wait-for-ssl.sh