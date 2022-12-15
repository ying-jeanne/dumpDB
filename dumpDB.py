# import sqlite3
import psycopg2
import mysql.connector
import os
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

def postgresWrite(lastId: int, version: str) -> int:
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="grafanadstest",
        user="grafanatest",
        password="grafanatest")

    curs = conn.cursor()
    query1 = "SELECT id FROM migration_log WHERE success=TRUE ORDER BY id DESC LIMIT 1;"
    curs.execute(query1)
    currentId = curs.fetchone()
    query2 = 'SELECT id, migration_id, sql FROM migration_log WHERE id >= {} AND success=TRUE;'
    queryStr2 = query2.format(lastId)
    curs.execute(queryStr2)

    if not curs.rowcount:
        print("no result for version %s" %(version)) 
        return currentId[0]

    # Fetch and output result
    result = curs.fetchall()

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = f"postgres/postgres.{version}.up.sql"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, 'w') as f:
        for id, migration_id, sqlQuery in result:
            f.write('-- %s\n' %migration_id)
            result = " ".join(line.strip() for line in sqlQuery.splitlines())
            f.write('%s\n' %result)

    # Close the cursor
    curs.close()
    return currentId[0]

def mysqlWrite(lastId: int, version: str) -> int:
    conn = mysql.connector.connect(host='localhost',
                                        database='grafana_ds_tests',
                                        user='grafana',
                                        password='password',
                                        port= 3306)
    curs = conn.cursor()
    query1 = 'SELECT id FROM migration_log WHERE success=1 ORDER BY id DESC LIMIT 1;'
    # query1 = 'SELECT id FROM migration_log WHERE migration_id = "create folder table" AND success=1;'
    curs.execute(query1)
    currentId = curs.fetchone()
    print("the result is:", currentId)
    query2 = f'SELECT id, migration_id, `sql` FROM migration_log WHERE success=1 AND id>{lastId} ORDER BY id ASC;'
    print(query2)
    curs.execute(query2)
    
    if not curs.rowcount:
        print("no result for version %s" %(version)) 
        return currentId[0]
    
    # Fetch and output result
    result = curs.fetchall()

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = f"mysql/mysql.{version}.up.sql"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, 'w') as f:
        for id, migration_id, sqlQuery in result:
            f.write('-- %s\n' %migration_id)
            result = " ".join(line.strip() for line in sqlQuery.splitlines())
            f.write('%s\n' %result)

    # Close the cursor
    curs.close()
    return currentId[0]

if __name__ == '__main__':
    versions = [
        "7.0.0",
        "7.1.0",
        "7.2.0",
        "7.3.0",
        "7.4.0",
        "7.5.0",
        "8.0.0",
        "8.1.0",
        "8.2.0",
        "8.3.0",
        "8.4.0",
        "8.5.0",
        "9.0.0",
        "9.1.0",
        "9.2.0",
        "9.3.0"
    ]
    lastId = 0
    for version in versions:
        fileName = '.env'
        content = 'grafana_version={}'
        with open(fileName, 'w') as f:
            f.write(content.format(version))

        print("the last id is: %d" %(lastId))
        docker.compose.build()
        docker.compose.up(detach=True) 
        time.sleep(50)
        # lastId = mysqlWrite(lastId, version)
        lastId = postgresWrite(lastId, version)
        docker.compose.down()
        docker.compose.rm()
