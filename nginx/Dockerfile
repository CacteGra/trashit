FROM nginx:1.19.6-alpine

EXPOSE 81
# EXPOSE 443

RUN mkdir /etc/nginx/templates
COPY default.conf.template /etc/nginx/templates

RUN rm /etc/nginx/conf.d/default.conf
