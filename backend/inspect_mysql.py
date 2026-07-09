"""Inspect the remote MySQL database schema."""
import mysql.connector

conn = mysql.connector.connect(
    host="172.105.48.130",
    port=3306,
    user="genuineh_dashboard",
    password="Honeybee@2025-26",
    database="genuineh_dashboard"
)
cursor = conn.cursor()

# 1. List all tables
cursor.execute("SHOW TABLES")
tables = [row[0] for row in cursor.fetchall()]
print(f"=== TABLES ({len(tables)}) ===")
for t in tables:
    print(f"  - {t}")

print("\n")

# 2. For each table, show columns, types, keys, and row counts
for table in tables:
    cursor.execute(f"DESCRIBE `{table}`")
    columns = cursor.fetchall()
    cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
    count = cursor.fetchone()[0]
    print(f"\n=== TABLE: {table} ({count} rows) ===")
    print(f"{'Column':<40} {'Type':<30} {'Null':<6} {'Key':<6} {'Default':<20} {'Extra'}")
    print("-" * 130)
    for col in columns:
        field, col_type, null, key, default, extra = col
        print(f"{field:<40} {col_type:<30} {null:<6} {key:<6} {str(default):<20} {extra}")

# 3. Show foreign keys
print("\n\n=== FOREIGN KEY RELATIONSHIPS ===")
cursor.execute("""
    SELECT 
        TABLE_NAME, COLUMN_NAME, 
        REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME,
        CONSTRAINT_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'genuineh_dashboard'
    AND REFERENCED_TABLE_NAME IS NOT NULL
    ORDER BY TABLE_NAME
""")
fks = cursor.fetchall()
if fks:
    for fk in fks:
        print(f"  {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}  (constraint: {fk[4]})")
else:
    print("  No foreign keys found")

# 4. Show sample data from main tables (first 3 rows)
print("\n\n=== SAMPLE DATA (first 3 rows per table) ===")
for table in tables:
    cursor.execute(f"SELECT * FROM `{table}` LIMIT 3")
    rows = cursor.fetchall()
    if rows:
        cursor.execute(f"DESCRIBE `{table}`")
        col_names = [c[0] for c in cursor.fetchall()]
        print(f"\n--- {table} ---")
        for row in rows:
            row_dict = dict(zip(col_names, row))
            # Truncate long values
            for k, v in row_dict.items():
                if isinstance(v, str) and len(v) > 100:
                    row_dict[k] = v[:100] + "..."
            print(f"  {row_dict}")

conn.close()
print("\n\nDone!")
