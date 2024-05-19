import os
import subprocess
import requests

# User-defined domain
domain = os.environ.get('DOMAIN', 'example.com')

# Function to run shell commands
def run_shell_command(command):
    subprocess.run(command, shell=True, check=True)

# Function to get the external IP address
def get_external_ip():
    response = requests.get('https://ipinfo.io/ip')
    return response.text.strip()

# Function to generate DKIM keys
def generate_dkim_keys(domain):
    run_shell_command(f"mkdir -p /etc/postfix/dkim")
    run_shell_command(f"opendkim-genkey -D /etc/postfix/dkim/ -d {domain} -s mail")
    run_shell_command(f"chgrp opendkim /etc/postfix/dkim/*")
    run_shell_command(f"chmod g+r /etc/postfix/dkim/*")

# Function to generate DNS records
def generate_dns_records(domain):
    with open(f'/etc/postfix/dkim/mail.txt', 'r') as file:
        dkim_key = file.read().replace("\n", "").replace('"', '').split('p=')[1]

    external_ip = get_external_ip()

    print("\nAdd these DNS records to your DNS server:\n")

    print("DKIM record:")
    print(f"mail._domainkey.{domain} IN TXT \"v=DKIM1; k=rsa; p={dkim_key}\"")

    print("\nDMARC record:")
    print(f"_dmarc.{domain} IN TXT \"v=DMARC1; p=reject; rua=mailto:dmarc@{domain}; fo=1\"")

    print("\nSPF record:")
    print(f"{domain} IN TXT \"v=spf1 mx a:mail.{domain} ip4:{external_ip} ~all\"")

# Function to replace placeholders in Dovecot config for SSL
def replace_ssl_placeholders(domain):
    ssl_config = rf"""
ssl = required
ssl_cert = </etc/letsencrypt/live/{domain}/fullchain.pem
ssl_key = </etc/letsencrypt/live/{domain}/privkey.pem
ssl_min_protocol = TLSv1.2
ssl_cipher_list = EECDH+ECDSA+AESGCM:EECDH+aRSA+AESGCM:EECDH+ECDSA+SHA256:EECDH+aRSA+SHA256:EECDH+ECDSA+SHA384:EECDH+ECDSA+SHA256:EECDH+aRSA+SHA384:EDH+aRSA+AESGCM:EDH+aRSA+SHA256:EDH+aRSA:EECDH:!aNULL:!eNULL:!MEDIUM:!LOW:!3DES:!MD5:!EXP:!PSK:!SRP:!DSS
ssl_prefer_server_ciphers = yes
ssl_dh = </usr/share/dovecot/dh.pem
auth_mechanisms = plain login
auth_username_format = %n
"""

    with open('/etc/dovecot/dovecot.conf', 'a') as file:
        file.write(ssl_config)

# Function to request SSL certificate using DNS challenge
def request_ssl_certificate(domain):
    run_shell_command(f"certbot certonly --manual --manual-auth-hook /etc/letsencrypt/acme-dns-auth.py --preferred-challenges dns --debug-challenges -d {domain}")

# Generate DKIM keys
generate_dkim_keys(domain)

# Replace SSL placeholders in Dovecot config
replace_ssl_placeholders(domain)

# Request SSL certificate
request_ssl_certificate(domain)

# Generate DNS records
generate_dns_records(domain)
