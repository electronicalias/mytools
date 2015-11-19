import pymssql

user = 'crumasterdba'
password = '6*(HF3!um:+H'
server = 'cru-poc-rds-db.cpqrib8hpigb.eu-west-1.rds.amazonaws.com'

conn = pymssql.connect(server, user, password, "InteractiveTool")
cursor = conn.cursor()
cursor.execute("""SELECT TABLE_NAME FROM InteractiveTool.INFORMATION_SCHEMA.Tables """)

for row in cursor:
    print ("%s" % (row))

conn.commit()
conn.close()
