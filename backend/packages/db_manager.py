import sqlite3

class DBManager:
    def __init__(self, DB_PATH):
        self.DB_PATH = DB_PATH
        self.connect()
        
    def connect(self):
        self._conn = sqlite3.connect(self.DB_PATH)
        self._cur = self._conn.cursor()
        
    def commit(self):
        self._conn.commit()
        
    def close(self):
        self._cur.close()
        self._conn.close()

    def execute(self, query, params = ()):
        response = self._cur.execute(query, params)
        return response
        
    def executemany(self, query, params = ()):
        response = self._cur.executemany(query, params)
        return response
        
    def description(self):
        return self._cur.description
    
    def get_column_names(self):
        return [c[0] for c in self.description()]
    
    def dict_factory(self, row, columns):
        return {c:row[i] for i, c in enumerate(columns)}
    
    def transaction(self, query, params = (), many = False):
        if many:
            self.executemany(query, params)
        else:
            self.execute(query, params)
        
        self.commit()
        self.close()
        self.connect()
    
    def check_table_exists(self, table_name):
        params = {
            "name": table_name
        }
        query = f"SELECT * FROM sqlite_master WHERE name=:name"
        response = self.execute(query, params)
        data = response.fetchall()
        return len(data) >= 1
        
if __name__ == "__main__":
    db_manager = DBManager("/Users/cwyoungg/timetable_manager/packages/test.db")
    table_name = "test"
    import numpy as np
    check = db_manager.check_table_exists(table_name)
    if not check:
        db_manager.transaction(f"CREATE TABLE {table_name}(col1 INT, col2 TEXT)")
        print("Success to create table")
    else:
        data = (np.nan, np.nan)
        db_manager.transaction(f"INSERT INTO {table_name} VALUES(?, ?)", data)
        
        response = db_manager.execute(f"SELECT * FROM {table_name}")
        print(response.fetchall())
        # print("There is already the same name's table")
        