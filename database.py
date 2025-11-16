#!/usr/bin/env python3
"""
Database configuration module.
Supports both SQLite (local development) and PostgreSQL (production/Supabase).
"""
import os
import sqlite3
import socket

# Try to import PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("Warning: psycopg2 not installed. PostgreSQL support disabled.")

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

# Determine which database to use
USE_POSTGRES = bool(DATABASE_URL and POSTGRES_AVAILABLE)

def get_db_connection():
    """
    Return a database connection.
    Uses PostgreSQL if DATABASE_URL is set, otherwise falls back to SQLite.
    """
    if USE_POSTGRES:
        # Parse DATABASE_URL manually to handle special characters in password
        # Format: postgresql://user:password@host:port/database
        import re
        
        url = DATABASE_URL
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        
        # Manual parsing to handle passwords with special characters like #
        # Pattern: postgresql://username:password@hostname:port/database
        pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+?)(?:\?|$)'
        match = re.match(pattern, url)
        
        if not match:
            raise ValueError(f"Invalid DATABASE_URL format: {url}")
        
        username = match.group(1)
        password = match.group(2)
        hostname = match.group(3)
        port = int(match.group(4))
        database = match.group(5)
        
        # Force port 6543 (Session Pooler) for IPv4 compatibility if using 5432
        if port == 5432:
            port = 6543
            print(f"✓ Switched from port 5432 to 6543 (Session Pooler)")
        
        # Resolve hostname to IPv4 address BEFORE connecting
        ipv4_host = hostname  # Default fallback
        
        try:
            # Get IPv4 address only (AF_INET)
            addr_info = socket.getaddrinfo(
                hostname, 
                None,  # Don't filter by port during DNS lookup
                socket.AF_INET,  # Force IPv4 only
                socket.SOCK_STREAM
            )
            # Use the first IPv4 address found
            if addr_info and len(addr_info) > 0:
                ipv4_host = addr_info[0][4][0]
                print(f"✓ Resolved {hostname} to IPv4: {ipv4_host}")
            else:
                print(f"⚠ No IPv4 address found for {hostname}, using hostname")
        except Exception as e:
            print(f"⚠ IPv4 resolution failed for {hostname}: {type(e).__name__}, using hostname")
        
        # Connect using individual parameters with resolved IPv4
        conn = psycopg2.connect(
            host=ipv4_host,
            port=port,
            database=database,
            user=username,
            password=password,
            sslmode='require',
            connect_timeout=10
        )
        return conn, 'postgres'
    else:
        # Fallback to SQLite
        conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'

def execute_query(query, params=None, fetch_all=True):
    """
    Execute a query and return results.
    Handles differences between SQLite and PostgreSQL.
    """
    conn, db_type = get_db_connection()
    
    try:
        if db_type == 'postgres':
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_all:
            if db_type == 'postgres':
                # RealDictCursor returns dicts
                results = cursor.fetchall()
                results = [dict(row) for row in results]
            else:
                # SQLite with Row factory
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]
            
            conn.close()
            return results
        else:
            conn.commit()
            conn.close()
            return None
            
    except Exception as e:
        conn.close()
        raise e

def row_to_dict(row, db_type='sqlite'):
    """Convert database row to dictionary."""
    if db_type == 'postgres':
        return dict(row)
    else:
        return {k: row[k] for k in row.keys()}

# Print database mode on import
if USE_POSTGRES:
    print(f"✓ Using PostgreSQL database")
else:
    print(f"✓ Using SQLite database: {SQLITE_DB_PATH}")
