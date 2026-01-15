#!/usr/bin/env python3
"""Test MCP protocol communication with the Resonite server."""

import json
import subprocess
import sys
import time


def test_mcp_protocol():
    print("Testing MCP server protocol communication...")

    try:
        # Start the server process
        proc = subprocess.Popen(
            [sys.executable, "-m", "resonite_mcp", "--stdio"],
            env={"PYTHONPATH": "D:/Dev/repos/resonite-mcp/src", "PYTHONUNBUFFERED": "1"},
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="D:/Dev/repos/resonite-mcp",
        )

        # Give it time to start
        time.sleep(3)

        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        print("Sending initialize request...")
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()

        # Read initialize response
        init_response = proc.stdout.readline().strip()
        print(f"Initialize response: {init_response[:200]}...")

        # Send tools/list request
        tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        print("Sending tools/list request...")
        proc.stdin.write(json.dumps(tools_request) + "\n")
        proc.stdin.flush()

        # Read tools response
        tools_response = proc.stdout.readline().strip()
        print(f"Tools response: {tools_response[:500]}...")

        # Parse tools response
        try:
            tools_data = json.loads(tools_response)
            if "result" in tools_data and "tools" in tools_data["result"]:
                tools_count = len(tools_data["result"]["tools"])
                print(f"SUCCESS: Server reports {tools_count} tools available")

                if tools_count > 0:
                    print("First few tools:")
                    for tool in tools_data["result"]["tools"][:5]:
                        print(f"  - {tool.get('name', 'unnamed')}")
                else:
                    print("ERROR: Server reports 0 tools!")
            else:
                print("ERROR: Unexpected tools response format")
                print(f"Full response: {tools_response}")

        except json.JSONDecodeError as e:
            print(f"ERROR: Could not parse JSON response: {e}")
            print(f"Raw response: {tools_response}")

        proc.terminate()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_mcp_protocol()
