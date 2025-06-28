# Connect to the MySQL database
import mysql.connector
# Provide secure password hashing
import bcrypt
# Read MySQL credentials from an external .ini file
import configparser
# Get the current date and time
import datetime
# Used for password strength validation
import re
# Allow easy program exit
import sys

# Load database configuration from db_config.ini
config = configparser.ConfigParser()
config.read('db_config.ini')

# Extract MySQL connection details
db_config = {
    'host': config['mysql']['host'],
    'user': config['mysql']['user'],
    'password': config['mysql']['password'],
    'database': config['mysql']['database']
}

# Connect to the MySQL database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Validate password strength
def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'\d', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    )
# Register a new user
def register():
    username = input("Enter new username: ")
    password = input("Enter new password: ")

    if not is_strong_password(password):
        print("Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character.")
        return

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
    conn.commit()
    cursor.execute("INSERT INTO accounts (username, balance) VALUES (%s, %s)", (username, 100.0))
    conn.commit()
    print("You have registered successfully. Welcome To Our Bank!")

# Log in an existing user
def login():
    username = input("Enter username: ")
    password = input("Enter password: ")
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        print("Your Login is Successful.")
        return username
    else:
        print("Invalid credentials.")
        return None

# View account balance
def view_balance(username):
    cursor.execute("SELECT balance FROM accounts WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result:
        print(f"Your current balance is: {result[0]:.2f} EUR")
    else:
        print("Account not found.")

# View transaction history
def view_transactions(username):
    cursor.execute("SELECT sender, receiver, amount, timestamp FROM transactions WHERE sender = %s OR receiver = %s ORDER BY timestamp DESC",(username, username))
    transactions = cursor.fetchall()
    if transactions:
        print("Transaction History:")
        for t in transactions:
            print(f"{t[3]} - From: {t[0]} To: {t[1]} Amount: Є{t[2]:.2f}")
    else:
        print("No transactions found.")

# Transfer funds to another user
def transfer_funds(sender):
    receiver = input("Enter recipient username: ")
    amount = float(input("Enter amount to transfer: "))
    cursor.execute("SELECT balance FROM accounts WHERE username = %s", (sender,))
    sender_balance = cursor.fetchone()[0]
    if sender_balance >= amount:
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE username = %s", (amount, sender))
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE username = %s", (amount, receiver))
        cursor.execute("INSERT INTO transactions (sender, receiver, amount, timestamp) VALUES (%s, %s, %s, %s)",
                       (sender, receiver, amount, datetime.datetime.now()))
        conn.commit()
        print("Your transfer is successful.")
    else:
        print("Insufficient funds.")

# Secure password reset
def reset_password():
    username = input("Enter your username for password reset: ")
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    if not result:
        print("Username not found.")
        return

    # Simulate reset token verification
    token = input("Enter your reset token (simulated): ")
    if token != "RESET":
        print("Invalid reset token.")
        return

    new_password = input("Enter your new password: ")
    if not is_strong_password(new_password):
        print("Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character.")
        return

    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed.decode('utf-8'), username))
        conn.commit()
        print("Password reset successful.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Main menu loop
def main():
    print("Welcome to the Most Secured Banking System in Europe")
    while True:
        print("\n1. Register\n2. Login\n3. Reset Password\n4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            register()
        elif choice == '2':
            user = login()
            if user:
                while True:
                    print("\n1. View Balance\n2. View Transactions\n3. Transfer Funds\n4. Logout")
                    action = input("Choose an action: ")
                    if action == '1':
                        view_balance(user)
                    elif action == '2':
                        view_transactions(user)
                    elif action == '3':
                        transfer_funds(user)
                    elif action == '4':
                        print("Logged out.")
                        break
                    else:
                        print("Invalid option.")
        elif choice == '3':
            reset_password()
        elif choice == '4':
            print("Thank you for choosing our bank!")
            cursor.close()
            conn.close()
            sys.exit()
# Run the application
if __name__ == "__main__":
    main()
