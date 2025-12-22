#!/usr/bin/env python3
"""Test script for Resonite MCP HTTP API."""

import subprocess
import time
import requests
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_http_api():
    """Test HTTP API endpoints."""
    # Start HTTP server
    print('Starting HTTP server...')
    proc = subprocess.Popen([sys.executable, '-m', 'resonite_mcp', '--host', '127.0.0.1', '--port', '8000'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           text=True)

    time.sleep(2)

    # Test various endpoints
    test_endpoints = [
        ('GET', '/health'),
        ('GET', '/plugins/list'),
        ('GET', '/plugins/discover'),
        ('POST', '/osc/send', {'host': '127.0.0.1', 'port': 9000, 'address': '/test'}),
    ]

    for method, endpoint, *data in test_endpoints:
        try:
            if method == 'GET':
                response = requests.get(f'http://127.0.0.1:8000{endpoint}', timeout=3)
            elif method == 'POST':
                response = requests.post(f'http://127.0.0.1:8000{endpoint}',
                                       json=data[0] if data else {}, timeout=3)

            print(f'{method} {endpoint}: {response.status_code}')
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if 'plugins' in resp_json and isinstance(resp_json['plugins'], dict):
                        print(f'  Found {len(resp_json["plugins"])} plugins')
                    else:
                        print('  Response OK')
                except:
                    print(f'  Response: {response.text[:50]}...')
            else:
                print(f'  Error: {response.text[:100]}...')

        except Exception as e:
            print(f'{method} {endpoint}: FAILED - {e}')

    # Stop server
    proc.terminate()
    proc.wait()
    print('Server terminated')

if __name__ == '__main__':
    test_http_api()
