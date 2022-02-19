import psycopg2
from sqlalchemy import column


print("=====================================")
DATABASE_URL = 'postgres://vsszkbimyldkmr:cfa2e2f3909965bf340fd61f95648e6311616a0feb10cbb05c39713878b2be2d@ec2-3-228-222-169.compute-1.amazonaws.com:5432/d35fogc38bmvng'
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
column_name = 'twitterid'
id = '2423455610'
cur.execute(
    "SELECT EXISTS (SELECT * FROM database WHERE {} = '{}')".format(column_name,id))

print(cur.fetchone()[0])