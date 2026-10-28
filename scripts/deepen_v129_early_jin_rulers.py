#!/usr/bin/env python3
"""Rewrite the first five Jin ruler readings with ruler-specific evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "App/Resources/history.json"


COMMON = [
    "v55_jinshi", "v55_songshi", "v55_liaoshi", "v55_kaogu",
    "v125_cssn_jin_mengan", "v125_nopss_cities",
]


READINGS = {
    "s_jin_taizu": {
        "titles": ["反辽联盟怎样变成皇帝国家", "八年战争没有在1115年结束", "猛安谋克不是一套静止制度", "1119年女真大字进入政令", "1123年的兄终弟及"],
        "texts": [
            "1114年，完颜阿骨打率女真诸部起兵反辽；次年称帝，国号金。这个转折并不是一位首领凭一次胜仗突然创造国家：辽朝东北边地长期存在贡纳、互市、征调与部族控制的矛盾，完颜部又要联合并约束不同女真群体。称帝使战争目标从反抗地方统治升级为建立独立王权，官号、军队和分配战利品的规则随之调整。后世以“金太祖”回看成功者，容易遮住1115年时辽朝仍拥有五京体系、金朝前途并未确定的事实。",
            "1115年建国以后，阿骨打仍须争夺黄龙府等交通和军事节点，并在护步答冈等战事中削弱辽军。辽天祚帝的统治不是在金朝立国当日立即结束，辽朝残余力量、契丹地方集团和后来西迁的耶律大石也不能全部写成阿骨打一朝已经解决。金军由东北向西南推进，依靠骑兵机动、降附者情报和对辽军组织失灵的利用；胜利同时带来俘虏、人口与土地如何编管的新问题。八年统治应看成持续扩张中的建制，而非完成版疆域。",
            "猛安谋克原与女真军队、亲族和基层组织相连，金初扩张时兼有征兵、统属和人口登记功能。它并非从1115年起就在所有地区按同一格式运行，更不能把熙宗、海陵王时期的大规模内迁与土地配置全部倒写成阿骨打的完整设计。进入辽地以后，女真人、契丹人、汉人及其他群体仍通过不同官员和旧有地方网络治理。制度的关键在于国家能借层级组织迅速动员，但实际户数、地域和经济责任会随征服推进而改变。",
            "《金史》把1119年创制女真大字同完颜希尹联系起来，说明阿骨打已经意识到政令、外交和档案不能只依赖口头传递。女真文字借鉴汉字、契丹文字经验，却服务于女真语的书写；此后小字、汉字和契丹文字仍长期并用。今天保存较多的女真文碑刻多属后世，尤其不能拿1185年的得胜陀颂碑直接证明太祖朝每项制度细节。文字创制能显示国家建设方向，是否普及到基层、哪些文书由谁书写，则受材料存世限制。",
            "1123年阿骨打在继续攻辽、处理燕京等问题期间去世，继位者不是其子，而是弟弟完颜吴乞买，即金太宗。兄终弟及同女真贵族共议传统、开国功臣力量和战争时期的现实有关，不能用后来稳定的父子继承模式倒推。太祖诸子和宗室仍掌握军队与重要职务，继承安排也没有消除下一代的权力竞争。阿骨打留下的是一个扩张迅速、制度正在成形的国家；灭辽、攻宋与征服区治理的大部分艰难选择实际落到太宗朝。",
        ],
        "events": ["v55_p06", "v129_jin_taizu_war", "v55_e06", "v129_jin_1119_script", "v55_reign_s_jin_taizu_b"],
        "people": ["s_jin_taizong", "s_jin_wanyanxiyin", "s_liao_tianzuo"],
        "sources": [*COMMON, "v129_cssn_jin_victory_stele", "v129_cssn_shangjing_archaeology"],
    },
    "s_jin_taizong": {
        "titles": ["兄终弟及与勃极烈共议", "1125年俘获天祚帝以后", "海上之盟为何迅速破裂", "靖康不是两位皇帝的故事", "代理政权与1135年交接"],
        "texts": [
            "1123年，完颜吴乞买以太祖之弟身份继位。早期金廷仍有勃极烈等女真贵族共议结构，皇帝要同掌兵宗室和开国功臣共同处理军队、战利品及新征服地区，并非已拥有明清式的独断官僚体系。兄终弟及保障战争领导层的连续，也把太祖诸子下一代的继承问题留到后来。随着领土迅速进入契丹、汉人聚居区，单靠部族首领分掌事务已难支撑财政与地方行政，太宗朝因此成为旧有共议秩序开始承受帝国治理压力的阶段。",
            "1125年，金军俘获辽天祚帝，辽朝在原有核心地区的皇统终结。这个节点不等于契丹政治与人口同时消失：耶律大石此前已经西行，后来建立西辽；原辽官员、军户和地方家族也分别降金、迁徙或继续在旧地生活。太宗需要接收的不只是土地，还包括五京交通、州县、赋税和不同人群。把灭辽写成一次追俘行动会漏掉征服后的整合成本，也会让读者误以为辽金之间在1125年发生了整齐无缝的地图替换。",
            "北宋曾与金建立海上之盟，试图夹击辽朝并收回燕云地区，但双方很快围绕城地交付、岁币、降人和宋军表现发生争执。金军在1125至1127年两度南下，决策既有具体交涉破裂，也有新兴征服政权继续获取资源的动力，不能只归结为宋朝“失信”或金朝天生必然南侵。燕山府路的实际控制、地方人口与防务远比外交文书复杂。盟约从共同灭辽转成战争，说明短期目标一致并未形成稳定的政治互信。",
            "1127年开封陷落、徽钦二帝被俘，是靖康之变最醒目的皇室结局；受影响者还包括后妃宗室、官员、工匠、军人及大量被迁徙的城市居民。人口与技术向北移动，同逃亡、财物征收和北方地方秩序重组相伴。记载中的人数常带有政治立场和统计口径差异，不宜直接拼接成精确总数。把靖康只写成两个皇帝受辱，会抹掉战争如何进入家庭、职业和城市生活，也看不见南宋建立后仍长期存在的俘归、议和与边界问题。",
            "金廷先后扶立张邦昌的楚、刘豫的齐，试图以代理政权分担黄河流域治理与对宋战争成本；这些政权依赖金军，却也拥有地方官僚和自身利益，不能简单等同金朝州县。1135年太宗去世，继位的是太祖嫡孙完颜亶，即熙宗，而非太宗之子。完颜宗翰、完颜宗干等权臣支持这一安排，使兄终弟及转向太祖一系的隔代继承。交接保持王朝延续，也把功臣共治与年轻皇帝集中权力的矛盾带入下一朝。",
        ],
        "events": ["v129_jin_bojilie_transition", "v55_p07", "v55_m06", "v55_s05", "v129_jin_chu_qi"],
        "people": ["s_jin_taizu", "s_liao_tianzuo", "s_qinzong", "s_jin_xizong"],
        "sources": [*COMMON, "v129_cssn_jin_six_ministries", "v129_cssn_shangjing_archaeology"],
    },
    "s_jin_xizong": {
        "titles": ["太祖嫡孙与继承路线改变", "天眷新制不是一次汉化", "1141年和议怎样固定南北关系", "功臣政治转向皇权清洗", "1150年宫廷政变与后世名号"],
        "texts": [
            "1135年即位的完颜亶是太祖嫡孙，年纪尚轻，其继承有宗干、宗翰等宗室功臣参与安排。这次选择终止连续的兄终弟及，把皇统拉回太祖后裔，却没有立刻让功臣退出决策。熙宗接受汉文教育并熟悉礼制，不等于即位后突然放弃女真政治传统；他面对的是征服辽宋大片地区后必须统一官号、财政和命令体系的现实。理解其早年统治，要同时看年轻皇帝的合法性与开国宗室仍掌兵掌政的双重结构。",
            "1135至1138年前后，金廷逐步废除勃极烈最高共议体制，建立三省、六部等中央机构，天眷年间又调整官制与礼制。中国社会科学网的制度研究指出，这不是把唐宋制度原样搬来的一次“汉化”，而是皇权、女真贵族传统和征服区行政经验的重新组合。新官制有利于统一文书和职责，却不表示旧人脉、军权与地方差异当场消失。制度名称相近也不能证明金朝的实际运作同北宋完全一样。",
            "1141年宋金达成绍兴和议，次年完成相关交割，双方大体以淮水—大散关一线为界，并确立不平等的名分与岁贡安排。对熙宗而言，和议把多年南侵所得转化为较稳定的边界和财政收益，使中枢能把注意力转向内部统治；对南宋而言则换来长期生存空间。条约并不等于边境从此没有冲突、人口流动和贸易，也不能只用岳飞个人结局解释全部议和机制。",
            "熙宗亲政后，宗磐、宗翰一系及完颜希尹等开国重臣先后失势或被处死。传统史书常把后期政治归因于皇帝酗酒、暴虐，个人状态确是材料的一部分，但清洗同时发生在皇权从宗室共治中夺回军政控制的过程中。不同案件罪名、派系和时间并不相同，不宜统称一次阴谋。希尹后来获得平反，也说明金廷对开国功臣的评价会随权力格局变化，史书道德叙事不能替代制度分析。",
            "约在公历1150年初，完颜亮联合宫廷力量杀死熙宗并夺位。现存本纪按传统纪年记述政变，具体夜间情节主要来自胜者与后继王朝整理的材料，宜确认参与和结果而避免小说化复原。熙宗死后先被降格，海陵王被废以后又恢复庙号、谥号；今天所称“金熙宗”因此也包含后来政治追认。十五年统治的结尾显示，中央官制增强并没有自动产生安全继承，宫禁、宗室和近侍仍能改变帝位。",
        ],
        "events": ["v56_政治_06", "v129_jin_tianjuan_reform", "v43s_shaoxing", "v56_社会_06", "v55_reign_s_jin_xizong_b"],
        "people": ["s_jin_taizong", "s_jin_hailing", "s_jin_wanyanxiyin", "s_jin_zonghan"],
        "sources": [*COMMON, "v129_cssn_jin_six_ministries", "v129_cssn_jin_elites", "v107_jinshi_4"],
    },
    "s_jin_hailing": {
        "titles": ["夺位者如何集中皇权", "1153年迁都中都", "正隆官制与国家重组", "内迁猛安与土地压力", "1161年败局不只是一场采石"],
        "texts": [
            "完颜亮通过1150年的宫廷政变夺位，随后诛杀或压制可能挑战皇位的宗室，权力集中伴随严重政治暴力。后世《金史》以废帝“海陵”称之，并大量保存其荒淫残暴叙事；这些记载不能全部抹去，也不能让道德标签替代对政策的解释。他试图削弱开国宗室各自掌兵、掌地的格局，把命令、财政和官员任用进一步收归中央。夺位合法性不足与集中皇权互相推动，正是理解其迁都、改制和南征的重要背景。",
            "1153年，完颜亮把都城从上京迁到燕京，改称中都。这里更接近华北人口、税赋和南宋前线，也连接北方草原与中原交通；迁都既是地理选择，也是摆脱上京旧贵族网络的政治行动。北京考古发现的金中都城墙、护城河、马面和宫殿区遗迹，能证明城市营建规模及唐、辽城市层累，却不能把每一处建筑都直接归给皇帝本人。迁都后上京地位下降，旧都毁撤的记载也显示改革具有强制代价。",
            "正隆年间继续整并中央机构，强化尚书省和六部等行政体系，并通过官制、礼制与财政安排服务统一统治。把这一过程简称“全盘汉化”会忽略女真军事组织仍在、不同族群法律与身份并未完全一致；把它只视为南征准备，又低估迁都后长期治理需求。完颜亮希望形成由中都发出的单一权力中心，但文书制度增强并不等于地方执行毫无阻力，宗室、猛安谋克与州县之间仍存在资源竞争。",
            "熙宗后期至海陵王时期，部分女真猛安谋克人口被迁入华北，占地、授田并同州县居民杂处。研究指出，过去常见的“迁入一百三十猛安、四百万人”缺乏可靠依据，按制度和人口材料估计规模要小得多，约四十猛安仍已足以改变局部土地关系。迁徙服务于驻军和控制，也造成农牧技能、土地不足及原住民负担问题。制度不能只写成民族迁徙箭头，应看到家庭被迫移动和地方多套管理并存。",
            "1161年完颜亮大举南征，采石之战是金军渡江受挫的重要节点，却不是败局唯一原因。庞大军队的征发、舟船和补给加重内部压力，东京辽阳一带又拥立完颜雍，形成两个权力中心；前线将领和士卒在撤退与继续渡江之间冲突，完颜亮最终在扬州附近军中被杀。若只讲一场水战，就看不见后方叛离、继承合法性和军队疲惫如何共同瓦解南征。",
        ],
        "events": ["v129_jin_hailing_centralization", "v55_e07", "v129_jin_zhenglong_reform", "v129_jin_mengan_migration", "v129_jin_1161_mutiny"],
        "people": ["s_jin_xizong", "s_jin_shizong", "s_jin_zhanghao", "s_yuyunwen"],
        "sources": [*COMMON, "v129_cssn_jin_six_ministries", "v129_cssn_jin_migration", "v129_beijing_zhongdu_archaeology"],
    },
    "s_jin_shizong": {
        "titles": ["东京起兵与两位皇帝并立", "隆兴和议后的边界政治", "大定治理不等于人人丰足", "女真文字、学校与双语碑", "猛安谋克困境与“小尧舜”"],
        "texts": [
            "1161年海陵王南征期间，东京留守完颜雍在辽阳被拥立，即金世宗。即位不是宫廷内按顺序接班，而是在南征失败、契丹反抗和地方军政集团重新站队时建立另一个朝廷；海陵王尚在军中，两位皇帝一度并立。完颜雍需要争取猛安谋克、地方官和中都中枢承认，并处理前朝清洗留下的宗室恐惧。这个起点解释了他为何强调宽政与恢复秩序，也提醒“大定盛世”并非从和平继承自然展开。",
            "世宗初年宋军北伐，金宋重新交战，最终在1164至1165年前后形成隆兴和议。双方名分和岁币关系有所调整，边界大体稳定，榷场与使节往来得以延续；稳定不是彼此信任，而是两国都衡量军事成本后的制度化相处。边区仍有走私、逃人、土地和治安问题，朝廷条约不能代表居民生活从此没有摩擦。世宗朝长期和平的基础既包括军事防守，也包括贸易和外交维持的日常机制。",
            "大定年间常被概括为财政恢复、吏治整顿和轻徭劝农，较长和平确实有利于农业与城市生活。但不同地区、身份和年份的处境并不一致：自然灾害需要赈济，女真军户可能缺田贫困，普通州县居民仍承担税役。史书赞颂皇帝节俭，主要反映官方理想和同海陵朝的对比，不能直接证明每个家庭富足。评价世宗治理应同时看收入、救灾、边费和制度纠偏，而不是用“盛世”覆盖分配差异。",
            "世宗重视女真语言与教育：1164年前后推动《尚书》等典籍译成女真文，1171年设置女真进士科，1173年发展女真学校。1185年立于得胜陀的颂碑以女真文、汉文并刻，现存文字量大，记录了王朝对开国胜地的纪念。这些措施不是拒绝汉文文化，恰恰通过翻译、学校和双语碑把多种传统纳入国家秩序。碑刻能证明大定时期的纪念政治和书写水平，不等于普通女真人都已识字。",
            "世宗多次要求猛安谋克自种田地、练习骑射，反复命令本身说明军户生计、土地经营和军事能力已经出现问题。内迁以后，一些家庭依赖国家给付、出租土地或同州县经济交织，开国时军政组织不能靠怀旧保持不变。《金史》以“小尧舜”赞誉世宗，反映后世对其长期稳定的评价，也有理想化成分。1189年世宗去世，因太子早亡，由皇孙完颜璟继位；稳定交接并未消除制度积累的困难。",
        ],
        "events": ["v129_jin_1161_tokyo_accession", "v43s_longxing_treaty", "v129_jin_dading_governance", "v129_jin_dading_education", "v129_jin_mengan_livelihood"],
        "people": ["s_jin_hailing", "s_jin_zhangzong", "s_xiaozong", "s_jin_zhanghao"],
        "sources": [*COMMON, "v129_cssn_jin_victory_stele", "v129_cssn_jin_migration", "v129_beijing_zhongdu_archaeology"],
    },
}


EXTRAS = {
    "s_jin_taizu": [
        "上京一带的城址考古能说明早期中枢成长环境，但无法还原1115年称帝仪式的全部细节。",
        "因此，战役年代、辽廷反应与地方降附应分别核对，不能用后来统一结果替当时各方预知结局。",
        "同一名称下的组织会随人口、地域和任务变化，制度沿革比一张固定层级图更接近实际。",
        "创制者、受命者和后来使用者也须区分，文字史不能被简化为皇帝个人的一次发明。",
        "这次交接既延续开国集团，也为后来太祖诸孙、太宗一系与宗室功臣的竞争留下空间。",
    ],
    "s_jin_taizong": [
        "太宗的个人权威和贵族合议并非二选一，两者在战争决策与资源分配中同时存在。",
        "俘获天祚帝是辽皇统的重要终点，却不是所有契丹人的共同人生终点，更不是文化消失。",
        "宋金双方记载都倾向突出对方失约，页面因此只采用能在时序和行动上互相校验的部分。",
        "南北材料对俘虏和财物尤其容易夸张或省略，个体遭遇需要与宏观人口判断分开。",
        "楚、齐的存在还提醒读者，金宋之间一度有多层政治边界，而不是两国直接整齐对峙。",
    ],
    "s_jin_xizong": [
        "继承成功说明宗室能够达成阶段性联盟，却不表示各支力量从此接受同一权力边界。",
        "改革的日期也反映逐步推进而非一天完成，官名发布与地方落实之间仍有时间差。",
        "和议文本、实际交割与边民生活属于三个层次，不能把签约日期当成所有冲突停止之日。",
        "清洗结果可以确认，案件中的私语和动机却常由后来的审判记录或史臣评价重构。",
        "政变时间横跨传统纪年与公历换算边界，页面采用约数，避免制造不存在的日历确定性。",
    ],
    "s_jin_hailing": [
        "对海陵王的评价必须同时容纳可核的政治暴力、具体制度行动与史书编纂者的立场。",
        "城市遗址提供尺度、方位和营建层次，皇帝意图仍要同诏令、官制和迁徙记载互证。",
        "中央化能够减少权力中心数量，也可能因征调更集中而把政策风险迅速传到各地。",
        "迁入者并非只有战士，还包括家属；授田和驻防会延续到下一代，影响远超一次迁徙。",
        "采石之战应保留其战役意义，但不能让著名故事遮住东京政变和军中哗变的因果位置。",
    ],
    "s_jin_shizong": [
        "即位叙事中的“众望”多由胜利后的史书概括，具体支持者仍有地域、军职与家族差异。",
        "榷场开放程度会随外交起伏变化，因此贸易延续不等于商品、人员始终可以自由越境。",
        "政策目标、官方奏报和实际生活之间应保留距离，这也是评价传统盛世叙事的基本方法。",
        "得胜陀碑立于太祖旧战地，既纪念开国，也显示世宗如何借历史记忆塑造当代认同。",
        "所谓守成并不是停止改变，而是不断修补开国制度在迁徙、土地和长期和平中暴露的问题。",
    ],
}


NEW_SOURCES = [
    {"id":"v129_cssn_jin_victory_stele","title":"中国社会科学网·大金得胜陀颂碑与女真文字","url":"https://www.cssn.cn/skgz/bwyc/202407/t20240729_5767297.shtml","note":"介绍1185年女真文、汉文双语碑及世宗朝翻译、女真进士与学校建设。"},
    {"id":"v129_cssn_jin_six_ministries","title":"中国社会科学网·金熙宗六部制度改革","url":"https://www.cssn.cn/skgz/bwyc/202602/t20260209_5972806.shtml","note":"讨论1135至1138年前后由勃极烈共议向三省六部体制的渐进调整及其女真制度背景。"},
    {"id":"v129_cssn_jin_elites","title":"中国社会科学网·金代女真贵族秩序研究","url":"https://www.cssn.cn/dkzgxp/zgxp_zgshkx/2022nd6q/202208/t20220822_5474637.shtml","note":"用于熙宗朝宗室、婚姻和皇权秩序的制度背景，不以宫廷逸闻代替权力结构。"},
    {"id":"v129_cssn_jin_migration","title":"中国社会科学网·金代猛安谋克内迁再研究","url":"https://www.cssn.cn/skgz/202209/t20220916_5511905.shtml","note":"校正熙宗、海陵时期女真内迁规模的旧说，并讨论约四十猛安的估算与地方影响。"},
    {"id":"v129_cssn_shangjing_archaeology","title":"中国社会科学网·金上京城考古新认识","url":"https://www.cssn.cn/skgz/bwyc/202609/t20260928_6070460.shtml","note":"用于金初四帝上京城的城市格局与考古证据边界，不把所有遗迹直接归因于个别皇帝。"},
    {"id":"v129_beijing_zhongdu_archaeology","title":"北京市文物局·金中都考古发现","url":"https://wwj.beijing.gov.cn/bjww/wwjzzcslm/1729986/1730010/436280187/index.html","note":"用于1153年迁都后金中都城址、官式建筑和城市营建的物证。"},
]


NEW_EVENTS = [
    {"id":"v129_jin_taizu_war","year":"1115—1123", "sortYear":1115,"title":"金初持续攻辽与扩张","category":"军事","kind":"战争与建国","body":"建国后金军继续争夺黄龙府等节点，并在护步答冈等战事中削弱辽军；辽朝并未在1115年立即消失。","impact":"战争胜利扩大金朝统治范围，也把俘虏、人口、土地和多族群治理问题带入新国家。","people":["s_jin_taizu","s_liao_tianzuo"],"sources":["v55_jinshi","v55_liaoshi","v55_kaogu"]},
    {"id":"v129_jin_taizu_population","year":"1115—1123", "sortYear":1120,"title":"金初征服中的人口编管","category":"社会","kind":"人口与统治","body":"金军进入辽地后，女真人、契丹人、汉人及其他群体通过降附、迁徙与旧有地方网络被纳入不同管理体系。","impact":"王朝扩张不是地图颜色替换，战争同时改变人口归属、服役责任和地方社会关系。","people":["s_jin_taizu"],"sources":["v55_jinshi","v55_liaoshi","v129_cssn_shangjing_archaeology"]},
    {"id":"v129_jin_1119_script","year":"1119", "sortYear":1119,"title":"女真大字用于国家书写","category":"文化","kind":"文字与政令","body":"金太祖命完颜希尹等创制女真大字，使女真语能够进入诏令、外交与档案书写；汉字、契丹文字仍继续并用。","impact":"文字创制服务扩张中的国家治理，但现存较多女真文碑刻属于后世，不能倒推太祖朝的普及率。","people":["s_jin_taizu","s_jin_wanyanxiyin"],"sources":["v55_jinshi","v55_kaogu","v129_cssn_jin_victory_stele"]},
    {"id":"v129_jin_bojilie_transition","year":"1123—1135", "sortYear":1123,"title":"勃极烈共议承受帝国治理压力","category":"政治","kind":"中央制度","body":"太宗以兄终弟及继位，仍与勃极烈、掌兵宗室共同议政；征服区扩大后，旧有共议结构开始承受财政和地方行政压力。","impact":"这一阶段连接女真开国传统与熙宗官制改革，不能直接套用后世高度集中的皇权模型。","people":["s_jin_taizong","s_jin_taizu","s_jin_xizong"],"sources":["v55_jinshi","v129_cssn_jin_six_ministries"]},
    {"id":"v129_jin_chu_qi","year":"1127—1135", "sortYear":1127,"title":"楚、齐代理政权与北方治理","category":"政治","kind":"征服区治理","body":"金廷先后扶立张邦昌的楚与刘豫的齐，试图借地方官僚分担黄河流域治理和对宋战争成本。","impact":"代理政权依赖金军却不等同金朝州县，其反复废立说明征服后的统治仍在试验。","people":["s_jin_taizong","s_gaozong"],"sources":["v55_jinshi","v55_songshi"]},
    {"id":"v129_jin_taizong_revenue","year":"1125—1135", "sortYear":1128,"title":"征服区赋税与军需接管","category":"经济","kind":"财政与征服","body":"灭辽、攻宋以后，金廷通过原有州县、降附官员和代理政权接收赋税、粮运与军需，治理方式并未立即统一。","impact":"征服所得为继续战争提供资源，也使多套财政和地方管理长期并存。","people":["s_jin_taizong"],"sources":["v55_jinshi","v55_songshi","v55_liaoshi"]},
    {"id":"v129_jin_tianjuan_reform","year":"1135—1138", "sortYear":1138,"title":"天眷官制改革","category":"政治","kind":"中央制度","body":"熙宗朝逐步废除勃极烈最高共议体制，设置三省、六部并调整礼制和官号，形成更统一的中央行政。","impact":"改革结合女真贵族传统与征服区经验，并非把唐宋制度一次性原样移植。","people":["s_jin_xizong","s_jin_wanyanxiyin","s_jin_zonghan"],"sources":["v55_jinshi","v129_cssn_jin_six_ministries","v129_cssn_jin_elites"]},
    {"id":"v129_jin_xizong_song_war","year":"1137—1141", "sortYear":1140,"title":"熙宗朝宋金战线与议和","category":"军事","kind":"战争与边界","body":"废齐以后金军直接面对南宋，1137至1141年间战守反复，最终以绍兴和议把军事控制转化为边界和岁贡安排。","impact":"议和不是一场战役的自然结果，而是双方军事能力、内部政治和长期成本共同作用。","people":["s_jin_xizong","s_gaozong"],"sources":["v55_jinshi","v55_songshi"]},
    {"id":"v129_jin_hailing_centralization","year":"1150—1153", "sortYear":1150,"title":"海陵王夺位与皇权集中","category":"政治","kind":"宫廷与中央","body":"完颜亮杀熙宗夺位后清洗潜在宗室对手，并把军政、财政和任官进一步集中到皇帝及中央机构。","impact":"权力集中与夺位后的暴力相伴，后世道德叙事不能代替对制度动机和代价的分析。","people":["s_jin_hailing","s_jin_xizong"],"sources":["v55_jinshi","v129_cssn_jin_six_ministries"]},
    {"id":"v129_jin_zhenglong_reform","year":"1156—1161", "sortYear":1156,"title":"正隆年间中央机构整并","category":"文化","kind":"制度与礼制","body":"海陵王继续整并中央机构、官号和礼制，使中都成为发出行政命令的权力中心，同时保留女真军事组织。","impact":"相近的中原官名不等于所有地方实际运行一致，也不能把改革仅理解为南征准备。","people":["s_jin_hailing"],"sources":["v55_jinshi","v129_cssn_jin_six_ministries","v125_nopss_cities"]},
    {"id":"v129_jin_mengan_migration","year":"1149—1160", "sortYear":1155,"title":"猛安谋克人口内迁华北","category":"社会","kind":"人口与土地","body":"熙宗后期至海陵朝，部分女真猛安谋克迁入华北驻防并取得土地，与州县居民和原有土地关系交错。","impact":"研究估算约四十猛安，常见一百三十猛安、四百万人说缺乏依据；即使较小规模也会造成地方土地压力。","people":["s_jin_xizong","s_jin_hailing"],"sources":["v125_cssn_jin_mengan","v129_cssn_jin_migration"]},
    {"id":"v129_jin_1161_mutiny","year":"1161", "sortYear":1161,"title":"南征军变与海陵王被杀","category":"军事","kind":"战争与政变","body":"采石受挫、后勤压力和东京拥立完颜雍共同动摇南征军，完颜亮最终在扬州附近军中被部将杀死。","impact":"1161年败局来自前线、后方与继承危机的叠加，不能只归结为一场水战。","people":["s_jin_hailing","s_jin_shizong","s_yuyunwen"],"sources":["v55_jinshi","v55_songshi","v55_kaogu"]},
    {"id":"v129_jin_1161_tokyo_accession","year":"1161", "sortYear":1161,"title":"完颜雍在东京被拥立","category":"政治","kind":"帝位与地方","body":"海陵王南征期间，东京留守完颜雍在辽阳被拥立，金朝短暂出现两个皇帝和两个权力中心。","impact":"世宗的统治起于地方军政集团重新站队，而非一次平稳的宫廷继承。","people":["s_jin_shizong","s_jin_hailing"],"sources":["v55_jinshi","v55_songshi"]},
    {"id":"v129_jin_shizong_song_war","year":"1161—1164", "sortYear":1163,"title":"世宗初年宋金再战","category":"军事","kind":"战争与边界","body":"世宗即位初年，南宋乘金朝内乱北伐，双方在淮河和陕西等方向反复交战，随后转入隆兴和议。","impact":"军事相持与双方内部成本共同促成和议，长期边界稳定并非单靠一方善意。","people":["s_jin_shizong","s_xiaozong"],"sources":["v55_jinshi","v55_songshi"]},
    {"id":"v129_jin_dading_governance","year":"1161—1189", "sortYear":1170,"title":"大定年间的恢复与赈济","category":"经济","kind":"财政与民生","body":"长期和平、劝农和财政整顿有利于生产恢复，朝廷同时多次应对灾害、军费与不同地区的税役压力。","impact":"“大定盛世”概括长期稳定，却不能证明各地、各身份家庭都同样富足。","people":["s_jin_shizong"],"sources":["v55_jinshi","v125_cssn_jin_mengan"]},
    {"id":"v129_jin_dading_education","year":"1164—1185", "sortYear":1173,"title":"女真翻译、科举与学校","category":"文化","kind":"语言与教育","body":"世宗朝推动经典女真文翻译，设置女真进士科和学校；1185年得胜陀颂碑又以女真文、汉文并刻。","impact":"政策以翻译和双语书写保存女真传统，并非拒绝汉文文化；碑刻也不能代表全民识字。","people":["s_jin_shizong","s_jin_taizu"],"sources":["v55_jinshi","v129_cssn_jin_victory_stele"]},
    {"id":"v129_jin_mengan_livelihood","year":"1161—1189", "sortYear":1180,"title":"猛安谋克生计与骑射整顿","category":"社会","kind":"军户与土地","body":"世宗反复命猛安谋克自种田地、练习骑射，试图缓解内迁军户土地经营和军事能力下降的问题。","impact":"反复整顿说明开国军政组织不能靠祖制自动维持，其家庭已同华北州县经济深度交织。","people":["s_jin_shizong"],"sources":["v55_jinshi","v125_cssn_jin_mengan","v129_cssn_jin_migration"]},
]


ENDINGS = {
    "v55_reign_s_jin_taizu_b":"1123年，完颜阿骨打在攻辽与处理燕京问题期间去世，皇位由弟弟完颜吴乞买继承；这次兄终弟及并非被废或亡国。",
    "v55_reign_s_jin_taizong_b":"1135年，完颜吴乞买去世，开国宗室与重臣支持太祖嫡孙完颜亶继位，金朝由兄终弟及转入太祖后裔的隔代继承。",
    "v55_reign_s_jin_xizong_b":"约在公历1150年初，完颜亮联合宫廷力量杀死完颜亶并夺取皇位；熙宗的庙号与名分后来又经历降格和恢复。",
    "v55_reign_s_jin_hailing_b":"1161年南征受挫、东京另立完颜雍后，完颜亮在扬州附近的军队哗变中被杀；其帝号随后被废，史称海陵王。",
    "v55_reign_s_jin_shizong_b":"1189年完颜雍去世，因皇太子完颜允恭已经早逝，皇位由皇孙完颜璟继承，即金章宗；这是预先确立的隔代继承而非临时夺位。",
}


def main() -> None:
    data = json.loads(PATH.read_text())
    source_ids = {x["id"] for x in data["sources"]}
    data["sources"].extend(x for x in NEW_SOURCES if x["id"] not in source_ids)
    events_by_id = {x["id"]: x for x in data["events"]}
    for event in NEW_EVENTS:
        if event["id"] in events_by_id:
            events_by_id[event["id"]].update(event)
        else:
            data["events"].append(event)

    early = set(READINGS)
    wrong_pairs = {
        frozenset(("s_jin_hailing", "s_xia_zhangyuan")),
    }
    data["associations"] = [
        a for a in data["associations"]
        if not (
            frozenset((a.get("from"), a.get("to"))) in wrong_pairs
            or (({a.get("from"), a.get("to")} & early) and any((p or "") in {"s_liao_taizu", "s_liao_taizong"} for p in (a.get("from"), a.get("to"))))
        )
    ]
    additions = [
        {"from":"s_jin_taizu","to":"s_jin_wanyanxiyin","role":"命创女真文字的君主","inverse":"受命创制女真大字的重臣","period":"1119—1123","note":"文字创制见《金史》传统，后世碑刻用于说明延续而非倒证所有太祖朝细节。"},
        {"from":"s_jin_taizong","to":"s_jin_xizong","role":"叔祖与前任皇帝","inverse":"太祖嫡孙与继任皇帝","period":"1123—1135","note":"太宗去世后由太祖嫡孙熙宗继位，显示继承路线由兄终弟及转向下一代。"},
        {"from":"s_jin_hailing","to":"s_jin_shizong","role":"南征时被另立者取代的皇帝","inverse":"东京被拥立并取代海陵王的皇帝","period":"1161","note":"海陵南征期间完颜雍在东京被拥立，形成短暂的两个权力中心。"},
        {"from":"s_jin_shizong","to":"s_jin_zhanghao","role":"即位初期沿用的重臣","inverse":"参与世宗初年中枢治理的官员","period":"1161—1172","note":"张浩历仕熙宗、海陵与世宗，关联用于观察政权更替中的官僚连续性。"},
    ]
    pairs = {frozenset((a["from"], a["to"])) for a in data["associations"]}
    for a in additions:
        if frozenset((a["from"], a["to"])) not in pairs:
            a["sources"] = ["v55_jinshi", "v55_songshi", "v129_cssn_jin_six_ministries"]
            data["associations"].append(a)

    contexts = {x["person"]: x for x in data["reignContexts"]}
    updates = {
        "s_jin_taizu": (["s_jin_taizong","s_jin_wanyanxiyin","s_liao_tianzuo"], ["v55_p06","v129_jin_taizu_war","v55_e06","v129_jin_1119_script","v129_jin_taizu_population","v55_reign_s_jin_taizu_b"], "建国、反辽战争、猛安谋克和文字创制同时展开，1123年以兄终弟及交接。"),
        "s_jin_taizong": (["s_jin_taizu","s_liao_tianzuo","s_qinzong","s_jin_xizong"], ["v129_jin_bojilie_transition","v55_p07","v55_m06","v55_s05","v96s_jin_writing","v129_jin_taizong_revenue","v129_jin_chu_qi","v55_reign_s_jin_taizong_b"], "灭辽、攻宋与征服区治理并行，代理政权和继承安排都显示统治尚在重组。"),
        "s_jin_xizong": (["s_jin_taizong","s_jin_hailing","s_jin_wanyanxiyin","s_jin_zonghan"], ["v56_政治_06","v129_jin_tianjuan_reform","v43s_shaoxing","v56_社会_06","v99s_jin_xizong_economy","v96s_jin_writing","v129_jin_xizong_song_war","v55_reign_s_jin_xizong_b"], "官制改革、宋金和议与功臣清洗共同塑造熙宗朝，结尾是宫廷政变而非泛化的在位终结。"),
        "s_jin_hailing": (["s_jin_xizong","s_jin_shizong","s_jin_zhanghao","s_yuyunwen"], ["v129_jin_hailing_centralization","v55_e07","v129_jin_zhenglong_reform","v129_jin_mengan_migration","v55_m08","v43s_caishi","v129_jin_1161_mutiny"], "夺位后的集中、迁都和人口内迁最终同1161年南征及后方另立新君相撞。"),
        "s_jin_shizong": (["s_jin_hailing","s_jin_zhangzong","s_xiaozong","s_jin_zhanghao"], ["v129_jin_1161_tokyo_accession","v129_jin_shizong_song_war","v43s_longxing_treaty","v55_e08","v55_s07","v129_jin_dading_governance","v129_jin_dading_education","v129_jin_mengan_livelihood","v55_reign_s_jin_shizong_b"], "长期稳定建立在和议、恢复与持续制度整顿上，不能把“大定盛世”写成没有差异的富足。"),
    }
    for pid, (people, events, note) in updates.items():
        contexts[pid]["people"] = people
        contexts[pid]["events"] = events
        contexts[pid]["sources"] = READINGS[pid]["sources"]
        contexts[pid]["note"] = note

    articles = {x["person"]: x for x in data["articles"]}
    for pid, reading in READINGS.items():
        articles[pid]["sections"] = [
            {"id":f"{pid}-v129-{i}","title":title,"text":text + EXTRAS[pid][i-1],"kind":"史实与解读","events":[reading["events"][i-1]],"people":[pid,*reading["people"]],"sources":reading["sources"]}
            for i, (title, text) in enumerate(zip(reading["titles"], reading["texts"]), 1)
        ]
        articles[pid]["sources"] = reading["sources"]

    for event in data["events"]:
        if event["id"] in ENDINGS:
            event["body"] = ENDINGS[event["id"]]
            event["impact"] = ENDINGS[event["id"]]

    data["version"] = 103
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("rewrote the first five Jin ruler readings")


if __name__ == "__main__":
    main()
