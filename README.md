# 车险比价助手

一个供 Codex 调用的中国大陆车险报价比较 Skill，适用于不同城市、品牌和燃油／新能源车型。把一份或多份报价图片、权益图和销售说明发给支持图片输入的 Codex，它会读图、拆解费用和保障，在证据足够时给出购买建议；影响判断的条件不明时，会拟出发给对应销售的具体问题。它不连接保险公司、不代用户投保，也不把销售宣传当作正式保单。

本地计算脚本使用 Python 3.9 或更新版本的标准库，无需安装第三方依赖。

## 使用

将本仓库克隆到 Codex 的 Skills 目录，文件夹名保持 `car-insurance-compare`。在 Codex 中调用 `$car-insurance-compare`，附上一份或多份报价图片、销售聊天和你关心的用车场景。Codex 会直接读图并回看关键数字；多份报价时再用本地脚本复算。你无需先做 OCR 或填写 JSON，原始保单可留在你的本地工作目录。

```bash
git clone "https://github.com/xiasimon7/car-insurance-compare.git" "$HOME/.codex/skills/car-insurance-compare"
python "$HOME/.codex/skills/car-insurance-compare/scripts/compare.py" \
  "$HOME/.codex/skills/car-insurance-compare/examples/quotes.json"
```

可直接使用上面的安装命令；在仓库目录中也可运行 `python scripts/compare.py examples/quotes.json`。示例数据完全虚构：A 应付 4980.00 元，销售承诺返现 200.00 元；B 应付 4760.00 元。脚本会提示车损、三者险和外部电网险的口径差异，不做最终价格排名。

## 一次完整使用示例

在 Codex 中附上两份报价截图和对应的销售说明，并输入：

> 请用 `$car-insurance-compare` 比较这两份车险报价。我更在意保障合适后少花钱；返现尚未到账。请标出图片中无法核实的数字、需要问销售的问题，并给我一段可复制的询问文字。

以仓库中的**虚构数据**演示，报告应先列出：A 今天应付 4980.00 元，承诺返现兑现后可能净支出 4780.00 元；B 今天应付 4760.00 元。随后指出 A、B 的车损保额分别为 22 万元和 21 万元，三者险分别为 300 万元和 400 万元，外部电网险只在 A 的输入报价中列出。因为保障口径不同，此时应请销售确认缺项并按相同保障重报，再决定哪份更合适。报告还应注明各数字来自哪张报价图或哪段销售说明；截图模糊时先请用户核对，不猜测。

## 能做什么

- 分开显示商业险、交强险、车船税、单列保障产品、应付总额与返现后的条件净价。
- 对报价未列的险种、不同保额和每车/每座等单位差异给出核对提示；商业险单独报价只显示已知小计，不冒充整单价格。
- 引导 Codex 对照原图、正式条款和用户实际需求，整理可发给销售的确认问题。
- 根据当前谈判阶段，拟出可复制的询价、重报或最终确认文字；不会自行发送。

## 当前边界

Codex 可直接阅读所附图片并给出有依据的建议；模糊、裁切或相互矛盾的关键数字需要回看原图或请用户确认。本地脚本只接受结构化 JSON，不承担读图。免赔、赔付比例、年龄分档和赠券价值须结合具体资料判断。报价未列某项不等于正式保单肯定没有。返现显示为条件算术结果，未到账前不能当作实际支出。

输入格式见 [references/schema.md](references/schema.md)，判断口径见 [references/review_rules.md](references/review_rules.md)，销售沟通方式见 [references/negotiation.md](references/negotiation.md)。测试命令：`python -m unittest discover -s tests -v`。

## 隐私与公开仓库

仓库只包含原创代码、规则和虚构示例。请勿提交真实报价截图、姓名、车牌、VIN、手机号、保单号或销售聊天记录。把本地输入放在 `private/` 或以 `.local.json` 结尾的文件中，并在提交前复核跟踪文件。计算脚本无需联网。

## 许可证

本项目采用 [MIT 许可证](LICENSE)，版权声明使用项目所有者的 GitHub 用户名 `xiasimon7`。

## 贡献

欢迎提交改进规则、虚构测试样例和代码修复。请先运行 `python -m unittest discover -s tests -v`，并在提交说明中写清改动验证方式。Issue、讨论和提交中不要附真实保单、报价截图、车牌、姓名、联系方式或其他个人资料；复现问题请改用虚构数据。
