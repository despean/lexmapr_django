FROM nginx:1.15-alpine

COPY ./compose/production/nginx/nginx.conf /etc/nginx

COPY /etc/nginx/cert.crt /etc/nginx
COPY /etc/nginx/cert.key /etc/nginx
