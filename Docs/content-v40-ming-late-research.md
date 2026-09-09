# 史迹 0.40 后明八帝扩充核查

交付 `/private/tmp/shiji-v40-ming-late.json`。19 位人物、19 篇三节长读（每篇500–800汉字）、16 项新事件、19 项旧事件更新、36 条人物关联、22 处章节链接、8 帝覆盖清单。未修改主仓库。

已使用 web-access skill，先检查依赖；Chrome CDP 未连接，公开资料使用 web 直接读取。核心依据是已实际阅读的公版《明史》本传、帝纪，科学交流补中科院科学史研究所与故宫词条。

| 范围 | 主要已读来源 | 核查点 |
|---|---|---|
| 弘治、正德 | [卷181](https://zh.wikisource.org/zh-hans/明史/卷181)、[卷15](https://zh.wikisource.org/zh-hans/明史/卷15)、[卷304](https://zh.wikisource.org/zh-hans/明史/卷304)、[卷195](https://zh.wikisource.org/zh-hans/明史/卷195) | 三阁臣任职与去留、节用议论、暑月录囚、刘瑾倒台、宁王作战先于武宗南征 |
| 嘉靖、隆庆 | [卷308](https://zh.wikisource.org/zh-hans/明史/卷308)、[卷213](https://zh.wikisource.org/zh-hans/明史/卷213)、[卷212](https://zh.wikisource.org/zh-hans/明史/卷212)、[卷226](https://zh.wikisource.org/zh-hans/明史/卷226) | 严嵩1562罢职不与严世蕃处死混同；海瑞1566上疏与隆庆获释；高拱/张居正支持封贡；戚继光转任蓟镇；海瑞1569起巡应天约半年 |
| 万历、泰昌 | [卷218](https://zh.wikisource.org/zh-hans/明史/卷218)、[卷21](https://zh.wikisource.org/zh-hans/明史/卷21)、[卷244](https://zh.wikisource.org/zh-hans/明史/卷244) | 申时行离职先于1601册储；方从哲长期缺阁员；光宗罢矿税发帑在正式登基前；在位补阁、蠲灾、恤刑；红丸不写成毒杀定案 |
| 天启、崇祯 | [卷305](https://zh.wikisource.org/zh-hans/明史/卷305)、[卷250](https://zh.wikisource.org/zh-hans/明史/卷250)、[卷259](https://zh.wikisource.org/zh-hans/明史/卷259)、[卷309](https://zh.wikisource.org/zh-hans/明史/卷309) | 杨涟1624弹劾和1625诏狱分开；宁远工程与守城分开；孙承宗高阳死于崇祯朝；袁崇焕责任不只归反间；李自成死因不定论 |
| 科学交流 | [徐光启本传](https://zh.wikisource.org/wiki/明史/卷251)、[中科院科学史研究所徐光启](https://agri-history.ihns.ac.cn/agriculturists/xgq.htm)、[故宫利玛窦](https://www.dpm.org.cn/lemmas/240156.html) | 1607前六卷不是全译；农书身后整理刊行；1629改历与后续团队接续；进献物品不说成见皇帝 |

## 明确时间边界

- 隆庆覆盖排除 `v26_zhang_chief`，成为首辅是在穆宗死后。
- `v26_zhang_death` 收束为1582–1584万历处分；新 `v40m2_zhang_restore_1622` 归天启。chapterLinks 尝试为原天启章节删除旧链接并换新；若基线天启正文无该events字段则主工程检查专题入口即可。
- 泰昌覆盖只两项：新 `v40m2_taichang_governance_1620`（即位后补阁蠲灾恤刑）、旧 `v2l_redpill`。旧 `v2l_taichang` 更新说明但不进入严格在位表；立储、梃击和移宫均排除。
- 天启覆盖排除 `v2l_yigong`（正式登极前）。事件仍保留人物生平关联和文章入口。
- `v40m2_mining_protests_1599` 用1599–1601范围而不填武昌/苏州具体月份：卷21校勘提示武昌1599/1600、苏州五月/六月差异。
- 海瑞应天田讼1569–1570范围与本传隆庆三年夏上任、约半年去职相容。

## 事实、评价与空白

- 正史本传含立场鲜明的标签和奏疏控诉；长读明确区分，未采用神异出生、猎奇酷刑、杀人食尸等叙事。
- 本轮19篇人物以概览+三层主题介绍，未新增未核实肖像、家族数据、生卒推算。Person 的 note 简述角色，不伪造年表。
- remainingGaps列每帝仍可补人物：刘大夏/王恕、杨一清/江彬、胡宗宪/俞大猷、王崇古/谭纶、李如松/李贽/汤显祖、熊廷弼/左光斗、杨嗣昌/孙传庭/宋应星等。并非宣称本轮已经穷尽。

## 自检

生成脚本 `/private/tmp/build_ming_late_v40.py` 已运行通过：所有人物事件来源引用存在，所有长读500–800汉字，8帝各有2–6当朝人物，严格在位事件分别6/4/6/5/13/2/7/7。
