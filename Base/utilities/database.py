# encoding utf-8
import sqlite3
import json
import os

class DataBase():
    def __init__(self, path, keys:list=None):
        self.path = path
        self.KEYS = keys

        self.conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../database/{path}"), check_same_thread=False)
        self.c = self.conn.cursor()
        self.na_create_table()

    async def update_one(self, query:dict, data:dict) -> None:
        t = "UPDATE main SET "

        qkey = list(query.keys())[0]
        qvalue = list(query.values())[0]
        for k, v in data.items():

            v = json.dumps(v)
            v = v.replace("'", "‘")
            t += f"{k}='{v}', "
        
        t = t[:-2] + " "
        if isinstance(qvalue, int):
            t += f"WHERE {qkey}={str(qvalue)}"
        else:
            t += f"WHERE {qkey}='{str(qvalue)}'"
        
        self.c.execute(t)
        self.conn.commit()

    async def find_one(self, query: dict) -> dict:
        out = {}

        qkey = list(query.keys())[0]
        qvalue = list(query.values())[0]

        self.c.execute(f'SELECT * FROM main WHERE {qkey}=?', (qvalue, ))
        fetch = self.c.fetchone()

        if not fetch and isinstance(qvalue, int):
            qvalue = str(qvalue)

            self.c.execute(f'SELECT * FROM main WHERE {qkey}=?', (qvalue, ))
            fetch = self.c.fetchone()

        if not fetch:
            return None

        kn = 0

        for item in fetch:
            if not isinstance(item, int) and not isinstance(item, float) and not item == None and not item == "":                
                try: out[self.KEYS[kn]] = json.loads(item)
                except:
                    out[self.KEYS[kn]] = item
            else:
                out[self.KEYS[kn]] = item
            kn += 1

        return out

    
    async def insert(self, data: dict) -> None:
        for k, v in data.items():
            if isinstance(v, dict):
                data[k] = json.dumps(v)
            elif isinstance(v, list):
                data[k] = str(v)

        args = tuple()
        for key in self.KEYS:
            if key in data:
                args += (data[key],)
            else:
                args += (json.dumps(None), )

        self.c.execute(f"INSERT OR IGNORE INTO main({', '.join(k for k in self.KEYS)}) VALUES ({', '.join('?'*len(self.KEYS))})",
                    (args))

        self.conn.commit()

    async def create_table(self):
        self.c.execute(f"CREATE TABLE IF NOT EXISTS main({', '.join(k for k in self.KEYS)})")

        self.conn.commit()

    async def delete_one(self, query: dict) -> None:
        qkey = list(query.keys())[0]
        qvalue = list(query.values())[0]
        self.c.execute(f"DELETE FROM main WHERE {qkey}=?",
                (qvalue,))

        self.conn.commit()

    async def find_all(self) -> dict:
        out = []
        self.c.execute("SELECT * FROM main")

        fetch = self.c.fetchall()

        if not fetch:
            return None

        for item in fetch:
            kn = 0
            now = {}
            for iv in item:
                now[self.KEYS[kn]] = iv
                kn += 1
            
            out.append(now)
        # for server in fetch:
        #     kn = 0
        #     out[server[0]] = {}
        #     for item in server:
        #         if not isinstance(item, int) and not isinstance(item, float) and not item == None and not item == "":
        #             try: out[server[0]][self.KEYS[kn]] = json.loads(item)
        #             except: out[server[0]][self.KEYS[kn]] = item
        #         else:
        #             out[server[0]][self.KEYS[kn]] = item
        #         kn += 1

        return out

    # NON ASYNC (na)

    def na_update_one(self, query:dict, data:dict) -> None:
        t = "UPDATE main SET "

        qkey = list(query.keys())[0]
        qvalue = list(query.values())[0]
        for k, v in data.items():

            v = json.dumps(v)
            v = v.replace("'", "‘")
            t += f"{k}='{v}', "
        
        t = t[:-2] + " "
        t += f"WHERE {qkey}='{str(qvalue)}'"
        self.c.execute(t)
        self.conn.commit()

    def na_find_one(self, query: dict) -> dict:
        out = {}
        qkey = list(query.keys())[0]
        qvalue = list(query.values())[0]
        self.c.execute(f'SELECT * FROM main WHERE {qkey}=?', (qvalue,))
        fetch = self.c.fetchone()

        if not fetch:
            return None

        kn = 0

        for item in fetch:
            if not isinstance(item, int) and not isinstance(item, float) and not item == None and not item == "":                
                try: out[self.KEYS[kn]] = json.loads(item)
                except:
                    out[self.KEYS[kn]] = item
            else:
                out[self.KEYS[kn]] = item
            kn += 1

        return out

    
    def na_insert(self, data: dict) -> None:
        for k, v in data.items():
            if isinstance(v, dict):
                data[k] = json.dumps(v)
            elif isinstance(v, list):
                data[k] = str(v)

        args = tuple()
        for key in self.KEYS:
            if key in data:
                args += (data[key],)
            else:
                args += (json.dumps(None), )

        self.c.execute(f"INSERT OR IGNORE INTO main({', '.join(k for k in self.KEYS)}) VALUES ({', '.join('?'*len(self.KEYS))})",
                    (args))

        self.conn.commit()

    def na_create_table(self):
        self.c.execute(f"CREATE TABLE IF NOT EXISTS main({', '.join(k for k in self.KEYS)})")

        self.conn.commit()

    def na_delete_one(self, query: dict) -> None:
        qkey = list(query.keys())[0]
        qvalue = list(query.values())[0]
        self.c.execute(f"DELETE FROM main WHERE {qkey}=?",
                (qvalue,))

        self.conn.commit()

    def na_find_all(self) -> dict:
        out = {}
        self.c.execute("SELECT * FROM main")

        fetch = self.c.fetchall()

        if not fetch:
            return None


        for server in fetch:
            kn = 0
            out[server[0]] = {}
            for item in server:
                if not isinstance(item, int) and not isinstance(item, float) and not item == None and not item == "":
                    try: out[server[0]][self.KEYS[kn]] = json.loads(item)
                    except: out[server[0]][self.KEYS[kn]] = item
                else:
                    out[server[0]][self.KEYS[kn]] = item
                kn += 1

        return out
