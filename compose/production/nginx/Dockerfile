FROM nginx:1.15-alpine

COPY ./compose/production/nginx/nginx.conf /etc/nginx

COPY ./compose/production/nginx/init_cert.sh /init_cert.sh

RUN chmod +x /init_cert.sh
