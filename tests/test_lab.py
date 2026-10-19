"""Тесты без обращения к сети (используются заглушки)."""
import unittest
from unittest.mock import MagicMock

import requests

from wolfram_lab.client import WolframAPIError, WolframClient
from wolfram_lab.parser import extract

SAMPLE = {"queryresult": {"success": True, "error": False, "timing": 1.2, "pods": [
    {"title": "Input", "id": "Input", "subpods": [{"plaintext": "molar mass of H2SO4"}]},
    {"title": "Result", "id": "Result", "primary": True,
     "subpods": [{"plaintext": "98.079 g/mol"}]},
]}}


def fake_response(status=200, payload=None):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = payload if payload is not None else SAMPLE
    r.text = "body"
    return r


class ParserTests(unittest.TestCase):
    def test_extract_primary(self):
        item = extract(3, "Химия", "molar mass of H2SO4", SAMPLE)
        self.assertTrue(item["success"])
        self.assertEqual(item["key_answer"], "98.079 g/mol")
        self.assertEqual(item["key_pod_title"], "Result")

    def test_extract_failure(self):
        item = extract(1, "x", "asdf", {"queryresult": {"success": False, "error": False,
                       "didyoumeans": {"val": "sdf"}}})
        self.assertFalse(item["success"])
        self.assertIsNone(item["key_answer"])
        self.assertEqual(item["didyoumeans"], ["sdf"])


class ClientTests(unittest.TestCase):
    def make(self, session):
        return WolframClient("id", "http://x", retries=2, backoff=0, session=session)

    def test_ok(self):
        s = MagicMock(); s.get.return_value = fake_response()
        self.assertEqual(self.make(s).query("q"), SAMPLE)

    def test_retry_then_ok(self):
        s = MagicMock()
        s.get.side_effect = [requests.ConnectionError("down"), fake_response()]
        self.assertEqual(self.make(s).query("q"), SAMPLE)
        self.assertEqual(s.get.call_count, 2)

    def test_bad_appid(self):
        s = MagicMock(); s.get.return_value = fake_response(403)
        with self.assertRaises(WolframAPIError):
            self.make(s).query("q")

    def test_api_error_object(self):
        s = MagicMock()
        s.get.return_value = fake_response(payload={"queryresult": {"error": {"code": "1", "msg": "Invalid appid"}}})
        with self.assertRaises(WolframAPIError):
            self.make(s).query("q")

    def test_all_attempts_fail(self):
        s = MagicMock(); s.get.side_effect = requests.Timeout("t")
        with self.assertRaises(WolframAPIError):
            self.make(s).query("q")


if __name__ == "__main__":
    unittest.main()
