import psycopg2
import pandas as pd

def getdblocation():

    db = psycopg2.connect(
 
        host='localhost',
        database='172proje',
        user='postgres',
        port=5432,
        password='myr69'
    )

    return db

print(getdblocation())

def modifydatabase(sql, values):
    db = getdblocation()
    cursor = db.cursor()
    cursor.execute(sql, values)
    db.commit()
    db.close()

def querydatafromdatabase(sql, values, dfcolumns):
    db = getdblocation()
    cur = db.cursor()
    cur.execute(sql, values)
    rows = pd.DataFrame(cur.fetchall(), columns=dfcolumns)
    db.close()
    return rows