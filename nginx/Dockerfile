FROM nginx:1.19.6-alpine

ARG DOMAIN DOMAINWWW API_KEY SECRET_KEY API_URL CERTIFICATE_PATH PRIVATE_KEY_PATH

RUN mkdir /etc/nginx/ssl
RUN mkdir /etc/nginx/ssl/live
RUN mkdir /etc/nginx/ssl/live/$env:DOMAIN

EXPOSE 80
EXPOSE 443

RUN mkdir /etc/nginx/templates
COPY default.conf.template /etc/nginx/templates
