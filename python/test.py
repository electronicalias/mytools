import pymssql

user = 'crumasterdba'
password = '6*(HF3!um:+H'
server = 'cru-poc-rds-db.cpqrib8hpigb.eu-west-1.rds.amazonaws.com'

conn = pymssql.connect(server, user, password, "test")
cursor = conn.cursor()
cursor.execute("""
IF OBJECT_ID('persons', 'U') IS NOT NULL
    DROP TABLE persons
CREATE TABLE persons (
    id INT NOT NULL,
    name VARCHAR(100),
    salesrep VARCHAR(100),
    PRIMARY KEY(id)
)
""")
cursor.executemany(
    "INSERT INTO persons VALUES (%d, %s, %s)",
    [(1, 'John Smith', 'John Doe'),
     (2, 'Jane Doe', 'Joe Dog'),
     (3, 'Mike T.', 'Sarah H.')])
conn.commit()
conn.close()
