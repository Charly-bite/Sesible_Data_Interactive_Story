import csv
import os

# --- Configuration ---
# Reduced to only the columns we actually display
EXPECTED_LABELS = [
    "NOMBRE", "PATERNO", "MATERNO", "FECNAC", "CALLE", "COLONIA", "CURP"
]
DATA_DIRECTORY = os.environ.get('DATA_DIRECTORY', './Data')

# --- Functions ---

def load_multiple_client_data(filepaths):
    """Loads client data from multiple CSV files and combines them."""
    all_data = []
    processed_headers = None
    expected_labels_set = set(EXPECTED_LABELS)
    print("\n--- Loading Data ---")
    for filepath in filepaths:
        if not os.path.exists(filepath):
            print(f"Warning: File path '{filepath}' seems invalid. Skipping.")
            continue
        print(f"Processing file: '{filepath}'...")
        processed_file = False
        try: # Try UTF-8
            with open(filepath, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                header = reader.fieldnames
                if not header: continue
                current_header_set = set(header)
                if processed_headers is None: # First file check
                    processed_headers = current_header_set
                    print("  Detected headers (UTF-8):", ", ".join(header))
                elif current_header_set != processed_headers:
                    print(f"  Warning: Headers in '{filepath}' (UTF-8) differ.")
                file_row_count = 0
                for row in reader:
                    cleaned_row = {k.strip(): v.strip() if v else '' for k, v in row.items()}
                    all_data.append(cleaned_row)
                    file_row_count += 1
                processed_file = True
                print(f"  Loaded {file_row_count} records (UTF-8).")
        except UnicodeDecodeError: # Fallback to Latin-1
            print(f"  Info: UTF-8 failed for '{filepath}'. Trying 'latin-1'...")
            try:
                with open(filepath, mode='r', newline='', encoding='latin-1') as csvfile:
                    reader = csv.DictReader(csvfile)
                    header = reader.fieldnames
                    if not header: continue
                    current_header_set = set(header)
                    if processed_headers is None: # First file check
                        processed_headers = current_header_set
                        print("  Detected headers (latin-1):", ", ".join(header))
                    elif current_header_set != processed_headers:
                         print(f"  Warning: Headers in '{filepath}' (latin-1) differ.")
                    file_row_count = 0
                    for row in reader:
                        cleaned_row = {k.strip(): v.strip() if v else '' for k, v in row.items()}
                        all_data.append(cleaned_row)
                    file_row_count += 1
                    processed_file = True
                    print(f"  Loaded {file_row_count} records (latin-1).")
            except Exception as e_latin:
                print(f"  Error: Failed reading '{filepath}' with latin-1: {e_latin}. Skipping.")
                continue
        except Exception as e:
            if not processed_file:
                print(f"An general error occurred reading '{filepath}': {e}. Skipping.")
            continue
    if not all_data:
        print("\nError: No data loaded.")
        return None
    print("--- Finished Loading ---")
    return all_data

def search_clients_single_field(client_data, search_label, search_value):
    """Searches for clients based on a SINGLE label and value."""
    matches = []
    search_value_lower = search_value.lower()
    for client_record in client_data:
        value_in_record = client_record.get(search_label)
        if value_in_record is not None and value_in_record.lower() == search_value_lower:
            matches.append(client_record)
    return matches

def search_clients_paterno_or_materno(client_data, search_term):
    """
    Searches for clients where EITHER PATERNO OR MATERNO matches the search term.
    """
    matches = []
    search_term_lower = search_term.lower()
    if not search_term_lower:
        return matches
    for client_record in client_data:
        record_paterno = client_record.get("PATERNO", "").lower()
        record_materno = client_record.get("MATERNO", "").lower()
        if search_term_lower == record_paterno or search_term_lower == record_materno:
             matches.append(client_record)
    return matches

def search_clients_paterno_and_materno(client_data, paterno_search, materno_search):
    """
    Searches for clients matching BOTH PATERNO and MATERNO last names exactly.
    """
    matches = []
    paterno_search_lower = paterno_search.lower()
    materno_search_lower = materno_search.lower()
    # This specific search requires both to be provided and match the corresponding fields
    if not paterno_search_lower or not materno_search_lower:
        return matches

    for client_record in client_data:
        record_paterno = client_record.get("PATERNO", "").lower()
        record_materno = client_record.get("MATERNO", "").lower()

        if paterno_search_lower == record_paterno and materno_search_lower == record_materno:
             matches.append(client_record)
    return matches

# --- NEW SEARCH FUNCTION: Full Name Search ---
def search_clients_full_name(client_data, nombre_search, paterno_search, materno_search):
    """
    Searches for clients matching NOMBRE, PATERNO, and MATERNO exactly.
    """
    matches = []
    nombre_search_lower = nombre_search.lower()
    paterno_search_lower = paterno_search.lower()
    materno_search_lower = materno_search.lower()

    # For a full name search, typically all three components are required.
    if not nombre_search_lower or not paterno_search_lower or not materno_search_lower:
        print("Warning: Full name search requires values for all three fields (NOMBRE, PATERNO, MATERNO).")
        return matches # Return empty list if any search term is empty

    for client_record in client_data:
        record_nombre = client_record.get("NOMBRE", "").lower()
        record_paterno = client_record.get("PATERNO", "").lower()
        record_materno = client_record.get("MATERNO", "").lower()

        # Match requires ALL three fields to match the search terms
        if (nombre_search_lower == record_nombre and
            paterno_search_lower == record_paterno and
            materno_search_lower == record_materno):
             matches.append(client_record)

    return matches


# --- Consolidated Display Function ---
def display_search_results(results, search_description):
    """Displays the list of found client records."""
    if not results:
        print(f"\n--- No clients found matching: {search_description} ---")
        return

    print(f"\n--- Found {len(results)} client(s) matching: {search_description} ---")
    for i, client in enumerate(results, 1):
        print(f"\nResult #{i}:")
        for label in EXPECTED_LABELS:
            value = client.get(label, "N/A")
            print(f"  {label:<10}: {value}")
        print("-" * 30)

# --- Main Execution ---
if __name__ == "__main__":
    print("Client Data Search Tool (Auto-Detect Files)")
    print("=" * 45)

    print(f"Looking for CSV files in: {DATA_DIRECTORY}")
    data_files = []
    try:
        if not os.path.isdir(DATA_DIRECTORY):
             print(f"\nError: Directory not found: '{DATA_DIRECTORY}'"); exit()
        found_csv_files = False
        for filename in os.listdir(DATA_DIRECTORY):
            if filename.lower().endswith('.csv'):
                full_path = os.path.join(DATA_DIRECTORY, filename)
                data_files.append(full_path); print(f"  Found: {filename}"); found_csv_files = True
        if not found_csv_files: print(f"\nError: No CSV files found in '{DATA_DIRECTORY}'"); exit()
    except Exception as e: print(f"\nError accessing directory: {e}"); exit()

    clients = load_multiple_client_data(data_files)

    if clients:
        total_clients = len(clients); num_files = len(data_files)
        print("-" * 30); print("Data Loading Complete!")
        print(f"Processed {num_files} CSV file(s).")
        print(f"Total client records loaded: {total_clients}"); print("-" * 30)

        while True:
            print("\nChoose search type:")
            print("  1: Search by a single specific field (e.g., NOMBRE, CURP)")
            print("  2: Search by a value in EITHER PATERNO OR MATERNO")
            print("  3: Search by values matching BOTH PATERNO AND MATERNO (Exact Match)")
            print("  4: Search by full name (NOMBRE AND PATERNO AND MATERNO)") # New option 4
            choice = input("Enter your choice (1, 2, 3, or 4): ").strip()

            found_clients = []
            search_description = "Invalid search" # Default description

            if choice == '1':
                # --- Single Field Search ---
                print("\nAvailable single fields:")
                for i, lbl in enumerate(EXPECTED_LABELS):
                     print(f"  {lbl:<10}", end='');
                     if (i + 1) % 5 == 0: print()
                print("\n")
                while True:
                    search_label_input = input("Enter the field label to search by: ").strip().upper()
                    if search_label_input in EXPECTED_LABELS: break
                    else: print(f"Error: '{search_label_input}' is not a valid field label.")
                search_value_input = input(f"Enter the exact value for '{search_label_input}': ").strip()
                if not search_value_input: print("Error: Search value cannot be empty."); continue

                found_clients = search_clients_single_field(clients, search_label_input, search_value_input)
                search_description = f"'{search_label_input}' = '{search_value_input}'"

            elif choice == '2':
                # --- PATERNO OR MATERNO Search ---
                search_term = input("Enter the last name value to search in PATERNO OR MATERNO: ").strip()
                if not search_term: print("Error: Search value cannot be empty."); continue

                found_clients = search_clients_paterno_or_materno(clients, search_term)
                search_description = f"PATERNO OR MATERNO = '{search_term}'"

            elif choice == '3':
                # --- PATERNO AND MATERNO Search ---
                print("\nEnter the exact last names for PATERNO AND MATERNO search:")
                paterno_value = input("  PATERNO: ").strip()
                materno_value = input("  MATERNO: ").strip()
                if not paterno_value or not materno_value:
                    print("Error: You must provide values for BOTH PATERNO and MATERNO for this search type.")
                    continue

                found_clients = search_clients_paterno_and_materno(clients, paterno_value, materno_value)
                search_description = f"PATERNO='{paterno_value}' AND MATERNO='{materno_value}'"

            elif choice == '4':
                # --- Full Name Search (NOMBRE AND PATERNO AND MATERNO) ---
                print("\nEnter the full name components to search for:")
                nombre_value = input("  NOMBRE: ").strip()
                paterno_value = input("  PATERNO: ").strip()
                materno_value = input("  MATERNO: ").strip()

                # Ensure all three fields have some input
                if not nombre_value or not paterno_value or not materno_value:
                     print("Error: You must provide values for NOMBRE, PATERNO, AND MATERNO for this search type.")
                     continue # Go back to choosing search type

                found_clients = search_clients_full_name(clients, nombre_value, paterno_value, materno_value)
                search_description = f"NOMBRE='{nombre_value}' AND PATERNO='{paterno_value}' AND MATERNO='{materno_value}'"


            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
                continue # Ask for choice again

            # --- Display Results (common for all choices) ---
            display_search_results(found_clients, search_description)

            # --- Ask to search again ---
            another_search = input("\nDo you want to perform another search? (yes/no): ").strip().lower()
            if another_search == 'no':
                break
            # The loop continues for any other input.
            # --- END MODIFIED ---

    print("\nExiting Client Search Tool.")