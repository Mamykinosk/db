import psycopg2
from faker import Faker
from faker_commerce import Provider
import random


try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="06040502",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    fake = Faker('ru_RU')
    fake.add_provider(Provider)
    #print([method for method in dir(fake) if 'ecommerce' in method.lower()])


    def set_parent_category(parent_category, category):
        cur.execute(
        "UPDATE market.categories SET parent_category_id = %s where category_id = %s",
        (parent_category, category)
        )


    NUM_SELLERS = 20
    NUM_CUSTOMERS = 1500
    NUM_CATEGORIES = 20
    NUM_PRODUCTS = 2000
    NUM_ORDERS = 5000


    cur.execute(
        "truncate users.users, users.user_profiles, users.addresses, market.categories, market.products, market.product_categories, market.orders, market.order_items, market.reviews, market.payements restart identity cascade"
    )


    print(f"Generating {NUM_SELLERS} sellers...")
    seller_ids = []
    for _ in range(NUM_SELLERS):
        cur.execute(
            """
            INSERT INTO users.users (email, phone_number, password_hash, user_type)
            VALUES (%s, %s, %s, 'seller') RETURNING user_id
            """,
            (fake.unique.company_email(), fake.unique.phone_number(), fake.password())
        )
        seller_ids.append(cur.fetchone()[0])
    print("... Sellers created.")


    print(f"Generating {NUM_CATEGORIES} categories...")
    category_ids = []
    for _ in range(NUM_CATEGORIES):
        cur.execute(
            "INSERT INTO market.categories (name) VALUES (%s) RETURNING category_id",
            (fake.unique.ecommerce_category(),)
        )
        category_ids.append(cur.fetchone()[0])
    print("... Categories created.")


    print(f"Generating {NUM_CUSTOMERS} customers with their profiles and addresses...")
    customer_data = {}
    for _ in range(NUM_CUSTOMERS):
        cur.execute(
            """
            INSERT INTO users.users (email, phone_number, password_hash, user_type)
            VALUES (%s, %s, %s, 'customer') RETURNING user_id
            """,
            (fake.unique.email(), fake.unique.phone_number(), fake.password())
        )
        customer_id = cur.fetchone()[0]
        customer_data[customer_id] = []

        cur.execute(
            "INSERT INTO users.user_profiles (profile_id, first_name, last_name, birth_date) VALUES (%s, %s, %s, %s)",
            (customer_id, fake.first_name(), fake.last_name(), fake.date_of_birth(minimum_age=18, maximum_age=70))
        )

        for _ in range(random.randint(1, 3)):
            cur.execute(
                """
                INSERT INTO users.addresses (user_id, city, street, house_number, apartment, postal_code)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING address_id
                """,
                (customer_id, fake.city(), fake.street_address(), fake.building_number(), str(random.randint(1, 200)),
                 fake.postcode())
            )
            customer_data[customer_id].append(cur.fetchone()[0])
    print("... Customers created.")

    print(f"Generating {NUM_PRODUCTS} products...")
    product_ids = []
    for _ in range(NUM_PRODUCTS):
        cur.execute(
            """
            INSERT INTO market.products (seller_id, name, description, price)
            VALUES (%s, %s, %s, %s) RETURNING product_id
            """,
            (random.choice(seller_ids), fake.ecommerce_name(), fake.text(max_nb_chars=200),
             round(random.uniform(100.0, 50000.0), 2))
        )
        product_ids.append(cur.fetchone()[0])
    print("... Products created.")

    print(category_ids)
    ''' 
    for i in range(10):
        print(random.sample(category_ids, k=random.randint(1, 3)))
    '''

    print("Linking products to categories...")
    for product_id in product_ids:
        # Assign each product to 1-3 random categories
        assigned_categories = random.sample(category_ids, k=random.randint(1, 3))
        for category_id in assigned_categories:
            cur.execute(
                "INSERT INTO market.product_categories (product_id, category_id) VALUES (%s, %s)",
                (product_id, category_id)
            )
    print("... Products linked.")

    print(f"Generating {NUM_ORDERS} orders and their related data. This may take a moment...")
    order_item_records = []
    customer_ids_list = list(customer_data.keys())

    for i in range(NUM_ORDERS):
        customer_id = random.choice(customer_ids_list)
        address_id = random.choice(customer_data[customer_id])

        cur.execute(
            "INSERT INTO market.orders (customer_id, address_id, status) VALUES (%s, %s, 'delivered') RETURNING order_id",
            (customer_id, address_id)
        )
        order_id = cur.fetchone()[0]

        order_total_amount = 0
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            product_id = random.choice(product_ids)
            quantity = random.randint(1, 3)

            cur.execute("SELECT price FROM market.products WHERE product_id = %s", (product_id,))
            price_per_item = cur.fetchone()[0]

            cur.execute(
                "INSERT INTO market.order_items (order_id, product_id, quantity, price_per_item) VALUES (%s, %s, %s, %s)",
                (order_id, product_id, quantity, price_per_item)
            )
            order_total_amount += quantity * price_per_item
            order_item_records.append({'customer_id': customer_id, 'product_id': product_id})

        cur.execute(
            "UPDATE market.orders SET total_amount = %s WHERE order_id = %s",
            (round(order_total_amount, 2), order_id)
        )

        cur.execute(
            "INSERT INTO market.payements (order_id, amount) VALUES (%s, %s)",
            (order_id, round(order_total_amount, 2))
        )

        if (i + 1) % 500 == 0:
            print(f"... {i + 1}/{NUM_ORDERS} orders generated.")

    print("... Orders, items, and payments created.")


    print("Generating reviews...")
    num_reviews = len(order_item_records) // 3  # Create reviews for 1/3 of items bought
    for record in random.sample(order_item_records, k=num_reviews):
        cur.execute(
            "INSERT INTO market.reviews (product_id, user_id, rating, comment) VALUES (%s, %s, %s, %s)",
            (record['product_id'], record['customer_id'], random.randint(1, 5), fake.paragraph(nb_sentences=3))
        )
    print("... Reviews created.")


    set_parent_category(3, 7)


    print("All data generated. Committing transaction...")
    conn.commit()
    print("SUCCESS: Transaction committed.")

except psycopg2.Error as e:
    print(f"Psycopg2 error: {e}")
    if conn:
        conn.rollback()


finally:
    if conn:
        cur.close()
        conn.close()