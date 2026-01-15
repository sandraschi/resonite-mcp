"""
Resonite OSC Simulation Script
Mimics Resonite's OSC responses for testing the resonite-mcp server.
"""

import argparse
import time

from pythonosc import dispatcher, osc_server, udp_client


def handle_inventory_list(address, *args):
    print(f"Received {address}: {args}")
    # Simulate a delay
    time.time()

    # Send response back to port 9001
    client = udp_client.SimpleUDPClient("127.0.0.1", 9001)

    # Mock inventory data
    items = [
        {"id": "item_1", "name": "Simulation Avatar", "type": "avatar"},
        {"id": "item_2", "name": "Simulation World", "type": "world"},
        {"id": "item_3", "name": "Simulation Gadget", "type": "object"},
    ]

    print("Sending /inventory/list/response...")
    client.send_message("/inventory/list/response", [items, 3])


def handle_inventory_info(address, *args):
    print(f"Received {address}: {args}")
    item_id = args[0] if args else "unknown"

    client = udp_client.SimpleUDPClient("127.0.0.1", 9001)

    item_info = {
        "id": item_id,
        "name": f"Simulated {item_id}",
        "description": "This is a simulated item response.",
        "created_at": "2025-12-31T12:00:00Z",
        "owner": "SimUser",
        "tags": ["simulated", "test"],
    }

    print(f"Sending /inventory/info/response for {item_id}...")
    client.send_message("/inventory/info/response", [item_info])


def main():
    parser = argparse.ArgumentParser(description="Resonite OSC Simulator")
    parser.add_argument("--ip", default="127.0.0.1", help="The IP to listen on")
    parser.add_argument("--port", type=int, default=9000, help="The port to listen on")
    args = parser.parse_args()

    disp = dispatcher.Dispatcher()
    disp.map("/inventory/list", handle_inventory_list)
    disp.map("/inventory/info", handle_inventory_info)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), disp)
    print(f"Serving on {server.server_address}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down simulator.")


if __name__ == "__main__":
    main()
