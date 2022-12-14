# import sqlite3
# import psycopg2
import mysql.connector
# import docker
import time
from python_on_whales import docker

# def sqlite3Write():
#     # Connect to DB and create a cursor
#     conn = sqlite3.connect('/Users/ying-jeanne/Workspace/grafana/data/grafana.db')
#     curs = conn.cursor()

#     query1 = 'SELECT id FROM migration_log WHERE migration_id = "create folder table" AND success=1;'
#     curs.execute(query1)
#     result = curs.fetchone()

#     query2 = 'SELECT id, migration_id, sql FROM migration_log WHERE id >= {} AND success=1;'
#     queryStr2 = query2.format(result[0])
#     curs.execute(queryStr2)

#     # Fetch and output result
#     result = curs.fetchall()

#     with open('sqlite3.sql', 'w') as f:
#         for id, migration_id, sqlQuery in result:
#             f.write('-- %s\n' %migration_id)
#             result = " ".join(line.strip() for line in sqlQuery.splitlines())
#             f.write('%s\n' %result)

#     # Close the cursor
#     curs.close()

# def postgresWrite(): 
#     conn = psycopg2.connect(
#         host="127.0.0.1",
#         database="grafanadstest",
#         user="grafanatest",
#         password="grafanatest")

#     curs = conn.cursor()
#     query1 = "SELECT id FROM migration_log WHERE migration_id = 'create folder table' AND success=TRUE;"
#     curs.execute(query1)
#     result = curs.fetchone()
#     query2 = 'SELECT id, migration_id, sql FROM migration_log WHERE id >= {} AND success=TRUE;'
#     queryStr2 = query2.format(result[0])
#     curs.execute(queryStr2)

#     # Fetch and output result
#     result = curs.fetchall()

#     with open('postgres.sql', 'w') as f:
#         for id, migration_id, sqlQuery in result:
#             f.write('-- %s\n' %migration_id)
#             result = " ".join(line.strip() for line in sqlQuery.splitlines())
#             f.write('%s\n' %result)

#     # Close the cursor
#     curs.close()

def mysqlWrite(lastId: int, version: str) -> int:
    conn = mysql.connector.connect(host='localhost',
                                        database='grafana_ds_tests',
                                        user='grafana',
                                        password='password',
                                        port= 3307)
    curs = conn.cursor()
    query1 = 'SELECT id FROM migration_log ORDER BY id DESC LIMIT 1;'
    # query1 = 'SELECT id FROM migration_log WHERE migration_id = "create folder table" AND success=1;'
    curs.execute(query1)
    currentId = curs.fetchone()
    query2 = 'SELECT id, migration_id, `sql` FROM migration_log WHERE id >= {} AND success=1;'
    queryStr2 = query2.format(lastId)
    curs.execute(queryStr2)
    # Fetch and output result
    result = curs.fetchall()

    fileName = 'mysql.{}.up.sql'
    with open(fileName.format(version), 'w') as f:
        for id, migration_id, sqlQuery in result:
            f.write('-- %s\n' %migration_id)
            result = " ".join(line.strip() for line in sqlQuery.splitlines())
            f.write('%s\n' %result)

    # Close the cursor
    curs.close()
    return currentId

if __name__ == '__main__':
    # sqlite3Write()
    versions = [
        "7.0.0",
        "7.1.0",
    ]
    lastId = 0
    for version in versions:
        # client = docker.from_env()
        # print("Login return", r)
        # client.images.pull('grafana/grafana-oss:last')
        # l = client.containers.list()
        # print(client.images.list)
        # client.containers.compose("up", "-d")
        # container = client.containers.run(
        #     image='grafana/grafana-oss:' + version, name="grafana", ports={'3000': 3000},
        #         environment={
        #             "GF_DATABASE_TYPE": "mysql",
        #             "GF_DATABASE_HOST": "172.20.0.2:3307", 
        #             "GF_DATABASE_NAME": "grafana_ds_tests", 
        #             "GF_DATABASE_USER": "grafana",
        #             "GF_DATABASE_PASSWORD": "password"},
        #         stderr=True, stdout=True, detach=True, network="ying"
        # )
        # container.logs()
        fileName = '.env'
        content = 'grafana_version={}'
        with open(fileName, 'w') as f:
            f.write(content.format(version))

        docker.compose.build(cache=False)
        docker.compose.up()
       
        
        time.sleep(120)
        # postgresWrite()
        print("Start container finished, reading mysql database")
        lastId = mysqlWrite(lastId, version)
        docker.compose.down()
        # container.stop()
        # container.remove()
