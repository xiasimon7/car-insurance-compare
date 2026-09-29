"""验证金额分位、返现状态与不同保障口径的提示。"""

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("compare", ROOT / "scripts" / "compare.py")
compare_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(compare_module)


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples" / "quotes.json").read_text(encoding="utf-8"))

    def test_money_and_conditional_cashback(self):
        result = compare_module.compare(self.data)
        a, b = result["quotes"]
        self.assertEqual((a["payable_now"], a["after_cashback_if_received"]), ("4980.00", "4780.00"))
        self.assertEqual(a["cashback_status"], "promised")
        self.assertEqual((b["payable_now"], b["after_cashback_if_received"]), ("4760.00", "4760.00"))
        self.assertNotIn("实际已付", json.dumps(result, ensure_ascii=False))

    def test_unlisted_rider_and_limit_differences_are_reported(self):
        differences = {row["code"]: row for row in compare_module.compare(self.data)["coverage_differences"]}
        self.assertIsNone(differences["external_grid"]["by_quote"]["B"])
        self.assertEqual(differences["vehicle_damage"]["by_quote"]["A"]["limit"], "220000.00")
        self.assertEqual(differences["third_party"]["by_quote"]["B"]["limit"], "4000000.00")

    def test_stated_total_mismatch_requires_review(self):
        self.data["quotes"][0]["premium"]["stated_payable"] = "4979.99"
        warning = compare_module.compare(self.data)["quotes"][0]["warnings"][0]
        self.assertIn("不一致", warning)

    def test_invalid_money_does_not_round_or_accept_float(self):
        self.data["quotes"][0]["premium"]["commercial"] = "3800.001"
        with self.assertRaises(compare_module.InputError):
            compare_module.compare(self.data)
        self.data["quotes"][0]["premium"]["commercial"] = 3800.0
        with self.assertRaises(compare_module.InputError):
            compare_module.compare(self.data)
        self.data["quotes"][0]["premium"]["commercial"] = "9" * 30
        with self.assertRaises(compare_module.InputError):
            compare_module.compare(self.data)

    def test_duplicate_quote_or_coverage_is_rejected(self):
        self.data["quotes"][1]["id"] = "A"
        with self.assertRaises(compare_module.InputError):
            compare_module.compare(self.data)
        self.data["quotes"][1]["id"] = "B"
        self.data["quotes"][0]["coverage"].append(self.data["quotes"][0]["coverage"][0])
        with self.assertRaises(compare_module.InputError):
            compare_module.compare(self.data)

    def test_per_seat_limit_needs_seat_count(self):
        self.data["quotes"][0]["coverage"].append({"code": "passenger_liability", "limit": "10000", "unit": "seat"})
        with self.assertRaises(compare_module.InputError):
            compare_module.compare(self.data)
        self.data["quotes"][0]["coverage"][-1]["count"] = 4
        differences = {row["code"]: row for row in compare_module.compare(self.data)["coverage_differences"]}
        self.assertEqual(differences["passenger_liability"]["by_quote"]["A"]["count"], 4)

    def test_source_page_does_not_create_fake_coverage_difference(self):
        self.data["quotes"][1]["coverage"][0]["limit"] = "220000.00"
        differences = {row["code"] for row in compare_module.compare(self.data)["coverage_differences"]}
        self.assertNotIn("vehicle_damage", differences)

    def test_missing_coverage_cannot_be_entered_as_zero_limit(self):
        self.data["quotes"][0]["coverage"][0]["limit"] = "0"
        with self.assertRaises(compare_module.InputError):
            compare_module.compare(self.data)

    def test_commercial_only_quote_cannot_look_like_full_policy_price(self):
        quote = self.data["quotes"][1]
        quote["premium"]["compulsory"] = None
        quote["premium"]["vehicle_tax"] = None
        result = compare_module.compare(self.data)["quotes"][1]
        self.assertEqual(result["known_subtotal"], "4000.00")
        self.assertEqual(result["missing_premium_components"], ["compulsory", "vehicle_tax"])
        self.assertIsNone(result["payable_now"])
        self.assertIsNone(result["after_cashback_if_received"])
        self.assertIn("不是整单应付", result["warnings"][0])

    def test_omitted_separate_products_or_cashback_cannot_imply_none(self):
        premium = self.data["quotes"][0]["premium"]
        premium.pop("separate_products")
        with self.assertRaises(compare_module.InputError):
            compare_module.compare(self.data)
        premium["separate_products"] = []
        premium.pop("cashback")
        with self.assertRaises(compare_module.InputError):
            compare_module.compare(self.data)

    def test_unknown_cashback_does_not_create_net_price(self):
        self.data["quotes"][0]["premium"]["cashback"] = {"amount": None, "status": "unknown"}
        quote = compare_module.compare(self.data)["quotes"][0]
        self.assertEqual(quote["payable_now"], "4980.00")
        self.assertIsNone(quote["after_cashback_if_received"])
        self.assertIn("未确认", quote["warnings"][0])


if __name__ == "__main__":
    unittest.main()
