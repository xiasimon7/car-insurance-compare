---
name: car-insurance-compare
description: 阅读中国大陆车险报价图片或文字与销售说明，拆解单份或多份报价，复算金额、比较保障并给出有依据的购买建议；适用于续保或购买车险时。
---

# 车险比价助手

遵循可跨平台复用的 [通用车险比价指令](PROMPT.md)。该文件包含读取图片或文字、费用复算、保障比较、条件性建议、销售询问和隐私边界；Codex 可在当前目录读取并执行。需要录入脚本时参照 [输入格式](references/schema.md)，核对细则见 [评估规则](references/review_rules.md)，话术细则见 [销售沟通规则](references/negotiation.md)。

对图片中的关键数字先回看原图；只有核对过的脱敏数值才交给 `python scripts/compare.py <输入.json>`。脚本只做确定性计算和差异提示，不负责读图或最终投保选择。
