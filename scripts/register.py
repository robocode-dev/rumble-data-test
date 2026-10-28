"""Register the issue author as a Rumble participant without a maintainer."""

from __future__ import annotations

import argparse
import re
import secrets
import sys
from pathlib import Path

from common import read_json, write_json
from validate import ValidationError, require

ACCOUNT_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


def register(root: Path, account: str) -> str:
    """Create or retain the registration for an account and return its stable client ID."""
    require(ACCOUNT_PATTERN.fullmatch(account) is not None, f"`{account}` is not a valid account name")
    banned = read_json(root / "bans.json")
    require(account not in set(banned.get("bannedAccounts", [])), f"account `{account}` is banned")
    path = root / "clients" / f"{account}.json"
    if path.is_file():
        existing = read_json(path)
        require(existing.get("account") == account and existing.get("clientIds"), f"registration for `{account}` is invalid")
        return existing["clientIds"][0]
    client_id = f"{account}-{secrets.token_hex(4)}"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, {"schemaVersion": 1, "account": account, "clientIds": [client_id]})
    return client_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--account", required=True, help="Account that opened the registration issue")
    args = parser.parse_args()
    try:
        print(f"Registered `{args.account}` with client ID `{register(args.root, args.account)}`.")
    except ValidationError as error:
        print(f"Registration refused: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
