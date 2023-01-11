import apps.dbconnect as db
from datetime import datetime

def addfewowners():

    sqlcode = """ INSERT INTO owners (
        owner_name,
        owner_contact,
        owner_modified_on
    )
    VALUES (%s, %s, %s)"""
   
    db.modifydatabase(sqlcode, ['Gian Regollo', '09178473633', datetime.now()])
    db.modifydatabase(sqlcode, ['Zy Boco', '09178473633', datetime.now()])
    db.modifydatabase(sqlcode, ['Myrrh Benigno', '09178473633', datetime.now()])
    db.modifydatabase(sqlcode, ['KC Serrano', '09178473633', datetime.now()])

    print('done!')
sql_resetowners = """
 TRUNCATE TABLE owners RESTART IDENTITY CASCADE
"""
db.modifydatabase(sql_resetowners, [])
addfewowners()

sql = 'SELECT * FROM owners'
values =[]
colnames = ['id', 'name', 'contact', 'modified', 'is_deleted']
df =  db.querydatafromdatabase(sql, values, colnames)
print(df)