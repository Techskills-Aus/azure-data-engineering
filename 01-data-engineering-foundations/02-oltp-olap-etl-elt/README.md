# Day 02 · OLTP, OLAP, ETL and ELT

**Module 01 · Chapter 02 of 05**

1. Read the [complete chapter](notes/OLTP%2C%20OLAP%2C%20ETL%20and%20ELT.md) or [download the textbook PDF](notes/OLTP%2C%20OLAP%2C%20ETL%20and%20ELT.pdf).
2. Open the [editable teaching slides](presentation/OLTP%2C%20OLAP%2C%20ETL%20and%20ELT.pptx).
3. Run the SQL exercise.

## Local practice

Download [oltp-olap-etl-elt-lab.sql](sql/oltp-olap-etl-elt-lab.sql) and [oltp-olap-etl-elt-validation.py](sql/oltp-olap-etl-elt-validation.py) to the same folder. Run `python oltp-olap-etl-elt-validation.py` with Python 3. The script uses in-memory SQLite and requires no cloud account or external dependencies. It models the ETL and ELT boundaries with separate tables and views inside one database.

| Region | Accepted order lines | Net amount in cents |
|---|---:|---:|
| North | 2 | 15,000 |
| South | 1 | 7,000 |

The verifier checks source control totals, accepted line grain, regional results and both directions of ETL/ELT equality. Azure deployments are outside the local exercise.

[Previous chapter](../01-introduction-to-data-engineering/) · [Foundations glossary](../01-introduction-to-data-engineering/notes/Data%20Engineering%20and%20Business%20Glossary.md)

**Author** Madhur Mehta (professorofdata)
