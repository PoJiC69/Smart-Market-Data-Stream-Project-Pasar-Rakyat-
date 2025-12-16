#!/usr/bin/env python3
"""
Enhanced CLI entrypoint for the device client.

Features:
- Accept --server (full base URL) and --port (port number) to customize target platform.
- Interactive menu (--interactive) to set server, register, run client, etc.
- Backwards compatible with previous args (--mode, --device-id, --market-id, --mock, --interval, --register).
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from urllib.parse import urlparse

from device_client.client import DeviceClient
from device_client.config import settings

def parse_args():
    p = argparse.ArgumentParser("smart-market-device-client")
    p.add_argument("--register", action="store_true", help="Register device with platform")
    p.add_argument("--server", type=str, default=None, help="Platform server base URL (e.g. http://localhost or http://host:8000)")
    p.add_argument("--port", type=int, default=None, help="Platform server port (used when --server is host without port)")
    p.add_argument("--device-id", type=str, default=None)
    p.add_argument("--market-id", type=str, default=None)
    p.add_argument("--mode", choices=("http","mqtt"), default=None)
    p.add_argument("--mock", type=str, default=None, help="Enable mock sensors true/false")
    p.add_argument("--interval", type=float, default=None, help="Send interval seconds")
    p.add_argument("--log", default=None, help="Logging level")
    p.add_argument("--interactive", action="store_true", help="Open interactive menu")
    return p.parse_args()

def normalize_server(server: str | None, port: int | None) -> str | None:
    """
    Normalize server input. If server is None return None.
    If server has no scheme, prepend http://.
    If server has no port and port provided, append port.
    Returns base URL like 'http://host:8000' or None.
    """
    if not server:
        return None
    # if user passed full URL with scheme, parse and maybe replace port
    parsed = urlparse(server)
    if parsed.scheme and parsed.netloc:
        host = parsed.netloc
        scheme = parsed.scheme
    else:
        # server might be "localhost" or "localhost:8000"
        scheme = "http"
        host = server
    # if host lacks port and port param provided, add it
    if ":" not in host and port:
        host = f"{host}:{port}"
    return f"{scheme}://{host}"

async def run_register(client: DeviceClient, server_base: str | None):
    print("Registering device...")
    res = await client.register(server_base=server_base)
    print("Registration response:", res)
    if res.get("token"):
        print("Saved token locally.")

async def run_client_loop(client: DeviceClient):
    try:
        await client.run()
    except KeyboardInterrupt:
        print("Stopping client...")

def interactive_menu(args):
    """
    Simple interactive menu loop. Allows customizing server, device id, market id,
    register device, run sender, or quit.
    """
    device_id = args.device_id or settings.DEVICE_ID
    market_id = args.market_id or settings.MARKET_ID
    mode = args.mode or settings.MODE
    mock = settings.MOCK if args.mock is None else (args.mock.lower() == "true")
    interval = settings.INTERVAL if args.interval is None else args.interval
    server_base = None
    if args.server:
        server_base = normalize_server(args.server, args.port)

    print("="*60)
    print("Smart Market Device Client — Interactive")
    print("="*60)
    while True:
        print(f"\nCurrent config: server={server_base or settings.PLATFORM_HTTP_BASE}, device_id={device_id}, market_id={market_id}, mode={mode}, mock={mock}, interval={interval}")
        print("Menu:")
        print(" 1) Set server URL / port")
        print(" 2) Set device id")
        print(" 3) Set market id")
        print(" 4) Set mode (http/mqtt)")
        print(" 5) Toggle mock sensors")
        print(" 6) Set interval (seconds)")
        print(" 7) Register device")
        print(" 8) Run client (start sending)")
        print(" 9) Exit")
        choice = input("Choose an option [1-9]: ").strip()
        if choice == "1":
            host = input("Enter server host or full URL (e.g. localhost or http://host:8000): ").strip()
            port_str = input("Enter port (leave blank if included in URL): ").strip()
            port = int(port_str) if port_str else None
            srv = normalize_server(host, port)
            if srv:
                server_base = srv
            else:
                print("Invalid input")
        elif choice == "2":
            device_id = input("Device ID: ").strip() or device_id
        elif choice == "3":
            market_id = input("Market ID: ").strip() or market_id
        elif choice == "4":
            m = input("Mode (http/mqtt): ").strip().lower()
            if m in ("http","mqtt"):
                mode = m
            else:
                print("Invalid mode")
        elif choice == "5":
            mock = not mock
            print("Mock sensors:", mock)
        elif choice == "6":
            try:
                interval = float(input("Interval seconds: ").strip() or interval)
            except ValueError:
                print("Invalid number")
        elif choice == "7":
            client = DeviceClient(device_id=device_id, market_id=market_id, mode=mode, mock=mock, interval=interval)
            asyncio.run(run_register(client, server_base))
        elif choice == "8":
            client = DeviceClient(device_id=device_id, market_id=market_id, mode=mode, mock=mock, interval=interval)
            if server_base:
                # pass server base to register if user wants to override registration server
                # DeviceClient.register accepts server_base; but run() uses settings.PLATFORM_HTTP_BASE
                # To ensure run uses the chosen server, we set settings.PLATFORM_HTTP_BASE temporarily
                old_base = settings.PLATFORM_HTTP_BASE
                settings.PLATFORM_HTTP_BASE = server_base
                try:
                    print("Starting client (press Ctrl+C to stop)...")
                    asyncio.run(run_client_loop(client))
                finally:
                    settings.PLATFORM_HTTP_BASE = old_base
            else:
                print("Starting client with current PLATFORM_HTTP_BASE...")
                asyncio.run(run_client_loop(client))
        elif choice == "9":
            print("Exiting interactive menu.")
            break
        else:
            print("Invalid choice, try again.")

def main():
    args = parse_args()

    log_level = args.log or settings.LOG_LEVEL
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO), format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # If interactive requested, launch menu
    if args.interactive or (len(sys.argv) == 1):
        # If user ran script without args, go interactive
        interactive_menu(args)
        return

    # Normalize server arg if provided and set PLATFORM_HTTP_BASE
    if args.server:
        server_normalized = normalize_server(args.server, args.port)
        if server_normalized:
            settings.PLATFORM_HTTP_BASE = server_normalized

    client = DeviceClient(device_id=args.device_id, market_id=args.market_id, mode=args.mode, mock=(args.mock.lower()=="true" if isinstance(args.mock,str) else None), interval=args.interval)

    # Handle registration
    if args.register:
        res = asyncio.run(client.register(server_base=(args.server or settings.PLATFORM_HTTP_BASE)))
        print("Registration response:", res)
        return

    # Run client (main loop)
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("Stopping client...")

if __name__ == "__main__":
    main()