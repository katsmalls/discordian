import sqlite3
from sqlite3 import Error


async def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param logger:
    :param conn: Connection object
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    finally:
        conn.close()

    return None


async def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param logger:
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    c = conn.cursor()
    c.execute(create_table_sql)


async def create_tables(db):
    if db is not None:
        # create zkill table
        zkill_table = """ CREATE TABLE IF NOT EXISTS zkill (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        channelid INTEGER NOT NULL,
                                        serverid INTEGER NOT NULL UNIQUE,
                                        groupid	INTEGER NOT NULL,
                                        ownerid INTEGER NOT NULL
                                    ); """
        await create_table(db, zkill_table)
    else:
        print('Database: Unable to connect to the database at ' + db_file)


async def select(sql):
    db = sqlite3.connect('firetail.sqlite')
    await create_tables(db)
    cursor = db.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    return data


async def execute_sql(sql, var=None):
    db = sqlite3.connect('firetail.sqlite')
    await create_tables(db)
    cursor = db.cursor()
    cursor.execute(sql, var)
    db.commit()
    db.close()
