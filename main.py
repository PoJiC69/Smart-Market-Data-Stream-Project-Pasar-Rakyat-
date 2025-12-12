#!/usr/bin/env python3
"""
CLI entrypoint for the device client.

Usage examples:
  python main.py --register --server http://localhost:8000
  python main.py --mode http --mock true --interval 2.0
"""
from __future__ import annotations

import argparse
import asyncio
import logging

from device_client.client import DeviceClient
from device_client.config import settings

def parse_args():
    p = argparse.ArgumentParser("smart-market-device-client")
    p.add_argument("--register", action="store_true", help="Register device with platform")
    p.add_argument("--server", type=str, default=None, help="Platform server base URL for registration")
    p.add_argument("--device-id", type=str, default=None)
    p.add_argument("--market-id", type=str, default=None)
    p.add_argument("--mode", choices=("http","mqtt"), default=None)
    p.add_argument("--mock", type=str, default=None, help="Enable mock sensors true/false")
    p.add_argument("--interval", type=float, default=None, help="Send interval seconds")
    p.add_argument("--log", default=None, help="Logging level")
    return p.parse_args()

async def main():
    args = parse_args()
    log_level = args.log or settings.LOG_LEVEL
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO), format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    client = DeviceClient(device_id=args.device_id, market_id=args.market_id, mode=args.mode, mock=(args.mock.lower()=="true" if isinstance(args.mock,str) else None), interval=args.interval)
    if args.register:
        res = await client.register(server_base=args.server)
        print("Registration response:", res)
        if res.get("token"):
            print("Saved token locally.")
    else:
        try:
            await client.run()
        except KeyboardInterrupt:
            print("Stopping client...")

if __name__ == "__main__":
    asyncio.run(main())