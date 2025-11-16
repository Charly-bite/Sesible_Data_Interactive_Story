#!/usr/bin/env python3
"""
Migrate SQLite database to PostgreSQL (Supabase).
This script will:
1. Read data from your optimized SQLite database
2. Create table in PostgreSQL
3. Upload data in batches
4. Create indexes for fast searching

Required: pip install psycopg2-binary
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import os
import sys

# Database configuration
SQLITE_DB = 'data.db'
# Get PostgreSQL URL from environment variable
POSTGRES_URL = os.environ.get('DATABASE_URL')

# Columns to migrate (reduced schema)
COLUMNS = ['NOMBRE', 'PATERNO', 'MATERNO', 'FECNAC', 'CALLE', 'COLONIA', 'CURP']
INDEX_FIELDS = ['NOMBRE', 'PATERNO', 'MATERNO', 'CURP']

BATCH_SIZE = 5000

def get_postgres_connection(url):
    """Connect to PostgreSQL database."""
    # Handle Render's postgres:// vs postgresql:// prefix
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    
    return psycopg2.connect(url)

def create_postgres_table(pg_conn):
    """Create the clients table in PostgreSQL."""
    cursor = pg_conn.cursor()
    
    # Drop table if exists (for clean migration)
    print("Dropping existing table if present...")
    cursor.execute("DROP TABLE IF EXISTS clients CASCADE;")
    
    # Create table with columns
    columns_def = ', '.join([f'"{col}" TEXT' for col in COLUMNS])
    lc_columns_def = ', '.join([f'"{col}_LC" TEXT' for col in INDEX_FIELDS])
    
    create_table_sql = f"""
    CREATE TABLE clients (
        id SERIAL PRIMARY KEY,
        {columns_def},
        {lc_columns_def}
    );
    """
    
    print("Creating clients table...")
    cursor.execute(create_table_sql)
    pg_conn.commit()
    print("✓ Table created successfully")

def migrate_data(sqlite_db, pg_conn, limit=None):
    """Migrate data from SQLite to PostgreSQL."""
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Count total rows
    sqlite_cursor.execute("SELECT COUNT(*) FROM clients")
    total_rows = sqlite_cursor.fetchone()[0]
    
    if limit:
        total_rows = min(total_rows, limit)
        print(f"Migrating {total_rows:,} rows (limited)...")
    else:
        print(f"Migrating {total_rows:,} rows...")
    
    # Prepare PostgreSQL insert
    pg_cursor = pg_conn.cursor()
    
    all_columns = COLUMNS + [f"{col}_LC" for col in INDEX_FIELDS]
    columns_str = ', '.join([f'"{col}"' for col in all_columns])
    placeholders = ', '.join(['%s'] * len(all_columns))
    insert_sql = f"INSERT INTO clients ({columns_str}) VALUES ({placeholders})"
    
    # Select data from SQLite
    select_columns = ', '.join([f'"{col}"' for col in COLUMNS])
    select_lc = ', '.join([f'"{col}_LC"' for col in INDEX_FIELDS])
    
    if limit:
        sqlite_cursor.execute(f"SELECT {select_columns}, {select_lc} FROM clients LIMIT {limit}")
    else:
        sqlite_cursor.execute(f"SELECT {select_columns}, {select_lc} FROM clients")
    
    # Batch insert
    batch = []
    inserted = 0
    
    for row in sqlite_cursor:
        batch.append(tuple(row))
        
        if len(batch) >= BATCH_SIZE:
            execute_batch(pg_cursor, insert_sql, batch)
            pg_conn.commit()
            inserted += len(batch)
            progress = (inserted / total_rows) * 100
            print(f"  Progress: {inserted:,}/{total_rows:,} rows ({progress:.1f}%)")
            batch = []
    
    # Insert remaining
    if batch:
        execute_batch(pg_cursor, insert_sql, batch)
        pg_conn.commit()
        inserted += len(batch)
    
    print(f"✓ Migrated {inserted:,} rows successfully")
    
    sqlite_conn.close()
    return inserted

def create_indexes(pg_conn):
    """Create indexes on LC columns for fast searching."""
    cursor = pg_conn.cursor()
    
    print("\nCreating indexes...")
    for field in INDEX_FIELDS:
        idx_name = f"idx_{field.lower()}_lc"
        idx_sql = f'CREATE INDEX {idx_name} ON clients ("{field}_LC");'
        print(f"  Creating {idx_name}...")
        cursor.execute(idx_sql)
    
    pg_conn.commit()
    print("✓ Indexes created successfully")

def analyze_database(pg_conn):
    """Run ANALYZE to update statistics."""
    cursor = pg_conn.cursor()
    print("\nAnalyzing database...")
    cursor.execute("ANALYZE clients;")
    pg_conn.commit()
    print("✓ Database analyzed")

def verify_migration(pg_conn):
    """Verify the migration was successful."""
    cursor = pg_conn.cursor()
    
    print("\n" + "="*60)
    print("MIGRATION VERIFICATION")
    print("="*60)
    
    # Count rows
    cursor.execute("SELECT COUNT(*) FROM clients;")
    count = cursor.fetchone()[0]
    print(f"Total rows in PostgreSQL: {count:,}")
    
    # Sample data
    cols_str = ', '.join([f'"{col}"' for col in COLUMNS])
    cursor.execute(f"SELECT {cols_str} FROM clients LIMIT 3;")
    print("\nSample records:")
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"\n  Record {i}:")
        for j, col in enumerate(COLUMNS):
            print(f"    {col}: {row[j]}")
    
    # Table size
    cursor.execute("""
        SELECT pg_size_pretty(pg_total_relation_size('clients')) as size;
    """)
    size = cursor.fetchone()[0]
    print(f"\nDatabase size: {size}")
    
    print("="*60)

def main():
    """Main migration process."""
    print("="*60)
    print("SQLite to PostgreSQL Migration")
    print("="*60)
    
    # Check if SQLite database exists
    if not os.path.exists(SQLITE_DB):
        print(f"Error: SQLite database '{SQLITE_DB}' not found!")
        print("Please make sure data.db exists in the current directory.")
        sys.exit(1)
    
    # Check for PostgreSQL URL
    if not POSTGRES_URL:
        print("\nError: DATABASE_URL environment variable not set!")
        print("\nPlease set it using:")
        print("  export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
        print("\nOr create a .env file with:")
        print("  DATABASE_URL=postgresql://user:pass@host:port/dbname")
        sys.exit(1)
    
    print(f"\nSource: {SQLITE_DB}")
    print(f"Target: PostgreSQL (Supabase)")
    
    # Optional: Limit rows for testing or to fit free tier
    limit = None
    if '--limit' in sys.argv:
        try:
            limit_idx = sys.argv.index('--limit')
            limit = int(sys.argv[limit_idx + 1])
            print(f"\nWarning: Limiting migration to {limit:,} rows")
        except (IndexError, ValueError):
            print("Error: --limit requires a number")
            sys.exit(1)
    
    # Confirm migration
    print("\n⚠️  This will DROP and recreate the 'clients' table in PostgreSQL!")
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Migration cancelled.")
        sys.exit(0)
    
    try:
        # Connect to PostgreSQL
        print("\nConnecting to PostgreSQL...")
        pg_conn = get_postgres_connection(POSTGRES_URL)
        print("✓ Connected successfully")
        
        # Create table
        create_postgres_table(pg_conn)
        
        # Migrate data
        migrate_data(SQLITE_DB, pg_conn, limit)
        
        # Create indexes
        create_indexes(pg_conn)
        
        # Analyze
        analyze_database(pg_conn)
        
        # Verify
        verify_migration(pg_conn)
        
        # Close connection
        pg_conn.close()
        
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test your application with: python api.py")
        print("2. Deploy to Render")
        print("3. Update environment variables on Render")
        
    except psycopg2.Error as e:
        print(f"\n❌ PostgreSQL Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
