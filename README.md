# Dockerized Email Server

A Dockerized setup for Postfix, Dovecot, SpamAssassin, and MySQL with TLS/SSL

## Getting Started

Git clone the repo and cd into it 

```
git clone https://github.com/BushyToaster88/dockerised-emailserver.git
cd dockerised-emailserver
```
Build the Dockerfile
```
docker build -t emailserver-mysql .
```


To run the container, use the following command:

```
docker run -d --name emailserver-mysql \
  -p 25:25 \
  -p 993:993 \
  -p 465:465 \
  -e MYSQL_ROOT_PASSWORD='PASSWORD' \
  -e DOMAIN='example.com' \
  -e EMAIL_USER='name@example.com' \
  -e EMAIL_PASSWORD='PASSWORD' \
  emailserver-mysql
```

Once the Docker container is running, execute the setup script with:

```
docker exec -it emailserver-mysql python3 /app/dns_sendability.py
```

This command will setup letsencrypt and show you what to put into your DNS.

## DNS Configuration
You will need some DNS entries to connect to your email server. First being the MX records. It will be best if you create these 5 MX records so it covers all email clients.
```
mail.example.com
smtp.example.com
webmail.example.com
imap.example.com
mx.example.com
```
This is an example MX record
![image](https://github.com/BushyToaster88/dockerised-emailserver/assets/67993175/fbd29d38-f532-42f6-863d-c847f8114c2c)

Letsencrypt requires a CNAME record.

CNAME
![19-05-2024_09-46-33-PM_screenshot](https://github.com/BushyToaster88/dockerised-emailserver/assets/67993175/e0a7934d-b98d-4729-b117-854c1113847f)

If you plan to send emails, you need to configure other records. **Note that for sending emails, a rDNS (Reverse DNS) record must also be configured.**
If you do not want to send emails, you can ignore the below DNS settings. Remove all quotes when copying.

DMARC Record (TXT)
![image](https://github.com/BushyToaster88/dockerised-emailserver/assets/67993175/c4457d7b-be2b-4d94-ad4d-e10f298a13ff)

SPF Record (TXT)
![image](https://github.com/BushyToaster88/dockerised-emailserver/assets/67993175/8034a353-2ef5-42bd-8d6c-e3a85a5aecce)

DKIM Record (TXT)
![image](https://github.com/BushyToaster88/dockerised-emailserver/assets/67993175/8dfd25d5-5fd6-4cdf-bccc-93f186f48dc9)

The dkim record may have a space in it, just remove that
![image](https://github.com/BushyToaster88/dockerised-emailserver/assets/67993175/2fd2a2f3-d012-4e4f-9b2c-bf2a5e06ca55)









