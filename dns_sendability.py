import os
import subprocess
import requests

# User-defined domain
domain = os.environ.get('DOMAIN', 'example.com')

print(f"Domain: {domain}")

# Function to run shell commands
def run_shell_command(command):
    subprocess.run(command, shell=True, check=True)

# Function to create SSL configuration in Dovecot
def create_dovecot_ssl_config():
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
protocols = $protocols imap
"""
    try:
        with open('/etc/dovecot/dovecot.conf', 'a') as file:
            file.write(ssl_config)
        print("Dovecot SSL configuration updated successfully.")
    except Exception as err:
        print(f"Error: {err}")

# Function to create SPF record
def create_spf_record():
    try:
        ip = requests.get("https://ipinfo.io/ip").text.strip()
        spf_record = f"v=spf1 mx a:mail.{domain} ip4:{ip} ~all"
        print(f"SPF Record: {spf_record}")
    except Exception as err:
        print(f"Error: {err}")

# Function to request a certificate
def request_certificate():
    try:
        run_shell_command(f"certbot certonly --manual --preferred-challenges dns -d {domain}")
        print("Certificate requested successfully.")
    except subprocess.CalledProcessError as err:
        print(f"Error: {err}")

# Create Dovecot SSL configuration
create_dovecot_ssl_config()

# Create SPF record
create_spf_record()

# Request certificate
request_certificate()
