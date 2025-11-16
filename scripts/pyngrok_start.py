#!/usr/bin/env python3
"""
Start the Flask server and open an ngrok tunnel using pyngrok.

Usage: python scripts/pyngrok_start.py [PORT]

This will download a modern ngrok binary (pyngrok does this), start a tunnel to the
local `PORT`, and print the public URL.
"""
import os
import subprocess
import sys
import time

def ensure_pyngrok():
    try:
        import pyngrok
    except Exception:
        # Install into the active venv (if any)
        print('pyngrok not installed; installing...')
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyngrok'], check=True)

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

    # Prefer project venv python if possible
    python = sys.executable
    print('Using Python:', python)

    ensure_pyngrok()
    from pyngrok import ngrok

    # If user set NGROK_AUTH_TOKEN in environment, pyngrok will pick it up.
    token = os.environ.get('NGROK_AUTH_TOKEN') or os.environ.get('NGROK_AUTHTOKEN')
    if token:
        ngrok.set_auth_token(token)

    # Start API server (flask) as background process
    proc = subprocess.Popen([python, 'api.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print('Started API server (pid):', proc.pid)

    # Wait a moment for server to start
    time.sleep(2)

    # Create the tunnel
    public_url = ngrok.connect(port, bind_tls=True).public_url
    print('Public URL:', public_url)

    # Wait until interrupted
    try:
        proc.wait()
    except KeyboardInterrupt:
        print('Shutting down...')
    finally:
        try:
            ngrok.disconnect(public_url)
        except Exception:
            pass
        proc.terminate()

if __name__ == '__main__':
    main()
