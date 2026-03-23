import psycopg2

conn = psycopg2.connect(
    host="localhost",
    user="Erneste304tech",
    password="12345",
    port=5432,
    database="postgres"
)

conn.autocommit = True
cur = conn.cursor()

cur.execute('CREATE DATABASE "Rutabo database management";')

print("✅ Database created!")

cur.close()
conn.close()
