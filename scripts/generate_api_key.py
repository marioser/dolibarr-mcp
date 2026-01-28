#!/usr/bin/env python3
"""Generate secure API keys for MCP authentication."""

import secrets
import argparse
import sys


def generate_key(length: int = 32) -> str:
    """Generate a secure API key.

    Args:
        length: Number of bytes (key will be 2x length in hex chars)

    Returns:
        Hex-encoded random string
    """
    return secrets.token_hex(length)


def main():
    parser = argparse.ArgumentParser(
        description="Generate secure API keys for Dolibarr MCP Server"
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=1,
        help="Number of keys to generate (default: 1)"
    )
    parser.add_argument(
        "-l", "--length",
        type=int,
        default=32,
        help="Key length in bytes (default: 32 = 64 hex chars)"
    )
    parser.add_argument(
        "--env",
        action="store_true",
        help="Output in .env format"
    )

    args = parser.parse_args()

    keys = [generate_key(args.length) for _ in range(args.count)]

    if args.env:
        if args.count == 1:
            print(f"MCP_API_KEY={keys[0]}")
        else:
            print(f"MCP_API_KEYS={','.join(keys)}")
    else:
        for i, key in enumerate(keys, 1):
            if args.count > 1:
                print(f"Key {i}: {key}")
            else:
                print(key)

    return 0


if __name__ == "__main__":
    sys.exit(main())
