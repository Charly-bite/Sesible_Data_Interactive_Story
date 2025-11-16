#!/usr/bin/env python3
"""
Migrate data from local SQLite to Neon PostgreSQL.
Usage: python3 migrate_to_neon.py
"""
import os
import sqlite3
import sys

# Check if psycopg2 is available
try:
    import psycopg2
    from psycopg2.extras import execute_batch
except ImportError:
    print("❌ Error: psycopg2-binary is required")
    print("Install with: pip install psycopg2-binary")
    sys.exit(1)

# Configuration
SQLITE_DB = 'data.db'
NEON_DATABASE_URL = os.environ.get('NEON_DATABASE_URL')

if not NEON_DATABASE_URL:
    print("❌ Error: NEON_DATABASE_URL environment variable not set")
    print("Set it with: export NEON_DATABASE_URL='your-neon-connection-string'")
    sys.exit(1)

def migrate():
    """Migrate data from SQLite to Neon PostgreSQL."""
    
    # Connect to SQLite
    print(f"📂 Opening SQLite database: {SQLITE_DB}")
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get total row count
    sqlite_cursor.execute("SELECT COUNT(*) FROM clients")
    total_rows = sqlite_cursor.fetchone()[0]
    print(f"📊 Total rows to migrate: {total_rows:,}")
    
    # Connect to Neon PostgreSQL
    print(f"🔌 Connecting to Neon PostgreSQL...")
    try:
        pg_conn = psycopg2.connect(NEON_DATABASE_URL, sslmode='require')
        pg_cursor = pg_conn.cursor()
        print("✓ Connected to Neon successfully")
    except Exception as e:
        print(f"❌ Failed to connect to Neon: {e}")
        sqlite_conn.close()
        sys.exit(1)
    
    # Create table
    print("📋 Creating table structure...")
    pg_cursor.execute("""
        DROP TABLE IF EXISTS clients CASCADE;
    """)
    pg_cursor.execute("""
        CREATE TABLE clients (
            NOMBRE TEXT,
            PATERNO TEXT,
            MATERNO TEXT,
            FECNAC TEXT,
            CALLE TEXT,
            COLONIA TEXT,
            CURP TEXT
        );
    """)
    pg_conn.commit()
    print("✓ Table created")
    
    # Migrate data in batches
    print(f"⏳ Migrating {total_rows:,} rows in batches of 5000...")
    batch_size = 5000
    migrated = 0
    
    sqlite_cursor.execute("""
        SELECT NOMBRE, PATERNO, MATERNO, FECNAC, CALLE, COLONIA, CURP 
        FROM clients
    """)
    
    while True:
        rows = sqlite_cursor.fetchmany(batch_size)
        if not rows:
            break
        
        # Convert rows to tuples
        data = [tuple(row) for row in rows]
        
        # Batch insert
        execute_batch(pg_cursor, """
            INSERT INTO clients (NOMBRE, PATERNO, MATERNO, FECNAC, CALLE, COLONIA, CURP)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, data, page_size=5000)
        
        pg_conn.commit()
        migrated += len(data)
        progress = (migrated / total_rows) * 100
        print(f"  Progress: {migrated:,}/{total_rows:,} rows ({progress:.1f}%)")
    
    print(f"✓ Migrated {migrated:,} rows successfully")
    
    # Create indexes for performance
    print("🔧 Creating indexes...")
    indexes = [
        ("idx_nombre_lc", "LOWER(NOMBRE)"),
        ("idx_paterno_lc", "LOWER(PATERNO)"),
        ("idx_materno_lc", "LOWER(MATERNO)"),
        ("idx_curp_lc", "LOWER(CURP)")
    ]
    
    for idx_name, idx_expr in indexes:
        print(f"  Creating {idx_name}...")
        pg_cursor.execute(f"CREATE INDEX {idx_name} ON clients ({idx_expr});")
    
    pg_conn.commit()
    print("✓ Indexes created")
    
    # Run ANALYZE for query optimization
    print("📊 Running ANALYZE...")
    pg_cursor.execute("ANALYZE clients;")
    pg_conn.commit()
    print("✓ ANALYZE complete")
    
    # Verify migration
    print("✅ Verifying migration...")
    pg_cursor.execute("SELECT COUNT(*) FROM clients")
    pg_count = pg_cursor.fetchone()[0]
    print(f"  PostgreSQL row count: {pg_count:,}")
    
    # Get database size
    pg_cursor.execute("""
        SELECT pg_size_pretty(pg_database_size(current_database())) as size
    """)
    db_size = pg_cursor.fetchone()[0]
    print(f"  Database size: {db_size}")
    
    # Show sample records
    print("\n📋 Sample records:")
    pg_cursor.execute("SELECT * FROM clients LIMIT 3")
    for i, row in enumerate(pg_cursor.fetchall(), 1):
        print(f"  {i}. {row}")
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    
    print("\n" + "="*60)
    print("✅ Migration completed successfully!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  - Migrated: {migrated:,} rows")
    print(f"  - Database size: {db_size}")
    print(f"  - Indexes: 4 created")
    print(f"\n🎯 Next steps:")
    print(f"  1. Update DATABASE_URL in Render environment variables")
    print(f"  2. Update .env file locally with NEON_DATABASE_URL")
    print(f"  3. Test your application")

if __name__ == '__main__':
    print("="*60)
    print("🚀 Neon PostgreSQL Migration")
    print("="*60)
    print(f"\nSource: {SQLITE_DB}")
    print(f"Target: Neon PostgreSQL\n")
    
    # Confirm before proceeding
    response = input("⚠️  This will DROP and recreate the 'clients' table in Neon.\nContinue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Migration cancelled")
        sys.exit(0)
    
    migrate()
