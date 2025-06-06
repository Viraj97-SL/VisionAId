import sqlite3

conn = sqlite3.connect('../vision_logs.db')
cursor = conn.cursor()

# Show table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# View contents of vision_logs
cursor.execute("SELECT * FROM vision_logs")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
