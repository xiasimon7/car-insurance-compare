# 本地计算输入格式

输入为 UTF-8 JSON，顶层 `quotes` 至少有两份报价。已知金额以**元为单位的字符串**输入，最多两位小数；未知金额使用 JSON `null`，不要使用浮点数或用 0 代替未知。此文件只记录计算所需的脱敏字段，原图与全文条款由使用者在本地保管。下方只展示一份报价的字段结构；可直接运行的双报价输入见 [examples/quotes.json](../examples/quotes.json)。

```json
{
  "quotes": [
    {
      "id": "A",
      "insurer": "示例甲财险",
      "source_ref": "报价图第1页",
      "premium": {
        "commercial": "3800.00",
        "compulsory": "760.00",
        "vehicle_tax": "0.00",
        "separate_products": [{"name": "驾乘意外组合", "amount": "420.00"}],
        "stated_payable": "4980.00",
        "cashback": {"amount": "200.00", "status": "promised"}
      },
      "coverage": [
        {"code": "vehicle_damage", "limit": "220000.00", "unit": "vehicle", "source_ref": "报价图第1页"},
        {"code": "third_party", "limit": "3000000.00", "unit": "vehicle", "source_ref": "报价图第1页"}
      ]
    }
  ]
}
```

字段说明：

- `id`：A/B/C 等脱敏编号，同一输入内唯一。`insurer`、`source_ref` 用于回溯，不写客户个人信息。
- `premium.commercial`、`compulsory`、`vehicle_tax`：已确认的各项金额；未列或看不清时填 `null` 并向销售核实，只有确认是 0 元或不适用才填 `"0.00"`。只要有一项未知，脚本仅输出已知小计，整单应付与返现后金额均为 `null`。`separate_products` 仅放**不包含在商业险小计中、却计入总应付额**的单列产品；用户可能另购的服务包不放进这里，避免重复计价。
- `stated_payable`：报价单显示的应付总价，可不填；填写后脚本会检验与逐项求和是否一致。
- `cashback.status`：`promised`、`received` 或 `none`。脚本给出的“返现后金额”仅为算术结果；`promised` 时绝不表述为已实付。
- `coverage`：只录报价实际列出的险种。`code` 可使用 `vehicle_damage`、`third_party`、`driver_liability`、`passenger_liability`、`third_party_out_of_medicare` 等稳定标识；新能源车相关险种可使用 `external_grid`，不适用的车型无需填写。也可为其他险种使用自定义稳定标识。`unit` 使用 `vehicle`、`person`、`seat` 等。`unit` 为 `seat` 时，`limit` 填每座保额，`count` 必填实际座位数。同一 `code` 在一份报价内只能出现一次。`limit` 看不清时请先人工核实，不要自行填 0。

脚本不会给赠券估值，也不会自动建议删减险种。`coverage` 的“未列”只表示输入报价没有该项。医疗免赔、赔付比例、年龄分档、服务券限制等须在人工报告中对照正式资料说明，不能硬塞成一个保额数字。
