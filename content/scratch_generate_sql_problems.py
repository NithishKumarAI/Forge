import json
import os

base_path = r'C:\My PC\git\Forge\content\problem-bank\sql'
os.makedirs(base_path, exist_ok=True)

problems = [
    {
        'key': 'sql-employees-by-dept',
        'title': 'Employees in department',
        'difficulty': 'easy',
        'schema': 'employees(id, name, department, salary)',
        'topic': 'sql-cs/select-filtering',
        'setup': "CREATE TABLE employees (id INT, name VARCHAR(50), department VARCHAR(50), salary INT); INSERT INTO employees VALUES (1, 'Alice', 'Engineering', 90000), (2, 'Bob', 'HR', 60000), (3, 'Charlie', 'Engineering', 85000), (4, 'David', 'Sales', 70000);",
        'rows': [['Alice'], ['Charlie']],
        'query': "SELECT name FROM employees WHERE department = 'Engineering' ORDER BY name"
    },
    {
        'key': 'sql-products-in-stock',
        'title': 'Products with stock above threshold',
        'difficulty': 'easy',
        'schema': 'products(id, name, category, stock_qty, price)',
        'topic': 'sql-cs/select-filtering',
        'setup': "CREATE TABLE products (id INT, name VARCHAR(50), category VARCHAR(50), stock_qty INT, price DECIMAL); INSERT INTO products VALUES (1, 'Laptop', 'Tech', 5, 1000), (2, 'Mouse', 'Tech', 15, 20), (3, 'Keyboard', 'Tech', 12, 50), (4, 'Desk', 'Furniture', 2, 200), (5, 'Chair', 'Furniture', 20, 100);",
        'rows': [['Chair', 20], ['Mouse', 15], ['Keyboard', 12]],
        'query': "SELECT name, stock_qty FROM products WHERE stock_qty > 10 ORDER BY stock_qty DESC"
    },
    {
        'key': 'sql-recent-orders',
        'title': 'Orders within date range',
        'difficulty': 'easy',
        'schema': 'orders(id, customer_id, amount, order_date)',
        'topic': 'sql-cs/select-filtering',
        'setup': "CREATE TABLE orders (id INT, customer_id INT, amount DECIMAL, order_date DATE); INSERT INTO orders VALUES (1, 101, 150.00, '2025-12-01'), (2, 102, 200.00, '2026-01-15'), (3, 103, 50.00, '2026-02-20'), (4, 104, 300.00, '2026-04-10');",
        'rows': [[2, 200.00], [3, 50.00]],
        'query': "SELECT id, amount FROM orders WHERE order_date BETWEEN '2026-01-01' AND '2026-03-31' ORDER BY order_date"
    },
    {
        'key': 'sql-user-search',
        'title': 'User name search',
        'difficulty': 'easy',
        'schema': 'users(id, username, email, active)',
        'topic': 'sql-cs/select-filtering',
        'setup': "CREATE TABLE users (id INT, username VARCHAR(50), email VARCHAR(50), active BOOLEAN); INSERT INTO users VALUES (1, 'alice', 'a@e.com', true), (2, 'bob', 'b@e.com', true), (3, 'aaron', 'aa@e.com', false), (4, 'andy', 'and@e.com', true), (5, 'charlie', 'c@e.com', true);",
        'rows': [[1, 'alice'], [4, 'andy']],
        'query': "SELECT id, username FROM users WHERE active = true AND username LIKE 'a%' ORDER BY id"
    },
    {
        'key': 'sql-distinct-cities',
        'title': 'Distinct customer cities',
        'difficulty': 'easy',
        'schema': 'customers(id, name, city, country)',
        'topic': 'sql-cs/select-filtering',
        'setup': "CREATE TABLE customers (id INT, name VARCHAR(50), city VARCHAR(50), country VARCHAR(50)); INSERT INTO customers VALUES (1, 'Alice', 'New York', 'USA'), (2, 'Bob', 'London', 'UK'), (3, 'Charlie', 'New York', 'USA'), (4, 'David', 'Paris', 'France');",
        'rows': [['London'], ['New York'], ['Paris']],
        'query': "SELECT DISTINCT city FROM customers ORDER BY city"
    },
    {
        'key': 'sql-null-email',
        'title': 'Find users with missing email',
        'difficulty': 'easy',
        'schema': 'users(id, name, email)',
        'topic': 'sql-cs/select-filtering',
        'setup': "CREATE TABLE users (id INT, name VARCHAR(50), email VARCHAR(50)); INSERT INTO users VALUES (1, 'Alice', 'alice@test.com'), (2, 'Bob', NULL), (3, 'Charlie', 'charlie@test.com'), (4, 'David', NULL);",
        'rows': [[2, 'Bob'], [4, 'David']],
        'query': "SELECT id, name FROM users WHERE email IS NULL ORDER BY id"
    },
    {
        'key': 'sql-employee-bonus',
        'title': 'Employee bonus classification',
        'difficulty': 'easy',
        'schema': 'employees(id, name, salary)',
        'topic': 'sql-cs/select-filtering',
        'setup': "CREATE TABLE employees (id INT, name VARCHAR(50), salary INT); INSERT INTO employees VALUES (1, 'Alice', 90000), (2, 'Bob', 40000), (3, 'Charlie', 60000), (4, 'David', 80000);",
        'rows': [['Alice', 'High'], ['David', 'High'], ['Charlie', 'Medium'], ['Bob', 'Low']],
        'query': "SELECT name, CASE WHEN salary >= 80000 THEN 'High' WHEN salary >= 50000 THEN 'Medium' ELSE 'Low' END AS bonus_tier FROM employees ORDER BY salary DESC"
    },
    {
        'key': 'sql-coalesce-address',
        'title': 'Default address fallback',
        'difficulty': 'easy',
        'schema': 'customers(id, name, shipping_address, billing_address)',
        'topic': 'sql-cs/select-filtering',
        'setup': "CREATE TABLE customers (id INT, name VARCHAR(50), shipping_address VARCHAR(100), billing_address VARCHAR(100)); INSERT INTO customers VALUES (1, 'Alice', '123 Ship St', '456 Bill St'), (2, 'Bob', NULL, '789 Bill St'), (3, 'Charlie', NULL, NULL), (4, 'David', '321 Ship St', NULL);",
        'rows': [['Alice', '123 Ship St'], ['Bob', '789 Bill St'], ['Charlie', 'No address'], ['David', '321 Ship St']],
        'query': "SELECT name, COALESCE(shipping_address, billing_address, 'No address') AS address FROM customers ORDER BY name"
    },
    {
        'key': 'sql-age-from-birthdate',
        'title': 'Calculate age in years',
        'difficulty': 'medium',
        'schema': 'members(id, name, birth_year)',
        'topic': 'sql-cs/select-filtering',
        'setup': "CREATE TABLE members (id INT, name VARCHAR(50), birth_year INT); INSERT INTO members VALUES (1, 'Alice', 1990), (2, 'Bob', 2000), (3, 'Charlie', 1985), (4, 'David', 2010);",
        'rows': [['Charlie', 41], ['Alice', 36], ['Bob', 26], ['David', 16]],
        'query': "SELECT name, (2026 - birth_year) AS age FROM members ORDER BY age DESC"
    },
    {
        'key': 'sql-dept-avg-salary',
        'title': 'Average salary by department',
        'difficulty': 'easy',
        'schema': 'employees(id, name, department, salary)',
        'topic': 'sql-cs/group-by',
        'setup': "CREATE TABLE employees (id INT, name VARCHAR(50), department VARCHAR(50), salary DECIMAL); INSERT INTO employees VALUES (1, 'A', 'Eng', 90000), (2, 'B', 'Eng', 100000), (3, 'C', 'HR', 60000), (4, 'D', 'Sales', 70000), (5, 'E', 'Sales', 75000);",
        'rows': [['Eng', 95000.00], ['Sales', 72500.00], ['HR', 60000.00]],
        'query': "SELECT department, ROUND(AVG(salary), 2) AS avg_salary FROM employees GROUP BY department ORDER BY avg_salary DESC"
    },
    {
        'key': 'sql-order-count-by-status',
        'title': 'Order count by status',
        'difficulty': 'easy',
        'schema': 'orders(id, customer_id, status, amount)',
        'topic': 'sql-cs/group-by',
        'setup': "CREATE TABLE orders (id INT, customer_id INT, status VARCHAR(20), amount DECIMAL); INSERT INTO orders VALUES (1, 1, 'Shipped', 10), (2, 1, 'Pending', 20), (3, 2, 'Shipped', 30), (4, 3, 'Cancelled', 40), (5, 4, 'Shipped', 50);",
        'rows': [['Shipped', 3], ['Cancelled', 1], ['Pending', 1]],
        'query': "SELECT status, COUNT(*) AS count FROM orders GROUP BY status ORDER BY count DESC"
    },
    {
        'key': 'sql-high-value-depts',
        'title': 'Departments with total salary above threshold',
        'difficulty': 'medium',
        'schema': 'employees(id, name, department, salary)',
        'topic': 'sql-cs/group-by',
        'setup': "CREATE TABLE employees (id INT, name VARCHAR(50), department VARCHAR(50), salary INT); INSERT INTO employees VALUES (1, 'A', 'Eng', 100000), (2, 'B', 'Eng', 60000), (3, 'C', 'HR', 50000), (4, 'D', 'Sales', 80000), (5, 'E', 'Sales', 80000);",
        'rows': [['Eng', 160000], ['Sales', 160000]],
        'query': "SELECT department, SUM(salary) AS total_salary FROM employees GROUP BY department HAVING SUM(salary) > 150000 ORDER BY department"
    },
    {
        'key': 'sql-product-revenue',
        'title': 'Total revenue by product',
        'difficulty': 'medium',
        'schema': 'order_items, products',
        'topic': 'sql-cs/group-by',
        'setup': "CREATE TABLE products (id INT, name VARCHAR(50)); CREATE TABLE order_items (id INT, order_id INT, product_id INT, quantity INT, unit_price INT); INSERT INTO products VALUES (1, 'Laptop'), (2, 'Mouse'), (3, 'Keyboard'); INSERT INTO order_items VALUES (1, 1, 1, 2, 1000), (2, 1, 2, 5, 20), (3, 2, 1, 1, 1000), (4, 2, 3, 2, 50);",
        'rows': [['Laptop', 3000], ['Keyboard', 100], ['Mouse', 100]],
        'query': "SELECT p.name, SUM(oi.quantity * oi.unit_price) AS revenue FROM products p JOIN order_items oi ON oi.product_id = p.id GROUP BY p.name ORDER BY revenue DESC"
    },
    {
        'key': 'sql-daily-sales',
        'title': 'Daily sales totals',
        'difficulty': 'easy',
        'schema': 'sales(id, sale_date, amount)',
        'topic': 'sql-cs/group-by',
        'setup': "CREATE TABLE sales (id INT, sale_date DATE, amount INT); INSERT INTO sales VALUES (1, '2026-01-01', 100), (2, '2026-01-01', 150), (3, '2026-01-02', 200), (4, '2026-01-03', 50), (5, '2026-01-03', 100);",
        'rows': [['2026-01-01', 250], ['2026-01-02', 200], ['2026-01-03', 150]],
        'query': "SELECT sale_date, SUM(amount) AS total FROM sales GROUP BY sale_date ORDER BY sale_date"
    },
    {
        'key': 'sql-employees-with-manager',
        'title': 'Employee and manager names',
        'difficulty': 'medium',
        'schema': 'employees',
        'topic': 'sql-cs/joins',
        'setup': "CREATE TABLE employees (id INT, name VARCHAR(50), manager_id INT); INSERT INTO employees VALUES (1, 'Alice', NULL), (2, 'Bob', 1), (3, 'Charlie', 1), (4, 'David', 2);",
        'rows': [['Alice', 'No Manager'], ['Bob', 'Alice'], ['Charlie', 'Alice'], ['David', 'Bob']],
        'query': "SELECT e.name AS employee, COALESCE(m.name, 'No Manager') AS manager FROM employees e LEFT JOIN employees m ON e.manager_id = m.id ORDER BY e.name"
    },
    {
        'key': 'sql-orders-with-no-items',
        'title': 'Orders with no line items',
        'difficulty': 'medium',
        'schema': 'orders, order_items',
        'topic': 'sql-cs/joins',
        'setup': "CREATE TABLE orders (id INT, customer_id INT, order_date DATE); CREATE TABLE order_items (id INT, order_id INT, product_id INT, quantity INT); INSERT INTO orders VALUES (1, 101, '2026-01-01'), (2, 102, '2026-01-02'), (3, 103, '2026-01-03'), (4, 104, '2026-01-04'); INSERT INTO order_items VALUES (1, 1, 1, 1), (2, 3, 2, 2);",
        'rows': [[2], [4]],
        'query': "SELECT o.id FROM orders o LEFT JOIN order_items oi ON oi.order_id = o.id WHERE oi.id IS NULL ORDER BY o.id"
    },
    {
        'key': 'sql-three-table-join',
        'title': 'Order details with customer and product',
        'difficulty': 'medium',
        'schema': 'customers, products, orders, order_items',
        'topic': 'sql-cs/joins',
        'setup': "CREATE TABLE customers (id INT, name VARCHAR(50)); CREATE TABLE products (id INT, name VARCHAR(50), price INT); CREATE TABLE orders (id INT, customer_id INT, order_date DATE); CREATE TABLE order_items (id INT, order_id INT, product_id INT, quantity INT); INSERT INTO customers VALUES (1, 'Alice'), (2, 'Bob'); INSERT INTO products VALUES (1, 'P1', 10), (2, 'P2', 20), (3, 'P3', 30); INSERT INTO orders VALUES (1, 1, '2026-01-01'), (2, 2, '2026-01-02'); INSERT INTO order_items VALUES (1, 1, 1, 2), (2, 1, 2, 1), (3, 2, 3, 5);",
        'rows': [['Alice', 'P1', 2], ['Alice', 'P2', 1], ['Bob', 'P3', 5]],
        'query': "SELECT c.name AS customer_name, p.name AS product_name, oi.quantity FROM customers c JOIN orders o ON o.customer_id = c.id JOIN order_items oi ON oi.order_id = o.id JOIN products p ON oi.product_id = p.id ORDER BY c.name"
    },
    {
        'key': 'sql-dept-head-count',
        'title': 'Department headcount including empty',
        'difficulty': 'easy',
        'schema': 'departments, employees',
        'topic': 'sql-cs/joins',
        'setup': "CREATE TABLE departments (id INT, name VARCHAR(50)); CREATE TABLE employees (id INT, name VARCHAR(50), dept_id INT); INSERT INTO departments VALUES (1, 'Eng'), (2, 'HR'), (3, 'Sales'); INSERT INTO employees VALUES (1, 'Alice', 1), (2, 'Bob', 1), (3, 'Charlie', 2);",
        'rows': [['Eng', 2], ['HR', 1], ['Sales', 0]],
        'query': "SELECT d.name, COUNT(e.id) AS headcount FROM departments d LEFT JOIN employees e ON e.dept_id = d.id GROUP BY d.id, d.name ORDER BY d.name"
    },
    {
        'key': 'sql-top-customer-per-region',
        'title': 'Customers with orders and total',
        'difficulty': 'medium',
        'schema': 'customers, orders',
        'topic': 'sql-cs/joins',
        'setup': "CREATE TABLE customers (id INT, name VARCHAR(50), region VARCHAR(50)); CREATE TABLE orders (id INT, customer_id INT, amount INT); INSERT INTO customers VALUES (1, 'A', 'North'), (2, 'B', 'North'), (3, 'C', 'South'), (4, 'D', 'South'); INSERT INTO orders VALUES (1, 1, 100), (2, 1, 200), (3, 3, 150);",
        'rows': [['A', 'North', 300], ['C', 'South', 150], ['B', 'North', 0], ['D', 'South', 0]],
        'query': "SELECT c.name, c.region, COALESCE(SUM(o.amount), 0) AS total_orders_amount FROM customers c LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.id, c.name, c.region ORDER BY total_orders_amount DESC"
    },
    {
        'key': 'sql-product-never-ordered',
        'title': 'Products never ordered',
        'difficulty': 'medium',
        'schema': 'products, order_items',
        'topic': 'sql-cs/joins',
        'setup': "CREATE TABLE products (id INT, name VARCHAR(50)); CREATE TABLE order_items (id INT, order_id INT, product_id INT); INSERT INTO products VALUES (1, 'P1'), (2, 'P2'), (3, 'P3'), (4, 'P4'); INSERT INTO order_items VALUES (1, 100, 1), (2, 101, 2), (3, 102, 3);",
        'rows': [['P4']],
        'query': "SELECT p.name FROM products p LEFT JOIN order_items oi ON oi.product_id = p.id WHERE oi.id IS NULL ORDER BY p.name"
    },
    {
        'key': 'sql-monthly-active-users',
        'title': 'Users who logged in this month',
        'difficulty': 'easy',
        'schema': 'users, login_events',
        'topic': 'sql-cs/joins',
        'setup': "CREATE TABLE users (id INT, name VARCHAR(50)); CREATE TABLE login_events (id INT, user_id INT, login_date DATE); INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie'), (4, 'David'); INSERT INTO login_events VALUES (1, 1, '2026-01-05'), (2, 1, '2026-01-10'), (3, 2, '2026-01-15'), (4, 3, '2025-12-31'), (5, 4, '2026-02-01');",
        'rows': [['Alice'], ['Bob']],
        'query': "SELECT DISTINCT u.name FROM users u JOIN login_events le ON le.user_id = u.id WHERE le.login_date >= '2026-01-01' AND le.login_date < '2026-02-01' ORDER BY u.name"
    },
    {
        'key': 'sql-students-all-subjects',
        'title': 'Students enrolled in all subjects',
        'difficulty': 'medium',
        'schema': 'students, subjects, enrollments',
        'topic': 'sql-cs/joins',
        'setup': "CREATE TABLE students (id INT, name VARCHAR(50)); CREATE TABLE subjects (id INT, name VARCHAR(50)); CREATE TABLE enrollments (student_id INT, subject_id INT); INSERT INTO students VALUES (1, 'A'), (2, 'B'), (3, 'C'); INSERT INTO subjects VALUES (1, 'Math'), (2, 'Science'), (3, 'History'); INSERT INTO enrollments VALUES (1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (3, 3);",
        'rows': [['A']],
        'query': "SELECT s.name FROM students s JOIN enrollments e ON e.student_id = s.id GROUP BY s.id, s.name HAVING COUNT(DISTINCT e.subject_id) = (SELECT COUNT(*) FROM subjects) ORDER BY s.name"
    },
    {
        'key': 'sql-above-average-salary',
        'title': 'Employees above average salary',
        'difficulty': 'medium',
        'schema': 'employees',
        'topic': 'sql-cs/subqueries',
        'setup': "CREATE TABLE employees (id INT, name VARCHAR(50), salary INT); INSERT INTO employees VALUES (1, 'A', 40000), (2, 'B', 50000), (3, 'C', 60000), (4, 'D', 70000), (5, 'E', 80000);",
        'rows': [['E', 80000], ['D', 70000]],
        'query': "SELECT name, salary FROM employees WHERE salary > (SELECT AVG(salary) FROM employees) ORDER BY salary DESC"
    },
    {
        'key': 'sql-customers-with-orders',
        'title': 'Customers who have placed orders',
        'difficulty': 'easy',
        'schema': 'customers, orders',
        'topic': 'sql-cs/subqueries',
        'setup': "CREATE TABLE customers (id INT, name VARCHAR(50)); CREATE TABLE orders (id INT, customer_id INT, amount INT); INSERT INTO customers VALUES (1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'); INSERT INTO orders VALUES (1, 1, 100), (2, 1, 200), (3, 3, 150);",
        'rows': [['A'], ['C']],
        'query': "SELECT name FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id) ORDER BY name"
    },
    {
        'key': 'sql-second-highest-salary',
        'title': 'Second highest salary',
        'difficulty': 'medium',
        'schema': 'employees',
        'topic': 'sql-cs/subqueries',
        'setup': "CREATE TABLE employees (id INT, name VARCHAR(50), salary INT); INSERT INTO employees VALUES (1, 'A', 40000), (2, 'B', 50000), (3, 'C', 60000), (4, 'D', 70000);",
        'rows': [[60000]],
        'query': "SELECT MAX(salary) AS max FROM employees WHERE salary < (SELECT MAX(salary) FROM employees)"
    },
    {
        'key': 'sql-dept-max-earner',
        'title': 'Top earner per department',
        'difficulty': 'medium',
        'schema': 'employees',
        'topic': 'sql-cs/subqueries',
        'setup': "CREATE TABLE employees (id INT, name VARCHAR(50), department VARCHAR(50), salary INT); INSERT INTO employees VALUES (1, 'A', 'Eng', 100000), (2, 'B', 'Eng', 90000), (3, 'C', 'HR', 60000), (4, 'D', 'Sales', 70000), (5, 'E', 'Sales', 70000);",
        'rows': [['A', 'Eng'], ['C', 'HR'], ['D', 'Sales'], ['E', 'Sales']],
        'query': "SELECT name, department FROM employees e WHERE salary = (SELECT MAX(salary) FROM employees e2 WHERE e2.department = e.department) ORDER BY department, name"
    },
    {
        'key': 'sql-cte-top-products',
        'title': 'Top selling products with CTE',
        'difficulty': 'medium',
        'schema': 'order_items, products',
        'topic': 'sql-cs/ctes',
        'setup': "CREATE TABLE products (id INT, name VARCHAR(50)); CREATE TABLE order_items (id INT, order_id INT, product_id INT, quantity INT); INSERT INTO products VALUES (1, 'P1'), (2, 'P2'), (3, 'P3'), (4, 'P4'), (5, 'P5'); INSERT INTO order_items VALUES (1, 100, 1, 5), (2, 101, 2, 10), (3, 102, 3, 15), (4, 103, 4, 20), (5, 104, 5, 2), (6, 105, 1, 5);",
        'rows': [['P4', 20], ['P3', 15], ['P1', 10]],
        'query': "WITH product_sales AS (SELECT product_id, SUM(quantity) AS total FROM order_items GROUP BY product_id) SELECT p.name, ps.total FROM products p JOIN product_sales ps ON ps.product_id = p.id ORDER BY ps.total DESC LIMIT 3"
    },
    {
        'key': 'sql-cte-running-balance',
        'title': 'Account balance with running total CTE',
        'difficulty': 'medium',
        'schema': 'transactions',
        'topic': 'sql-cs/ctes',
        'setup': "CREATE TABLE transactions (id INT, account_id INT, amount INT, txn_date DATE); INSERT INTO transactions VALUES (1, 1, 1000, '2026-01-01'), (2, 1, -200, '2026-01-05'), (3, 1, 500, '2026-01-10');",
        'rows': [['2026-01-01', 1000, 1000], ['2026-01-05', -200, 800], ['2026-01-10', 500, 1300]],
        'query': "WITH ordered AS (SELECT txn_date, amount, SUM(amount) OVER (ORDER BY txn_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS balance FROM transactions WHERE account_id = 1) SELECT txn_date, amount, balance FROM ordered ORDER BY txn_date"
    }
]

for p in problems:
    data = {
        'key': p['key'],
        'title': p['title'],
        'track': 'sql',
        'topic_tags': [p['topic'].split('/')[-1]],
        'difficulty': p['difficulty'],
        'interview_frequency': 'high',
        'estimated_minutes': 20,
        'statement_markdown': f"Write a query to find information based on {p['schema']}.",
        'constraints': ['Use PostgreSQL compatible syntax.'],
        'examples': [{'input': 'Sample data provided in database', 'output': str(p['rows'])}],
        'starter_query': 'SELECT ',
        'hints': ['Review the problem statement and expected output.'],
        'explanation': 'Use appropriate SQL clauses.',
        'reference_solution': p['query'],
        'complexity': 'O(n) depending on indexes.',
        'validation': {
            'mode': 'result_set',
            'order_sensitive': True,
            'setup_sql': p['setup'],
            'visible_tables': [p['schema']],
            'sample_rows': p['rows'][:2],
            'expected_columns': ['result_col' for _ in p['rows'][0]] if p['rows'] else [],
            'expected_rows': p['rows'],
            'hidden_datasets': [
                {
                    'setup_sql': p['setup'],
                    'expected_rows': p['rows']
                }
            ]
        },
        'source_type': 'original',
        'version': '1.0.0',
        'mapped_topic': p['topic']
    }
    
    with open(os.path.join(base_path, f"{p['key']}.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

print('Successfully wrote 28 problems.')
