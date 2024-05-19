# Dockerized Mail Server

A Dockerized setup for Postfix, Dovecot, SpamAssassin, and MySQL with TLS/SSL

## Getting Started

Git clone the repo and cd into it 

```
git clone https://github.com/BushyToaster88/dockerised-mailserver.git
cd dockerised-mailserver
```
Build the Dockerfile
```
sudo docker build -t mailserver-mysql .
```


To run the container, use the following command:

```
sh
docker run -d --name mailserver \
  -p 25:25 \
  -p 993:993 \
  -p 465:465 \
  -e MYSQL_ROOT_PASSWORD='PASSWORD' \
  -e DOMAIN='example.com' \
  -e EMAIL_USER='name@example.com' \
  -e EMAIL_PASSWORD='PASSWORD' \
  mailserver-mysql
```

Once the Docker container is running, execute the setup script with:

```
docker exec -it mailserver-mysql python3 dns_sendability.py
```

This command will setup letsencrypt and show you what to put into your DNS

## DNS Configuration

If you plan to send emails, you need to configure your DNS server. The pictures below demonstrate how to input the necessary records. Note that for sending emails, an rDNS (Reverse DNS) must also be configured.
If you do not want to send emails, you can ignore the DNS settings.

![DNS Configuration Example](path/to/your/image.png)

