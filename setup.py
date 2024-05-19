import os
import subprocess
import mysql.connector
from mysql.connector import errorcode
import bcrypt

# User-defined domain, MySQL root password, and user credentials
domain = os.environ.get('DOMAIN', 'example.com')
mysql_root_password = os.environ.get('MYSQL_ROOT_PASSWORD', 'rootpassword')
email_user = os.environ.get('EMAIL_USER')
email_password = os.environ.get('EMAIL_PASSWORD')

print(f"Domain: {domain}")
print(f"MySQL Root Password: {mysql_root_password}")
print(f"Email User: {email_user}")
print(f"Email Password: {email_password}")

# Function to run shell commands
def run_shell_command(command):
    subprocess.run(command, shell=True, check=True)

# Function to start MySQL server
def start_mysql():
    run_shell_command("service mysql start")

# Function to change MySQL root password directly using mysql command
def change_mysql_root_password():
    try:
        print("Changing MySQL root password directly using mysql command")
        run_shell_command(f"mysql -u root -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY '{mysql_root_password}'; FLUSH PRIVILEGES;\"")
        print("MySQL root password changed successfully.")
    except subprocess.CalledProcessError as err:
        print(f"Error: {err}")

# Function to create the database and necessary tables
def create_database_and_tables():
    try:
        print("Creating database and tables")
        conn = mysql.connector.connect(
            user='root',
            password=mysql_root_password,
            host='localhost'
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS mailserver")
        cursor.execute("USE mailserver")

        # Create virtual_domains table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS virtual_domains (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(50) NOT NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
        """)

        # Insert data into virtual_domains table
        cursor.execute(f"INSERT INTO virtual_domains (id, name) VALUES (1, '{domain}')")

        # Create virtual_users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS virtual_users (
            id INT NOT NULL AUTO_INCREMENT,
            domain_id INT NOT NULL,
            password VARCHAR(106) NOT NULL,
            email VARCHAR(100) NOT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY email (email),
            KEY domain_id (domain_id),
            CONSTRAINT virtual_users_ibfk_1 FOREIGN KEY (domain_id) REFERENCES virtual_domains (id) ON DELETE CASCADE
        ) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb3;
        """)

        # Create virtual_aliases table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS virtual_aliases (
            id INT NOT NULL AUTO_INCREMENT,
            domain_id INT NOT NULL,
            source VARCHAR(100) NOT NULL,
            destination VARCHAR(100) NOT NULL,
            PRIMARY KEY (id),
            KEY domain_id (domain_id),
            CONSTRAINT virtual_aliases_ibfk_1 FOREIGN KEY (domain_id) REFERENCES virtual_domains (id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
        """)

        # Add user if credentials are provided
        if email_user and email_password:
            # Check if domain exists in virtual_domains table
            cursor.execute(f"SELECT id FROM virtual_domains WHERE name='{domain}'")
            result = cursor.fetchone()
            if result:
                domain_id = result[0]
            else:
                cursor.execute(f"INSERT INTO virtual_domains (name) VALUES ('{domain}')")
                domain_id = cursor.lastrowid

            # Encrypt the password using bcrypt
            hashed_password = bcrypt.hashpw(email_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Insert user into virtual_users table
            cursor.execute(f"INSERT INTO virtual_users (domain_id, password, email) VALUES ({domain_id}, '{hashed_password}', '{email_user}')")
            username = email_user.split('@')[0]
            cursor.execute(f"INSERT INTO virtual_users (domain_id, password, email) VALUES ({domain_id}, '{hashed_password}', '{username}')")

            print(f"User {email_user} and {username} added to the MySQL database successfully.")

        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        print("Database and tables created successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to create /etc/mailname
def create_mailname_file(domain):
    try:
        with open('/etc/mailname', 'w') as file:
            file.write(domain)
        print("/etc/mailname created successfully.")
    except Exception as err:
        print(f"Error: {err}")

# Start MySQL server
start_mysql()

# Change MySQL root password
change_mysql_root_password()

# Create the database and tables
create_database_and_tables()

# Create /etc/mailname file
create_mailname_file(domain)

# Function to replace placeholders in files
def replace_placeholders(file_path, replacements):
    with open(file_path, 'r') as file:
        content = file.read()
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    with open(file_path, 'w') as file:
        file.write(content)

# Replace placeholders in configuration files
dovecot_config_files = [os.path.join(root, file) for root, _, files in os.walk('/etc/dovecot') for file in files]
postfix_config_files = [os.path.join(root, file) for root, _, files in os.walk('/etc/postfix') for file in files]

replacements = {'$DOMAIN': domain, '$PASSWORD': mysql_root_password}

for config_file in dovecot_config_files + postfix_config_files:
    replace_placeholders(config_file, replacements)

# Create DKIM keys
run_shell_command(f"mkdir -p /etc/postfix/dkim")
run_shell_command(f"opendkim-genkey -D /etc/postfix/dkim/ -d {domain} -s mail")
run_shell_command(f"chgrp opendkim /etc/postfix/dkim/*")
run_shell_command(f"chmod g+r /etc/postfix/dkim/*")

# Restart services to apply configuration changes
run_shell_command("service dovecot restart")
run_shell_command("service postfix restart")
run_shell_command("service opendkim restart")
