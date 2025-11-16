#!/usr/bin/env python3
"""
Script to reduce CSV files to only essential columns.
This will significantly reduce the database size from ~900MB to much less.

Only keeps: NOMBRE, PATERNO, MATERNO, FECNAC, CALLE, COLONIA, CURP
"""
import csv
import os

# Columns to keep (7 instead of 22)
COLUMNS_TO_KEEP = ['NOMBRE', 'PATERNO', 'MATERNO', 'FECNAC', 'CALLE', 'COLONIA', 'CURP']

DATA_DIR = './Data'
OUTPUT_DIR = './Data_Reduced'

def reduce_csv(input_file, output_file):
    """Read a CSV and write only the columns we need."""
    rows_processed = 0
    
    with open(input_file, 'r', encoding='utf-8', newline='') as infile:
        reader = csv.DictReader(infile)
        
        # Check if all required columns exist
        missing = set(COLUMNS_TO_KEEP) - set(reader.fieldnames or [])
        if missing:
            print(f"Warning: Missing columns {missing} in {input_file}")
            return 0
        
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=COLUMNS_TO_KEEP)
            writer.writeheader()
            
            for row in reader:
                # Extract only the columns we need
                reduced_row = {col: row.get(col, '').strip() for col in COLUMNS_TO_KEEP}
                writer.writerow(reduced_row)
                rows_processed += 1
                
                if rows_processed % 10000 == 0:
                    print(f"  Processed {rows_processed} rows...")
    
    return rows_processed

def main():
    """Process all CSV files in the Data directory."""
    if not os.path.exists(DATA_DIR):
        print(f"Error: {DATA_DIR} directory not found")
        return
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    csv_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return
    
    total_rows = 0
    print(f"Found {len(csv_files)} CSV file(s)")
    print(f"Reducing columns from 22 to 7: {', '.join(COLUMNS_TO_KEEP)}\n")
    
    for csv_file in csv_files:
        input_path = os.path.join(DATA_DIR, csv_file)
        output_path = os.path.join(OUTPUT_DIR, csv_file)
        
        print(f"Processing: {csv_file}")
        rows = reduce_csv(input_path, output_path)
        total_rows += rows
        
        # Show file size comparison
        input_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        reduction = (1 - output_size / input_size) * 100
        
        print(f"  ✓ {rows} rows processed")
        print(f"  Original: {input_size:.2f} MB → Reduced: {output_size:.2f} MB")
        print(f"  Size reduction: {reduction:.1f}%\n")
    
    print(f"Complete! Total rows processed: {total_rows}")
    print(f"Reduced CSV files saved to: {OUTPUT_DIR}")
    
    # Calculate total size comparison
    total_input = sum(os.path.getsize(os.path.join(DATA_DIR, f)) 
                     for f in csv_files) / (1024 * 1024)
    total_output = sum(os.path.getsize(os.path.join(OUTPUT_DIR, f)) 
                      for f in os.listdir(OUTPUT_DIR) 
                      if f.lower().endswith('.csv')) / (1024 * 1024)
    
    print(f"\nTotal size: {total_input:.2f} MB → {total_output:.2f} MB")
    print(f"Overall reduction: {(1 - total_output / total_input) * 100:.1f}%")

if __name__ == '__main__':
    main()
