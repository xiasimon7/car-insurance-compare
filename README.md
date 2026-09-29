# 车险比价助手

一个适用于中国大陆车险报价比较的 [Agent Skills](https://agentskills.io/specification) 项目，包含跨工具使用的 `SKILL.md`、核对规则和本地计算脚本；不限定城市、汽车品牌或燃油／新能源车型。把一份或多份报价图片、权益图和销售说明交给支持图片输入的 AI 助手，它可以据此拆解费用和保障、提出购买建议与待确认问题。若当前助手不支持图片输入，可提供脱敏的 OCR 文本或手工摘录。项目不连接保险公司、不代用户投保，也不把销售宣传当作正式保单。

本地计算脚本使用 Python 3.9 或更新版本的标准库，无需安装第三方依赖。

## 作为 Skill 使用

整个仓库就是一个 Skill 文件夹：`SKILL.md` 是完整的标准入口，`references/` 和 `scripts/` 是配套资源。将仓库克隆到所用工具的 Skills 目录，即可按该工具的方式调用。`agents/openai.yaml` 仅提供 Codex 的界面信息，不影响其他工具读取 `SKILL.md`。

| 工具 | 个人 Skill 目录或安装方式 |
| --- | --- |
| [Codex](https://developers.openai.com/codex/skills) | `~/.codex/skills/car-insurance-compare/` |
| [Claude Code](https://code.claude.com/docs/en/skills) | `~/.claude/skills/car-insurance-compare/` |
| [Cursor](https://prod.cursor.com/docs/skills) | `~/.cursor/skills/car-insurance-compare/` |
| [Gemini CLI](https://geminicli.com/docs/cli/using-agent-skills/) | `gemini skills install https://github.com/xiasimon7/car-insurance-compare` |
| [GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) | `~/.copilot/skills/car-insurance-compare/` |
| [千问办公](https://docs.qwenwork.cn/features/skills) | `~/.qwenworkcn/skills/car-insurance-compare/`，或在「扩展 → 技能」上传包含 `SKILL.md` 的技能包 |
| [腾讯 WorkBuddy](https://cloud.tencent.com/document/product/1831/134432) | 在「专家·技能·连接器 → 添加技能 → 上传技能」导入本地技能包 |
| [Qoder IDE／CLI](https://docs.qoder.com/zh/extensions/skills) | `~/.qoder/skills/car-insurance-compare/`，或项目内 `.qoder/skills/car-insurance-compare/` |

上表依据各工具的官方文档列出入口；除 Codex 外尚未在本项目中逐一实测。各工具的触发方式、图片附件支持和脚本权限可能不同，请按其官方说明设置。豆包普通聊天界面可接收报价图片并回答问题，但目前未查到将本仓库安装为 Agent Skill 的官方方法，因此未列入安装表。

AI **模型**与承载它的**应用或 Agent 工具**需要区分：使用豆包、DeepSeek 等模型，并不自动说明当前聊天界面能安装 Skill；若承载该模型的工具支持 Agent Skills，就按上面的方法安装。没有图片输入时提供脱敏的 OCR 文字；不能运行本地脚本时 Skill 会要求助手列出算式与待核对数字。各平台对附件和个人资料的处理方式不同，上传前请自行核对其隐私设置。

## 安装与试运行

按上表将仓库放入所用工具的 Skills 目录，文件夹名保持 `car-insurance-compare`。在支持图片输入的工具中调用该 Skill，附上一份或多份报价图片、销售聊天和用车需求；多份报价时可用本地脚本复算。用户无需先填写 JSON，原始保单可留在自己的工作目录。

```bash
git clone "https://github.com/xiasimon7/car-insurance-compare.git"
cd car-insurance-compare
python3 scripts/compare.py examples/quotes.json
```

上面的命令可先在任意工作目录试运行；正式安装时再按所用工具的目录放置整个文件夹。Codex 中可用 `$car-insurance-compare` 调用，其他工具遵循各自的 Skill 调用方式。示例数据完全虚构：A 应付 4980.00 元，销售承诺返现 200.00 元；B 应付 4760.00 元。脚本会提示车损、三者险和外部电网险的口径差异，不做最终价格排名。

## 一次完整使用示例

在已安装本 Skill、支持图片输入的 AI 工具中附上两份报价截图和对应的销售说明，再输入：

> 请用车险比价助手比较这两份报价。我更在意保障合适后少花钱；返现尚未到账。请标出图片中无法核实的数字、需要问销售的问题，并给我一段可复制的询问文字。

以仓库中的**虚构数据**演示，报告应先列出：A 今天应付 4980.00 元，承诺返现兑现后可能净支出 4780.00 元；B 今天应付 4760.00 元。随后指出 A、B 的车损保额分别为 22 万元和 21 万元，三者险分别为 300 万元和 400 万元，外部电网险只在 A 的输入报价中列出。因为保障口径不同，此时应请销售确认缺项并按相同保障重报，再决定哪份更合适。报告还应注明各数字来自哪张报价图或哪段销售说明；截图模糊时先请用户核对，不猜测。

## 能做什么

- 分开显示商业险、交强险、车船税、单列保障产品、应付总额与返现后的条件净价。
- 对报价未列的险种、不同保额和每车/每座等单位差异给出核对提示；商业险单独报价只显示已知小计，不冒充整单价格。
- 引导 AI 助手对照原图或文字、正式条款和用户实际需求，整理可发给销售的确认问题。
- 根据当前谈判阶段，拟出可复制的询价、重报或最终确认文字；不会自行发送。

## 当前边界

支持图片输入的助手可直接阅读所附图片；不支持的助手只能依据用户提供的文字。模糊、裁切或相互矛盾的关键数字需要回看原图或请用户确认。本地脚本只接受结构化 JSON，不承担读图。免赔、赔付比例、年龄分档和赠券价值须结合具体资料判断。报价未列某项不等于正式保单肯定没有。返现显示为条件算术结果，未到账前不能当作实际支出。

输入格式见 [references/schema.md](references/schema.md)，判断口径见 [references/review_rules.md](references/review_rules.md)，销售沟通方式见 [references/negotiation.md](references/negotiation.md)。测试命令：`python -m unittest discover -s tests -v`。

## 隐私与公开仓库

仓库只包含原创代码、规则和虚构示例。请勿提交真实报价截图、姓名、车牌、VIN、手机号、保单号或销售聊天记录。把本地输入放在 `private/` 或以 `.local.json` 结尾的文件中，并在提交前复核跟踪文件。计算脚本无需联网。

## 许可证

本项目采用 [MIT 许可证](LICENSE)，版权声明使用项目所有者的 GitHub 用户名 `xiasimon7`。

## 贡献

欢迎提交改进规则、虚构测试样例和代码修复。请先运行 `python -m unittest discover -s tests -v`，并在提交说明中写清改动验证方式。Issue、讨论和提交中不要附真实保单、报价截图、车牌、姓名、联系方式或其他个人资料；复现问题请改用虚构数据。
