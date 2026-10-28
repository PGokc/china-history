#!/usr/bin/env python3
"""Rewrite the last five Western Xia ruler readings and their late-state events."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "App/Resources/history.json"


COMMON_SOURCES = [
    "v55_xixia",
    "v55_songshi",
    "v55_jinshi",
    "v43y_ys001",
    "v55_kaogu",
    "v125_cssn_xixia_documents",
]


READINGS = {
    "s_xia_huanzong": {
        "titles": ["十七岁继承的不是一个空壳", "《德行集》与后期政治文化", "1205年以后出现新的北方压力", "边贸和地方社会仍在运行", "被废不是亡国的同义词"],
        "texts": [
            "李纯祐1193年继承仁宗留下的皇位时约十七岁。此前五十四年的稳定交接、法典、学校、寺院和多语文书体系仍在运行，西夏也继续维持与金朝的册封往来及同宋朝的边境贸易。年轻皇帝面对的并非等待拯救的空壳，而是一套能够征税、调兵、传递公文并经营河西城市的国家机器。长期和平并未消除宗室竞争、地方军力和北方草原格局变化，继承顺利也不保证此后权力始终稳固。",
            "中国社会科学网介绍的西夏文献显示，桓宗初年命大臣总结古今治乱，番大学院教授曹道乐编成《德行集》，按修身、从谏、知人、用人、立政等门类组织历史经验。这说明后期宫廷并非只会应付战事，历史知识也被用于皇帝教育和施政讨论。但一部劝诫读物能证明政治文化的目标，不能直接证明皇帝逐条采纳，更不能据此推导全国治理成效。书名、编纂者和用途应与后世对桓宗的道德评价分开。",
            "1205年前后，蒙古军开始进入西夏西北与河西相关区域，北部堡寨、牧地和交通线承受新压力。此次行动的规模、路线和直接目标在不同后出材料中并不完全一致，稳妥的结论是：西夏此前主要在宋、辽、金之间安排外交，如今必须面对一个尚未定型却迅速扩张的草原力量。战争不应倒写成1227年灭亡的预演；桓宗朝仍能修复城堡、组织防务，但每次动员都会消耗牲畜、粮运和边地家庭。",
            "桓宗时期的宋夏互市、贡赐与河西交通继续为城市提供茶、布帛和其他物资，西夏也输出马匹、盐及地方产品。武威一带墓葬、文书和宗教遗存反映官员、军人、僧侣、商人与工匠并存，而不是只有皇室和战场。官方记录偏重禁令、使节与额度，难以覆盖民间交换；考古发现又集中于少数地点。不能因为蒙古压力已出现就把1190年代社会写成全面崩溃，也不能由精品遗物推出所有居民生活富足。",
            "1206年，宗室李安全在宫廷政变中废黜李纯祐，桓宗不久去世。现存材料对政变参与者、死亡过程和责任的记述并不完全一致，因此页面保留可核的废立结果，不补写密室情节。桓宗被废说明宗室和宫廷联盟足以改变帝位，却不等于国家在这一年灭亡；官僚、军队和城市体系转入新皇帝名下继续运作。理解其十四年统治，应分开文化建设、边贸延续、蒙古初次压力与最后的权力翻转。",
        ],
        "events": ["v55_reign_s_xia_huanzong_a", "v128_xixia_dexingji", "v128_xixia_1205_conflict", "v100s_xia_huanzong_economy", "v55_reign_s_xia_huanzong_b"],
        "people": ["s_xia_renzong", "s_xia_xiangzong", "s_xia_luoshichang"],
        "sources": [*COMMON_SOURCES, "v128_cssn_xixia_historiography", "v128_nxkg_chunyou"],
    },
    "s_xia_xiangzong": {
        "titles": ["政变取得的皇位", "1209年围城与屈服", "为什么转而同金朝交战", "战争成本落在谁身上", "五年统治怎样结束"],
        "texts": [
            "李安全是西夏宗室，1206年通过废黜桓宗取得皇位。政变使他迅速掌握帝号，却没有改变金朝册封、宗室合法性、军队支持和地方财政仍需重新确认的事实。后世常以“篡位”概括全部统治，这能说明继承方式，不能代替对其面对的外部局势和行政连续性的分析。桓宗时期的官员、驿传、州县和文书并未在政变当日消失，李安全必须接管而非重新发明这些制度。",
            "1209年蒙古军深入西夏并围逼中兴府，西夏主力和城防承受巨大压力。蒙古军因城市攻坚、河渠环境和补给等限制没有立即占领都城，李安全最终以臣服、贡纳等安排换取撤军；婚姻与人质细节在不同材料中存在差异，不应渲染为单一传奇。此次结局既不是西夏战胜蒙古，也不是政权当场被征服，而是一种不对等关系的开始，意味着此后可能承担征调、贡赋和军事协作。",
            "金朝没有按西夏期待出兵援救，夏金关系随后恶化。1210年前后西夏进攻金境，襄宗朝把旧有宗主关系转为战争，但动机不能只归结为一次报复：蒙古压力、边境利益、榷场和金朝自身危机共同作用。与蒙古暂时妥协并不表示双方拥有稳定同盟，对金开战也没有消除西夏北方威胁。把政策写成“联蒙灭金”会把后来结果提前塞进当时决策，忽略各方仍在反复试探。",
            "围城、贡纳和对金战争都需要粮食、马匹、运输与服役人口。官方史书多记录皇帝、使节和战果，普通家庭的损失只能从逃亡、市场关闭、军需和后期文书间接观察。边境人口可能在夏金双方的掠夺与迁徙中改变居所，河西城市则要维持守军和交通。战争没有让每个地区同时停摆，却会把风险不均匀地转嫁给军户、农牧家庭、商旅和被征发者；页面不以“国力衰弱”四字替代这些具体机制。",
            "1211年，宗室李遵顼再次发动废立，李安全失去皇位并在同年死亡。关于他被废后的具体处置，外部正史和后出编年材料并非无缝一致，因此可靠叙述以政权交接为界。襄宗五年统治的重要性不在个人品德标签，而在蒙古对西夏建立强制关系、夏金战争开启和宫廷政变连续发生。帝位两次由宗室强行更换，也削弱了长期政策与责任边界，使下一任继承的是已经同时承受北、东两线压力的国家。",
        ],
        "events": ["v55_reign_s_xia_xiangzong_a", "v128_xixia_1209_siege", "v128_xixia_jin_war", "v128_xixia_jin_war", "v55_reign_s_xia_xiangzong_b"],
        "people": ["s_xia_huanzong", "s_xia_shenzong", "s_jin_zhangzong"],
        "sources": [*COMMON_SOURCES, "v128_xixia_protection_plan", "v128_nxkg_chunyou"],
    },
    "s_xia_shenzong": {
        "titles": ["从宗室官员到废立者", "十三年夏金战争", "蒙古的命令不是稳定同盟", "战报之外的流亡与市场", "退位以后仍活到1226年"],
        "texts": [
            "李遵顼出自西夏宗室，后出材料称其曾通过策试进入官场，1211年废黜李安全后即位。无论考试名次如何解释，他的上升同时依靠宗室身份、官职经历和宫廷行动，不能按现代科举故事写成平民凭才学成为皇帝。政变让神宗取得皇位，也继承了襄宗对蒙古屈服、同金交战的局面。新君没有面对一张可以自由选择盟友的白纸，而是在军队、边境和旧怨已经形成后继续作决定。",
            "1210至1223年间夏金边境长期冲突，神宗朝多次进攻金境，也有金军反击。战争与通使有时并行，说明外交联系没有因敌对而完全中断；战线又分布于陕甘多处，不能想象成每年同一支军队沿一路推进。蒙古攻金为西夏提供局部机会，却也让夏军承担远距离出征和补给。把十三年战争都归为神宗个人好战，会忽略襄宗已经开战；把责任全推给蒙古命令，则抹去西夏中枢自己的边境选择。",
            "蒙古曾要求西夏提供军队和物资，西夏也在部分行动中配合攻金，但双方关系始终带有胁迫。西夏拒绝或未能满足征调时会遭报复，配合作战也不保证蒙古尊重其边界。1223年前后夏军参加对金凤翔方向的行动后撤回，正显示共同敌人没有产生平等联盟。所谓“联蒙攻金”应拆成一次次征调、出兵与撤退来读；草原统治者、西夏君臣和前线将领的目标并不完全相同。",
            "长期战争使夏金榷场、使节贸易和边地生产受到冲击，官方材料提到败卒流散、饥民迁徙与掠夺人口。数字和责难多来自交战一方，不能不经核对直接累计，但军队所需粮草、牲畜和运输必然压向地方社会。黑水城文书能展示国家对户籍、军役和物资的分类，却多不直接记录某位皇帝的战争决策。将国家衰耗落实到市场中断、人口移动和役负，比抽象说“民不聊生”更接近可核证据。",
            "1223年李遵顼退位，皇子李德旺继位；这是西夏帝序中少见的在世交接。退位的直接压力在材料中有不同解释，可确认的是他成为太上皇，而非当年死亡。1226年神宗去世，时间已进入蒙古最后一次大规模攻夏期间。将1223年写成其“在位终结”必须同1226年的生命终点分开，也不能把献宗此后三年的决策继续算在他名下。退位并未立刻解除危机，只是把停战、修复金夏关系和守卫国土的任务交给下一代。",
        ],
        "events": ["v55_reign_s_xia_shenzong_a", "v128_xixia_jin_war", "v128_xixia_mongol_coercion", "v128_xixia_war_displacement", "v55_reign_s_xia_shenzong_b"],
        "people": ["s_xia_xiangzong", "s_xia_xianzong", "s_jin_xuanzong"],
        "sources": [*COMMON_SOURCES, "v128_xixia_protection_plan", "v125_cssn_xixia_documents"],
    },
    "s_xia_xianzong": {
        "titles": ["太上皇仍在时的新君", "停止夏金消耗战", "1226年攻势为何难以抵挡", "最后三帝为什么没有陵号", "死亡与继承都发生在战时"],
        "texts": [
            "李德旺1223年接受父亲李遵顼退位后即位，最初仍与在世的太上皇处于同一政治结构。新旧君主的权力如何分配，现存材料不足以逐日还原，因此不能把所有政策自动归给一人。献宗接手的是经过多年夏金战争、蒙古征调和边贸受损的国家，但中枢、城市、军队与文书制度仍然存在。三年统治虽短，重点不是寻找一项扭转国运的妙计，而是观察可选择空间如何被前期战争压缩。",
            "献宗朝试图结束对金的长期战争并恢复共同应对蒙古的关系。停战能减少东线消耗，却无法立即补回兵员、牲畜、粮储和互市网络，也不能保证金朝有足够力量援助西夏。金同样在蒙古压力下收缩，双方从敌对转向合作是现实调整，而不是旧宗主关系完整恢复。页面将这一转向写成有限止损：它改变外交方向，却发生得太晚，且此前十三年的冲突已经在边境留下长期成本。",
            "1226年蒙古军从西部与河西方向推进，西夏多座城镇、交通线和防御节点先后失守，中兴府逐渐孤立。不同材料对具体城池次序、抵抗过程和伤亡数字并不完全一致，产品不把后出的完整战役表当作无误军报。可以确认的是，蒙古此次目标已从惩罚和征调转为摧毁西夏政权；河西走廊的纵深被压缩后，都城难以持续获得外援。防线崩解是连续过程，不是某位皇帝一次命令造成。",
            "宁夏公布的西夏陵保护规划指出，陵区九座帝陵止于襄宗，最后三位皇帝未及营建陵园。这个结论把政治危机落实到物质时间：神宗死于战争期，献宗和末帝更没有长期组织大型陵寝的条件。没有陵号或已确认陵墓，不等于这些人物不存在，也不能随意把未定名遗址分配给他们。陵区保存的是早期王朝长期营建成果；末期历史更多依赖外部正史、后出编年和战争遗址，证据结构已经改变。",
            "1226年夏，李德旺在蒙古大军压境时去世，确切病情和临终决策缺少同等可靠的内部记录。宗室李睍随后继位，西夏进入最后一年。《金史》还直言继立者姓名在其材料系统中失载，说明不同史籍保存并不整齐。献宗的死亡不应视为其抵抗失败后的道德结局，也不能把末帝时期的围城和投降倒接给他。可靠叙事应把外交修复、蒙古总攻、陵寝中断和战时继承分别列明。",
        ],
        "events": ["v55_reign_s_xia_xianzong_a", "v128_xixia_jin_reconciliation", "v128_xixia_final_campaign", "v128_xixia_last_tombs", "v55_reign_s_xia_xianzong_b"],
        "people": ["s_xia_shenzong", "s_xia_mozhu", "s_jin_xuanzong"],
        "sources": [*COMMON_SOURCES, "v128_xixia_protection_plan", "v63_xixia_ningxia"],
    },
    "s_xia_mozhu": {
        "titles": ["史书连姓名都没有同样保存", "中兴府被围的一年", "投降、死亡与材料分歧", "王朝结束不等于人口消失", "如何书写1227年"],
        "texts": [
            "李睍在1226年献宗去世后继位，通常称西夏末帝。关于他的姓名、宗室关系和年号，主要依靠不同传统的后出材料互补；《金史·西夏传》甚至只说继立者姓名失载。这个空缺提醒我们，末代皇帝并非史料天然最丰富的人物。页面采用学界常用姓名，同时明确它不是所有同时代记录共同保存的结果。继位时河西防线已大幅收缩，皇帝能够调动的资源远少于帝号所暗示的完整权力。",
            "1226至1227年，蒙古军继续围逼中兴府，并控制周边交通和救援空间。都城防御依赖城墙、粮储、河渠、守军和居民共同维持，围城造成的饥饿、疾病与人口损失却难以获得精确统计。后世叙述有时把灾异、战斗和成吉思汗死亡压成一条戏剧性时间线，不同来源的月份与因果并不完全一致。可以确认的是长期孤立使西夏中枢失去继续抵抗条件，而非一场瞬间“城破”概括全部过程。",
            "1227年西夏向蒙古军投降，政权终结，李睍随后死亡。关于成吉思汗去世消息是否隐瞒、末帝是否亲自会见、王室具体在何时被处置，各材料存在差异，不能拼成唯一确定的现场报道。产品将可核的投降、政权终结和皇帝死亡分开陈述，不用传说填补日程。对屠杀和伤亡规模也保持同样原则：战争破坏确实严重，但没有可靠统计时不制造精确数字。",
            "西夏政权消失后，党项人、汉人、吐蕃人、回鹘人和其他居民并未随国号一同消失。幸存者被迁徙、编入蒙古统治体系或继续生活在河西与其他地区，西夏出身官员和家族后来仍见于元代材料。黑水城的行政、法律、宗教和私人文书保存了此前社会的多层面，也说明王朝史不能只写皇室死亡。人口去向缺少完整统计，不能把文化延续浪漫化，更不能把“灭国”误写成所有人瞬间消亡。",
            "书写1227年，需要同时承认征服暴力和证据限度。蒙古扩张、夏金多年战争、河西城镇失守与都城围困共同造成结局，不能归因于末帝一年的个人品质；但结构压力也不意味着每项决策都无关紧要。西夏没有完整官修正史传世，外部正史各有立场，近现代又因黑水城文献和考古不断修正旧说。一个可靠的末帝页面应让读者看见哪些事实明确、哪些次序仍有争议，以及国家灭亡以后人和文献怎样继续存在。",
        ],
        "events": ["v55_reign_s_xia_mozhu_a", "v128_xixia_final_siege", "v55_m10", "v55_c09", "v55_reign_s_xia_mozhu_b"],
        "people": ["s_xia_xianzong", "s_xia_luoshichang", "y_genghis"],
        "sources": [*COMMON_SOURCES, "v128_xixia_protection_plan", "v63_xixia_unesco"],
    },
}


EXTRAS = {
    "s_xia_huanzong": [
        "年号和皇帝姓名保存较清楚，具体决策过程却仍须借外部史书与西夏文材料互证。",
        "它还说明西夏知识人会主动编排中国历代经验，而非只是被动接受一种现成制度。",
        "1205年的阶段性冲突与1209年围逼都城不是同一场战役，时间与在位者不可混接。",
        "同一时期不同区域可能一面备战、一面贸易，政治边界不等于社会联系完全中断。",
        "他的庄陵归属有陵号传统与陵区研究支持，仍需同未定名遗址的具体考古判断区分。",
    ],
    "s_xia_xiangzong": [
        "宫廷废立与边疆治理之间存在时间差，地方官员往往先延续原有征收和防务。",
        "蒙古撤军也有自身补给与战略考虑，不能把所有结果都解释为襄宗的谈判能力。",
        "金朝材料会强调西夏背盟，西夏内部决策记录不足，双方话语必须相互校正。",
        "征调还会改变耕作季节和牲畜存量，这些影响通常不会进入以战果为中心的本纪。",
        "因此，襄宗朝既是外交转折，也是继承秩序连续失稳的一段，二者相互放大风险。",
    ],
    "s_xia_shenzong": [
        "所谓策试经历能说明文官教育背景，却不足以证明其后来每项军事政策更为理性。",
        "战报中的获胜与失地必须放回长期消耗中比较，单次战果不能代表国家净收益。",
        "蒙古方面的记录突出征服秩序，金史突出边境受损，西夏自身声音则保存零散。",
        "制度文书记录国家希望怎样管理人口，逃亡和规避恰好提示实际执行并不整齐。",
        "这一区分也避免将神宗、献宗和末帝三人的在位年份压缩成一个含糊的亡国阶段。",
    ],
    "s_xia_xianzong": [
        "太上皇存在也说明退位不是国家权力完全更新，旧有官员与关系网络仍可能延续。",
        "共同威胁能够促成和解，却不能自动恢复已被破坏的军需、互信和边防协调。",
        "城镇失守后的居民去向各异，现有资料不足以为每一座城市给出完整人口结局。",
        "规划文本解决的是陵区整体沿革，不会替代每一处遗址的发掘报告和年代判断。",
        "《金史》的坦率缺载本身也是证据：正史并不总能替战败政权保存完整帝王名录。",
    ],
    "s_xia_mozhu": [
        "对同一名字的不同写法也要保留释读余地，不能反过来虚构一套完整宫廷档案。",
        "围城中的日常经验几乎没有当事人连续叙述，证据沉默应当被看见而非被小说填满。",
        "成吉思汗之死与西夏投降接近发生，但事件接近不等于所有文献都同意其先后因果。",
        "语言、宗教和家族记忆也以不同速度变化，文化延续不能简化为一个族群从未改变。",
        "这也是产品保留资料出处的原因：读者可以看到结论来自何种材料及其缺口所在。",
    ],
}


NEW_SOURCES = [
    {
        "id": "v128_cssn_xixia_historiography",
        "title": "中国社会科学网·西夏对中国传统史学的继承发展",
        "url": "https://www.cssn.cn/skgz/bwyc/202411/t20241107_5800370.shtml",
        "note": "依据西夏文《德行集》、历书和官署材料讨论桓宗朝政治劝诫与西夏修史传统。",
    },
    {
        "id": "v128_nxkg_chunyou",
        "title": "宁夏文物考古研究所·西夏纯祐时期夏金关系述评",
        "url": "https://www.nxkg.org.cn/xueshuyanjiu/665.html",
        "note": "结合金夏使节、边境关系与河西墓葬材料讨论桓宗时期，并明确材料来源与后期蒙古压力。",
    },
    {
        "id": "v128_xixia_protection_plan",
        "title": "宁夏回族自治区文化和旅游厅·西夏陵保护规划（2019—2035）",
        "url": "https://whhlyt.nx.gov.cn/zwgk/fdzdgknr/tzgg/202405/P020250609549636060930.pdf",
        "note": "官方保护规划概述1205—1227年蒙古攻夏、陵区沿革，并说明西夏最后三帝未及营建陵园。",
    },
]


NEW_EVENTS = [
    {
        "id": "v128_xixia_dexingji", "year": "1193年前后", "sortYear": 1193, "title": "桓宗命编《德行集》", "category": "文化", "kind": "政治文化",
        "body": "桓宗初年命番大学院教授曹道乐汇集历代治乱经验，按修身、从谏、知人、用人、立政等门类编成《德行集》。",
        "impact": "该书显示历史知识被用于皇帝教育和施政劝诫，但文本目标不能直接等同于实际政策效果。",
        "people": ["s_xia_huanzong"], "sources": ["v128_cssn_xixia_historiography", "v55_xixia"],
    },
    {
        "id": "v128_xixia_1205_conflict", "year": "1205—1206", "sortYear": 1205, "title": "蒙古初次进入西夏边境", "category": "军事", "kind": "蒙夏战争",
        "body": "蒙古势力进入西夏西北与河西相关区域，北部堡寨、牧地和交通线开始承受新压力；行动规模与路线在后出材料中仍需互校。",
        "impact": "西夏仍能修复城堡并组织防务，但既有宋金外交框架已不足以处理新的草原扩张。",
        "people": ["s_xia_huanzong", "y_genghis"], "sources": ["v43y_ys001", "v128_nxkg_chunyou", "v128_xixia_protection_plan"],
    },
    {
        "id": "v128_xixia_1209_siege", "year": "1209", "sortYear": 1209, "title": "蒙古围逼中兴府", "category": "军事", "kind": "蒙夏战争",
        "body": "蒙古军深入西夏并围逼中兴府，西夏在防御与补给压力下以臣服、贡纳等安排换取撤军。婚姻和人质细节在不同材料中并不完全一致。",
        "impact": "西夏没有在此役灭亡，却由此进入对蒙古承担贡赋与军事压力的不对等关系。",
        "people": ["s_xia_xiangzong"], "sources": ["v43y_ys001", "v55_jinshi", "v128_xixia_protection_plan"],
    },
    {
        "id": "v128_xixia_jin_war", "year": "1210—1223", "sortYear": 1210, "title": "后期夏金长期交战", "category": "军事", "kind": "夏金关系",
        "body": "西夏因蒙古压力、金朝拒援及边境利益转而攻金；襄宗开启、神宗延续的战争与通使有时并行，战线分布于陕甘多处。",
        "impact": "十三年冲突消耗兵员、粮储和边贸网络，也使夏金在蒙古总攻前更难形成有效共同防御。",
        "people": ["s_xia_xiangzong", "s_xia_shenzong", "s_jin_xuanzong"], "sources": ["v55_jinshi", "v55_xixia"],
    },
    {
        "id": "v128_xixia_mongol_coercion", "year": "1211—1223", "sortYear": 1217, "title": "蒙古征调与西夏出兵", "category": "政治", "kind": "不对等外交",
        "body": "蒙古多次要求西夏提供军队与物资，西夏曾配合攻金，也会因拒绝或未能满足征调而遭受军事压力。",
        "impact": "共同敌人没有带来平等同盟；征调、出兵和报复进一步压缩西夏独立选择空间。",
        "people": ["s_xia_shenzong"], "sources": ["v43y_ys001", "v55_jinshi", "v128_xixia_protection_plan"],
    },
    {
        "id": "v128_xixia_wartime_economy", "year": "1211—1223", "sortYear": 1218, "title": "夏金战争下的边贸与军需", "category": "经济", "kind": "战争经济",
        "body": "夏金长期交战破坏榷场与使节贸易，军队又持续征集粮食、牲畜和运输；战时通使并未完全停止，市场影响也并非各地同时发生。",
        "impact": "军事机会伴随财政和供应成本，东线消耗削弱了西夏应对蒙古压力的物质空间。",
        "people": ["s_xia_shenzong"], "sources": ["v55_jinshi", "v55_xixia", "v125_cssn_xixia_documents"],
    },
    {
        "id": "v128_xixia_war_displacement", "year": "1211—1223", "sortYear": 1219, "title": "败卒、饥民与边地迁徙", "category": "社会", "kind": "战争与人口",
        "body": "长期夏金战争造成败卒流散、饥民迁徙和人口掠夺；交战方记录的数字带有立场，仍须与地方文书和区域证据互校。",
        "impact": "国家衰耗具体表现为家庭离散、役负和生产中断，而不只是史书中的胜负与国力评价。",
        "people": ["s_xia_shenzong"], "sources": ["v55_jinshi", "v55_xixia", "v125_cssn_xixia_documents"],
    },
    {
        "id": "v128_xixia_jin_reconciliation", "year": "1223—1224", "sortYear": 1224, "title": "献宗修复夏金关系", "category": "政治", "kind": "外交转向",
        "body": "献宗即位后停止对金的长期消耗战，并尝试恢复共同应对蒙古的关系；双方此前损失和互市破坏无法立即修复。",
        "impact": "外交方向得到调整，但金夏都已处在蒙古进攻下，合作时间和实际能力十分有限。",
        "people": ["s_xia_xianzong", "s_jin_xuanzong"], "sources": ["v55_jinshi", "v55_xixia"],
    },
    {
        "id": "v128_xixia_final_campaign", "year": "1226", "sortYear": 1226, "title": "蒙古展开最后攻夏", "category": "军事", "kind": "蒙夏战争",
        "body": "蒙古军沿河西与黄河相关交通线推进，多处城镇和防御节点先后失守，中兴府逐渐失去外援。具体城池次序与伤亡数字在材料中仍需互校。",
        "impact": "此次行动从征调与惩罚转为摧毁西夏政权，连续防线崩解使都城陷入孤立。",
        "people": ["s_xia_xianzong", "s_xia_mozhu"], "sources": ["v43y_ys001", "v128_xixia_protection_plan", "v55_kaogu"],
    },
    {
        "id": "v128_xixia_last_tombs", "year": "1226—1227", "sortYear": 1226, "title": "最后三帝未及营建陵园", "category": "社会", "kind": "陵寝与战争",
        "body": "西夏陵保护规划指出九座帝陵止于襄宗，神宗、献宗和末帝身处最后战争期，未及营建陵园。",
        "impact": "陵寝中断是战争压缩国家组织时间的物质证据，也提醒读者不要把未定名遗址强配给末期皇帝。",
        "people": ["s_xia_shenzong", "s_xia_xianzong", "s_xia_mozhu"], "sources": ["v128_xixia_protection_plan", "v63_xixia_ningxia"],
    },
    {
        "id": "v128_xixia_final_siege", "year": "1226—1227", "sortYear": 1227, "title": "中兴府长期围困", "category": "社会", "kind": "城市与围城",
        "body": "蒙古军控制中兴府周边交通和救援空间，守军与居民在粮储、疾病和持续军事压力下维持都城；精确伤亡缺少可靠统计。",
        "impact": "长期孤立而非单次城破使西夏中枢失去继续抵抗条件，围城代价同时落在军队与城市居民身上。",
        "people": ["s_xia_mozhu"], "sources": ["v43y_ys001", "v128_xixia_protection_plan", "v55_kaogu"],
    },
]


ENDINGS = {
    "v55_reign_s_xia_huanzong_b": "1206年，宗室李安全发动宫廷政变，李纯祐被废并不久去世；死亡过程的细节在现存材料中并不完全一致。",
    "v55_reign_s_xia_xiangzong_b": "1211年，李遵顼再次发动宗室废立，李安全失去皇位并于同年死亡；其被废后的具体处置不宜脱离材料补写。",
    "v55_reign_s_xia_shenzong_b": "1223年，李遵顼退位并由皇子李德旺继承皇位，自己成为太上皇；他并非当年去世，而是活到1226年。",
    "v55_reign_s_xia_xianzong_b": "1226年夏，李德旺在蒙古大军压境期间去世，宗室李睍继位；确切病情和临终决策缺少同等可靠的内部记录。",
    "v55_reign_s_xia_mozhu_b": "1227年，西夏在中兴府长期围困后投降，李睍随后死亡；关于会见、消息隐瞒和王室处置的具体次序，各材料仍有分歧。",
}


def main() -> None:
    data = json.loads(PATH.read_text())
    source_ids = {source["id"] for source in data["sources"]}
    data["sources"].extend(source for source in NEW_SOURCES if source["id"] not in source_ids)

    event_ids = {event["id"] for event in data["events"]}
    data["events"].extend(event for event in NEW_EVENTS if event["id"] not in event_ids)

    # An early dynasty-wide template connected the 1227 ruler to two tenth-century
    # Liao emperors merely because they shared a broad period page. Remove that
    # false relationship and expose the historically relevant conquest instead.
    late_xia_ids = set(READINGS)
    data["associations"] = [
        association
        for association in data["associations"]
        if not (
            ({association.get("from"), association.get("to")} & late_xia_ids)
            and any((person_id or "").startswith("s_liao_") for person_id in (association.get("from"), association.get("to")))
        )
    ]
    accurate_associations = [
        {"from": "s_xia_huanzong", "to": "y_genghis", "role": "北部边境冲突中的对手", "inverse": "开始承受蒙古进攻的西夏君主", "period": "1205—1206", "note": "桓宗末期蒙古势力开始进入西夏边境；行动规模和路线仍须谨慎互校。"},
        {"from": "s_xia_xiangzong", "to": "y_genghis", "role": "围城与臣服关系中的对手", "inverse": "在1209年围城后屈服的西夏君主", "period": "1206—1211", "note": "关联来自1209年围逼中兴府及此后的不对等关系，婚姻和人质细节存在材料差异。"},
        {"from": "s_xia_shenzong", "to": "s_jin_xuanzong", "role": "夏金长期战争中的对手", "inverse": "夏金长期战争中的对手", "period": "1213—1223", "note": "神宗朝夏金交战与通使并行，两国又同时承受蒙古压力。"},
        {"from": "s_xia_xianzong", "to": "y_genghis", "role": "最后攻夏中的对手", "inverse": "1226年总攻时的西夏君主", "period": "1223—1226", "note": "献宗试图修复夏金关系，1226年蒙古总攻期间去世。"},
        {"from": "s_xia_mozhu", "to": "y_genghis", "role": "征服战争中的对手", "inverse": "西夏末期的征服对象", "period": "1226—1227", "note": "两人关联来自蒙古最后攻夏及西夏投降；是否亲自会见和具体时间次序仍有材料分歧。"},
        {"from": "s_xia_mozhu", "to": "s_jin_aizong", "role": "同受蒙古进攻的并立君主", "inverse": "同受蒙古进攻的并立君主", "period": "1226—1227", "note": "两国都面对蒙古扩张，但这一并立背景不推定两位君主有可证的私人往来。"},
    ]
    for association in accurate_associations:
        if any({item.get("from"), item.get("to")} == {association["from"], association["to"]} for item in data["associations"]):
            continue
        association["sources"] = ["v43y_ys001", "v55_jinshi", "v128_xixia_protection_plan"]
        data["associations"].append(association)

    contexts = {context["person"]: context for context in data["reignContexts"]}
    contexts["s_liao_taizu"]["people"] = [
        "s_liao_taizong", "s_liao_shulu", "s_liao_shizong", "s_liao_yelubei"
    ]
    context_updates = {
        "s_xia_huanzong": (["s_xia_renzong", "s_xia_xiangzong", "y_genghis"], ["v55_reign_s_xia_huanzong_a", "v128_xixia_dexingji", "v100s_xia_huanzong_economy", "v100s_xia_huanzong_society", "v128_xixia_1205_conflict", "v55_reign_s_xia_huanzong_b"], "仁宗长期统治后的制度仍在运行；1205年起北方蒙古压力进入西夏政治。"),
        "s_xia_xiangzong": (["s_xia_huanzong", "s_xia_shenzong", "y_genghis"], ["v55_reign_s_xia_xiangzong_a", "v100s_xia_huanzong_society", "v128_xixia_1209_siege", "v128_xixia_jin_war", "v55_reign_s_xia_xiangzong_b"], "宫廷政变继承桓宗末年的北部压力，1209年围城与夏金关系破裂又共同限定其五年统治。"),
        "s_xia_shenzong": (["s_xia_xiangzong", "s_xia_xianzong", "s_jin_xuanzong"], ["v55_reign_s_xia_shenzong_a", "v128_xixia_jin_war", "v128_xixia_mongol_coercion", "v55_c09", "v128_xixia_wartime_economy", "v128_xixia_war_displacement", "v55_reign_s_xia_shenzong_b"], "夏金长期战争与蒙古征调并存；1223年退位不等于同年去世。"),
        "s_xia_xianzong": (["s_xia_shenzong", "s_xia_mozhu", "y_genghis"], ["v55_reign_s_xia_xianzong_a", "v128_xixia_jin_reconciliation", "v128_xixia_final_campaign", "v128_xixia_last_tombs", "v55_reign_s_xia_xianzong_b"], "停止夏金消耗战后仍面对1226年蒙古总攻，选择空间已经极小。"),
        "s_xia_mozhu": (["s_xia_xianzong", "y_genghis", "s_jin_aizong"], ["v55_reign_s_xia_mozhu_a", "v128_xixia_final_siege", "v55_m10", "v55_reign_s_xia_mozhu_b"], "在河西防线崩解后继位；围城、投降和死亡的具体次序须按材料边界说明。"),
    }
    for person_id, (people_ids, event_ids, note) in context_updates.items():
        contexts[person_id]["people"] = people_ids
        contexts[person_id]["events"] = event_ids
        contexts[person_id]["sources"] = READINGS[person_id]["sources"]
        contexts[person_id]["note"] = note

    articles = {article["person"]: article for article in data["articles"]}
    for person_id, reading in READINGS.items():
        article = articles[person_id]
        article["sections"] = [
            {
                "id": f"{person_id}-v128-{index}",
                "title": title,
                "text": text + EXTRAS[person_id][index - 1],
                "kind": "史实与解读",
                "events": [reading["events"][index - 1]],
                "people": [person_id, *reading["people"]],
                "sources": reading["sources"],
            }
            for index, (title, text) in enumerate(zip(reading["titles"], reading["texts"]), start=1)
        ]
        article["sources"] = reading["sources"]

    for event in data["events"]:
        if event["id"] in ENDINGS:
            event["body"] = ENDINGS[event["id"]]
            event["impact"] = ENDINGS[event["id"]]
        if event["id"] == "v55_c09":
            event["people"] = ["s_xia_shenzong"]
            event["peopleRoles"] = {"s_xia_shenzong": "在位时期的文书传统背景"}

    data["version"] = 102
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("rewrote the last five Western Xia ruler readings")


if __name__ == "__main__":
    main()
