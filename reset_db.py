import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def reset_db():
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='123456',
        host='localhost',
        port='5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        cur.execute('DROP DATABASE "page-spark"')
        print("Dropped database page-spark")
    except Exception as e:
        print(f"Error dropping: {e}")
        
    try:
        cur.execute('CREATE DATABASE "page-spark"')
        print("Created database page-spark")
    except Exception as e:
        print(f"Error creating: {e}")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    reset_db()
