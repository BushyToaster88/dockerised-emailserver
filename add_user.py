import os
import mysql.connector
import bcrypt
import argparse

# Function to add a user to the email server
def add_user(email, password):
    domain = email.split('@')[1]
    user = email.split('@')[0]

    # Connect to the MySQL database
    conn = mysql.connector.connect(
        user='root',
        password=os.environ.get('MYSQL_ROOT_PASSWORD'),
        host='localhost',
        database='mailserver'
    )
    cursor = conn.cursor()

    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Check if domain exists in virtual_domains table
    cursor.execute(f"SELECT id FROM virtual_domains WHERE name='{domain}'")
    result = cursor.fetchone()
    if result:
        domain_id = result[0]
    else:
        cursor.execute(f"INSERT INTO virtual_domains (name) VALUES ('{domain}')")
        domain_id = cursor.lastrowid

    # Insert user into virtual_users table
    cursor.execute(f"INSERT INTO virtual_users (domain_id, password, email) VALUES ({domain_id}, '{hashed_password}', '{email}')")
    cursor.execute(f"INSERT INTO virtual_users (domain_id, password, email) VALUES ({domain_id}, '{hashed_password}', '{user}')")

    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()

    print(f"User {email} and {user} added to the MySQL database successfully.")

# Main function
def main():
    parser = argparse.ArgumentParser(description='Add a user to the email server.')
    parser.add_argument('email', type=str, help='Email address of the user to add.')
    parser.add_argument('password', type=str, help='Password for the user.')

    args = parser.parse_args()

    add_user(args.email, args.password)

if __name__ == "__main__":
    main()
