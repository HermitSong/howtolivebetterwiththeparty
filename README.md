# How to Live Better with the Party

**在党的光辉下，如何过得更好**

中国特色社会主义与中国发展实用指南。这里的“党”指中国共产党（the Communist Party of China）；仓库名为 `howtolivebetterwiththeparty`。

**从理论到有证据的行动：理解过去，分析现在，推演未来。**

这是一套围绕**中国特色社会主义与中国发展**的开放研究指南和 AI 技能。以毛泽东、邓小平、江泽民、胡锦涛、习近平及其他中国领导人的相关公开文献为理论与历史线索，结合党和政府公开文件、统计资料与实证研究，贯通**国家发展 → 地方与产业 → 家庭与个人**。

既研究“是什么、为什么、效果如何”，也回答“怎样落实、怎么选择、先做什么”。每一步都要分清：文件提出的目标、已经观察到的结果、研究者的解释与建议，以及尚待验证的未来情景。

**[开始阅读](book/README.md) · [理论与领导人文献](skills/china-development/references/theory-history.md) · [使用 AI 技能](skills/china-development/SKILL.md) · [项目定位](docs/project-focus.md)**

喜欢按关键词查找，可以下载仓库后用浏览器打开 [`index.html`](index.html)，按国家、产业或个人筛选并展开完整条目。页面无需安装依赖，目录、网页和技能条目来自同一份数据。

## 从你的问题开始

| 层面 | 可以研究什么 | 阅读入口 |
|---|---|---|
| 国家发展 | 理论演变、规划与实际进度、增长与民生、改革效果、未来情景 | [国家发展：6 条行动卡](book/national.md) |
| 地方与产业 | 产业园需求、产业链招商、乡村产业、养老服务、财政承受能力、企业机会 | [地方与产业：6 条行动卡](book/industry.md) |
| 家庭与个人 | 换城就业、失业欠薪、住房、培训、养老照护、创业与政策适用 | [家庭与个人：6 条行动卡](book/personal.md) |

行动卡逐项说明适用条件、所需信息、行动步骤、成本与取舍、暂停条件、地方核验、来源和复查信号。宏观政策进入具体选择，要经过政策工具、执行主体、地方规则和个人条件的核验；国家方向本身不等于项目收益或个人资格。

## 理论、文件和证据怎么连接

- **理论与历史**：比较毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想的形成背景与概念，区分个人论述、集体文件和后来的历史评价。[理论导读](skills/china-development/references/theory-history.md)
- **现实与政策**：查清规则效力、地方实施和统计口径；官方文件用于确认官方目标与规定，政策实效仍需数据和适当的分析方法检验。[研究方法](skills/china-development/references/research-method.md)
- **未来与行动**：比较可行方案，写出假设、约束、成本、受益与负担、失败条件和改判信号；不把规划目标写成未来事实。[行动卡使用方法](skills/china-development/references/practical-guide.md)

当前种子版本截至 **2026-10-06**，含 **18 张行动卡**和 **53 条来源记录**：40 条已打开正文、12 条门户或目录、1 条访问受阻记录。它们是可继续研究的起点，并非全部著作或全文数据库；访问受阻的记录不作为已核验正文使用。[来源目录](skills/china-development/references/source-catalog.json) · [来源状态说明](skills/china-development/references/source-guide.md)

## 交给 AI 使用

将 [`skills/china-development`](skills/china-development) 文件夹复制到所用工具规定的技能目录；该工具需支持 `SKILL.md`，具体位置和调用方式以其文档为准。技能通过原文检索和行动卡辅助回答，当前政策、地方规则与新数据在使用时需要联网核验。

项目展示名已更新；技能调用标识仍为 `china-development`，已有调用方式继续适用。

示例提问：

> 使用 china-development，比较邓小平关于发展生产力的相关论述与当前高质量发展要求，分别说明历史语境、政策目标和可检验指标。

> 使用 china-development，分析一个人口流出县建设新能源产业园的条件，从国家规划、地方约束到企业需求逐层验证，提出试点及停止条件。

> 使用 china-development，把国家就业政策落实到我的换城选择，核对当地岗位、生活成本、社保接续与补贴资格，列出还缺的信息。

维护后运行结构与引用检查：

```bash
python tools/check.py
```

检查通过不等于所有历史解释、现实建议或预测都正确；回答行为还需按[验收题](skills/china-development/references/evaluation.md)检验。已完成的检查和试用范围见[验证记录](docs/validation.md)。欢迎按[贡献说明](CONTRIBUTING.md)补充文献、纠错和新增条目。

## 范围与方法来源

本指南支持持续扩展，不宣称收齐所有领导人文献、掌握未公开决策或回答一切问题。历史研究保留时代条件；现实建议核对地区和日期；未来分析给出条件情景。材料公开可读也不等于可以任意复制完整书籍。

指南内容为原创，仅借鉴 [HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter/tree/20718eeab32cb8506971fb71b03e66a91077be07) 的可读条目、证据溯源和“阅读 + skill”双入口组织方法。该项目本身已面向中国大陆生活；本项目聚焦中国特色社会主义理论与中国发展，并将研究延伸到地方产业和个人实践。[对标记录](skills/china-development/references/benchmark.md)

本项目为独立研究与实践指南，不隶属党政机关。第三方文献保留各自权利；项目原创材料暂未指定统一的开放许可。
