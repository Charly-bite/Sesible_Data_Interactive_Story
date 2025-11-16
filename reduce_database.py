#!/usr/bin/env python3
"""
Script to reduce the SQLite database to only essential columns.
This will create a new optimized database with only the columns you actually display.

Keeps only: NOMBRE, PATERNO, MATERNO, FECNAC, CALLE, COLONIA, CURP
Reduces from 22 columns to 7 columns (68% reduction in column count)
"""
import sqlite3
import os

# Original database
SOURCE_DB = 'data.db'
# New optimized database
TARGET_DB = 'data_optimized.db'

# Columns to keep (only what you display)
COLUMNS_TO_KEEP = ['NOMBRE', 'PATERNO', 'MATERNO', 'FECNAC', 'CALLE', 'COLONIA', 'CURP']

# Fields we'll index for fast searching (lowercase versions)
INDEX_FIELDS = ['NOMBRE', 'PATERNO', 'MATERNO', 'CURP']

BATCH_SIZE = 5000

def reduce_database():
    """Create optimized database with only essential columns."""
    
    if not os.path.exists(SOURCE_DB):
        print(f"Error: Source database '{SOURCE_DB}' not found")
        return
    
    print(f"Reading from: {SOURCE_DB}")
    print(f"Creating optimized database: {TARGET_DB}")
    print(f"Keeping only columns: {', '.join(COLUMNS_TO_KEEP)}\n")
    
    # Remove target DB if it exists
    if os.path.exists(TARGET_DB):
        os.remove(TARGET_DB)
        print(f"Removed existing {TARGET_DB}")
    
    # Connect to both databases
    source_conn = sqlite3.connect(SOURCE_DB)
    source_conn.row_factory = sqlite3.Row
    target_conn = sqlite3.connect(TARGET_DB)
    
    source_cur = source_conn.cursor()
    target_cur = target_conn.cursor()
    
    # Speed up the target database creation
    target_cur.execute('PRAGMA synchronous = OFF;')
    target_cur.execute('PRAGMA journal_mode = MEMORY;')
    target_cur.execute('PRAGMA temp_store = MEMORY;')
    
    # Create optimized table with only needed columns
    cols = COLUMNS_TO_KEEP
    col_defs = ', '.join([f'"{c}" TEXT' for c in cols])
    
    # Add lowercase columns for indexed fields
    lc_defs = ', '.join([f'"{f}_LC" TEXT' for f in INDEX_FIELDS])
    
    create_sql = f'CREATE TABLE clients ({col_defs}, {lc_defs});'
    print(f"Creating table with {len(COLUMNS_TO_KEEP)} columns + {len(INDEX_FIELDS)} index columns")
    target_cur.execute(create_sql)
    
    # Prepare insert statement
    all_cols = cols + [f + '_LC' for f in INDEX_FIELDS]
    placeholders = ','.join(['?'] * len(all_cols))
    cols_quoted = ','.join([f'"{c}"' for c in all_cols])
    insert_sql = f'INSERT INTO clients ({cols_quoted}) VALUES ({placeholders})'
    
    # Read all data from source
    print("\nReading from source database...")
    # Select only the columns we need
    select_cols = ', '.join([f'"{c}"' for c in COLUMNS_TO_KEEP])
    source_cur.execute(f'SELECT {select_cols} FROM clients')
    
    batch = []
    total = 0
    
    print("Copying data to optimized database...")
    for row in source_cur:
        # Extract values for the columns we want
        values = []
        for c in COLUMNS_TO_KEEP:
            v = row[c] if row[c] is not None else ''
            values.append(v)
        
        # Add lowercase versions for indexed fields
        for f in INDEX_FIELDS:
            v = row[f] if row[f] is not None else ''
            values.append(v.lower())
        
        batch.append(tuple(values))
        
        if len(batch) >= BATCH_SIZE:
            target_cur.executemany(insert_sql, batch)
            target_conn.commit()
            total += len(batch)
            print(f"  Inserted {total:,} rows...")
            batch = []
    
    # Insert remaining rows
    if batch:
        target_cur.executemany(insert_sql, batch)
        target_conn.commit()
        total += len(batch)
    
    print(f"  ✓ Total rows copied: {total:,}")
    
    # Create indexes on lowercase columns for fast searching
    print("\nCreating indexes for fast search...")
    for f in INDEX_FIELDS:
        idx_name = f'idx_{f.lower()}_lc'
        idx_sql = f'CREATE INDEX IF NOT EXISTS {idx_name} ON clients ("{f}_LC");'
        print(f"  Creating index: {idx_name}")
        target_cur.execute(idx_sql)
    
    # Optimize the database
    print("\nOptimizing database...")
    target_cur.execute('VACUUM;')
    target_cur.execute('ANALYZE;')
    target_conn.commit()
    
    # Get file sizes
    source_size = os.path.getsize(SOURCE_DB) / (1024 * 1024)  # MB
    target_size = os.path.getsize(TARGET_DB) / (1024 * 1024)  # MB
    reduction = (1 - target_size / source_size) * 100
    
    print("\n" + "="*60)
    print("OPTIMIZATION COMPLETE!")
    print("="*60)
    print(f"Original database:  {source_size:.2f} MB")
    print(f"Optimized database: {target_size:.2f} MB")
    print(f"Size reduction:     {reduction:.1f}%")
    print(f"Space saved:        {source_size - target_size:.2f} MB")
    print(f"\nTotal rows:         {total:,}")
    print(f"Columns reduced:    22 → 7 (+ 4 index columns)")
    print("="*60)
    
    # Close connections
    source_conn.close()
    target_conn.close()
    
    print(f"\n✓ Optimized database saved as: {TARGET_DB}")
    print("\nNext steps:")
    print("1. Test the optimized database with your application")
    print("2. If everything works, replace data.db with data_optimized.db:")
    print("   mv data.db data_backup.db")
    print("   mv data_optimized.db data.db")

if __name__ == '__main__':
    try:
        reduce_database()
    except Exception as e:
        import traceback
        print(f"\nError: {e}")
        traceback.print_exc()
