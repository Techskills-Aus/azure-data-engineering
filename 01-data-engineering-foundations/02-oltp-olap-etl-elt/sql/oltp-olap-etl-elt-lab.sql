PRAGMA foreign_keys = ON;

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    region TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('CONFIRMED', 'CANCELLED'))
);
CREATE TABLE order_line (
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    line_id INTEGER NOT NULL,
    gross_cents INTEGER NOT NULL CHECK (gross_cents >= 0),
    discount_cents INTEGER NOT NULL CHECK (discount_cents BETWEEN 0 AND gross_cents),
    PRIMARY KEY (order_id, line_id)
);
BEGIN;
INSERT INTO orders VALUES
    ('A101', 'North', 'CONFIRMED'), ('A102', 'North', 'CANCELLED'),
    ('A103', 'South', 'CONFIRMED');
INSERT INTO order_line VALUES
    ('A101', 1, 12000, 2000), ('A101', 2, 5000, 0),
    ('A102', 1, 9000, 0), ('A103', 1, 7500, 500);
COMMIT;

-- ETL: transform the source rows before writing the analytical target table.
CREATE TABLE etl_fact (
    order_id TEXT NOT NULL,
    line_id INTEGER NOT NULL,
    region TEXT NOT NULL,
    net_cents INTEGER NOT NULL,
    PRIMARY KEY (order_id, line_id)
);
INSERT INTO etl_fact
SELECT l.order_id, l.line_id, o.region, l.gross_cents - l.discount_cents
FROM order_line AS l JOIN orders AS o USING (order_id)
WHERE o.status = 'CONFIRMED';

-- ELT: land source-shaped tables, then apply the target-side business rule.
CREATE TABLE landed_orders AS SELECT * FROM orders;
CREATE TABLE landed_lines AS SELECT * FROM order_line;
CREATE VIEW elt_fact AS
SELECT l.order_id, l.line_id, o.region, l.gross_cents - l.discount_cents AS net_cents
FROM landed_lines AS l JOIN landed_orders AS o USING (order_id)
WHERE o.status = 'CONFIRMED';

CREATE VIEW regional_totals AS
SELECT region, COUNT(*) AS lines, SUM(net_cents) AS net_cents
FROM elt_fact GROUP BY region;
SELECT * FROM regional_totals ORDER BY region;

-- Both set differences must be empty. The test runner also verifies grain.
SELECT * FROM etl_fact EXCEPT SELECT * FROM elt_fact;
SELECT * FROM elt_fact EXCEPT SELECT * FROM etl_fact;
