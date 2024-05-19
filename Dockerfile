# Use the latest Ubuntu image
FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get update && \
    apt-get install -y certbot nginx mysql-server dovecot-core dovecot-imapd dovecot-mysql dovecot-sieve postfix postfix-mysql spamassassin spamc python3 python3-pip python-is-python3 opendkim opendkim-tools wget pkg-config libmysqlclient-dev rsyslog && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir mysql-connector-python mysqlclient requests bcrypt --break-system-packages

# Download and move the acme-dns-auth.py script
RUN wget https://github.com/joohoi/acme-dns-certbot-joohoi/raw/master/acme-dns-auth.py && \
    mv acme-dns-auth.py /etc/letsencrypt/ && \
    chmod +x /etc/letsencrypt/acme-dns-auth.py

# Copy configuration files to their respective directories
COPY dovecot/ /etc/dovecot/
COPY postfix/ /etc/postfix/

# Ensure the vmail and dmarc users exist and set appropriate permissions
RUN grep -q '^vmail:' /etc/passwd || useradd vmail && \
    grep -q '^dmarc:' /etc/passwd || useradd -m -G mail dmarc && \
    chown -R vmail:vmail /var/lib/dovecot && \
    mkdir -p /var/lib/dovecot/sieve && \
    touch /var/lib/dovecot/sieve/default.sieve && \
    sievec /var/lib/dovecot/sieve/default.sieve

# Set the correct ownership and permissions for Postfix configuration files
RUN chown -R root:root /etc/postfix && \
    chmod -R 644 /etc/postfix && \
    find /etc/postfix -type d -exec chmod 755 {} \; && \
    chmod 755 /etc/postfix/postfix-script

# Configure rsyslog for Dovecot and Postfix
RUN echo "mail.*    -/var/log/mail.log" >> /etc/rsyslog.d/50-default.conf && \
    echo "local0.*  -/var/log/dovecot-info.log" >> /etc/rsyslog.d/50-default.conf

# Create log files and set permissions
RUN touch /var/log/mail.log && \
    touch /var/log/dovecot-info.log && \
    chown syslog:adm /var/log/mail.log && \
    chmod 664 /var/log/mail.log && \
    chown syslog:adm /var/log/dovecot-info.log && \
    chmod 664 /var/log/dovecot-info.log

# Copy the setup script and dns_sendability script
COPY setup.py /usr/local/bin/setup.py
COPY dns_sendability.py /app/dns_sendability.py
COPY add_user.py /app/add_user.py
RUN chmod +x /usr/local/bin/setup.py /app/dns_sendability.py /app/add_user.py

# Expose necessary ports
EXPOSE 25 993 465

# Start services and run the setup script
CMD rsyslogd && \
    service mysql start && \
    python3 /usr/local/bin/setup.py && \
    tail -f /var/log/mail.log -f /var/log/dovecot-info.log
