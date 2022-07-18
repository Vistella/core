import growattServer
from datetime import date, datetime
import psycopg2
import psycopg2.extras

api = growattServer.GrowattApi()
login_response = api.login('vistella', 'vistella1234')

plant_list = api.plant_list(login_response['user']['id'])
d1 = date.today()
d1_str = d1.strftime("%Y-%m-%d")
query_data = []

print("***List of plants***")
for plant in plant_list['data']:
    print("ID: %s, Name: %s"%(plant['plantId'], plant['plantName']), 2)
    power_data = api.plant_detail(plant['plantId'], timespan=growattServer.Timespan['day'],date = d1)
    for entry in power_data["data"]:
        dt = datetime.strptime(d1_str + " " + entry, "%Y-%m-%d %H:%M")
        query_data.append((dt,  power_data["data"][entry], plant['plantId']))

conn = psycopg2.connect(user="jzztvyjdirgomm", password="974386311e9bf8265574baead65862ee677601c0f8e05bc954785e899d86dfaa", host="ec2-34-247-151-118.eu-west-1.compute.amazonaws.com",port="5432",database="djaki03gmcu3o")
cur = conn.cursor()
query = """INSERT INTO production.power_log (time_stamp, power, farm_id) VALUES (%s, %s, %s)
ON CONFLICT (time_stamp) DO UPDATE
SET power = EXCLUDED.power
"""
psycopg2.extras.execute_batch(cur, query, query_data)
conn.commit()
conn.close()
print("data uploaded to db")