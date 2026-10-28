#!/usr/bin/env python3
"""Connect six missing Hongwu-era figures to people, events and relationships."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "App/Resources/history.json"


def upsert(items: list[dict], item: dict) -> None:
    for index, existing in enumerate(items):
        if existing.get("id") == item["id"]:
            items[index] = item
            return
    items.append(item)


def upsert_article(items: list[dict], item: dict) -> None:
    for index, existing in enumerate(items):
        if existing.get("person") == item["person"]:
            items[index] = item
            return
    items.append(item)


def upsert_association(items: list[dict], item: dict) -> None:
    for index, existing in enumerate(items):
        if existing.get("from") == item["from"] and existing.get("to") == item["to"]:
            items[index] = item
            return
    items.append(item)


def upsert_family(items: list[dict], item: dict) -> None:
    for index, existing in enumerate(items):
        if existing.get("from") == item["from"] and existing.get("to") == item["to"] and existing.get("kind") == item["kind"]:
            items[index] = item
            return
    items.append(item)


def section(sid: str, title: str, text: str, sources: list[str], events: list[str], people: list[str]) -> dict:
    return {"id": sid, "title": title, "text": text, "kind": "史实与解读", "sources": sources, "events": events, "people": people}


def article(person: str, title: str, dek: str, sections: list[dict]) -> dict:
    source_union: list[str] = []
    for item in sections:
        for source in item["sources"]:
            if source not in source_union:
                source_union.append(source)
    return {"person": person, "title": title, "dek": dek, "sections": sections, "sources": source_union}


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    for source in [
        {"id": "ms2", "title": "《明史》卷二 · 太祖本纪二", "url": "https://zh.wikisource.org/zh-hans/明史/卷2", "note": "清修《明史》太祖本纪的开放转录，核对洪武元年至二十三年的诏令、任免、战争与案件时间线；本纪以皇帝和朝廷为叙事中心，定罪结论与战果数字仍须同列传及其他材料互证。"},
        {"id": "v136_ms126_muying", "title": "《明史》卷126｜沐英传", "url": "https://zh.wikisource.org/zh-hans/明史/卷126", "note": "清修《明史》的开放转录，核对沐英收养经历、征战、留镇云南及身后世系。战果数字、性格评语和地方安定叙事带有功臣传与王朝立场，不能直接当作中立统计。"},
        {"id": "v136_ms128_songlian", "title": "《明史》卷128｜宋濂传", "url": "https://zh.wikisource.org/zh-hans/明史/卷128", "note": "清修《明史》的开放转录，核对宋濂的元代经历、太子教育、两次修《元史》、礼制工作和流放结局；君臣问答是后世编纂文本，不视为逐字实录。"},
        {"id": "v136_ms129_generals", "title": "《明史》卷129｜冯胜、傅友德传", "url": "https://zh.wikisource.org/zh-hans/明史/卷129", "note": "清修《明史》的开放转录，核对两位将领的战役、军职、屯田与死亡。神异出生、精确杀俘数字和动机判断不作未经互证的事实使用。"},
        {"id": "v136_ms308_hu", "title": "《明史》卷308｜胡惟庸传", "url": "https://zh.wikisource.org/zh-hans/明史/卷308", "note": "胡惟庸被收入清修《明史》奸臣传。可核对仕历、1380年处死及案件后续扩张；通倭、通元、毒杀与谋反等叙述多由多年后的审讯和定罪材料构成，须明确证据层级。"},
    ]:
        upsert(data["sources"], source)

    people = [
        {"id": "ma", "name": "马皇后", "call": "孝慈高皇后", "temple": "—", "era": "元末—洪武", "reign": "1332—1382", "summary": "从郭子兴养女到明朝开国皇后，参与军中供给、宫廷治理与劝谏；传世事迹主要由后世官修史书塑造，须区分制度行动与典范化叙事。", "kind": "皇后", "note": "《明史》保存大量对话与德行故事，能够说明后世如何塑造开国皇后典范，却未必都是可逐字复原的现场记录。", "sources": ["v2e_ms113", "portrait-npm-1861", "ms2"], "dynasty": "ming", "image": "portrait_ma"},
        {"id": "m136_songlian", "name": "宋濂", "call": "太子师与开国文臣", "temple": "—", "era": "元末—洪武", "reign": "1310—1381", "summary": "由元末地方学者进入明初朝廷，主持修《元史》、教授太子并参与礼制文书；晚年因孙辈牵入胡惟庸案而流放，死于途中。", "kind": "学者与官员", "note": "不能把他只写成散文家，也不能因长期近侍而假定其每次进言都被采纳。", "sources": ["v136_ms128_songlian", "v15_ms128", "ms2"], "dynasty": "ming"},
        {"id": "m136_huweiyong", "name": "胡惟庸", "call": "明朝最后一任中书省丞相", "temple": "—", "era": "洪武", "reign": "生年不详—1380", "summary": "从地方官升至左丞相，长期主持中书省；1380年被处死后，案件不断追补为庞大谋反案，并成为废中书省丞相的重要转折。", "kind": "宰辅与重案人物", "note": "当时的行政擅权、1380年定罪与其后十余年的谋反供辞必须分层阅读。", "sources": ["v136_ms308_hu", "v2f_ms127", "v15_ms128", "ms2"], "dynasty": "ming"},
        {"id": "m136_muying", "name": "沐英", "call": "西平侯、云南留镇将领", "temple": "—", "era": "洪武", "reign": "1345—1392", "summary": "幼年由朱元璋与马皇后抚养，历经西北与云南战争；1382年后长期留镇云南，参与卫所、屯田、交通与赋役安排。", "kind": "将领与地方统治者", "note": "明朝文献称其安定云南，也应同时看到征服、移民、军屯和地方社会承受的暴力与重组。", "sources": ["v136_ms126_muying", "v136_ms129_generals", "v2f_ms132"], "dynasty": "ming"},
        {"id": "m136_fuyoude", "name": "傅友德", "call": "颍国公、征南将军", "temple": "—", "era": "元末—洪武", "reign": "生年不详—1394", "summary": "辗转多支元末军队后归朱元璋，参与北伐、平蜀并统军征云南；晚年练军屯田，1394年在缺少公开案由的情况下被赐死。", "kind": "将领", "note": "史书明确记载赐死，却没有提供足以确认具体罪名的完整案卷，不把后世传说当作定论。", "sources": ["v136_ms129_generals", "ms2", "v4p_ms3"], "dynasty": "ming"},
        {"id": "m136_fengsheng", "name": "冯胜", "call": "宋国公、北征统帅", "temple": "—", "era": "元末—洪武", "reign": "生年不详—1395", "summary": "随兄冯国用归附朱元璋，参加江南战争、北伐和辽东纳哈出归降；多次因军纪与战利品问题受责，1395年被赐死。", "kind": "将领", "note": "军功、处分和死亡均有记载，但“谋反”不能在没有明确同时代案证时倒推成立。", "sources": ["v136_ms129_generals", "ms2", "v4p_ms3"], "dynasty": "ming"},
    ]
    for person in people:
        upsert(data["people"], person)

    events = [
        {"id": "v136_ma_war_logistics", "year": "1352—1367", "title": "军中家属、衣物与犒赏构成战争后方", "category": "社会", "body": "马氏随朱元璋军队迁移，在太平、江宁等阶段组织将士家属渡江、缝制军衣，并在龙湾战事时动用宫中财物犒军。", "impact": "开国战争不只有将领与战阵，妇女、家属、衣物、食物和财物调度也是军队持续行动的条件；具体细节主要见后世后妃传。", "kind": "战争与家庭", "people": ["ma", "yuanzhang", "guo"], "sources": ["v2e_ms113", "ms1"]},
        {"id": "v136_ma_palace_mediation", "year": "1368—1382", "title": "皇后劝谏与宫廷处分的缓冲", "category": "政治", "body": "《明史》记马皇后多次在朱元璋震怒后劝缓刑罚，并就李文忠、宋濂及宫人处分进言；她还反对以外戚身份授官。", "impact": "后宫并非完全隔绝于政治，但劝谏效果依赖私人接近皇帝，不能等同于有固定程序和公开责任的司法复核机构。", "kind": "宫廷政治", "people": ["ma", "yuanzhang", "liwenzhong", "m136_songlian"], "sources": ["v2e_ms113", "v136_ms128_songlian"]},
        {"id": "v136_red_board_granary", "year": "洪武初", "sortYear": 1370, "title": "太学生家属粮与红板仓", "category": "社会", "body": "后妃传记载，马皇后询问国子学生家属生计，推动设仓积粮供给。它把中央教育机构背后的家庭生活带入宫廷讨论。", "impact": "这不是覆盖全国的社会保障制度，却显示培养官学生也牵涉家属供养、仓储与财政，不应只写课堂和考试。", "kind": "教育与救济", "people": ["ma", "yuanzhang", "m136_songlian"], "sources": ["v2e_ms113", "ms2"]},
        {"id": "v136_yuan_history_compilation", "year": "1369—1370", "title": "两次修纂《元史》", "category": "文化", "body": "洪武二年宋濂任总裁官，朝廷汇集元代材料修成《元史》；因元统以后史事不足，又补采材料并续修。", "impact": "修史既保存前朝制度与人物资料，也由新王朝安排前朝兴亡叙事；成书迅速带来材料价值，也留下取舍与编纂局限。", "kind": "修史", "people": ["m136_songlian", "yuanzhang", "liuji"], "sources": ["v136_ms128_songlian", "ms2"]},
        {"id": "v136_prince_education", "year": "1360年代—1377", "sortYear": 1372, "title": "宋濂讲授太子并参与礼制文书", "category": "文化", "body": "宋濂长期为朱标讲读经史，又参与封爵、祭祀、朝会、历法与诏令文字，把儒家经典解释带入新王朝制度建构。", "impact": "太子教育不是私人读书，关系到继承者如何理解刑罚、礼制和君臣责任；文臣的影响仍受皇帝选择与政治环境限制。", "kind": "教育与制度", "people": ["m136_songlian", "biao", "yuanzhang"], "sources": ["v136_ms128_songlian", "v15_ms128"]},
        {"id": "cabinet", "year": "1380", "title": "胡惟庸被诛与废中书省丞相", "category": "政治", "body": "占城贡使未及时上闻等争议加剧中书省与六部互相推责。1380年胡惟庸、陈宁等被处死，朱元璋随后废中书省和丞相职位，使六部直接承受皇帝指挥。", "impact": "行政擅权与当年定罪有史料依据；通倭、通元和庞大谋反网络多在其死后多年追认。制度改变不能只解释为查办一名奸臣，也意味着皇帝亲自承担更重文书负荷。", "kind": "制度转折", "people": ["yuanzhang", "m136_huweiyong", "lishanzhang"], "sources": ["v136_ms308_hu", "v2f_ms127", "ms2"]},
        {"id": "v136_hu_case_expansion", "year": "1385—1390", "title": "胡惟庸案多年扩张", "category": "政治", "body": "胡惟庸死后，朝廷在1385年以后陆续追查李存义、林贤、封绩等线索，1390年又将李善长及多名侯爵卷入，形成大规模株连。", "impact": "后出的审讯供辞、告发和官方《昭示奸党录》属于定罪体系的一部分，不能自动证明1380年前已经存在一个边界清楚、成员一致的谋反组织。", "kind": "政治案件", "people": ["m136_huweiyong", "lishanzhang", "yuanzhang"], "sources": ["v136_ms308_hu", "v2f_ms127"]},
        {"id": "v136_yunnan_campaign_stages", "year": "1381—1382", "title": "曲靖、大理与云南征服的分阶段推进", "category": "军事", "body": "傅友德统军，蓝玉、沐英任副将，从贵州方向进入云南，在曲靖击败元梁王军，继而攻取昆明、大理并向乌撒、东川等地扩展。", "impact": "攻取城市不等于全境立即稳定；不同土司、山地社群和交通节点的归附与反抗持续发生，战争造成的杀伤也不能被“统一”一词遮蔽。", "kind": "征服战争", "people": ["m136_fuyoude", "m136_muying", "lanyu", "yuanzhang"], "sources": ["v136_ms129_generals", "v136_ms126_muying", "v2f_ms132"]},
        {"id": "v136_yunnan_postwar_rule", "year": "1382—1392", "title": "沐英留镇与云南军政重组", "category": "经济", "body": "傅友德、蓝玉班师后，沐英留镇云南，设置和维护卫所、堡寨与军屯，整治交通、水利、盐井和粮道，并持续处理地方反抗。", "impact": "屯田和交通支持驻军及行政运转，也伴随人口迁移、土地重新配置与赋役重编；明朝功臣传所称安定，应与地方社会的损失和适应并读。", "kind": "地方治理", "people": ["m136_muying", "m136_fuyoude", "yuanzhang"], "sources": ["v136_ms126_muying", "v136_ms129_generals", "v134_nopss_yuan_ming_jiangnan"]},
        {"id": "v136_naghachu_surrender", "year": "1387", "title": "纳哈出归降与辽东军民收编", "category": "军事", "body": "冯胜为征虏大将军，傅友德、蓝玉为副将，明军筑城并逼近金山。纳哈出在交涉与军事压力下归降，大量部众、牲畜和车辆随后被带入关内。", "impact": "这不是一次单纯会战胜利，而是招降、筑城、威慑和收编共同完成；途中冲突、降众安置及战利品争议又导致冯胜被夺兵权。", "kind": "边疆战争与收编", "people": ["m136_fengsheng", "m136_fuyoude", "lanyu", "yuanzhang"], "sources": ["v136_ms129_generals", "ms2"]},
        {"id": "v136_generals_forced_deaths", "year": "1394—1395", "title": "傅友德、冯胜先后被赐死", "category": "政治", "body": "蓝玉案后，傅友德于1394年、冯胜于1395年被赐死。《明史》对两人的死亡均缺少完整公开审判过程，冯胜诸子也未能承袭爵位。", "impact": "可确认的是皇帝处分与死亡结果；具体罪名和现场传说证据不足。洪武晚年老将退出统兵体系，与皇权对军队控制加强同时发生。", "kind": "功臣政治", "people": ["m136_fuyoude", "m136_fengsheng", "yuanzhang", "lanyu"], "sources": ["v136_ms129_generals", "v4p_ms3", "v2f_ms132"]},
    ]
    for event in events:
        upsert(data["events"], event)

    articles = [
        article("ma", "马皇后：开国战争与宫廷之间", "从军中供给到皇帝身边的劝谏，她的行动值得看见；后世把她塑成理想皇后的过程，也同样需要辨认。", [
            section("ma-1", "郭子兴家中的养女", "马氏早年父母去世，由父亲旧交郭子兴收养，后来嫁给在郭子兴军中的朱元璋。这个婚姻把个人生活放进元末起事者的关系网络。后世传记写她调和郭子兴与朱元璋的嫌隙，细节带有贤内助叙事，但郭氏集团内部的信任、婚姻和军权确实彼此相连。不能把她只当作皇帝成名前的陪伴者，也不宜把每次危机都解释成一位女性私下化解。", ["v2e_ms113", "ms1"], ["v136_ma_war_logistics"], ["yuanzhang", "guo"]),
            section("ma-2", "军队背后的衣食与家属", "渡江和江南战争期间，军队不仅需要武器和将领，也需要安置家属、缝制衣鞋、准备食物并在紧急时调出财物。后妃传把这些工作集中记在马氏身上，并称龙湾战事时她发宫中金帛犒军。即使无法逐项还原数量，这些材料仍揭示传统战史经常省略的后方劳动。女性与军属不是等待胜利的人，她们参与维持迁徙中的军事共同体。", ["v2e_ms113", "ms1"], ["v136_ma_war_logistics"], ["yuanzhang"]),
            section("ma-3", "皇帝震怒时的缓冲", "1368年册立皇后后，马氏能够在朱元璋回到内廷时直接进言。《明史》记她为李文忠、宋濂、囚徒和宫人劝解，也强调刑罚不应随喜怒加重。私人劝谏有时改变处分，却不是稳定的司法制度：它依赖皇帝是否接受，也无法让被告公开申辩。读这些故事，既要看到后宫女性的政治能动性，也要看到个人慈惠无法替代程序约束。", ["v2e_ms113", "v136_ms128_songlian"], ["v136_ma_palace_mediation"], ["yuanzhang", "liwenzhong", "m136_songlian"]),
            section("ma-4", "从灾荒到学生家属", "传记记马皇后询问灾荒、仓储和国子学生家属的粮食来源，并把红板仓与她联系起来。她也劝皇帝厚待承担政务的人，而自己与宫人节用。这里反映宫廷怎样理解救济、教育供养与日常消费。不过，个别赐粮不是全国社会政策，史书的节俭描写也服务于母仪天下的典范。更稳妥的读法，是把具体制度线索同道德赞辞分开。", ["v2e_ms113", "ms2"], ["v136_red_board_granary"], ["yuanzhang", "m136_songlian"]),
            section("ma-5", "画像与贤后记忆", "马皇后1382年去世，葬于孝陵，朱元璋此后未再立皇后。清修《明史》把她置于后妃传之首，以大量对话塑造仁慈、节俭、拒绝外戚干政的典范。台北故宫所藏《明孝慈高皇后半身像》提供后世宫廷视觉记忆，但馆藏页未说明它是生前写照，不能用来断定真实容貌。她的历史形象由行动、官方伦理和后世图像共同形成。", ["v2e_ms113", "portrait-npm-1861"], ["v136_ma_palace_mediation"], ["yuanzhang", "biao"]),
        ]),
        article("m136_songlian", "宋濂：文章之外的制度工作", "他讲授经典、主持修史并书写礼制；晚年却因家属案件被流放，显出开国文臣与皇权之间的不对等。", [
            section("songlian-1", "从元代学者到应天文臣", "宋濂早年从多位金华学者读经史，元末曾获荐任翰林编修，因奉养母亲辞谢，入山著书。朱元璋取得婺州后，他先任地方经学教师，后来经李善长推荐，与刘基等被召至应天。这个过程不是隐士突然被明主发现的传奇，而是新政权接收地方学术网络、学校和文书人才的一部分。宋濂选择进入朝廷，也意味着知识开始服务新的政治秩序。", ["v136_ms128_songlian", "v15_ms128"], ["v136_prince_education"], ["yuanzhang", "liuji", "lishanzhang"]),
            section("songlian-2", "太子教育是一项政治工作", "宋濂长期为朱标讲读经史，以前代兴亡、刑罚和礼义劝说继承人。他又教授进入文华堂的年轻儒士，参与培养朝廷后备官员。经典讲解并非脱离现实的课堂：怎样赏罚、怎样对待臣民、如何理解君臣关系，都可能进入未来皇帝的判断。朱标对他的尊重见于后世传记，但教师能提供语言和历史经验，不能单独决定太子和朝廷的政治选择。", ["v136_ms128_songlian", "ms2"], ["v136_prince_education"], ["biao", "yuanzhang"]),
            section("songlian-3", "一年多修成的前朝史", "1369年宋濂任《元史》总裁官，首轮成书后，朝廷又补采元统以后的材料续修。快速编纂保存了大量元代制度、人物和战争资料，也让新王朝掌握解释前朝盛衰的权力。今天使用《元史》，既不能因成书仓促而全部否定，也不能忽视材料缺漏、传抄错误和明初正统立场。宋濂的角色，是组织材料与确立叙述框架，不是独自写完全部卷帙。", ["v136_ms128_songlian", "ms2"], ["v136_yuan_history_compilation"], ["yuanzhang", "liuji"]),
            section("songlian-4", "礼制、诏令与国家日常", "祭祀、朝会、封爵、衣冠、历法以及接待各地使者，都需要可反复执行的文字和程序。宋濂参与这些工作，也撰写功臣碑记与朝廷文告。他因此常被称为开国文臣之首，但制度从来不是一位文章家的个人作品：皇帝、礼部、翰林、各类官员与前朝成例共同作用。把宋濂放回这些协作关系，才能理解文章为何会改变政治日常，也能看见文字服务权力的一面。", ["v136_ms128_songlian", "v15_ms128"], ["v15_liuji_law", "v136_prince_education"], ["liuji", "lishanzhang", "yuanzhang"]),
            section("songlian-5", "孙辈案件为何追到老师", "宋濂1377年致仕。1380年，其长孙宋慎被牵入胡惟庸案，宋濂一度被判死，后改为安置茂州，次年死于夔州。史书记马皇后和朱标营救，这一细节属于后世传记叙事，却与赦死流放的结果相合。案件以家属关系扩大责任，说明长期近侍和太子师身份也不能提供稳定安全。宋濂之死应同胡案扩张相连，而不能写成自然退休后的平静终章。", ["v136_ms128_songlian", "v136_ms308_hu", "v2e_ms113"], ["cabinet", "v136_hu_case_expansion"], ["ma", "biao", "m136_huweiyong"]),
        ]),
        article("m136_huweiyong", "胡惟庸：丞相之死与案件的生长", "1380年的处死、废丞相的制度转折，以及此后十余年不断扩张的谋反叙事，应当分开理解。", [
            section("hu-1", "从地方文书到中书省", "胡惟庸在朱元璋占据和州时归附，先做奏差、宣使和县级官员，随后升入中央。1370年任中书省参知政事，后来历左、右丞，1374年任右丞相，最终成为左丞相。他的上升既依靠行政能力和皇帝信任，也经过明初尚未定型的中书省体系。不能因为结局是谋反大案，便把每一次升迁都解释为预谋夺权。", ["v136_ms308_hu", "ms2"], ["cabinet"], ["yuanzhang", "lishanzhang"]),
            section("hu-2", "丞相怎样控制信息", "《明史》指控胡惟庸先拆阅各方奏章、隐匿不利材料，并在官员任免上越权。这些记载说明皇帝与中书省之间围绕信息、用人和处分存在尖锐冲突，也符合朱元璋对臣下结党和壅蔽的警惕。然而，胡惟庸被列入奸臣传，文本会把制度矛盾集中成个人品行。即使承认擅权问题，也不能由此自动推出所有后来追加的谋反细节。", ["v136_ms308_hu", "v15_ms128"], ["cabinet"], ["yuanzhang", "liuji"]),
            section("hu-3", "1380年到底发生了什么", "1379年占城贡使未及时上报，引发中书省和礼部互相推责，汪广洋先被赐死。次年涂节等告发胡惟庸，胡、陈宁及告发者涂节均被诛。随后中书省和丞相职位被废，六部直接对皇帝负责。可确认的是处死与制度改变；现存材料不足以重建一场透明审判。把“废相”说成一名奸臣被查后的自然结果，会漏掉朱元璋长期重组决策权的选择。", ["v136_ms308_hu", "ms2", "v2f_ms127"], ["cabinet"], ["yuanzhang", "lishanzhang"]),
            section("hu-4", "人死之后，案情仍在扩大", "胡惟庸死后，通倭、通元等指控在1385、1386和1390年前后的审讯中陆续出现，李善长、陆仲亨、费聚等功臣被追入案件。官方把供辞汇成《昭示奸党录》，株连延续多年。告发和审讯材料是研究政治清洗的重要史料，却不是中立旁观记录；被告面临的压力、供辞形成时间和朝廷需要证明的结论，都应进入判断。后出的证词不能无条件倒推早年的行动。", ["v136_ms308_hu", "v2f_ms127"], ["v136_hu_case_expansion", "v2f_lishanzhang"], ["lishanzhang", "yuanzhang"]),
            section("hu-5", "不要让奸臣标签替代制度史", "清修《明史》把胡惟庸置于奸臣传，强调贪权、符瑞和异谋，使个人道德成为解释中心。更完整的阅读还要看到：中书省怎样筛选文书，皇帝为何拒绝中间权力中心，废相后政务为何需要翰林和后来内阁协助，以及案件如何重塑功臣群体。胡惟庸不必被洗成无辜官员，但对擅权的批评也不能证明全部谋反叙事。制度后果、司法证据和史家评价应各自陈列。", ["v136_ms308_hu", "v2f_ms127", "v15_ms128"], ["cabinet", "v136_hu_case_expansion"], ["yuanzhang", "lishanzhang", "liuji"]),
        ]),
        article("m136_muying", "沐英：留在云南的开国将领", "被收养的战争孤儿成长为统帅，又成为明朝在云南长期驻军与治理的核心；功臣传的安定叙事背后仍有征服代价。", [
            section("muyang-1", "战争孤儿与皇帝养子", "沐英幼年在战乱中失去父母，朱元璋与马氏将他收养，一度从朱姓，成年后才恢复沐姓。养育关系给他进入亲军和军政机构的机会，也形成不同于一般将领的宫廷信任。史书强调马皇后关怀和他的感恩，符合功臣传的伦理框架；更重要的结构是，元末军队吸收大量失亲少年，通过养子、亲军和赐姓把家庭关系转化为军事忠诚。", ["v136_ms126_muying", "v2e_ms113"], ["v136_ma_war_logistics"], ["yuanzhang", "ma"]),
            section("muyang-2", "从福建、西北到云南", "沐英青年时守镇江、广信，参加福建战事，后来进入大都督府。1377年随邓愈征西，随后又在河西、贺兰山和漠北方向作战。这些经历使他熟悉长距离行军、降附部众和边地驻守。1381年征云南时，他不是突然出现的地方总督，而是已经有多地军政经验的副将。传记中的大规模俘获数字应谨慎使用，不能以数字大小简单衡量治理能力。", ["v136_ms126_muying", "v136_ms129_generals"], ["v136_yunnan_campaign_stages"], ["m136_fuyoude", "lanyu"]),
            section("muyang-3", "攻下昆明不等于控制云南", "傅友德统军、蓝玉与沐英为副将，在曲靖击败梁王军后进入昆明；沐英又率军攻取大理，并分兵处理乌撒、东川等地。不同山地和坝区有各自首领、交通与利益，归附后仍可能再次反抗。史书常以斩获和投降串成统一进程，却很少展开普通居民的死亡、迁徙与粮食损失。把战役拆成阶段，才能看见城市易手与地方控制之间的距离。", ["v136_ms126_muying", "v136_ms129_generals", "v2f_ms132"], ["v136_yunnan_campaign_stages"], ["m136_fuyoude", "lanyu", "yuanzhang"]),
            section("muyang-4", "卫所、屯田和粮道", "1382年傅友德、蓝玉班师，沐英留镇云南。他组织堡寨、卫所和军屯，维护从永宁到大理的道路，也处理盐井、水利、赋役和地方官员。屯田为驻军提供粮食，并把外来军户长期嵌入地方；道路和仓储增强行政联系，同时重新分配土地与劳役。明朝传记称这些措施便民安业，今天还要追问谁获得田地、谁承担运输，以及不同社群如何协商或抵抗。", ["v136_ms126_muying", "v134_nopss_yuan_ming_jiangnan"], ["v136_yunnan_postwar_rule"], ["yuanzhang", "m136_fuyoude"]),
            section("muyang-5", "沐氏留镇的长远影响", "沐英在云南继续应对麓川等方向的战争，1392年得知朱标去世后不久病逝，归葬南京。他的儿子沐春、沐晟等继续镇守云南，沐氏由个人功臣发展为跨世代军政家族。这种连续性有助于朝廷维持地方指挥，也让重要权力长期集中于一家。理解沐英既要看到个人经历与制度建设，也不能把明朝扩张描述成无摩擦的文明输入；征服、治理与地方社会的再组织始终相连。", ["v136_ms126_muying", "v4p_ms3"], ["v136_yunnan_postwar_rule"], ["biao", "yuanzhang"]),
        ]),
        article("m136_fuyoude", "傅友德：多次转营的征南统帅", "他的生涯连接元末军队流动、明初跨区域战争与洪武晚年的功臣不安；最后一次赐死没有足够材料支持传奇化解释。", [
            section("fu-1", "在多个政权之间寻找出路", "傅友德早年先后进入刘福通部将、明玉珍与陈友谅军中，直到朱元璋攻江州时率部归附。元末军人频繁转营，不只是个人反复，也反映政权兴亡、粮饷和将领关系不断变化。归附后他在安丰、鄱阳湖、武昌等战事中受伤作战，逐渐获得独立领军机会。后来的明朝功臣身份，不应抹去他此前复杂的政治路径。", ["v136_ms129_generals", "v134_ms123_rivals"], ["v134_hongdu_poyang_system"], ["chenyou", "yuanzhang", "y_ming_yuzhen"]),
            section("fu-2", "平蜀体现的是协同与补给", "1371年伐蜀时，傅友德率步骑从秦陇方向进入，廖永忠等水军由长江推进。山路、江水、桥梁与粮饷决定进度，傅军一度造船渡水并通过木牌传递战果。成都、重庆的降服来自多路压力，不是某位统帅单独奇袭。史书称“傅一廖二”，记录朝廷论功次序；它不能遮蔽战斗杀伤，也不能把汤和等人的迟滞简单等同于怯战。", ["v136_ms129_generals", "v2f_ms126"], ["v134_daxia_sichuan"], ["tanghe", "y_ming_yuzhen", "yuanzhang"]),
            section("fu-3", "征云南的总指挥", "1381年傅友德任征南将军，以蓝玉、沐英为副，分路进入贵州、云南。曲靖、大理和乌撒等战场的推进需要前锋、道路修缮、粮运与地方向导。攻取主要城市后，傅友德仍在东川、越州等地反复用兵。把云南征服写成一年完成，会把后续抵抗、军屯和地方权力重组全部压平；统帅的战功也必须与普通军民的代价同时呈现。", ["v136_ms129_generals", "v136_ms126_muying", "v2f_ms132"], ["v136_yunnan_campaign_stages", "v136_yunnan_postwar_rule"], ["m136_muying", "lanyu"]),
            section("fu-4", "老将还要练军、屯田", "云南战争后，傅友德继续在北方备边，跟随晋王、燕王出塞，并与冯胜训练山西、河南军队、经营屯田。洪武后期把部分老将置于亲王节制下，显示边军指挥、皇室分封和中央控制彼此交织。屯田不是战争之外的闲务，它决定卫所能否取得粮食，也会改变地方土地和民户负担。傅友德因此既是前线将领，也是军事制度的执行者。", ["v136_ms129_generals", "v4p_ms3", "v4p_ms116"], ["v136_naghachu_surrender"], ["gang", "di", "m136_fengsheng"]),
            section("fu-5", "赐死以后，不替史料补写罪名", "1394年傅友德被赐死。《明史》此前记皇帝因他请求田地而不悦，却没有给出一套完整罪名与审判记录。后世关于宴席上逼其自尽、携首复命等故事流传很广，现有主传不足以证明这些细节。可以确定的是，蓝玉案后又一位资深统帅死亡，孙辈因公主关系获得有限安置。叙述应停在证据边界：说明政治环境，不把推测写成案情。", ["v136_ms129_generals", "v2f_ms132", "v4p_ms3"], ["v136_generals_forced_deaths"], ["yuanzhang", "lanyu", "m136_fengsheng"]),
        ]),
        article("m136_fengsheng", "冯胜：大军统帅与失去兵权", "从江南攻城到辽东收编，他多次承担大规模军队指挥；战果、军纪处分与最后赐死构成彼此相关却不能混成一条的线索。", [
            section("feng-1", "兄弟归附与亲军信任", "冯胜原名国胜、宗异，与兄冯国用在元末筑寨自保，朱元璋进至妙山时一同归附。冯国用早逝后，冯胜承接部分军职，参加龙湾、鄱阳湖、淮东与平江战事。功臣传以兄长献策定金陵为开端，带有追述开国远见的意味；可确认的是兄弟较早进入核心军队，亲军关系为冯胜后来统率大军提供了政治基础。", ["v136_ms129_generals", "ms1"], ["v134_hongdu_poyang_system", "v134_pingjiang_siege_society"], ["yuanzhang", "xuda", "changyuchun"]),
            section("feng-2", "北伐不只有直取大都", "明朝建立后，冯胜随徐达攻取河南、山西、陕西，又在1372年三路北征中率西路进入甘肃，傅友德任其部将。三路战果不同，冯军较完整撤回并取得降附与牲畜，却因被指隐匿战利品未获预期赏赐。这说明北伐既是战斗，也是战利品登记、降众处理和统帅问责。一次胜利不会自动消除皇帝对将领资源的疑虑。", ["v136_ms129_generals", "ms2"], ["v15_xuda_1372"], ["xuda", "liwenzhong", "m136_fuyoude"]),
            section("feng-3", "1387年的招降、筑城与冲突", "纳哈出拥众驻金山并影响辽东边防，冯胜率傅友德、蓝玉等出征。明军先筑大宁等城，再借归降将领传递诏书，纳哈出在大军压力下请求投降。受降现场又因常茂砍伤纳哈出而发生惊乱。最终大量部众被收编入关，过程同时包含谈判、威慑和强制迁移，不能只称一场漂亮的大捷。", ["v136_ms129_generals", "ms2"], ["v136_naghachu_surrender"], ["m136_fuyoude", "lanyu", "yuanzhang"]),
            section("feng-4", "为何胜利后反而被夺兵权", "班师后，冯胜被告隐匿良马、索取珍宝、处置降人不当，又因后军损失受到追责；常茂也反过来揭发他。朱元璋收回大将军印，冯胜此后不再统领这样规模的军队。传记未必能让每项指控得到独立互证，但它清楚显示朝廷评价统帅不只看战果，还看军纪、财物和降附秩序。皇帝对独掌大军者的防范也由此加强。", ["v136_ms129_generals", "v4p_ms3"], ["v136_naghachu_surrender"], ["yuanzhang", "m136_fuyoude"]),
            section("feng-5", "没有完整谋反案的赐死", "冯胜后来仍参与练军、屯田，并在皇太孙建立后加太子太师。蓝玉被诛两年后，1395年冯胜被赐死，诸子不能承袭。《明史》以朱元璋晚年猜忌解释结局，却没有给出冯胜谋反的完整案情。可以讨论老将集团与皇权的紧张，也可以比较傅友德、蓝玉的命运，但不能因死亡相近就虚构共同密谋。证据不足本身应成为读者看见的历史信息。", ["v136_ms129_generals", "v2f_ms132", "v4p_ms3"], ["v136_generals_forced_deaths"], ["m136_fuyoude", "lanyu", "yuanzhang"]),
        ]),
    ]
    extensions = {
        "ma-1": "郭子兴的妻子和女儿也参与这组关系，说明婚姻不是两个人的私事，而是起事集团内部结盟、庇护与猜疑的一条通道。",
        "ma-2": "衣鞋、干粮和犒赏看似琐碎，正因史书很少逐项登记，更需要从偶然留下的记录中恢复战争如何依靠日常劳动。",
        "ma-3": "李文忠最终留任、宋濂最终免死，却不能据结果认定每段对话都照史书文字发生；传记作者也在用故事说明理想后妃应怎样约束暴怒。",
        "ma-4": "她关于先行储备胜过临时赈恤的说法，也把灾害治理从皇帝临时施恩推进到仓储准备，但实际执行规模仍需更多财政材料互证。",
        "ma-5": "画像的服饰、姿态与题名首先证明收藏和纪念传统；若没有画家、绘制年代及流传链，就不应给它贴上“真实复原”的标签。",
        "songlian-1": "地方郡学是新政权建立秩序的重要接口：它既恢复教育，也帮助召集能处理经典、礼仪和公文的人才。",
        "songlian-2": "他还随太子和诸王前往中都讲武，把经典解释带到皇室军事训练现场，文教与武备并不是两套完全分离的培养方案。",
        "songlian-3": "首修与续修相隔很短，显示朝廷急于形成完整前朝史；读者应把具体传记同元代文书、碑刻和其他史籍交叉比对。",
        "songlian-4": "外国使者购买文集的记载还提示明初文章跨越政治边界流通，不过声名远播的赞辞同样来自为文臣立传的体例。",
        "songlian-5": "宋慎与宋璲被处死、家属迁徙，责任沿亲属链扩散；这种结果比“皇帝仍念师生旧情”的温情叙述更能显示案件压力。",
        "hu-1": "从宁国知县、吉安通判到太常寺和中书省，他的履历也提醒人们：开国朝廷急需能处理地方与中央事务的行政人员。",
        "hu-2": "奏章先经过中书省本是行政分工的一部分，争议在于筛选何时越过授权、是否阻断皇帝知情；这需要制度问题而非性格标签来解释。",
        "hu-3": "废相以后没有中间机关自动解决所有问题，皇帝需要亲阅更多章奏，后来又借殿阁大学士等人员协助，权力集中同时制造新的工作机制。",
        "hu-4": "1390年李善长案距离胡惟庸之死已有十年，时间差本身就要求读者追问证词何时形成、为何此时被启用、谁从扩案中获益。",
        "hu-5": "“奸臣”是史书编排的分类，不是分析结论；分类能够保存材料，也会预先告诉读者应该用什么道德框架理解人物。",
        "muyang-1": "朱元璋收养的异姓子不止一人，沐英后来成就最显著；这说明养子网络既有家庭情感，也承担培养可靠军政代理人的功能。",
        "muyang-2": "他曾受命在关陕询问民间不便并上报调整，表明将领出行还可能承担巡视职责，军事经验与地方行政在其生涯中逐步合流。",
        "muyang-3": "曲靖渡江、大理上下关等细节展现地形对战术的影响；但后世传记偏重胜方视角，败者与被征服社群的记忆保存明显较少。",
        "muyang-4": "所谓垦田数量来自功臣传的总括，难以直接等同于新增加的净耕地；其中可能包含接管、重报和不同年度的累计。",
        "muyang-5": "沐氏后代与中央皇室保持婚姻和军职联系，使云南既非普通内地省份的复制，也不是完全独立的世袭领地。",
        "fu-1": "不同阵营都需要有实战经验的基层军官，归附者也会带来原部众和地方知识；胜利王朝后来往往把这些转换压缩成识主故事。",
        "fu-2": "木牌顺江传讯等情节适合说明多路军如何沟通，却不宜加工成神奇计谋；真正困难仍是山川阻隔下的协同、补给与时机。",
        "fu-3": "傅友德在乌撒等地筑城并继续处理反抗，表明征南将军的职责从突破防线延伸到建立可供驻守的交通和据点。",
        "fu-4": "亲王节制宿将既提供皇室学习统军的机会，也改变将领直接受皇帝指挥的关系，为洪武末年的军权安排留下张力。",
        "fu-5": "请求田地的记载只能证明君臣曾有不快，不能承担解释死亡的全部重量；原因不明时明确写出“不明”比补齐戏剧细节更可靠。",
        "feng-1": "冯胜曾因高邮战事失误受杖责，显示早期亲信也受军令约束；把传记只整理成连续胜绩，会看不到其指挥生涯的反复。",
        "feng-2": "甘肃方向的降附、牲畜与人口又关系边地经济，远征成果不仅是地图推进，也包括国家如何登记、迁置并使用新取得的资源。",
        "feng-3": "纳哈出部众以家庭和牲畜为重要组成，所谓二十万人不只是士兵；迁入关内意味着生活空间和政治归属同时被改变。",
        "feng-4": "夺印后他仍奉朝请并承担局部任务，说明失去大军指挥权不等于立即成为罪犯，政治位置是在处分中逐级收缩的。",
        "feng-5": "传记以“猜忌”概括皇帝晚年心理，只能作为清代史官的解释；更可核的是统兵资格被削、赐死及爵位断绝这些制度结果，也应保留史料没有说明的部分。",
    }
    for item in articles:
        for item_section in item["sections"]:
            item_section["text"] += extensions[item_section["id"]]
        item["sources"] = list(dict.fromkeys(source for item_section in item["sections"] for source in item_section["sources"]))
    for item in articles:
        upsert_article(data["articles"], item)

    for link in [
        {"from": "m136_muying", "to": "yuanzhang", "kind": "adoptiveFather", "sources": ["v136_ms126_muying"], "note": "幼年由朱元璋收养，一度从朱姓，成年后复沐姓。"},
        {"from": "m136_muying", "to": "ma", "kind": "adoptiveMother", "sources": ["v136_ms126_muying", "v2e_ms113"], "note": "《明史》记朱元璋与孝慈皇后共同抚养。"},
    ]:
        upsert_family(data["familyLinks"], link)

    associations = [
        {"from": "ma", "to": "m136_songlian", "role": "为其免死进言的皇后", "inverse": "受其劝救的太子师", "period": "1380", "note": "劝谏细节见后妃传与宋濂传，结果是由死刑改为安置茂州。", "sources": ["v2e_ms113", "v136_ms128_songlian"]},
        {"from": "m136_songlian", "to": "biao", "role": "长期教授经史与礼法的老师", "inverse": "接受其讲授的皇太子", "period": "1360年代—1377", "note": "教育影响不等于宋濂能够决定太子全部政治立场。", "sources": ["v136_ms128_songlian", "ms2"]},
        {"from": "m136_huweiyong", "to": "lishanzhang", "role": "受其荐举并形成姻亲往来的丞相", "inverse": "荐举者、后来被追入其案", "period": "洪武前中期", "note": "交往和姻亲可核，不足以单独证明共同谋反。", "sources": ["v136_ms308_hu", "v2f_ms127"]},
        {"from": "m136_huweiyong", "to": "liuji", "role": "在相位人选与晚年案情中同其冲突", "inverse": "曾批评其能力与品行的文臣", "period": "洪武前期", "note": "毒杀刘基的说法来自后出的案件叙事，不作无争议定论。", "sources": ["v136_ms308_hu", "v15_ms128"]},
        {"from": "m136_fuyoude", "to": "m136_muying", "role": "征云南主将", "inverse": "征云南副将、后留镇当地", "period": "1381—1382", "note": "两人分工随战役阶段变化，不能把全部战果归于一人。", "sources": ["v136_ms129_generals", "v136_ms126_muying"]},
        {"from": "m136_fengsheng", "to": "m136_fuyoude", "role": "北征主将与同僚", "inverse": "副将与长期军中同僚", "period": "1372—1392", "note": "共同参与甘肃、辽东及练军屯田等任务。", "sources": ["v136_ms129_generals", "v4p_ms3"]},
        {"from": "m136_muying", "to": "lanyu", "role": "云南战役副将与同僚", "inverse": "云南战役副将与同僚", "period": "1381—1382", "note": "二人都受傅友德节制，沐英后来留镇云南。", "sources": ["v136_ms126_muying", "v2f_ms132"]},
    ]
    for association in associations:
        upsert_association(data["associations"], association)

    data["version"] = 110
    data["reviewed"] = "2026-10-29"
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
