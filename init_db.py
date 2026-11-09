import sqlite3

def initialize_database():
    conn = sqlite3.connect('orchestrator.db')
    with open('schema.sql', 'r') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("Database orchestrator.db successfully created with strict NFR3 triggers.")

if __name__ == "__main__":
    initialize_database()