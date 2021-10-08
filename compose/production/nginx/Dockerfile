FROM nginx:alpine

COPY ./compose/production/nginx/nginx.conf /etc/nginx

COPY ./compose/production/nginx/init_cert.sh /init_cert.sh

RUN chmod +x /init_cert.sh

CMD ["./init-cert.sh"]
