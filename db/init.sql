-- 1. Get the Northwind schema (We use a lightweight remote fetch for the standard dataset)
-- Since docker-entrypoint-initdb.d runs scripts in order, we will create the tables and data first.
-- For the sake of this setup, we will create a few core tables locally to guarantee it works instantly.
-- (If you have a full Northwind SQL file, you can paste it here, but let's use a minimal functional setup for our MVP!)

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_name VARCHAR(255)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Insert dummy data
INSERT INTO products (name, price, category) VALUES 
('Product A', 100.00, 'Electronics'), ('Product B', 50.00, 'Clothing'), ('Product C', 20.00, 'Food');

INSERT INTO orders (order_date, customer_name) VALUES 
(CURRENT_DATE - INTERVAL '1 month', 'Alice'), (CURRENT_DATE - INTERVAL '2 months', 'Bob');

INSERT INTO order_items (order_id, product_id, quantity, price) VALUES 
(1, 1, 2, 100.00), (1, 2, 1, 50.00), (2, 3, 5, 20.00), (2, 1, 1, 100.00);

-- 2. CREATE THE READ-ONLY ROLE (Crucial step from your spec)
CREATE ROLE agent_readonly WITH LOGIN PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE northwind TO agent_readonly;
GRANT USAGE ON SCHEMA public TO agent_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO agent_readonly;

-- Ensure future tables also get read-only access (optional but good practice)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO agent_readonly;