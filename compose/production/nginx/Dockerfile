FROM nginx:alpine
COPY ./compose/production/nginx/nginx.conf /etc/nginx
COPY ./compose/production/nginx/init_cert.sh /etc/nginx

RUN chmod +x /etc/nginx/init_cert.sh

CMD ["./etc/nginx/init-cert.sh"]
