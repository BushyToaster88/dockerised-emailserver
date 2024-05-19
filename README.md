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
mail.example.com
smtp.example.com
webmail.example.com
imap.example.com
mx.example.com

This is an example MX record
[MX](https://100mbupload.com/uploads/6649e232a8f3a_19-05-2024_09-27-35-PM_screenshot.png)

If you plan to send emails, you need to configure other records. **Note that for sending emails, a rDNS (Reverse DNS) record must also be configured.**
If you do not want to send emails, you can ignore the below DNS settings.

DMARC Record (TXT)
[DMARC](https://100mbupload.com/uploads/6649e1e06a042_19-05-2024_09-26-10-PM_screenshot.png)

SPF Record (TXT)
[SPF](https://100mbupload.com/uploads/6649e19acf1f3_19-05-2024_09-22-18-PM_screenshot.png)]

DKIM Record (TXT)
[DKIM](https://100mbupload.com/uploads/6649e1c1925f0_19-05-2024_09-23-21-PM_screenshot.png)






