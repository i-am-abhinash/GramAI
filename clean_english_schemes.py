from backend.database.mysql_connection import db

conn = db.connect()
cursor = conn.cursor()

# Delete the english mock schemes
cursor.execute("DELETE FROM imported_schemes WHERE name IN ('PM Kisan Samman Nidhi (Auto)', 'NTR Bharosa Pension (Auto)', 'White Ration Card (Auto)')")
conn.commit()

# Delete any pending reviews related to them (cascade might not be set up)
# But it's easier to just delete them if needed. 
# Better yet, let's just delete from imported_schemes where name contains English characters for the old ones.
print(f"Deleted {cursor.rowcount} old English mock scheme records.")

cursor.close()
conn.close()
