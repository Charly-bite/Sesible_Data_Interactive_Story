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
    Optimized for Neon.tech with IPv4 support.
    """
    if USE_POSTGRES:
        # Neon.tech connection string format
        # postgresql://user:password@host:port/database
        url = DATABASE_URL
        
        # Handle postgres:// prefix (convert to postgresql://)
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        
        # Neon provides IPv4 addresses, so no special handling needed
        # Just connect with SSL required
        conn = psycopg2.connect(url, sslmode='require', connect_timeout=10)
        return conn, 'postgres'
    else:
        # Fallback to SQLite for local development
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
