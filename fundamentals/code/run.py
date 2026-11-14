"""Generate synthetic bank postings and reconcile incremental deliveries locally."""
import argparse
import csv
import json
import sqlite3
from pathlib import Path
from random import Random
from datetime import date, timedelta

parser = argparse.ArgumentParser()
parser.add_argument('--rows', type=int, choices=[1000,100000,500000,1000000], default=100000)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
out = args.output
out.mkdir(parents=True, exist_ok=True)
rng = Random(2718)
fields = ('posting_id','account_id','branch','business_date','amount_cents','version','arrival_batch')
n = args.rows
accounts = max(50,n//20)
base, delta, expected = [], [], {}
for i in range(n):
    account = rng.randrange(accounts)
    branch = 'NY' if account % 10 < 6 else ('IL' if account % 10 < 9 else 'TX')
    posting = [i, account, branch, str(date(2026,1,1)+timedelta(days=i%90)), rng.randint(1,20000)*(-1 if i%3 else 1), 1, 1]
    if i%100 == 0:
        posting[-1] = 2
        delta.append(posting)
    else:
        base.append(posting)
        if i%100 == 1:
            delta.append(posting[:-1]+[2])
        if i%200 == 2:
            delta.append(posting[:4]+[posting[4]+125,2,2])
    last = delta[-1] if delta and delta[-1][0] == i else posting
    expected[i] = last
db = sqlite3.connect(':memory:')
db.execute('CREATE TABLE posting(id INTEGER PRIMARY KEY, account INTEGER, branch TEXT, day TEXT, cents INTEGER, version INTEGER, batch INTEGER)')
sql = '''INSERT INTO posting VALUES (?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE
SET cents=excluded.cents, version=excluded.version, batch=excluded.batch
WHERE excluded.version > posting.version'''
for name, rows in [('batch_01',base),('batch_02',delta)]:
    with (out/f'{name}.csv').open('w',newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(fields)
        writer.writerows(rows)
    with (out/f'{name}.csv').open(newline='') as stream, db:
        reader = csv.reader(stream)
        next(reader)
        db.executemany(sql,reader)
assert db.execute('SELECT COUNT(*),SUM(cents) FROM posting').fetchone() == (n,sum(r[4] for r in expected.values()))
with db:
    db.executemany(sql,delta)
assert db.execute('SELECT COUNT(*),SUM(cents) FROM posting').fetchone() == (n,sum(r[4] for r in expected.values()))
summary = {'canonical_rows':n,'batch_01_rows':len(base),'batch_02_rows':len(delta),'net_cents':sum(r[4] for r in expected.values()),'replay':'PASS'}
(out/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
with (out/'branch_daily.csv').open('w',newline='') as stream:
    writer=csv.writer(stream)
    writer.writerow(['branch','business_date','posting_count','net_cents'])
    writer.writerows(db.execute('SELECT branch,day,COUNT(*),SUM(cents) FROM posting GROUP BY branch,day ORDER BY branch,day'))
print(json.dumps(summary))
