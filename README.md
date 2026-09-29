# 车险比价助手

一个适用于中国大陆车险报价比较的 [Agent Skills](https://agentskills.io/specification) 项目，包含跨工具使用的 `SKILL.md`、核对规则和本地计算脚本；不限定城市、汽车品牌或燃油／新能源车型。把一份或多份报价图片、权益图和销售说明交给支持图片输入的 AI 助手，它可以据此拆解费用和保障、提出购买建议与待确认问题。若当前助手不支持图片输入，可提供脱敏的 OCR 文本或手工摘录。项目不连接保险公司、不代用户投保，也不把销售宣传当作正式保单。

本地计算脚本使用 Python 3.9 或更新版本的标准库，无需安装第三方依赖。

## 安装 Skill

将整个仓库作为一个 Skill 安装，保留根目录的 `SKILL.md` 及同级的 `references/`、`scripts/`。

### 让 AI 助手安装

在能联网、能操作本地文件的 Agent 中发送下面这段话。它需要获得相应的网络和文件权限；如果当前工具不支持从 GitHub 安装，就使用下一节的手动方式。

> 请从 https://github.com/xiasimon7/car-insurance-compare 下载完整仓库，将其安装到你当前工具的个人 Skills 目录，保留 `SKILL.md`、`references/` 和 `scripts/`。安装后检查 `car-insurance-compare/SKILL.md` 是否位于技能目录内，确认技能已加载，并告诉我如何调用。若不能直接安装，请说明当前界面支持的本地导入方式。

### 手动安装

1. 在 [GitHub 仓库](https://github.com/xiasimon7/car-insurance-compare)点击 **Code → Download ZIP**，解压后将文件夹命名为 `car-insurance-compare`；也可以用 `git clone` 下载。
2. 若工具提供“上传／导入技能”，导入包含完整 Skill 的文件夹或压缩包。若工具使用个人 Skills 目录，把整个 `car-insurance-compare` 文件夹放到下表对应位置；最终应能找到 `car-insurance-compare/SKILL.md`。
3. 在工具的已安装技能列表中确认名称，必要时重开会话或按工具说明重新加载，再用下方的虚构示例试运行。

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
| [豆包](https://docs.volcengine.com/docs/volcano-engine-skills/overview-2?lang=zh) | 桌面版：「插件·技能·伙伴 → 技能 → ＋添加」 |

### 可选：试运行本地计算脚本

多份报价会先整理为统一字段：从图片或文字提取信息，标注来源与待确认项，核对关键数字后按[输入格式](references/schema.md)生成脱敏 JSON，再用脚本复算。用户无需手填 JSON；脚本不是安装 Skill 的必需步骤。

```bash
git clone "https://github.com/xiasimon7/car-insurance-compare.git"
cd car-insurance-compare
python3 scripts/compare.py examples/quotes.json
```

Codex 中可用 `$car-insurance-compare` 调用，其他工具遵循各自的 Skill 调用方式。示例数据完全虚构：A 应付 4980.00 元，销售承诺返现 200.00 元；B 应付 4760.00 元。脚本会提示车损、三者险和外部电网险的口径差异，不做最终价格排名。

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

本项目采用 [MIT 许可证](LICENSE)。

## 贡献

欢迎提交改进规则、虚构测试样例和代码修复。请先运行 `python -m unittest discover -s tests -v`，并在提交说明中写清改动验证方式。Issue、讨论和提交中不要附真实保单、报价截图、车牌、姓名、联系方式或其他个人资料；复现问题请改用虚构数据。
