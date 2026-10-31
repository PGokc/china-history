#!/usr/bin/env python3
"""Deepen Hongzhi governance through personnel, frontier, river and fiscal systems."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "App/Resources/history.json"
NARRATION = ROOT / "App/Resources/narration_manifest.json"


def upsert(items: list[dict], item: dict, key: str = "id") -> None:
    for index, old in enumerate(items):
        if old.get(key) == item[key]:
            items[index] = item
            return
    items.append(item)


def section(sid: str, title: str, text: str, sources: list[str], events: list[str], people: list[str]) -> dict:
    return {"id": sid, "title": title, "text": text, "kind": "史实与解读", "sources": sources, "events": events, "people": people}


def article(person: str, title: str, dek: str, sections: list[dict]) -> dict:
    sources: list[str] = []
    for item in sections:
        for source in item["sources"]:
            if source not in sources:
                sources.append(source)
    return {"person": person, "title": title, "dek": dek, "sections": sections, "sources": sources}


def upsert_association(data: dict, item: dict) -> None:
    for index, old in enumerate(data["associations"]):
        if old["from"] == item["from"] and old["to"] == item["to"]:
            data["associations"][index] = item
            return
    data["associations"].append(item)


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for source in data["sources"]:
        if source["id"] == "v42m_ms182":
            source["title"] = "《明史》卷182 · 王恕、马文升、刘大夏传"
            source["note"] = "清修正史开放转录，用于核对王恕地方赈济与吏部争议、马文升边政与赋役奏议、刘大夏河工和兵政。列传以老成名臣为编纂框架，奏报数字、君臣对话和声望评价仍须与本纪、志书互证。"
    upsert(data["sources"], {"id": "v142_ms80", "title": "《明史》卷80 · 食货志四·盐法与茶马", "url": "https://zh.wikisource.org/zh-hans/明史/卷80", "note": "清修食货志开放转录，用于核对弘治五年盐引折银、边地开中变化、盐商守支及弘治茶马政策。制度志总结长期变化，不能把后果全部归给一次改革，也不能把账面银收入等同于边镇实物供应。"})

    people = [
        {"id": "m142_wangshu", "name": "王恕", "call": "把地方赈济、吏部铨选与公开争论连在一起的弘治老臣", "temple": "—", "era": "正统—弘治", "reign": "1416—1508", "summary": "从司法、知府、巡抚和河道治理积累地方经验，成化朝反复批评采办与权幸；弘治初主持吏部，坚持任命应由有职官署负责，后因与丘濬冲突退职。", "parent": None, "sources": ["v42m_ms182", "v2l_ms15", "v141_ms77"], "kind": "吏部与地方治理大臣", "note": "字宗贯，陕西三原人。官修传记突出其刚直声望，也保留自撰行状和人事冲突；不能把每次反对意见自动视为正确。", "dynasty": "ming"},
        {"id": "m142_liudaxia", "name": "刘大夏", "call": "从张秋治河到军饷与京营改革的弘治兵部尚书", "temple": "—", "era": "成化—正德", "reign": "1437—1516", "summary": "由兵部职方官转任地方，弘治年间主持张秋治河、宣府粮储与两广治理，晚年任兵部尚书，揭示军士被克扣、额外采办和京营控制问题。", "parent": None, "sources": ["v42m_ms182", "v42m_ms83", "v2l_ms15"], "kind": "河工与兵政大臣", "note": "字时雍，湖广华容人。传统名臣传中的君臣问答和后世颂誉需要互证；治河工程的阶段性效果不应写成永久驯服黄河。", "dynasty": "ming"},
    ]
    for person in people:
        upsert(data["people"], person)
    for person in data["people"]:
        if person["id"] == "m42_mawensheng":
            person.update({"call": "把边防、军粮、灾荒和繁重差役放在同一张财政图上的弘治重臣", "summary": "从御史与西北、辽东边务进入兵部，弘治朝长期整顿将校、团营、屯田和马政；又以漕运、治河、王府营建和地方灾荒说明民力已近极限。", "sources": ["v42m_ms182", "v2l_ms15", "v42m_ms73", "v142_ms80"]})

    events = [
        {"id": "v142_wangshu_yangzhou_relief", "year": "1450年代", "title": "王恕在扬州先发粮赈灾，再补报朝廷", "category": "社会", "body": "王恕任扬州知府时遇饥荒，先开仓发粮而没有等待完整上报程序。地方官面对饥民时，时效可能比文书齐备更重要；这也要求事后留下灾户、粮数与追补记录。", "impact": "列传以果断塑造能吏，但没有保存逐户发放账册，不能由“不待报”推定救济没有遗漏或侵占。它更适合说明授权边界：紧急处置与事后审计必须同时存在。", "people": ["m142_wangshu"], "sources": ["v42m_ms182", "v2l_ms15"], "kind": "地方赈济"},
        {"id": "v142_nanzhili_white_grain", "year": "1470—1480年代", "title": "南直隶白粮、上供与织造把额外损耗压给运输家庭", "category": "经济", "body": "王恕巡抚南直隶时指出，江南白粮运输可使民户破产，光禄监收又索取额外耗羡；织造、花木禽鸟采办往来不绝。官方正额之外，包装、脚费、等候和索取构成隐性成本。", "impact": "列传没有给出各府统一比例，不能虚构每户负担；但它揭示账面税额不足以解释真实成本。王恕多次上疏未被采纳，也说明提出问题与改变供应链是两件事。", "people": ["m142_wangshu", "jianshen"], "sources": ["v42m_ms182", "v141_ms77"], "kind": "贡赋与运输"},
        {"id": "v142_hongzhi_appointments", "year": "1488—1493年", "title": "王恕以吏部职权抵制中旨改换人选", "category": "政治", "body": "弘治初，王恕在巡抚、营造授官、外戚升迁和御医进秩等事项上反复要求按吏部资格和责任办理。他认为若皇帝否定所荐者，应公开说明理由，而不应让近臣预定人选。", "impact": "坚持官署职掌能提高可追责性，不等于吏部选择天然无私。王恕与丘濬后来在人事考核上激烈冲突，提醒我们程序原则仍需案卷、回避和复核，而不能只依赖刚直声望。", "people": ["m142_wangshu", "m42_qiujun"], "sources": ["v42m_ms182", "v40m2_ms181", "v2l_ms15"], "kind": "铨选与中旨"},
        {"id": "v142_ma_grain_relief", "year": "1485年", "title": "淮、徐、和州饥荒以漕粮与盐价银共同救济", "category": "经济", "body": "马文升总督漕运时，淮安、徐州、和州受灾，他调江南粮十万石、盐价银五万两赈济。做法把现有漕粮和专卖收入转为救荒资源，显示不同财政账户可以在紧急时重新调配。", "impact": "十万石与五万两是列传奏报口径，不能证明全部到户。调粮还涉及仓储、船运和原定军需，评价救济须追踪到运输时间、受灾名单与是否挤压其他供应。", "people": ["m42_mawensheng"], "sources": ["v42m_ms182", "v142_ms80"], "kind": "漕运与赈济"},
        {"id": "v142_hami_campaign", "year": "1490年代", "title": "哈密危机在互市、羁縻与有限用兵之间选择", "category": "军事", "body": "吐鲁番势力控制哈密并迫使周边部众依附后，马文升调查道路和当地兵力，主张由罕东、赤斤、哈密兵配合明军采取有限行动，同时对其他部众的入贡与互市分别处理。", "impact": "边疆并非两方对战，哈密、吐鲁番、罕东等政治体各有利益。列传的“果克”省略协作者损失与后续控制成本，不能把一次军事恢复写成长期稳定或单纯中央胜利。", "people": ["m42_mawensheng"], "sources": ["v42m_ms182", "v2l_ms15"], "kind": "西北边务"},
        {"id": "v142_prince_education", "year": "1495年前后", "title": "太子教育被理解为讲读、照料与宫廷环境的共同责任", "category": "文化", "body": "马文升主张太子幼年即选择熟悉书史、品行谨慎的照料者，从言语举止开始教育，并限制过度宴游表演。建议体现当时以经史、礼制和日常模仿塑造君主的观念。", "impact": "这套方案带有十五世纪儒家和宫廷等级价值，不能视作现代儿童教育规范；其制度意义在于承认教育不只发生在讲筵，身边人员和娱乐安排同样塑造未来决策者。", "people": ["m42_mawensheng", "m40_liujian", "m40_xieqian"], "sources": ["v42m_ms182", "v40m2_ms181"], "kind": "东宫教育"},
        {"id": "v142_zhangqiu_river", "year": "1493—1495年", "title": "张秋治河先分泄上游，再塞决口和筑长堤", "category": "经济", "body": "黄河冲入张秋、威胁运河后，刘大夏先疏贾鲁河、孙家渡和四府营故道分散水势，再以沉船、大埽和石堤堵塞决口，并修筑连接多州县的长堤。", "impact": "工程恢复了阶段性漕运，却征用大量夫役、木石和船只，水流后来仍反复迁徙。河渠志保存工程次序与尺度，数字是官府工程记录；不能把成功命名“安平”写成黄河从此安定。", "people": ["m142_liudaxia", "m142_wangshu"], "sources": ["v42m_ms83", "v42m_ms182"], "kind": "河工与漕运"},
        {"id": "v142_xuanfu_grain_market", "year": "1497年", "title": "宣府边粮采购降低门槛，削弱势家垄断", "category": "经济", "body": "刘大夏处理宣府兵饷时，取消只有大宗粮草才能报纳的高门槛，允许十石粮、百束草以上的小额供应者参与。原先控制大额采购的中官、武臣家庭失去部分差价。", "impact": "开放采购可扩大供应和降低垄断，并不保证所有小户都能承担运输、验收与等候成本。列传称两月储备充足，应理解为阶段性奏报，仍需结合仓册和边军实际领粮。", "people": ["m142_liudaxia", "m42_mawensheng"], "sources": ["v42m_ms182", "v2l_ms15"], "kind": "边粮市场"},
        {"id": "v142_sixteen_reforms", "year": "1502—1504年", "title": "十六项清弊在涉及权贵时遭遇反复复核", "category": "政治", "body": "刘大夏与廷臣汇总传奉官、内官增设、禁军空额、织造、斋醮和光禄浮费等十六项问题。外朝事项较易获准，涉及权贵与宫廷者则被要求再次核查，最终只部分实施。", "impact": "部分织造、斋醮和浮费确有削减，不能据此宣称积弊尽除。改革清单显示权力边界：证据相同的事项，只因利益主体不同就面临不同审查强度。", "people": ["m142_liudaxia", "m40_liujian", "m42_mawensheng"], "sources": ["v42m_ms182", "v40m2_ms181", "v2l_ms15"], "kind": "财政与宫廷清弊"},
        {"id": "v142_soldier_pay_clawback", "year": "1504年", "title": "边军名义有月粮、行粮，实际所得却被将领侵扣", "category": "社会", "body": "孝宗询问军士既有月粮、出征又有行粮，为何仍贫困。刘大夏回答将领侵克过半，并把广西木材、广东香药等额外采办与军民困乏并列。皇帝随后命令禁止。", "impact": "君臣对话由官修传记整理，不能当作逐字记录；它仍揭示制度账面与实际收入的差距。禁令若没有独立核饷、申诉和惩处，无法证明克扣已经消失。", "people": ["m142_liudaxia", "m42_mawensheng", "m40_liujian"], "sources": ["v42m_ms182", "v2l_ms15"], "kind": "军士生计"},
        {"id": "v142_salt_silver_reform", "year": "1492年", "title": "盐引纳银缓解商人守支，却削弱边地粮草开中", "category": "经济", "body": "叶淇建议盐商向运司纳银，银解太仓再分给边镇，商人不必长期等待支盐。太仓短期积银增加，但原本赴边输粮换取盐引的开中、商屯和边地粮源随之收缩。", "impact": "银收入和实物供应不是同一指标。食货志把后来边储困难与改革相连，但盐法变化由守支、私盐、权势请引和市场价格共同造成，不能用单一政策解释全部后果。", "people": ["m42_mawensheng", "m40_liujian"], "sources": ["v142_ms80", "v2l_ms15"], "kind": "盐法与边储"},
    ]
    for event in events:
        upsert(data["events"], event)

    S182, S15, S83, S73, S80, S181, S77 = "v42m_ms182", "v2l_ms15", "v42m_ms83", "v42m_ms73", "v142_ms80", "v40m2_ms181", "v141_ms77"
    readings = [
        article("m142_wangshu", "王恕：刚直之外，铨选与地方财政怎样落地", "他的声望来自持续发言，也来自知府、巡抚、河道和吏部的具体经历；反对中旨不等于所有判断都无需复核。", [
            section("v142_wangshu_s1", "先发赈粮，再补行政程序", "王恕从大理寺司法官转任扬州知府，遇饥荒时不等上报完成便发粮赈济。紧急状态下，迟延可能直接增加死亡，地方官需要一定临机权限；但速度不能替代事后账册和受灾核验。列传以此证明治行优异，没有留下完整仓单与户册，因此不能推定所有粮食都准确到户。王恕的价值不在“敢违程序”，而在提醒制度应预先规定何时可先行动、何时必须追补审核。", [S182, S15], ["v142_wangshu_yangzhou_relief"], []),
            section("v142_wangshu_s2", "荆襄与河道经历改变问题尺度", "成化初，王恕参与荆襄军事与流民复业，要求约束部队不得滥杀；后来总督河道，修湖塘水闸。列传把结果集中在大臣行动，普通家庭面对的迁返、土地和劳役更复杂。治水也不是一次工程：水位、淤积、运道与农田利益会不断变化。这些经历使他理解中枢命令落地时的成本，也不能据此把每项地方决断都视为仁政。", [S182, S83], ["v140_jingxiang_campaign", "v142_zhangqiu_river"], ["m140_xiangzhong", "m140_yuanjie"]),
            section("v142_wangshu_s3", "白粮、上供与隐藏在正额外的成本", "巡抚南直隶时，王恕看到白粮运输使民户破产，监收者索取耗羡，织造和花木禽鸟采办又不断经过道路。税册只写应纳数量，却常不写包装、脚费、等候、损耗与额外索取。列传没有各府逐年账目，不能编出统一负担比例；它仍证明宫廷消费与地方财政通过供应链相连。多次上疏未被采纳，则显示发现问题和改变利益结构之间存在距离。", [S182, S77], ["v142_nanzhili_white_grain"], ["jianshen"]),
            section("v142_wangshu_s4", "吏部为何要对推荐负责", "弘治即位后，王恕主持吏部。他反对用中旨跳过推荐程序，理由不是文官天然更贤，而是有职官署应为所荐者表现负责。皇帝若拒绝人选，也应说明理由，避免近臣预定空缺。营造授官、外戚求迁和御医超擢都是同一程序问题。王恕的坚持提高公开性，却仍需要回避、考核与监察；否则吏部也可能形成自己的关系网络。", [S182, S15], ["v142_hongzhi_appointments"], ["m42_qiujun"]),
            section("v142_wangshu_s5", "与丘濬冲突暴露刚直政治的限度", "王恕考察官员后，丘濬主张保留九十余人，双方又因刘文泰告发和王恕自撰传记激烈冲突。谁更正直不能替代逐案证据：考核可能误伤，阁臣留人也可能夹带私怨。孝宗最终责王恕沽名、让其退职，处理同样受皇帝好恶影响。官修史倾向同情王恕，应保留这一编纂立场。制度需要让争议进入可复核案卷，而不是靠两位名臣的声望决胜。", [S182, S181, S15], ["v142_hongzhi_appointments"], ["m42_qiujun", "m40_liujian"]),
        ]),
        article("m42_mawensheng", "马文升：边防不能脱离饥荒、运输与民力", "他以军政见长，却不断把边疆安全拉回粮价、转运、王府工程和地方劳役；这比单列战功更接近弘治治理。", [
            section("v142_mawensheng_s1", "西北、辽东与近侍边功", "马文升由御史进入西北军务，参与镇压满四，又在辽东处理军纪和部族关系。他反对将士以罚马、冒功方式激化矛盾，因此遭陈钺、汪直排挤并被谪戍。列传突出其不屈，也记录他曾参与严厉用兵；边地居民和不同部众不能被统一写成寇。近侍、边将与巡抚争夺战功时，战果核验和市场禁令都可能成为攻击工具。", [S182, "v40m1_ms304"], ["v140_west_factory_border"], ["m40_wangzhi", "m42_yuzijun"]),
            section("v142_mawensheng_s2", "赈灾调动的不只是粮仓", "总督漕运时，马文升面对淮、徐、和州饥荒，调江南粮与盐价银赈济。粮食需要仓储、船只和沿途交接，银则要面对当地粮价与兑换渠道；两种资源不能只按奏报数字相加。列传称十万石、五万两，是中枢认可的调度规模，不是逐户收讫证明。救荒还可能挤压原定漕运和边饷，因此透明排序与灾后结算同样重要。", [S182, S80], ["v142_ma_grain_relief"], ["m142_wangshu"]),
            section("v142_mawensheng_s3", "团营整顿与哈密行动的不同节奏", "弘治朝马文升长期掌兵部，审核团营将校、裁汰贪懦者，并处理大同与哈密局势。面对小王子驻牧，他主张密备而不轻启大战；哈密危机则调动周边部众和有限明军行动。两种判断说明边防没有固定答案，需比较情报、补给和政治目标。列传的胜利语言省略盟友损失与后续成本，不能把短期恢复等同于永久控制。", [S182, S15], ["v142_hami_campaign", "v141_border_finance_1501"], ["m40_liujian", "m142_liudaxia"]),
            section("v142_mawensheng_s4", "赋役全景比一项减免更接近民困", "马文升把边粮运输、治河夫役、苏松水利、王府营建、地方战争和织造放在同一奏疏中。他给出的税率、役夫与运输损耗是劝谏和官府统计口径，不能当作现代全国抽样；但这些项目确会在同一家庭劳力和财物上叠加。所谓节用不只是皇帝少一场宴游，而是减少临时科派、缩短工程、赈济灾户并核查运输中的额外损耗。", [S182, S15, S77], ["v141_border_finance_1501", "v142_nanzhili_white_grain"], ["m40_liujian", "m40_xieqian"]),
            section("v142_mawensheng_s5", "老成声望也不能替代制度", "马文升晚年转任吏部，孝宗在暖阁嘱其公正考察。太子教育建议又把照料者、讲读和宫廷娱乐纳入政治准备。正德初，他按遗诏清退传奉官，却因近侍要求复用人员而受阻，最终离职。清退七百余、保留十七等数字是名册口径，不是逐人能力判决。弘治时期的信任能扩大其作用，却没有把铨选和兵政变成跨君主稳定执行的规则。", [S182, S15, S181], ["v142_prince_education", "v141_hongzhi_accession_cleanup"], ["m142_wangshu", "m40_liujian"]),
        ]),
        article("m142_liudaxia", "刘大夏：河道、边粮与军士实际所得", "他最重要的贡献不是留下几句名臣格言，而是反复追问账面制度为何到军民手中已经变形。", [
            section("v142_liudaxia_s1", "职方司里先阻止一场轻率战争", "刘大夏在兵部职方任职时，汪直因安南与老挝冲突想调取永乐征安南旧档，谋划乘机用兵。刘大夏没有公开销毁档案，而是暂不交付并向尚书余子俊说明西南可能糜烂，计划遂止。列传写法带有名臣机智色彩，细节未必完整；其政策判断仍清楚：前代战争档案不能只当胜利模板，补给、地方社会和长期驻守成本必须重新评估。", [S182, "v40m1_ms304"], ["v140_west_factory_border"], ["m40_wangzhi", "m42_yuzijun"]),
            section("v142_liudaxia_s2", "张秋治河先处理水势", "1493年黄河冲击张秋运道，刘大夏先开越河维持漕运，再疏贾鲁河等故道分泄上游，最后以沉船、大埽和石堤合龙决口。顺序体现“先疏后塞”，不是单凭人力与洪水对撞。工程也征用民夫、军士、船只和材料，改变沿线农田受水分配。官修河渠志能说明方案与尺度，不能证明所有负担得到补偿，也不能把阶段成功写成黄河永久稳定。", [S83, S182], ["v142_zhangqiu_river"], ["m142_wangshu"]),
            section("v142_liudaxia_s3", "边粮采购为何要拆掉大额门槛", "处理宣府兵饷时，刘大夏发现只有势家能满足千石粮、万束草的报纳门槛，从而控制采购差价。他把最低数量降到十石、百束，让较小供应者进入。竞争可能增加储备，也不等于普通农户都能承担运输、验收和等待。列传称两月积储有余是阶段性成果；判断长期效果还要看仓粮品质、付款时点和军士实际领到多少。", [S182, S15], ["v142_xuanfu_grain_market"], ["m42_mawensheng"]),
            section("v142_liudaxia_s4", "军士贫困来自制度之外的侵扣", "孝宗困惑军士已有月粮、行粮为何仍穷，刘大夏指出将领侵克过半，又以木材、香药等额外采办说明常额之外的负担。君臣对话由后来的列传整理，不是速记记录，但账面待遇与实得收入的差距具有制度意义。禁令只能表态，真正改变需要独立核饷、允许军士申诉，并限制将领以装备、差役等名目再次扣除。", [S182, S15], ["v142_soldier_pay_clawback"], ["m40_liujian", "m42_mawensheng"]),
            section("v142_liudaxia_s5", "改革清单触及宫廷时为何减速", "刘大夏任兵部尚书后，汇总十六项清弊，涉及传奉、禁军空额、织造、斋醮、光禄浮费和增设内官。外朝事项较易通过，触及权贵者反复复核，最终只有部分落地。他还拒绝用私密揭帖替代府部、内阁程序，并谨慎反对仓促出兵。孝宗信任提供召对机会，却没有消除宫廷利益。正德即位后清理迅速逆转，说明个人受知不是可继承制度。", [S182, S181, S15], ["v142_sixteen_reforms", "v141_border_finance_1501"], ["m40_liujian", "m42_mawensheng"]),
        ]),
    ]
    additions = {
        "v142_wangshu_s1": "赈济还应区分官仓、义仓与临时购粮，避免把不同财源都写成知府个人恩惠。地方社会是否能申诉错漏，是衡量紧急授权的重要指标。",
        "v142_wangshu_s2": "流民复业也不仅是停止杀戮，还要处理原籍追索、现居田土与税籍归属。列传一句复业，背后可能是多年才能完成的家庭重建。",
        "v142_wangshu_s3": "所谓上供并非全部无用，宫廷、祭祀和官署确有物资需求；问题在于数量、损耗和监收权缺少公开标准，使必要供应容易成为额外索取。",
        "v142_wangshu_s4": "他在推荐萧祯时以去留相争，强化了官员责任，也可能压缩不同意见空间。程序必须允许皇帝或监察官提出可核实反证，而不是只能接受或罢免尚书。",
        "v142_wangshu_s5": "王恕自刻传记又让后世材料混入自我辩护，阅读时需把本人陈述、政敌指控和官修结论分开。名声很高，不能因此省略材料来源。",
        "v142_mawensheng_s1": "茶马贸易、互市与军事巡抚在边区互相牵连，禁止农器或收紧市场也可能直接伤害日常生产。边防判断必须把交易者写回地图。",
        "v142_mawensheng_s2": "盐价银来自专卖体系，并非无成本资金：盐商、灶户和消费者分别承担课额、生产与价格。救灾调拨一端有效，也应说明另一端可能减少的用途。",
        "v142_mawensheng_s3": "团营裁汰会触动俸粮与依附关系，因此有人以匿名箭书威胁。暴力威胁不能证明被裁者全部有罪，只说明改革需要证据和安全保护。",
        "v142_mawensheng_s4": "一项工程对朝廷可能是王府落成，对家庭则是离田服役和自行备粮。只有将这些时间成本计算进去，民力才不是奏疏中的抽象词。",
        "v142_mawensheng_s5": "东宫教育中对佛道的排斥属于当时士大夫立场，不能扩大为对宗教群体的贬低。可以保留的是对儿童所处信息环境的制度关注。",
        "v142_liudaxia_s1": "对外战争是否启动，不应由能否找到旧案决定；档案提供经验，也会遮蔽地形、政权和国际关系已发生的变化。拒绝机械复刻才是这一故事的核心。",
        "v142_liudaxia_s2": "黄河分流意味着一地减灾可能把水势转向另一地，漕运畅通与农田安全也未必一致。工程评价必须同时列出受益地区和承担风险的地区。",
        "v142_liudaxia_s3": "小额供应者增加后，势家垄断受限，但官府检验权仍可能产生新的寻租。降低门槛只是市场改革第一步，公开价格与收讫凭证同样关键。",
        "v142_liudaxia_s4": "军士家庭还会承担番上、转漕和私役导致的离家成本。即使粮饷足额，长期不能耕作或照料家属，也可能使账面保障无法抵消生活损失。",
        "v142_liudaxia_s5": "名臣传喜欢把清弊归于一次召对，实际改变要由兵部、户部、内府和地方仓场共同执行。部门之间能否共享账册，比皇帝一句称善更能决定持续性。",
    }
    for reading in readings:
        for item in reading["sections"]:
            item["text"] += additions[item["id"]]
        upsert(data["articles"], reading, key="person")

    for item in [
        {"from": "m142_wangshu", "to": "m42_qiujun", "role": "在人事考核与告发案中发生冲突", "inverse": "在人事考核与告发案中发生冲突", "period": "1491—1493", "note": "双方都有制度主张与个人意气，不能只用正邪标签裁断。", "sources": [S182, S181]},
        {"from": "m142_wangshu", "to": "m142_liudaxia", "role": "以吏部尚书身份推荐其主持张秋治河", "inverse": "经其推荐由地方官转任治河重臣", "period": "1493", "note": "推荐提供人事入口，工程方案与执行责任仍由刘大夏及协作官员承担。", "sources": [S182, S83]},
        {"from": "m42_mawensheng", "to": "m142_liudaxia", "role": "先后在兵部、边防与财政清弊中协作", "inverse": "先后在兵部、边防与财政清弊中协作", "period": "1490年代—1505", "note": "二人意见常相近，并不表示所有边务判断一致。", "sources": [S182, S15]},
        {"from": "m142_liudaxia", "to": "m40_liujian", "role": "以兵部证据支持谨慎用兵和节省军费", "inverse": "以内阁奏议支持其兵政判断", "period": "1502—1505", "note": "内阁与兵部掌握信息不同，协作仍以皇帝裁决为终点。", "sources": [S182, S181]},
    ]:
        upsert_association(data, item)

    data["version"] = 116
    data["reviewed"] = "2026-10-31"
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    narration = json.loads(NARRATION.read_text(encoding="utf-8"))
    changed = {reading["person"] for reading in readings}
    narration["entries"] = [entry for entry in narration["entries"] if entry["articleID"] not in changed]
    NARRATION.write_text(json.dumps(narration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
