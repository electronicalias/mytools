import pymssql

user = 'test'
password = 'blah'
server = 'WIN-AMNJ64HBK41.crugroup.internal'

conn = pymssql.connect(server, user, password, "InteractiveTool")
cursor = conn.cursor()
cursor.execute("""SELECT TABLE_NAME FROM InteractiveTool.INFORMATION_SCHEMA.Tables """)

for row in cursor:
    print row

conn.commit()
conn.close()
