import psycopg2
import psycopg2.extras

while True:
    scanInputString = input()
    if scanInputString:                    # Check that the input string is not empty
        if scanInputString[0].isdigit():   # Panel QR Codes start with integers, i.e. 00012
            panelId = scanInputString
            stringIds = [] #list to store the 6 strings
        elif scanInputString[0] == 's':    # String QR Codes start with s, i.e. s00012
            stringIds.append((scanInputString[1:], panelId)) #save strings in db without leading 's'

        if len(stringIds) == 6:            # If all strings are scanned, upload to DB
            #Write to DB
            conn = psycopg2.connect(user="ukvuowsb", password="xOy8nq3xddLpXCYoioU2q1r9O_0iFkkt", host="tai.db.elephantsql.com",port="5432",database="ukvuowsb")
            cur = conn.cursor()
            query = """INSERT INTO production.string_panel (string_id, panel_id) VALUES (%s, %s)"""
            psycopg2.extras.execute_batch(cur, query, stringIds)
            conn.commit()
            conn.close()
            print('data uploaded to db')
            stringIds = []
