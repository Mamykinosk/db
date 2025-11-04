
CREATE SCHEMA if not exists users;
CREATE SCHEMA if not exists market;


CREATE TABLE if not exists  users.users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(10) NOT NULL CHECK (user_type IN ('customer', 'seller')),
    created_at TIMESTAMPTZ DEFAULT NOW()
) TABLESPACE ozon_data_space;

CREATE TABLE if not exists  users.user_profiles (
    profile_id INT PRIMARY KEY REFERENCES users.users(user_id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    birth_date DATE
) TABLESPACE ozon_data_space;

CREATE TABLE if not exists  users.addresses (
    address_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users.users(user_id) ON DELETE CASCADE,
    city VARCHAR(100) NOT NULL,
    street VARCHAR(255) NOT NULL,
    house_number VARCHAR(20) NOT NULL,
    apartment VARCHAR(20),
    postal_code VARCHAR(10)
) TABLESPACE ozon_data_space;

CREATE TABLE if not exists  market.categories (
    category_id SERIAL PRIMARY KEY,
    parent_category_id INT REFERENCES market.categories(category_id),
    name VARCHAR(255) NOT NULL UNIQUE
) TABLESPACE ozon_data_space;

CREATE TABLE if not exists  market.products (
    product_id SERIAL PRIMARY KEY,
    seller_id INT NOT NULL REFERENCES users.users(user_id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
) TABLESPACE ozon_data_space;

CREATE TABLE if not exists  market.product_categories (
    product_id INT NOT NULL REFERENCES market.products(product_id) ON DELETE CASCADE,
    category_id INT NOT NULL REFERENCES market.categories(category_id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, category_id)
) TABLESPACE ozon_data_space;

CREATE TABLE if not exists  market.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES users.users(user_id) ON DELETE CASCADE,
    address_id INT NOT NULL REFERENCES users.addresses(address_id),
    status VARCHAR(50) DEFAULT 'created',
    total_amount DECIMAL(12, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
) TABLESPACE ozon_data_space;

CREATE TABLE if not exists  market.order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES market.orders(order_id) ON DELETE CASCADE,
    product_id INT REFERENCES market.products(product_id) ON DELETE SET NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_per_item DECIMAL(10, 2) NOT NULL
) TABLESPACE ozon_data_space;

CREATE TABLE if not exists market.reviews (
    review_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES market.products(product_id),
    user_id INT NOT NULL REFERENCES users.users(user_id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
) TABLESPACE ozon_data_space;

CREATE TABLE if not exists market.payements (
    payement_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES market.orders(order_id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL
) TABLESPACE ozon_data_space;


CREATE INDEX  if not exists idx_orders_customer_id ON market.orders(customer_id) TABLESPACE ozon_idx_space;
CREATE index  if not exists idx_products_seller_id ON market.products(seller_id) TABLESPACE ozon_idx_space;

select count(*) from users.users;
