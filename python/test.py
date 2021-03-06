import pymssql
import os
import subprocess
import sys

source.user = sys.argv[1]
source.password = sys.arv[2]
source.server = sys.argv[3]
dest.user = sys.argv[4]
dest.password = sys.arv[5]
dest.server = sys.argv[6]
database = sys.argv[7]

conn = pymssql.connect(server, user, password, database)
cursor = conn.cursor()
cursor.execute("""SELECT TABLE_NAME FROM InteractiveTool.INFORMATION_SCHEMA.Tables WHERE TABLE_TYPE='BASE TABLE'""")

for row in cursor:
    filename = ("%s" % (row))
    dbout = subprocess.call("bcp "+ database +".dbo."+ filename +" out C:\\"+ filename +".txt -n -S "+ source.server +" -U "+ source.user +" -P "+ source.password +"", shell=True)
    dbin = subprocess.call("bcp "+ database +".dbo."+ filename +" in C:\\"+ filename +".txt -n -S "+ dest.server +" -U "+ dest.user +" -P "+ dest.password +"", shell=True)

conn.commit()
conn.close()
