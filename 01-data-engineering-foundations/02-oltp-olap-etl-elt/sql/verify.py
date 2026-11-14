from pathlib import Path
import sqlite3


def verify():
    script = Path(__file__).with_name("retail-processing.sql").read_text()
    with sqlite3.connect(":memory:") as connection:
        connection.executescript(script)
        expected = [("North", 2, 15000), ("South", 1, 7000)]
        actual = connection.execute(
            "SELECT * FROM regional_totals ORDER BY region"
        ).fetchall()
        assert actual == expected, actual

        for first, second in (("etl_fact", "elt_fact"), ("elt_fact", "etl_fact")):
            difference = connection.execute(
                f"SELECT * FROM {first} EXCEPT SELECT * FROM {second}"
            ).fetchall()
            assert not difference, difference

        source_lines, source_gross = connection.execute(
            "SELECT COUNT(*), SUM(gross_cents) FROM landed_lines"
        ).fetchone()
        accepted_lines, accepted_gross, discounts = connection.execute(
            """SELECT COUNT(*), SUM(gross_cents), SUM(discount_cents)
               FROM landed_lines JOIN landed_orders USING (order_id)
               WHERE status = 'CONFIRMED'"""
        ).fetchone()
        assert (source_lines, source_gross) == (4, 33500)
        assert (accepted_lines, accepted_gross, discounts) == (3, 24500, 2500)
        fact_count, unique_keys = connection.execute(
            """SELECT (SELECT COUNT(*) FROM elt_fact), COUNT(*) FROM
               (SELECT DISTINCT order_id, line_id FROM elt_fact)"""
        ).fetchone()
        assert fact_count == unique_keys == accepted_lines
        assert sum(row[2] for row in actual) == accepted_gross - discounts
        for region, lines, net_cents in actual:
            print(f"{region}: {lines} accepted lines, {net_cents:,} net cents")
        print("PASS: grain, source controls, reconciliation, and ETL/ELT parity")


if __name__ == "__main__":
    verify()
