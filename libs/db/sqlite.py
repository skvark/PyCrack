from sqlite3 import dbapi2 as sqlite

class HashDatabase():    
    def __init__(self, db='hash.db'):
        self.connection = sqlite.connect(db)
        self.cursor = self.connection.cursor()
        
        try:
            self.init_db()
        except sqlite.OperationalError:
            pass  # DB already exists.
            
    def init_db(self):
        self.cursor.execute('''CREATE TABLE hashes
                              (id INTEGER PRIMARY KEY,
                               key TEXT UNIQUE,
                               hash TEXT UNIQUE)''')
           
    def hash(self, hash, key = None):
        # Get?
        if key == None:
            # Prepared statements
            select = "SELECT key FROM hashes WHERE hash = ?"
            self.cursor.execute(select, [hash])
            result = self.cursor.fetchone()
            if result and len(result) > 0:
                return result[0]
            else:
                return False
        # OR set?
        elif hash is not None and key is not None:
            insert = "INSERT INTO hashes VALUES (?,?,?)"
            try:
                self.cursor.execute(insert, [None, key, hash])
                self.connection.commit()
            except sqlite.IntegrityError:
                pass  # Column not unique -> already exists =)