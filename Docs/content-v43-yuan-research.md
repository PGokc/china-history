# 史迹 v0.43 元代包：研究、边界与验证

封包日期：2026-09-20（亚洲/上海）。本包仅写入 /private/tmp，未修改仓库文件，未下载肖像或器物照片。

## 交付与数量

- 数据包：`/private/tmp/shiji-v43-yuan.json`
- 构造脚本：`/private/tmp/build-v43-yuan.py`（父任务无需运行；交付JSON已完整）
- 验证脚本：`/private/tmp/validate-v43-yuan.py`
- 验证结果：`/private/tmp/shiji-v43-yuan-validation.json`

JSON按原有Person / Article / ArticleSection / HistoryEvent / Association / FamilyLink / Succession / ReignContext / Artifact / Tomb模式组织。Person增加可选dynasty="yuan"，其余字段沿用schema。dynastyProfileUpdates含元代总览替换项。人物ID全为y_；其他条目为v43y_；sequence特按要求为y_0至y_11。

| 数组 | 条数 |
|---|---:|
| people | 33 |
| sources | 48 |
| articles | 33 |
| events | 50 |
| associations | 33 |
| familyLinks | 19 |
| sequence | 12 |
| reignContexts | 11 |
| objects | 8 |
| tombs | 0 |
| dynastyProfileUpdates | 1 |

事件分类：政治17项、军事8项、经济7项、社会7项、文化11项。

## 必须保留的时间及关系边界

1. 元朝实际帝序为11个人、12段：忽必烈、铁穆耳、海山、爱育黎拔力八达、硕德八剌、也孙铁木儿、阿速吉八、图帖睦尔首次、和世㻋、图帖睦尔复位、懿璘质班、妥懽帖睦尔。文宗不是两个人，且1329年两段之间有明宗在位，不能合成不中断的1328—1332。
2. 1328年上都阿速吉八与大都图帖睦尔是并列争位。帝序排列不是先退位再继位。两都之战事件给出peopleRoles；两人的Association明确是对手。
3. 阿速吉八的context只有一位确证本方辅臣倒剌沙，第二个时代关系人物为敌对文宗。note明确不称文宗为其臣子；这是极短在位例外，不为凑满两名臣僚虚构传记。其死后去向和墓址均无确定断言。
4. 明宗context为文宗（当时让位而居储位的弟弟）与燕铁木儿（迎接、玺绶、中枢集团）。其两项核心事件只有即位、南行死亡及文宗复位，没有虚构改革。
5. 宁宗context为卜答失里、燕铁木儿、蔑儿乞部伯颜；两项事件为即位及朝廷赦免、早逝及后继讨论。至顺沿用，史载七岁为虚岁；诏令不归为儿童个人设计。
6. 忽必烈1260即汗位、1271定国号、1279南宋终结分别处理。其元朝context从1271起；1260即位、1269新字列为前置人生背景。
7. 妥懽帖睦尔1333—1368为本包元朝context，1368—1370北元续统在人物与文章说明，未把1370硬计入元朝在中原统治。燕铁木儿1333年正式即位前已死，不进入顺帝当朝人物列表。
8. 铁木真、窝阔台、贵由、蒙哥kind均为“蒙古大汗”，不进入元朝sequence。拖雷、真金、答剌麻八剌、甘麻剌为宗室辅助人物，追尊庙号不等于实际在位。
9. 父系闭合：铁木真→拖雷→忽必烈→真金；真金之子甘麻剌、答剌麻八剌、铁穆耳；答剌麻八剌→武宗与仁宗；武宗→明宗与文宗；仁宗→英宗；甘麻剌→泰定帝→天顺帝；明宗→顺帝与宁宗。人物parent与father链接完全一致。
10. 八邻部伯颜y_bayan（1236—1295）与蔑儿乞部伯颜y_late_bayan（1280—1340）严格分开。拜住为安童之孙，与后妃传同名宦者不合并。脱脱为蔑儿乞部丞相，与康里脱脱不合并。

## 联网方法与证据

已加载 `/Users/huangxianchao/.agents/skills/web-access/SKILL.md`。按要求执行check-deps，Node v22可用但Chrome CDP未连接。本任务为公开原文研究，依skill的工具选择表改用公开网页搜索发现来源及open读取正文，没有声称使用了CDP或登录浏览器。仓库文件受FileProvider读取超时影响，改用git show读取History.swift与history.json，临时样例shiji-v42-qing.json已不存在；父任务另提供schema快照。

主要采用明初官修《元史》的本纪、传、志原文（维基文库转录），并以已读取的机构藏品说明、考古研究与国博资料补足文化实物。仅作为找到原文入口的百科和搜索摘要没有作为人物核心证据。

关键读取与核查：

- 卷1—4：前四汗、拖雷家族、1251继承、1259死亡、1260开平即位。
- 卷7及《建国号诏》全文：1271国号大元与乾元释义；与1260年分开。
- 卷10、11、127：南宋最后阶段、元军南征及战争之后接收问题。
- 卷18、21—30：成宗至泰定帝本纪，1303地震、1307兄弟迎立、至大财政、延祐取士、南坡政变及泰定灾荒。
- 卷31—34、37—38：明宗、文宗、宁宗、顺帝早年；两都之战、让位与复位、明宗死因政治指控、宁宗赦免原文、顺帝延迟登极。
- 卷40—43、47及卷138：顺帝权臣政治、1343—1345三史、1351河工与起义、1354高邮罢帅、1368北行。
- 卷81、93—94：元代多途径入仕、分类考试要求及名额、税粮、钞法、海运和经界。没有把“四等人”写成一套包办所有法律和日常关系的整齐统一阶梯。
- 卷114、115、136、138、146、157、164、172、202：后妃、追尊宗室、拜住、燕铁木儿、两位伯颜、脱脱、耶律楚材、刘秉忠、郭守敬、赵孟頫、八思巴的本传互校。
- 故宫《农书》正文：明确其所介绍的是1776年辑印本，著作时代与藏品版本分开。木活字1298与农书约1313成书分开。
- 故宫赵孟頫人物及《为中庭老书七绝卷》正文：作品材质、署款、后世题跋；未编造准确作年和御用经历。原拟千字文条目间歇读取失败，最终改用成功读取的中庭卷，未保留失效引用。
- 故宫青花鱼莲纹罐正文：文物号资陶瓷00010774，元代断代，高31厘米；未强配皇帝、年款或出土地点。
- 国博“关汉卿与元曲”正文：生卒与籍贯异说、作品与杂剧意义。独立时代事件drama明确约略创作期，未把1323法制或1315科举误写成其在世经历。
- 魏坚《草原文化与元上都考古》：本人参与考古的研究说明，区分皇家祭祀场所、陵寝推定方向与个体帝陵。统一展柜专题区分文献葬地与具体帝陵，不把任何纪念性造像当本人墓址。

《元史》带有追尊、正统、灾异与胜方评价，原文存在校勘，人物动机与私生活逸闻不作为已证事实铺陈。明宗死亡只确认时间链与后续谋害指控，不编造毒物、凶手对话；阿速吉八败后结局保留缺证；铁木真、关汉卿、王祯等生年或生卒争议明示。

## 长读与引用质量

33个人全部有长读。每篇至少3节，每节具kind、sources、people、events，引用全部闭合；章节people与events是相关阅读链接，跨代后果在正文明确，不意味着人物在场。4篇核心长读以纯汉字正则统计也达到1200；其他元帝均达到650；前史、文化人物、辅臣与辅助宗室均达到500。

| 人物ID | 纯汉字数 |
|---|---:|
| y_kublai | 1340 |
| y_temur | 1261 |
| y_ayurbarwada | 1287 |
| y_toghon_temur | 1272 |
| y_kulug | 676 |
| y_gegeen | 722 |
| y_yesun_temur | 731 |
| y_ragibagh | 697 |
| y_tugh_temur | 707 |
| y_kusala | 711 |
| y_rinchinbal | 703 |
| y_genghis | 530 |
| y_ogedei | 568 |
| y_guyuk | 561 |
| y_mongke | 542 |
| y_tolui | 576 |
| y_zhenjin | 584 |
| y_darmabala | 596 |
| y_gammala | 573 |
| y_yelu_chucai | 575 |
| y_liu_bingzhong | 547 |
| y_phagpa | 541 |
| y_guo_shoujing | 539 |
| y_zhao_mengfu | 625 |
| y_guan_hanqing | 552 |
| y_bayan | 540 |
| y_toghto | 515 |
| y_baizhu | 538 |
| y_daolasha | 555 |
| y_yan_tiemuer | 554 |
| y_budashiri | 519 |
| y_late_bayan | 556 |
| y_wang_zhen | 555 |

## 校验结果与工程提示

- 全部source / people / event引用存在；数组ID无重复，文章覆盖33/33。
- parent与father FamilyLink逐一一致，配偶链接不当作父链。
- 每帝context至少2条确证事件和2个政治语境人物；天顺帝的对手关系例外见前述说明。
- context关联事件均包含该皇帝people ID，满足原HistoryStore.reignEvents筛选机制；人物出现在时代文化事件中时用peopleRoles说明其仅为在位背景，避免误归创作。
- context事件年份与整数年periods相交；文宗中断及两都重叠必须同时尊重period.label/note，不把整数年过滤当成精确日界。
- 8项objects均有明确dynasties=["yuan"]、note与来源。实物不下载图片，缺image为正常可选字段。
- 按父任务编辑审查，删除了11条内容重复且未定位的个人陵寝卡。最终tombs为空数组；新增一个实质展柜专题“元代帝陵与起辇谷”，只关联有具体本纪支持的宁宗，并在宁宗note注明葬起辇谷的史载。该专题明确区分皇家祭祀遗址、文献中的祖茔方向、具体墓穴与后世纪念场所。
- dynastyProfileUpdates按id替换元朝总览，其余数组追加。不要把4位前史大汗或4位追尊宗室加入sequence。
- 该子任务未执行Swift构建与UI测试，交由父任务集成验证。

## 来源清单（数据包内同ID）

- `v43y_ys001` [《元史》卷1 · 太祖本纪](https://zh.wikisource.org/wiki/元史/卷001)
- `v43y_ys002` [《元史》卷2 · 太宗、定宗本纪](https://zh.wikisource.org/wiki/元史/卷002)
- `v43y_ys003` [《元史》卷3 · 宪宗本纪](https://zh.wikisource.org/wiki/元史/卷003)
- `v43y_ys004` [《元史》卷4 · 世祖本纪一](https://zh.wikisource.org/wiki/元史/卷004)
- `v43y_ys011` [《元史》卷11 · 世祖本纪八](https://zh.wikisource.org/wiki/元史/卷011)
- `v43y_ys018` [《元史》卷18 · 成宗本纪一](https://zh.wikisource.org/wiki/元史/卷018)
- `v43y_ys021` [《元史》卷21 · 成宗本纪四](https://zh.wikisource.org/wiki/元史/卷021)
- `v43y_ys022` [《元史》卷22 · 武宗本纪一](https://zh.wikisource.org/wiki/元史/卷022)
- `v43y_ys023` [《元史》卷23 · 武宗本纪二](https://zh.wikisource.org/wiki/元史/卷023)
- `v43y_ys024` [《元史》卷24 · 仁宗本纪一](https://zh.wikisource.org/wiki/元史/卷024)
- `v43y_ys026` [《元史》卷26 · 仁宗本纪三](https://zh.wikisource.org/wiki/元史/卷026)
- `v43y_ys027` [《元史》卷27 · 英宗本纪一](https://zh.wikisource.org/wiki/元史/卷027)
- `v43y_ys028` [《元史》卷28 · 英宗本纪二](https://zh.wikisource.org/wiki/元史/卷028)
- `v43y_ys029` [《元史》卷29 · 泰定帝本纪一](https://zh.wikisource.org/wiki/元史/卷029)
- `v43y_ys030` [《元史》卷30 · 泰定帝本纪二](https://zh.wikisource.org/wiki/元史/卷030)
- `v43y_ys031` [《元史》卷31 · 明宗本纪](https://zh.wikisource.org/wiki/元史/卷031)
- `v43y_ys032` [《元史》卷32 · 文宗本纪一](https://zh.wikisource.org/wiki/元史/卷032)
- `v43y_ys033` [《元史》卷33 · 文宗本纪二](https://zh.wikisource.org/wiki/元史/卷033)
- `v43y_ys034` [《元史》卷34 · 文宗本纪三](https://zh.wikisource.org/wiki/元史/卷034)
- `v43y_ys037` [《元史》卷37 · 宁宗本纪](https://zh.wikisource.org/wiki/元史/卷037)
- `v43y_ys038` [《元史》卷38 · 顺帝本纪一](https://zh.wikisource.org/wiki/元史/卷038)
- `v43y_ys040` [《元史》卷40 · 顺帝本纪三](https://zh.wikisource.org/wiki/元史/卷040)
- `v43y_ys041` [《元史》卷41 · 顺帝本纪四](https://zh.wikisource.org/wiki/元史/卷041)
- `v43y_ys042` [《元史》卷42 · 顺帝本纪五](https://zh.wikisource.org/wiki/元史/卷042)
- `v43y_ys047` [《元史》卷47 · 顺帝本纪十](https://zh.wikisource.org/wiki/元史/卷047)
- `v43y_ys081` [《元史》卷81 · 选举志](https://zh.wikisource.org/wiki/元史/卷081)
- `v43y_ys093` [《元史》卷93 · 食货志一](https://zh.wikisource.org/wiki/元史/卷093)
- `v43y_ys094` [《元史》卷94 · 食货志二](https://zh.wikisource.org/wiki/元史/卷094)
- `v43y_ys114` [《元史》卷114 · 后妃传](https://zh.wikisource.org/wiki/元史/卷114)
- `v43y_ys115` [《元史》卷115 · 睿宗、裕宗、显宗、顺宗传](https://zh.wikisource.org/wiki/元史/卷115)
- `v43y_ys127` [《元史》卷127 · 伯颜传](https://zh.wikisource.org/wiki/元史/卷127)
- `v43y_ys136` [《元史》卷136 · 哈剌哈孙、拜住等传](https://zh.wikisource.org/wiki/元史/卷136)
- `v43y_ys138` [《元史》卷138 · 燕铁木儿、伯颜、脱脱等传](https://zh.wikisource.org/wiki/元史/卷138)
- `v43y_ys146` [《元史》卷146 · 耶律楚材传](https://zh.wikisource.org/wiki/元史/卷146)
- `v43y_ys157` [《元史》卷157 · 刘秉忠等传](https://zh.wikisource.org/wiki/元史/卷157)
- `v43y_ys164` [《元史》卷164 · 郭守敬等传](https://zh.wikisource.org/wiki/元史/卷164)
- `v43y_ys172` [《元史》卷172 · 赵孟頫等传](https://zh.wikisource.org/wiki/元史/卷172)
- `v43y_ys202` [《元史》卷202 · 释老传](https://zh.wikisource.org/wiki/元史/卷202)
- `v43y_guan` [中国国家博物馆 · 关汉卿与元曲](https://en.chnmuseum.cn/Portals/0/web/exhibition/exhibitions/161120Chines-Epic/)
- `v43y_zhao` [故宫博物院 · 赵孟頫](https://www.dpm.org.cn/lemmas/240325.html)
- `v43y_nongshu` [故宫博物院 · 《农书》](https://www.dpm.org.cn/ancient/hall/151496.html)
- `v43y_ys007` [《元史》卷7 · 世祖本纪四](https://zh.wikisource.org/wiki/元史/卷007)
- `v43y_ys010` [《元史》卷10 · 世祖本纪七](https://zh.wikisource.org/wiki/元史/卷010)
- `v43y_ys043` [《元史》卷43 · 顺帝本纪六](https://zh.wikisource.org/wiki/元史/卷043)
- `v43y_edict` [《建国号诏》](https://zh.wikisource.org/zh-hant/建國號詔)
- `v43y_ceramic` [故宫博物院 · 青花鱼莲纹罐](https://www.dpm.org.cn/collection/ceramic/227866.html)
- `v43y_zhongting` [故宫博物院 · 赵孟頫行书为中庭老书七绝卷](https://www.dpm.org.cn/subject_zhaomengfu/achievement/245813.html)
- `v43y_shangdu_archaeology` [魏坚 · 草原文化与元上都考古（中国社会科学网）](https://www.cssn.cn/lsx/lsx_kgx/202210/t20221024_5552655.shtml)

JSON SHA-256：`63037a6a6f8e9d2000422b570e2455a4664de8678cb633bb5e3ebacdde897da2`

最终验证：errors=[]；纯汉字合计22348字。父亲链接再核对与Person.parent一致。

## 最终文风与专题复核

- 本次直接修订封包 JSON，清除文章、人物注记、来源说明、事件影响、人物关系、在位语境和朝代总览中的页面制作与写作指导口吻，史料争议改为直接说明确证范围。
- 阿速吉八仍保留1328年并立争位及败后去向无确证；和世㻋仍保留死因疑问；宁宗诏令归于皇太后与大臣主持的幼帝朝廷。
- 8项专题均为3段，分别说明背景、具体内容及影响或证据边界。7项旧专题由短卡补为实质介绍，未增加专题范围。
- 再次打开核读故宫《农书》、赵孟頫人物说明、为中庭老书七绝卷、青花鱼莲纹罐，以及《元史》卷202、卷28正文。未下载图片，未加入未经馆方支持的御用、确切年款或墓穴坐标。
- 旧 build-v43-yuan.py 保留了修订前文字，不再用于重新生成；最终以本 JSON 与此处 SHA-256 为准。

| 专题 ID | 正文纯汉字 | 段落数 |
|---|---:|---:|
| v43y_phagpa_letters | 232 | 3 |
| v43y_shoushi_calendar | 227 | 3 |
| v43y_nongshu_book | 227 | 3 |
| v43y_tongzhi_book | 234 | 3 |
| v43y_zhongting_scroll | 232 | 3 |
| v43y_fish_jar | 237 | 3 |
| v43y_calligraphy_idea | 257 | 3 |
| v43y_yuan_burial | 268 | 3 |

封包复核：errors=[]；编辑指令扫描命中0；33篇正文合计22348汉字，核心四帝均≥1200，其余帝均≥650，其他人物均≥500。

## 集成复核

全局内容校验补上4条已在正文和上下文中确立但缺少独立关系记录的连接：成宗—王祯、仁宗—王祯、成宗—海山、文宗—卜答失里。王祯两条明确为同时代关系，不推定皇帝直接参与技术或著述。海山按北边统军宗王及皇侄标示，卜答失里按皇后标示。

另移除没有人物或章节入口的青花瓷重复事件v43y_craft；相关实物与来源已完整保留在青花鱼莲纹罐专题。最终并入49项元代事件，不靠不可见记录增加数量。
