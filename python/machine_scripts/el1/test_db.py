import psycopg2
try:
	conn = psycopg2.connect(user="ukvuowsb", password="xOy8nq3xddLpXCYoioU2q1r9O_0iFkkt", host="tai.db.elephantsql.com",port="5432",database="ukvuowsb")
except:
	print("unable to connect")
cur=conn.cursor()#cursor_factory=psycopg2.extras.DictCursor)
try:
	cur.execute("CREAT TABLE shay_test(image_name,image_quality_lable);")
except:
	print("can select from bar")
conn.commit()
textDict=({"image_name":"12345","image_quality_lable":"good"},
	{"image_name":"12346","image_quality_lable":"bad"})
cur.executemany("""INSER INTO shay_test(image_name,image_quality_lable) VALUES (%(image_name)s,%(image_quality_lable)s) """,textDict)

rows = cur.fetchall()
for row in rows:
	print(row)