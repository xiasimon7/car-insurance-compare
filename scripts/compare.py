#!/usr/bin/env python3
"""本地复算车险报价；只处理已人工核对的结构化数字。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

MONEY = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?$")
CENT = Decimal("0.01")


class InputError(ValueError):
    pass


def amount(value: object, path: str) -> Decimal:
    """拒绝浮点数和负数，避免保费分位被隐式舍入。"""
    if not isinstance(value, str) or not MONEY.fullmatch(value):
        raise InputError(f"{path} 必须是非负金额字符串，最多两位小数")
    return Decimal(value).quantize(CENT)


def optional_amount(value: object, path: str) -> Decimal | None:
    """未知金额用 null 表示，不能用 0 冒充已确认的零元。"""
    if value is None:
        return None
    return amount(value, path)


def money(value: Decimal) -> str:
    return f"{value:.2f}"


def obj(value: object, path: str) -> dict:
    if not isinstance(value, dict):
        raise InputError(f"{path} 必须是对象")
    return value


def nonempty(value: object, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{path} 必须是非空字符串")
    return value.strip()


def parse_quote(raw: object, index: int) -> tuple[dict, dict]:
    quote = obj(raw, f"quotes[{index}]")
    qid = nonempty(quote.get("id"), f"quotes[{index}].id")
    insurer = nonempty(quote.get("insurer"), f"quotes[{index}].insurer")
    source_ref = nonempty(quote.get("source_ref"), f"quotes[{index}].source_ref")
    premium = obj(quote.get("premium"), f"{qid}.premium")
    commercial = optional_amount(premium.get("commercial"), f"{qid}.commercial")
    compulsory = optional_amount(premium.get("compulsory"), f"{qid}.compulsory")
    tax = optional_amount(premium.get("vehicle_tax"), f"{qid}.vehicle_tax")
    components = {"commercial": commercial, "compulsory": compulsory, "vehicle_tax": tax}
    missing_components = [name for name, value in components.items() if value is None]
    if len(missing_components) == len(components):
        raise InputError(f"{qid}.premium 至少需要一项已确认的保费金额")
    products = premium.get("separate_products", [])
    if not isinstance(products, list):
        raise InputError(f"{qid}.separate_products 必须是数组")
    product_sum = Decimal("0.00")
    for n, raw_product in enumerate(products):
        product = obj(raw_product, f"{qid}.separate_products[{n}]")
        nonempty(product.get("name"), f"{qid}.separate_products[{n}].name")
        product_sum += amount(product.get("amount"), f"{qid}.separate_products[{n}].amount")

    known_subtotal = sum((value for value in components.values() if value is not None), Decimal("0.00")) + product_sum
    gross = known_subtotal if not missing_components else None
    cashback_raw = obj(premium.get("cashback", {"amount": "0", "status": "none"}), f"{qid}.cashback")
    cashback = amount(cashback_raw.get("amount"), f"{qid}.cashback.amount")
    status = cashback_raw.get("status")
    if status not in {"promised", "received", "none"}:
        raise InputError(f"{qid}.cashback.status 必须为 promised、received 或 none")
    if (status == "none" and cashback != 0) or (gross is not None and cashback > gross):
        raise InputError(f"{qid}.cashback 与状态或应付总价不一致")
    warnings: list[str] = []
    if missing_components:
        warnings.append("保费组成未齐，已知小计不是整单应付；请向销售确认缺项")
    if "stated_payable" in premium:
        stated = amount(premium["stated_payable"], f"{qid}.stated_payable")
        if gross is None:
            warnings.append("报价单总价尚无法与逐项金额核对")
        elif stated != gross:
            warnings.append(f"报价单应付 {money(stated)} 元与逐项求和 {money(gross)} 元不一致，需核对")

    coverage_raw = quote.get("coverage", [])
    if not isinstance(coverage_raw, list) or not coverage_raw:
        raise InputError(f"{qid}.coverage 至少列出一项险种")
    coverage: dict[str, dict[str, str]] = {}
    for n, raw_line in enumerate(coverage_raw):
        line = obj(raw_line, f"{qid}.coverage[{n}]")
        code = nonempty(line.get("code"), f"{qid}.coverage[{n}].code")
        unit = nonempty(line.get("unit"), f"{qid}.coverage[{n}].unit")
        limit = amount(line.get("limit"), f"{qid}.coverage[{n}].limit")
        if limit == 0:
            raise InputError(f"{qid}.coverage[{n}].limit 必须大于零；未列险种请不要填零")
        line_source = nonempty(line.get("source_ref", source_ref), f"{qid}.coverage[{n}].source_ref")
        count = line.get("count")
        if unit == "seat" and count is None:
            raise InputError(f"{qid}.coverage[{n}].count 每座保额必须填写座位数")
        if count is not None and (type(count) is not int or count < 1):
            raise InputError(f"{qid}.coverage[{n}].count 必须是正整数")
        if code in coverage:
            raise InputError(f"{qid}.coverage 中 {code} 重复；按单位拆分为不同 code")
        coverage[code] = {"limit": money(limit), "unit": unit, "source_ref": line_source}
        if count is not None:
            coverage[code]["count"] = count

    result = {
        "id": qid,
        "insurer": insurer,
        "source_ref": source_ref,
        "premium_breakdown": {
            "commercial": money(commercial) if commercial is not None else None,
            "compulsory": money(compulsory) if compulsory is not None else None,
            "vehicle_tax": money(tax) if tax is not None else None,
            "separate_products": [
                {"name": p["name"], "amount": money(amount(p["amount"], f"{qid}.separate_products.amount"))}
                for p in products
            ],
        },
        "known_subtotal": money(known_subtotal),
        "missing_premium_components": missing_components,
        "payable_now": money(gross) if gross is not None else None,
        "cashback_amount": money(cashback),
        "cashback_status": status,
        "after_cashback_if_received": money(gross - cashback) if gross is not None else None,
        "separate_products_total": money(product_sum),
        "warnings": warnings,
    }
    return result, coverage


def compare(data: object) -> dict:
    payload = obj(data, "root")
    quotes = payload.get("quotes")
    if not isinstance(quotes, list) or len(quotes) < 2:
        raise InputError("quotes 至少需要两份报价")
    results: list[dict] = []
    coverages: dict[str, dict[str, dict[str, str]]] = {}
    for index, raw_quote in enumerate(quotes):
        result, coverage = parse_quote(raw_quote, index)
        qid = result["id"]
        if qid in coverages:
            raise InputError(f"报价编号 {qid} 重复")
        results.append(result)
        coverages[qid] = coverage

    # 未列险种仅说明输入报价中未列，不能推定正式保单不存在。
    differences: list[dict] = []
    for code in sorted(set().union(*(c.keys() for c in coverages.values()))):
        values = {qid: coverage.get(code) for qid, coverage in coverages.items()}
        comparable = {
            None if v is None else (v["limit"], v["unit"], v.get("count"))
            for v in values.values()
        }
        if len(comparable) > 1:
            differences.append({"code": code, "by_quote": values, "note": "保额/单位不同或报价未列；需核对正式条款"})
    return {
        "quotes": results,
        "coverage_differences": differences,
        "decision_note": "只复算金额并提示差异；返现、条款、赠券及最终投保选择需人工核实。",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="本地复算多份车险报价 JSON")
    parser.add_argument("input", type=Path, help="UTF-8 JSON 输入文件")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = compare(data)
    except (OSError, json.JSONDecodeError, InputError) as exc:
        print(f"输入错误：{exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
