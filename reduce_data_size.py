#!/usr/bin/env python3
"""
Further reduce the database by selecting only recent or relevant records.
This script can reduce from 2.99M rows to a target size that fits free tier limits.

Strategies:
1. Limit by date (most recent records)
2. Sample evenly (every Nth record)
3. Random sample
"""
import sqlite3
import os
import sys

SOURCE_DB = 'data.db'
TARGET_DB = 'data_reduced.db'

def get_db_stats(db_path):
    """Get database statistics."""
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM clients")
    count = cur.fetchone()[0]
    
    size = os.path.getsize(db_path) / (1024 * 1024)  # MB
    
    conn.close()
    return {'count': count, 'size_mb': size}

def create_sampled_database(source_db, target_db, target_rows):
    """Create a new database with sampled data."""
    
    if not os.path.exists(source_db):
        print(f"Error: {source_db} not found")
        return False
    
    # Remove target if exists
    if os.path.exists(target_db):
        os.remove(target_db)
    
    source_conn = sqlite3.connect(source_db)
    source_conn.row_factory = sqlite3.Row
    target_conn = sqlite3.connect(target_db)
    
    source_cur = source_conn.cursor()
    target_cur = target_conn.cursor()
    
    print("Creating optimized database structure...")
    
    # Copy table structure
    source_cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='clients'")
    create_sql = source_cur.fetchone()[0]
    target_cur.execute(create_sql)
    
    # Sample data using random sampling for even distribution
    print(f"Sampling {target_rows:,} rows from database...")
    
    # Get total count
    source_cur.execute("SELECT COUNT(*) FROM clients")
    total = source_cur.fetchone()[0]
    
    # Calculate sampling rate
    sample_rate = target_rows / total
    
    print(f"Total rows: {total:,}")
    print(f"Target rows: {target_rows:,}")
    print(f"Sampling rate: {sample_rate*100:.1f}%")
    
    # Use random sampling with RANDOM()
    # This ensures even distribution across the dataset
    sample_sql = f"""
        SELECT * FROM clients 
        ORDER BY RANDOM() 
        LIMIT {target_rows}
    """
    
    print("Selecting random sample...")
    source_cur.execute(sample_sql)
    
    # Get column names
    columns = [description[0] for description in source_cur.description]
    placeholders = ','.join(['?'] * len(columns))
    columns_str = ','.join([f'"{col}"' for col in columns])
    insert_sql = f"INSERT INTO clients ({columns_str}) VALUES ({placeholders})"
    
    # Insert sampled data
    batch = []
    inserted = 0
    
    print("Inserting sampled data...")
    for row in source_cur:
        batch.append(tuple(row))
        
        if len(batch) >= 5000:
            target_cur.executemany(insert_sql, batch)
            target_conn.commit()
            inserted += len(batch)
            print(f"  Inserted {inserted:,} rows...")
            batch = []
    
    if batch:
        target_cur.executemany(insert_sql, batch)
        target_conn.commit()
        inserted += len(batch)
    
    print(f"✓ Inserted {inserted:,} rows")
    
    # Copy indexes
    print("\nCreating indexes...")
    source_cur.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='clients'")
    for row in source_cur:
        if row[0]:  # Skip auto-created indexes
            target_cur.execute(row[0])
    
    # Optimize
    print("Optimizing database...")
    target_cur.execute('VACUUM')
    target_cur.execute('ANALYZE')
    target_conn.commit()
    
    source_conn.close()
    target_conn.close()
    
    return True

def main():
    print("="*60)
    print("Database Size Reducer")
    print("="*60)
    print()
    
    # Get current stats
    stats = get_db_stats(SOURCE_DB)
    if not stats:
        print(f"Error: {SOURCE_DB} not found!")
        return
    
    print(f"Current database: {SOURCE_DB}")
    print(f"  Rows: {stats['count']:,}")
    print(f"  Size: {stats['size_mb']:.2f} MB")
    print()
    
    # Calculate target sizes
    print("Target options:")
    print()
    print("1. Free tier optimized (1.5M rows → ~320 MB)")
    print("2. Very small (750K rows → ~160 MB)")
    print("3. Custom row count")
    print("4. Cancel")
    print()
    
    choice = input("Choose option (1-4): ").strip()
    
    if choice == '1':
        target_rows = 1_500_000
    elif choice == '2':
        target_rows = 750_000
    elif choice == '3':
        try:
            target_rows = int(input("Enter target row count: ").strip())
            if target_rows <= 0 or target_rows > stats['count']:
                print("Invalid row count!")
                return
        except ValueError:
            print("Invalid input!")
            return
    else:
        print("Cancelled.")
        return
    
    print()
    print(f"Creating reduced database with {target_rows:,} rows...")
    print(f"Output: {TARGET_DB}")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    print()
    success = create_sampled_database(SOURCE_DB, TARGET_DB, target_rows)
    
    if success:
        new_stats = get_db_stats(TARGET_DB)
        
        print()
        print("="*60)
        print("REDUCTION COMPLETE!")
        print("="*60)
        print(f"Original: {stats['count']:,} rows, {stats['size_mb']:.2f} MB")
        print(f"Reduced:  {new_stats['count']:,} rows, {new_stats['size_mb']:.2f} MB")
        print(f"Savings:  {stats['size_mb'] - new_stats['size_mb']:.2f} MB ({(1 - new_stats['size_mb']/stats['size_mb'])*100:.1f}%)")
        print()
        print(f"✓ Reduced database saved as: {TARGET_DB}")
        print()
        print("Next steps:")
        print(f"1. Test with: mv data.db data_full.db && mv {TARGET_DB} data.db")
        print("2. Or migrate to PostgreSQL: python3 migrate_to_postgres.py")
    else:
        print("\n❌ Reduction failed!")

if __name__ == '__main__':
    main()
