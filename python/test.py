import pymssql
import os
import subprocess

user = 'crumasterdba'
password = '6*(HF3!um:+H'
server = 'cru-poc-rds-db.cpqrib8hpigb.eu-west-1.rds.amazonaws.com'

conn = pymssql.connect(server, user, password, "InteractiveTool")
cursor = conn.cursor()
cursor.execute("""SELECT TABLE_NAME FROM InteractiveTool.INFORMATION_SCHEMA.Tables """)

for row in cursor:
    filename = print ("%s" % (row))
    dbout = subprocess.call("bcp InteractiveTool.dbo."+ filename +" out C:\\"+ filename +".txt -n -S WIN-AMNJ64HBK41\SQLEXPRESS -U test -P blah", shell=True)
    dbin = subprocess.call("bcp InteractiveTool.dbo."+ filename +" in C:\\"+ filename +".txt -n -S cru-poc-rds-db.cpqrib8hpigb.eu-west-1.rds.amazonaws.com -U crumasterdba -P 6*(HF3!um:+H", shell=True)

conn.commit()
conn.close()
