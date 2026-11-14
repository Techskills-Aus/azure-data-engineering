# Day 02 · OLTP, OLAP, ETL and ELT

**Module 01 · Chapter 02 of 05**

1. Read the [complete chapter](notes/02-processing-workloads.md) or [download the textbook PDF](notes/day02-lecture-blue-white.pdf).
2. Compare the two pipeline boundaries using the [architecture PDF](architecture/day02-processing.pdf) or [editable draw.io](architecture/day02-processing.drawio). Page ARCH-201 shows ETL and ELT side by side.
3. Open the [editable teaching slides](presentation/day02-processing.pptx).
4. Run the SQL exercise, then try the [eight interview questions and worked answers](interview-questions/).

## Local practice

Download [retail-processing.sql](sql/retail-processing.sql) and [verify.py](sql/verify.py) to the same folder. Run `python verify.py` with Python 3. The script uses in-memory SQLite and requires no cloud account or external dependencies. It models the ETL and ELT boundaries with separate tables and views inside one database.

| Region | Accepted order lines | Net amount in cents |
|---|---:|---:|
| North | 2 | 15,000 |
| South | 1 | 7,000 |

The verifier checks source control totals, accepted line grain, regional results and both directions of ETL/ELT equality. Azure deployments are outside the local exercise.

[Previous chapter](../01-introduction-to-data-engineering/) · [Foundations glossary](../01-introduction-to-data-engineering/notes/00-glossary.md)

**Author** Madhur Mehta (professorofdata)
