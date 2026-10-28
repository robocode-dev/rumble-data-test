"""Registration of the issue author without a maintainer."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from register import register
from validate import ValidationError


class RegisterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "bans.json").write_text(json.dumps({"schemaVersion": 1, "bannedAccounts": ["banned-one"], "disqualifiedBots": []}))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_new_account_gets_a_registration_file(self) -> None:
        client_id = register(self.root, "outsider")
        data = json.loads((self.root / "clients" / "outsider.json").read_text())
        self.assertEqual({"schemaVersion": 1, "account": "outsider", "clientIds": [client_id]}, data)
        self.assertTrue(client_id.startswith("outsider-"))

    def test_repeat_registration_keeps_the_same_client_id(self) -> None:
        self.assertEqual(register(self.root, "outsider"), register(self.root, "outsider"))

    def test_banned_account_is_refused_and_nothing_is_written(self) -> None:
        with self.assertRaises(ValidationError):
            register(self.root, "banned-one")
        self.assertFalse((self.root / "clients" / "banned-one.json").exists())

    def test_account_name_cannot_escape_the_clients_folder(self) -> None:
        with self.assertRaises(ValidationError):
            register(self.root, "../evil")


if __name__ == "__main__":
    unittest.main()
