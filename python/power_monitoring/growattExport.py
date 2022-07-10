import requests
import json
from datetime import date, datetime
import psycopg2
import psycopg2.extras

today = date.today()

# dd/mm/YY
d1 = today.strftime("%Y-%m-%d")
url = "https://server.growatt.com/panelB.do/getInvRealTimeCharts?plantId=1348164&date=" + d1

payload={}
headers = {
  'authority': 'server.growatt.com',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,de;q=0.7',
  'cache-control': 'max-age=0',
  'cookie': 'JSESSIONID=697F6CFF03CBE94194570A85E6A9539A; loginPage=login.do; termsLogoName=logo.png; termsCName=Growatt; termsSName=ShineServer; selectedUserId=1621469; selectedPlantId=1348164; SERVERID=7a64d333cd3c577f6b5bb0f1d4c58fd5|1657447977|1657447040; JSESSIONID=4BD3407D9F23A650EB2577DAC6F50E94; SERVERID=7a64d333cd3c577f6b5bb0f1d4c58fd5|1657448349|1657447040',
  'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

response = requests.request("GET", url, headers=headers, data=payload)
test = json.loads(response.text)
test2 = json.loads(test["chartData"])

data = []
for entry in test2["pac"]:
    dt = datetime.strptime(d1 + " " + entry, "%Y-%m-%d %H:%M")
    data.append((dt, test2["pac"][entry]))

conn = psycopg2.connect(user="jzztvyjdirgomm", password="974386311e9bf8265574baead65862ee677601c0f8e05bc954785e899d86dfaa", host="ec2-34-247-151-118.eu-west-1.compute.amazonaws.com",port="5432",database="djaki03gmcu3o")
cur = conn.cursor()
query = """INSERT INTO production.power_log (time_stamp, power, farm_id) VALUES (%s, %s, 1)
ON CONFLICT (time_stamp) DO UPDATE
SET power = EXCLUDED.power
"""
psycopg2.extras.execute_batch(cur, query, data)
conn.commit()
conn.close()
print("data uploaded to db")