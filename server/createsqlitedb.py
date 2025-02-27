import json
import sqlite3

with open("fall2025.json", "r") as file:
    data = json.load(file) 

# conn = sqlite3.connect("fall2025.db")

# cursor = conn.cursor()

# cursor.execute("""
#    CREATE TABLE IF NOT EXISTS courses (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     course_code TEXT,
#     course_name TEXT,
#     attribute TEXT ,
#     credits TEXT,
#     section TEXT,
#     times TEXT
#     );
# """
# )

for entry in data:
    insert_query = '''
        INSERT INTO courses (course_code, course_name, pre_requisite,section,credits,times,attribute)
        VALUES (?, ?, ?, ?,?,?,?)
    '''
    
    course_code = data["subject"] + " " + data["courseNumber"]
    course_name = data["courseTitle"]
    prerequisite = None
    section = None 
    credits = data["creditHours"]
    times = ""
    
    print(entry)
    print("\n\n")
    
    # cursor.execute(insert_query,
    #                (entry["id"], entry["name"], entry["age"]))

# conn.commit()
# conn.close()

print("JSON data successfully inserted into SQLite!")
