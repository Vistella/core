import psycopg2

conn = psycopg2.connect(user="ukvuowsb", password="xOy8nq3xddLpXCYoioU2q1r9O_0iFkkt", host="tai.db.elephantsql.com",port="5432",database="ukvuowsb")
cur = conn.cursor()
cur.execute("INSERT INTO production.string_el_image (created_At, link) VALUES (%s, %s)",(str(date), ))
conn.commit()
