import os
import csv
import sqlite3
from client_data import EXPECTED_LABELS, DATA_DIRECTORY

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

BATCH_SIZE = 5000


def build_db(db_path=DB_PATH, data_dir=DATA_DIRECTORY):
    """Builds an SQLite DB from CSV files found in data_dir.

    Creates a table `clients` with columns from EXPECTED_LABELS and extra
    lowercase columns for indexed fields (NOMBRE_LC, PATERNO_LC, MATERNO_LC, CURP_LC).
    """
    csv_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.lower().endswith('.csv')]
    if not csv_files:
        raise RuntimeError(f"No CSV files found in {data_dir}")

    # Ensure directory for DB exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # Remove existing DB to recreate
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create table with TEXT columns
    # Now using reduced column set (7 columns instead of 22)
    cols = EXPECTED_LABELS
    col_defs = ', '.join([f'"{c}" TEXT' for c in cols])
    # Add LC columns for indexed fields
    lc_fields = ['NOMBRE', 'PATERNO', 'MATERNO', 'CURP']
    lc_defs = ', '.join([f'"{f}_LC" TEXT' for f in lc_fields])
    create_sql = f'CREATE TABLE clients ({col_defs}, {lc_defs});'
    cur.execute(create_sql)

    # Set pragmas to speed up bulk insert
    cur.execute('PRAGMA synchronous = OFF;')
    cur.execute('PRAGMA journal_mode = MEMORY;')
    cur.execute('PRAGMA temp_store = MEMORY;')

    # Prepare insert
    all_cols = cols + [f + '_LC' for f in lc_fields]
    placeholders = ','.join(['?'] * len(all_cols))
    cols_quoted = ','.join([f'"{c}"' for c in all_cols])
    insert_sql = f'INSERT INTO clients ({cols_quoted}) VALUES ({placeholders})'

    total = 0
    for csv_path in csv_files:
        print(f'Processing file: {csv_path}')
        with open(csv_path, 'r', encoding='utf-8', newline='') as fh:
            reader = csv.DictReader(fh)
            batch = []
            for row in reader:
                # Ensure all expected columns exist
                values = []
                for c in cols:
                    v = row.get(c, '')
                    if v is None:
                        v = ''
                    values.append(v)
                # LC columns
                for f in lc_fields:
                    v = row.get(f, '') or ''
                    values.append(v.lower())
                batch.append(tuple(values))
                if len(batch) >= BATCH_SIZE:
                    cur.executemany(insert_sql, batch)
                    conn.commit()
                    total += len(batch)
                    print(f'  Inserted {total} rows so far...')
                    batch = []
            if batch:
                cur.executemany(insert_sql, batch)
                conn.commit()
                total += len(batch)
                print(f'  Inserted {total} rows total after file.')

    # Vacuum/Analyze to optimize
    conn.commit()

    # Create indexes on LC columns AFTER bulk insert for better performance
    for f in lc_fields:
        idx_sql = f'CREATE INDEX IF NOT EXISTS idx_{f.lower()}_lc ON clients ("{f}_LC");'
        cur.execute(idx_sql)

    cur.execute('ANALYZE;')
    conn.commit()
    conn.close()
    print(f'Database built at {db_path} with {total} rows')


if __name__ == '__main__':
    build_db()
