import psycopg
import os
from dotenv import load_dotenv
from faker import Faker
from datetime import datetime, timedelta
import random

#Load .env variables
load_dotenv()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DBNAME = os.getenv("POSTGRES_DB")

# Create Faker instance
faker = Faker()

# Connect to PostgreSQL instance
conn = psycopg.connect(f"""host=localhost port={PORT} user={USER} password={PASSWORD} dbname={DBNAME}""")
cur = conn.cursor()

# Generate random datetime from last 2 years
def random_date():
    start_date = datetime.now() - timedelta(days=730)
    date = faker.date_time_between(start_date=start_date, end_date="now")
    return date

# Insert fake users
def insert_users(n):
    for _ in range(n):
        name = faker.name()
        email = faker.email()
        created_at = random_date()
        cur.execute("INSERT INTO users (name, email, created_at) VALUES (%s, %s, %s)",
                    (name, email, created_at))
    conn.commit()
    print(f"{n} users inserted.")

# Insert products
def insert_products(n):
    products = ["Notebook", "Mouse", "Keyboard", "Monitor", "Printer"]
    for _ in range(n):
        name = random.choice(products)
        price = round(random.uniform(50, 5000), 2)  #Between $50,00 and $5.000,00
        cur.execute("INSERT INTO products (name, price) VALUES (%s, %s)",
                    (name, price))
    conn.commit()
    print(f"{n} products inserted.")

# Insert fake orders
def insert_orders(n):
    # Collects created users from users table
    cur.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cur.fetchall()]

    for _ in range(n):
        user_id = random.choice(user_ids)
        cur.execute("INSERT INTO orders (user_id, total, created_at) VALUES (%s, %s, %s) RETURNING id",
                    (user_id, 0, random_date()))
        
        # Inserts order items fields
        order_id = cur.fetchone()[0]
        total = insert_order_items(order_id)

        # Inserts the total value of the order based on order items values
        cur.execute("UPDATE orders SET total = %s WHERE id = %s",
                    (total, order_id))
    
    conn.commit()
    print(f"{n} orders inserted.")

# Insert fake order items
def insert_order_items(order_id):
    cur.execute("SELECT id, price FROM products")
    products = cur.fetchall()

    total = 0
    for _ in range(random.randint(1, 3)):
        product_id, price = random.choice(products)
        quantity = random.randint(1, 5)
        total += quantity * price

        cur.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                    (order_id, product_id, quantity, price))
    
    conn.commit()  
    return total

# Run insertions
insert_users(30)
insert_products(5)
insert_orders(30)

#Close connection
cur.close()
conn.close()