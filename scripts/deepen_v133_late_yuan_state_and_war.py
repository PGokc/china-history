#!/usr/bin/env python3
"""Deepen five late-Yuan actors across court, river works and regional armies."""

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


def upsert_association(items: list[dict], item: dict) -> None:
    for index, existing in enumerate(items):
        if existing.get("from") == item["from"] and existing.get("to") == item["to"]:
            items[index] = item
            return
    items.append(item)


def upsert_article(items: list[dict], item: dict) -> None:
    for index, existing in enumerate(items):
        if existing.get("person") == item["person"]:
            items[index] = item
            return
    items.append(item)


def section(sid: str, title: str, text: str, sources: list[str], events: list[str], people: list[str]) -> dict:
    return {
        "id": sid,
        "title": title,
        "text": text,
        "kind": "史实与解读",
        "sources": sources,
        "events": events,
        "people": people,
    }


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
        {
            "id": "v133_dpm_toghto",
            "title": "故宫博物院：脱脱",
            "url": "https://www.dpm.org.cn/lemmas/242735.html",
            "note": "故宫博物院人物资料，概述脱脱罢黜伯颜、恢复科举、主持三史及1355年死于朝廷斗争；具体政策与战事仍需同本纪、列传互证。",
        },
        {
            "id": "v133_dpm_chaghan",
            "title": "故宫博物院：察汗帖林儿",
            "url": "https://www.dpm.org.cn/lemmas/243673.html",
            "note": "故宫博物院人物资料，采用察汗帖林儿译名，记其1352年结集地方武装、1359年攻取汴梁、1362年在益都被刺等节点。",
        },
        {
            "id": "v133_ys187_jialu",
            "title": "《元史》卷187｜贾鲁传",
            "url": "https://zh.wikisource.org/zh-hans/元史/卷187",
            "note": "明初官修《元史》的开放转录，保存贾鲁勘河、两套方案、至正十一年施工及其官历；工程数字与功绩叙述带有官修表彰立场。",
        },
        {
            "id": "v133_ys141_chaghan",
            "title": "《元史》卷141｜察罕帖木儿传",
            "url": "https://zh.wikisource.org/zh-hans/元史/卷141",
            "note": "明初官修《元史》的开放转录，记录察罕帖木儿与扩廓帖木儿的地方军队、汴梁和益都战事及元末军阀冲突；忠义评价不能代替战争影响分析。",
        },
        {
            "id": "v133_ys044",
            "title": "《元史》卷44｜顺帝本纪七",
            "url": "https://zh.wikisource.org/zh-hans/元史/卷044",
            "note": "明初官修《元史》的开放转录，记录至正中期各地战事与官员调动；本纪以朝廷为中心，需同地方统帅列传互证。",
        },
        {
            "id": "v133_ys045",
            "title": "《元史》卷45｜顺帝本纪八",
            "url": "https://zh.wikisource.org/zh-hans/元史/卷045",
            "note": "明初官修《元史》的开放转录，记录1358至1359年前后红巾军、汴梁与地方军队活动；贼寇称呼反映官修立场。",
        },
        {
            "id": "v133_ys046",
            "title": "《元史》卷46｜顺帝本纪九",
            "url": "https://zh.wikisource.org/zh-hans/元史/卷046",
            "note": "明初官修《元史》的开放转录，记录1360年代初山东、山西战事与察罕帖木儿之死；须与列传和明初材料互证。",
        },
        {
            "id": "v133_ms124_koke",
            "title": "《明史》卷124｜扩廓帖木儿传",
            "url": "https://zh.wikisource.org/zh-hans/明史/卷124",
            "note": "清修《明史》的开放转录，从明朝立场记扩廓帖木儿与明军交战、北元活动及其拒绝归降；姓名、功过与招降叙事须结合元方材料辨析。",
        },
        {
            "id": "v133_nmc_yuan_coins",
            "title": "中国国家博物馆：至大通宝、至正通宝",
            "url": "https://www.chnmuseum.cn/zp/zpml/201812/t20181218_25230.shtml",
            "note": "中国国家博物馆藏品资料，说明元代以纸币为主、1350年铸至正通宝及历代铜钱并用；实物可证明币制组合，不能单独换算各地物价。",
        },
        {
            "id": "v133_cssn_local_admin",
            "title": "中国社会科学网：元代地方行政文书研究",
            "url": "https://cssn.cn/lsx/lsx_zgs/202302/t20230201_5585359.shtml",
            "note": "中国社会科学网介绍黑水城文书所见至正十一年钱粮考较、仓储、税粮和地方行政流程，说明元末制度并非瞬间停止运转。",
        },
        {
            "id": "v133_dpm_northern_yuan",
            "title": "故宫博物院：北元朝",
            "url": "https://www.dpm.org.cn/lemmas/243963.html",
            "note": "故宫博物院概述1368年后元廷转往上都、应昌及扩廓帖木儿等继续作战。北元是后续政治阶段，不等于1368年以前元朝统治未发生断裂。",
        },
    ]:
        upsert(data["sources"], source)

    for existing_event in data["events"]:
        if existing_event.get("id") == "v50y_late_currency" and "v133_nmc_yuan_coins" not in existing_event["sources"]:
            existing_event["sources"].append("v133_nmc_yuan_coins")

    for person in [
        {
            "id": "y_jia_lu",
            "name": "贾鲁",
            "call": "治河总负责人",
            "temple": "—",
            "era": "顺帝时期",
            "reign": "1297—1353",
            "summary": "先勘河提出两套方案，1351年主持疏塞并举的大规模治河；工程成效、征役成本与同年起义须分别辨析。",
            "kind": "大臣",
            "note": "字友恒，河东高平人；不要把民间石人传说当作治河或红巾军起事的完整解释。",
            "sources": ["v133_ys187_jialu", "v43y_ys041", "v133_cssn_local_admin"],
            "dynasty": "yuan",
        },
        {
            "id": "y_chaghan_temur",
            "name": "察罕帖木儿",
            "call": "元末地方军统帅",
            "temple": "—",
            "era": "顺帝至正时期",
            "reign": "生年不详—1362",
            "summary": "由沈丘地方武装起家，收复汴梁并进攻山东红巾军；军功强化了中央不得不依赖的区域军事集团。",
            "kind": "将领",
            "note": "字廷瑞，故宫页面作察汗帖林儿；籍贯、族属表述随材料不同，应以可核家世与活动为主。",
            "sources": ["v133_dpm_chaghan", "v133_ys141_chaghan", "v133_ys044", "v133_ys046"],
            "dynasty": "yuan",
        },
        {
            "id": "y_koke_temur",
            "name": "扩廓帖木儿",
            "call": "元末至北元将领",
            "temple": "—",
            "era": "顺帝、北元时期",
            "reign": "生年不详—1375",
            "summary": "又见王保保之名，承接察罕帖木儿军队，卷入元廷内战，并在1368年后继续为北元作战。",
            "kind": "将领",
            "note": "察罕帖木儿外甥兼养子；不同史书对姓名、出身和功过的安排带有元明双方政治立场。",
            "sources": ["v133_ys141_chaghan", "v133_ms124_koke", "v133_dpm_northern_yuan", "v43y_ys047"],
            "dynasty": "yuan",
        },
    ]:
        upsert(data["people"], person)

    for event in [
        {
            "id": "v133_bayan_court_concentration",
            "year": "1333—1340",
            "title": "蔑儿乞伯颜控制中枢与扩大排斥政策",
            "category": "社会",
            "body": "顺帝初年伯颜凭军政资历控制中枢，停罢科举并推动针对汉人、南人的限制；史书所载极端建议并非都成为正式法令。",
            "impact": "身份差别通过选官、宿卫和司法进入日常机会，但政策主张、颁行范围与地方执行必须分开核对。",
            "kind": "历史事件",
            "people": ["y_toghon_temur", "y_late_bayan", "y_toghto"],
            "sources": ["v43y_ys038", "v43y_ys138"],
        },
        {
            "id": "v133_toghto_restoration",
            "year": "1340—1344",
            "title": "脱脱更张、复科举与重开经筵",
            "category": "政治",
            "body": "伯颜被罢后，脱脱及其父马札儿台主持调整，恢复科举、重开经筵并重组部分中枢人事。",
            "impact": "这是一场统治集团内部的制度转向，不等于既有身份差别、财政压力和地方执行问题同时消失。",
            "kind": "历史事件",
            "people": ["y_toghon_temur", "y_toghto", "y_late_bayan"],
            "sources": ["v133_dpm_toghto", "v43y_ys040", "v43y_ys138"],
        },
        {
            "id": "v133_jialu_river_survey",
            "year": "1344—1351",
            "title": "贾鲁勘河、比较方案与确定故道",
            "category": "经济",
            "body": "黄河多次决口后，贾鲁往返勘察数千里，先提出筑北堤与疏塞并举、使河复故道两案，后者获脱脱与朝廷采用。",
            "impact": "治河不是一次灵感，而是测量、漕运、盐场和沿岸聚落风险之间的技术与财政选择。",
            "kind": "历史事件",
            "people": ["y_jia_lu", "y_toghto", "y_toghon_temur"],
            "sources": ["v133_ys187_jialu", "v43y_ys041"],
        },
        {
            "id": "v133_jialu_labor",
            "year": "1351",
            "title": "至正十一年河工的民夫、军士与地方供给",
            "category": "社会",
            "body": "贾鲁主持的河工调集十三路十五万民夫与十八翼两万军士，数月内完成开河、导水、堤埽等工程。",
            "impact": "工程恢复部分河道与漕运，也把粮食、木料、运输和离家服役的成本集中压向沿线社会。",
            "kind": "历史事件",
            "people": ["y_jia_lu", "y_toghto", "y_toghon_temur"],
            "sources": ["v133_ys187_jialu", "v43y_ys041", "v133_cssn_local_admin"],
        },
        {
            "id": "v133_chaghan_local_army",
            "year": "1352—1356",
            "title": "察罕帖木儿从沈丘地方武装进入官军体系",
            "category": "军事",
            "body": "察罕帖木儿与李思齐由数百地方子弟起兵，攻取罗山后获得官职，继续吸纳各地武装并扩展至万人规模。",
            "impact": "中央借地方自组织恢复战力，地方统帅也由此掌握兵员、地盘和升迁网络，军队不再完全受单一中枢直接控制。",
            "kind": "历史事件",
            "people": ["y_chaghan_temur", "y_toghon_temur"],
            "sources": ["v133_dpm_chaghan", "v133_ys141_chaghan", "v133_ys044"],
        },
        {
            "id": "v133_kaifeng_recovery",
            "year": "1359",
            "title": "察罕帖木儿攻取红巾军汴梁",
            "category": "军事",
            "body": "察罕帖木儿诸军围攻汴梁，韩林儿、刘福通撤往安丰；北方红巾军失去重要城市，但各地战争并未因此终止。",
            "impact": "收复一座都城依靠多支区域军队和长期补给，胜利同时增强统帅独立于中央的资源基础。",
            "kind": "历史事件",
            "people": ["y_chaghan_temur", "han"],
            "sources": ["v133_dpm_chaghan", "v133_ys141_chaghan", "v133_ys045"],
        },
        {
            "id": "v133_yidu_assassination",
            "year": "1362",
            "title": "益都围城、降将刺杀与军权继承",
            "category": "政治",
            "body": "察罕帖木儿围益都时，被先前归降的田丰、王士诚刺杀；其外甥兼养子扩廓帖木儿随后接掌主力。",
            "impact": "招降可以迅速扩大控制，也把旧敌带入军营核心；军权依靠私人和亲属网络完成继承。",
            "kind": "历史事件",
            "people": ["y_chaghan_temur", "y_koke_temur"],
            "sources": ["v133_dpm_chaghan", "v133_ys141_chaghan"],
        },
        {
            "id": "v133_koke_court_war",
            "year": "1363—1365",
            "title": "扩廓帖木儿、孛罗帖木儿与元廷内战",
            "category": "政治",
            "body": "扩廓帖木儿与大同的孛罗帖木儿争夺山西、河北，冲突又卷入顺帝、皇太子与宫廷集团；1364年孛罗帖木儿一度进入大都。",
            "impact": "元军仍有战斗力，却被用于争夺中枢和地方地盘，削弱了共同应对江淮各政权的能力。",
            "kind": "历史事件",
            "people": ["y_koke_temur", "y_toghon_temur"],
            "sources": ["v133_ys141_chaghan", "v43y_ys047"],
        },
        {
            "id": "v133_koke_northern_yuan",
            "year": "1368—1375",
            "title": "大都失守后扩廓帖木儿继续北元作战",
            "category": "军事",
            "body": "明军进入大都后，扩廓帖木儿没有随中原政权易代而消失，继续在山西、甘肃与漠北方向支持元廷并同明军作战。",
            "impact": "1368年是元朝失去中原首都和全国统治的断点，不是蒙古政治力量或元廷军事网络瞬间终结。",
            "kind": "历史事件",
            "people": ["y_koke_temur", "y_toghon_temur"],
            "sources": ["v133_ms124_koke", "v133_dpm_northern_yuan", "v43y_ys047"],
        },
    ]:
        upsert(data["events"], event)

    for association in [
        {"from": "y_late_bayan", "to": "y_toghto", "role": "侄子、早年受其提携并参与罢黜者", "inverse": "伯父、政治庇护者与被其参与罢黜的权臣", "period": "1330年代—1340", "note": "亲属庇护与政治分裂并存，不能简化成固定族群阵线。", "sources": ["v43y_ys138", "v133_dpm_toghto"]},
        {"from": "y_toghto", "to": "y_jia_lu", "role": "支持治河方案并授予工程权限的丞相", "inverse": "负责勘测、方案与施工的治河官员", "period": "1349—1351", "note": "脱脱提供政治支持，贾鲁承担技术和现场组织；河工不是一人独力完成。", "sources": ["v133_ys187_jialu", "v43y_ys041"]},
        {"from": "y_chaghan_temur", "to": "y_koke_temur", "role": "外甥兼养子、军队继承者", "inverse": "舅父兼养父、前任统帅", "period": "1350年代—1362", "note": "察罕帖木儿遇刺后，扩廓帖木儿依靠亲属和军中网络接掌主力。", "sources": ["v133_ys141_chaghan", "v133_ms124_koke"]},
        {"from": "y_toghon_temur", "to": "y_koke_temur", "role": "后期倚重又反复削夺其权力的统帅", "inverse": "授官、削权并再度倚重他的皇帝", "period": "1362—1370", "note": "皇帝、皇太子和地方军集团之间既合作又冲突，扩廓帖木儿并非始终服从统一指挥。", "sources": ["v133_ys141_chaghan", "v43y_ys047", "v133_dpm_northern_yuan"]},
    ]:
        upsert_association(data["associations"], association)

    articles = {
        "y_late_bayan": article(
            "y_late_bayan", "伯颜：军功怎样变成顺帝初年的中枢垄断", "同名统帅必须分开，排斥政策也要区分提议、法令与实际执行。", [
                section("v133_bayan_s1", "先分清两位伯颜", "顺帝初年的伯颜出自蔑儿乞部，约生于1280年，曾在武宗及其后朝廷积累军政资历。他不是忽必烈时期统军灭宋的八邻部伯颜：后者在1295年已经去世，活动年代相隔数十年。两人在汉文中同名，却有不同部属、亲族和功业。蔑儿乞伯颜参加1328年两都之战，站在大都与文宗一方，军功使他进入中枢。宁宗早逝、妥懽帖睦尔继位又被拖延时，掌握宿卫和军政经验的重臣能够影响交接。先辨清人物，才能明白顺帝初年的停科举、权臣政治和脱脱政变都属于十四世纪的另一条经历，而不是灭宋名将晚年。", ["v43y_ys138", "v43y_ys038", "v132_dpm_yuanshi_benji"], ["v43y_two_capitals", "v43y_shun_accession"], ["y_bayan", "y_toghon_temur", "y_toghto"]),
                section("v133_bayan_s2", "幼帝即位为何让军政重臣坐大", "妥懽帖睦尔1333年即位时尚年轻，燕铁木儿刚刚去世，卜答失里太后、宿卫将领和中书大臣之间需要重新分配权力。伯颜凭两都之战军功与军队联系出任右丞相，逐步压过其他官员。权臣坐大并非皇帝完全不存在，而是奏报、人事、兵权和接近皇帝的通道集中在少数人手中。顺帝仍能发布诏令，地方官署仍运作；但某项建议能否到达皇帝、反对者能否保住职位，受到伯颜集团影响。把这一阶段只写成“昏君遇奸臣”会遮蔽制度机制：幼年继承、宿卫控制、拥立功劳和中书程序共同制造了不对称。", ["v43y_ys038", "v43y_ys138", "v132_cssn_official_docs"], ["v43y_shun_accession"], ["y_toghon_temur", "y_budashiri", "y_yan_tiemuer"]),
                section("v133_bayan_s3", "停罢科举改变了谁的仕进通道", "伯颜主政期间停罢科举，恢复时间要等到他失势以后。元代入仕本来就有荫叙、吏员、荐举、宿卫与科举等多条通道，停科举不会让全部官员任用停止，却会直接缩小依靠经学考试进入官场的机会。受影响者也不只是一群抽象士人：地方学校、家庭教育投入和未来职位预期都会随之改变。伯颜及支持者把科举与特定政治群体相联系，反对者则把恢复考试作为朝政转向的标志。不能夸大元代科举覆盖面，也不能因为录取人数有限就说停罢毫无社会意义。选官通道决定哪些知识和关系能被国家承认。", ["v43y_ys038", "v43y_ys138", "v133_dpm_toghto"], ["v43y_bayan_exam", "v133_bayan_court_concentration"], ["y_toghon_temur", "y_toghto"]),
                section("v133_bayan_s4", "极端言论不等于全部成为法令", "《元史》记伯颜排斥汉人、南人，并保存若干极端主张。阅读这些材料必须区分三个层次：权臣或近臣提出过什么，皇帝正式批准了什么，地方又实际执行到何种范围。现有记录足以说明身份不平等和排斥政策真实存在，却不足以把所有惊人言论都写成全国完成实施的制度。蒙古、色目官员内部也并非立场一致，脱脱与父亲马札儿台后来参与罢黜伯颜，并恢复科举。分歧既涉及治理理念，也涉及皇权、家族安全和官位竞争。指出材料边界不是淡化歧视，而是让读者看清不平等通过任官、宿卫、法律和机会结构分别发生。", ["v43y_ys138", "v43y_ys040", "v133_dpm_toghto"], ["v133_bayan_court_concentration", "v133_toghto_restoration"], ["y_toghto", "y_toghon_temur"]),
                section("v133_bayan_s5", "1340年罢黜为何是一场宫廷政变", "1340年顺帝与脱脱、马札儿台等秘密合作，趁伯颜离开大都时剥夺其权位，随后把他贬出中枢；伯颜在南行途中去世。行动依靠皇帝名义、宿卫配合和信息保密，说明罢免权臣并非一次普通行政调任。脱脱是伯颜之侄，早年受其提携，亲属关系却没有消除政治冲突。事后恢复科举、重开经筵并调整人事，被概括为“更张”；但换掉权臣不会自动修复财政、身份差别和地方负担。官修史严厉批评伯颜，也服务于证明新政正当。评价他既要承认具体排斥与专权，也要把个人权势放回幼帝继承和军政资源集中的结构中。", ["v43y_ys040", "v43y_ys138", "v133_dpm_toghto"], ["v43y_bayan_fall", "v133_toghto_restoration"], ["y_toghto", "y_toghon_temur"]),
            ]
        ),
        "y_toghto": article(
            "y_toghto", "脱脱：更张、修史、治河与高邮罢兵", "同一名丞相既推动制度修复，也组织大工程和镇压战争，不能只留下忠臣标签。", [
                section("v133_toghto_s1", "从伯父门下走向罢黜伯父", "脱脱生于1314年，字大用，出自蔑儿乞部，父亲马札儿台与伯父伯颜都处在高层军政网络中。他早年获得职位离不开家族庇护，却在伯颜控制中枢、排斥异己后转而与顺帝合作。1340年的行动既可解释为恢复皇权与制度程序，也涉及家族自保和新集团争夺中枢。正史用“大义灭亲”组织人物道德，真实政治则需要宿卫、父亲、皇帝近臣共同配合。蒙古出身的脱脱主张恢复科举和经筵，也说明元廷冲突不能被压成蒙古与汉人的两队对抗；身份、亲属、官署利益和治理选择交叉在同一个人身上。", ["v43y_ys138", "v133_dpm_toghto", "v43y_ys040"], ["v43y_bayan_fall", "v133_toghto_restoration"], ["y_late_bayan", "y_toghon_temur"]),
                section("v133_toghto_s2", "“更张”恢复了什么，又没有解决什么", "伯颜失势后，脱脱及马札儿台一方恢复科举、重开经筵，撤改部分人事和政策。这些措施重新承认经学考试与公开讲论的政治价值，也让被排斥官员获得回归机会。但更张不是现代意义的平等改革：多种任官通道和身份差别仍在，宗王岁赐、宫廷支出、军费与地方税粮压力也没有消失。脱脱本人后来一度退居，再次入相后才承担治河和军事。把1340年至1355年写成连续不变的一套改革，会忽略其两次执政及政治环境变化。制度修复能改善程序，却必须依赖财政、官员和地方执行，不能凭“贤相”名声自行运转。", ["v133_dpm_toghto", "v43y_ys040", "v43y_ys138"], ["v133_toghto_restoration", "v43y_bayan_exam"], ["y_toghon_temur", "y_late_bayan"]),
                section("v133_toghto_s3", "三史并修不是脱脱一人写成", "至正初年朝廷正式推进辽、金、宋三史，脱脱以总裁身份主持。长期争议之一是三个并立政权如何安排正统，采取各修本纪的方式为成书提供了框架。具体搜集、编排和撰写由欧阳玄、揭傒斯等多位史官及书吏共同完成，脱脱不是三部史书的单独作者。成书速度快，保存了大量前代材料，也留下重复、疏漏和明初再修时的政治判断。把三史简单称作“文化功绩”会漏掉档案、人力和中枢组织；因成书仓促而否认全部价值同样失当。今天研究辽宋金并立史，仍需借助这些文本，同时与墓志、文书和考古互证。", ["v133_dpm_toghto", "v132_dpm_kuizhang", "v43y_ys041"], ["v43y_three_histories"], ["y_toghon_temur", "y_jia_lu"]),
                section("v133_toghto_s4", "支持贾鲁治河意味着承担政治风险", "黄河自至正四年起多次决口，威胁沿岸居民、运河、盐场和京师供给。贾鲁勘察后提出两案，脱脱再次入相时支持工程量更大的疏塞并举方案，并让贾鲁获得跨路调度军民的权限。工程在1351年数月内使河道恢复通航并完成多处堤埽，是可核的行政和技术成果；十余万民夫、军士的粮饷、木料和离家服役也是同一成果的成本。同年红巾军兴起，河工征役加剧不满，却不能被写成唯一原因。灾荒、钞法、税役、宗教动员和基层失控共同作用，治河有成与社会危机可以同时为真，工程成效与动员代价应放在同一条因果链中衡量。", ["v133_ys187_jialu", "v43y_ys041", "v133_cssn_local_admin"], ["v43y_river", "v133_jialu_labor"], ["y_jia_lu", "y_toghon_temur"]),
                section("v133_toghto_s5", "高邮前线罢免为何伤及整支军队", "红巾军和张士诚等势力扩张后，脱脱转而组织镇压。1354年他调集大军围攻高邮，胜负未定时，顺帝因哈麻等中枢斗争下诏罢免。将领、军队、粮饷和诸王部属围绕丞相临时组织，主帅在前线突然失权后，军队出现离散，中央协调受到重创。脱脱被流放，1355年奉诏自尽。这个结局能说明宫廷斗争破坏军事组织，却不能反推“只要不罢脱脱元朝就不会灭亡”。地方军队坐大、税源断裂、各地政权竞争早已展开。他既是制度修复者和工程支持者，也是镇压战争的统帅；被征役、围城和迁徙的人承担了这些决策的另一面。", ["v43y_ys042", "v43y_ys138", "v133_dpm_toghto"], ["v43y_toghto_dismiss", "v43y_redturban"], ["y_toghon_temur"]),
            ]
        ),
        "y_jia_lu": article(
            "y_jia_lu", "贾鲁：勘河、漕运与十五万民夫", "治河既有真实技术成效，也有集中征役成本；同年起义不能由一则石人传说解释。", [
                section("v133_jialu_s1", "治河以前，他先处理过仓粮和漕运", "贾鲁字友恒，河东高平人，早年通过明经乡贡进入仕途，做过儒学教授、县尹和中书、工部相关职务，也参加《宋史》编修。他并非突然被选中的民间水利奇才。任职中，他曾讨论河仓亏损、土地兼并、贫民流亡与漕运管理，又提出疏浚运河、调整船户和坝夫负担等事项。这些经历使他理解黄河问题不只关乎河槽，也连接粮仓、盐场、船户与京师供给。《元史》列传强调其谋略和孝行，具有传统名臣传记写法；官历与具体奏议较可核，神化式性格赞语则应与制度记录分开阅读。治河能力来自长期行政经验，而不是一段传奇式灵感。", ["v133_ys187_jialu", "v133_cssn_local_admin", "v43y_ys041"], ["v133_jialu_river_survey"], ["y_toghto"]),
                section("v133_jialu_s2", "黄河不是1351年才突然决口", "至正四年黄河决白茅堤、金堤，此后北侵运河，影响济南、河间及漕运盐场。贾鲁受命沿河往返勘察，记录地形和关键险段。河道变化来自泥沙、堤防、支流和长期人类利用，不是一场灾害或一名官员能够单独制造。他先提出两套方案：一是修筑北堤控制横溢，工程较省；二是疏浚与堵塞并举，使水流回到故道，工程更大。方案比较说明朝廷知道成本与效果存在权衡。今天不能凭后来河道继续变化否定当时工程，也不能因短期成功就说它永久解决黄河问题；河流仍会继续调整，堤防也需要长期维护。", ["v133_ys187_jialu", "v43y_ys041"], ["v133_jialu_river_survey", "v43y_river"], ["y_toghto", "y_toghon_temur"]),
                section("v133_jialu_s3", "疏、浚、塞、筑如何在数月内衔接", "1349年脱脱再次入相后重议河患，采纳贾鲁工程量更大的方案。1351年四月开工，先组织开河和疏浚，七月河槽告成，八月导水进入故道，随后继续修筑堤防和埽工，至十一月主要水土工程完成。所谓“贾鲁河”不是他凭一人之力挖出整条新河，而是对旧河道、决口和堤防系统的综合处置。皇帝授予他总治河防使等权限，使不同路、军队和地方官接受调度。工程时间表来自官修传记和河渠记录，反映朝廷认可的成果；施工现场的损耗、偷工和地方差异未必同样完整保留，碑文式功绩也不能替代工地日常记录。", ["v133_ys187_jialu", "v43y_ys041", "v133_cssn_local_admin"], ["v133_jialu_river_survey", "v43y_river"], ["y_toghto", "y_toghon_temur"]),
                section("v133_jialu_s4", "十五万民夫之外还有谁承担河工", "《元史》记河工征调汴梁、大名等十三路民夫十五万，又有十八翼军士两万。数字展示工程规模，却不能把十七万人看成没有家庭的劳动力。役夫离开田地，沿线需要供应粮食、木料、绳索、舟车与工具；地方官还要清点钱粮、组织轮换并处理逃亡和疾病。工程确实较快恢复河道与通航，沿河部分居民也会从控制洪水中受益；受益与负担并不由同一群体在同一时间平均承担，各地区承担的方式和强度也不一致。只说“劳民伤财”会抹去技术成效，只颂扬河平碑又会让普通人的服役消失。社会史需要把两面同时保留。", ["v133_ys187_jialu", "v133_cssn_local_admin", "v43y_ys041"], ["v133_jialu_labor", "v43y_river"], ["y_toghto"]),
                section("v133_jialu_s5", "河工与红巾军之间不能只画一条直线", "1351年河工期间和随后，韩山童、刘福通等组织起事，民间流传独眼石人等故事。传说能反映动员如何利用河工人群和不满，却不能替代对灾荒、税役、钞法贬值、地方冲突与宗教网络的分析。大量征役提高了组织与传播的条件，也不是所有役夫都自动加入同一支红巾军。贾鲁后来随脱脱参与镇压徐州一带起义，1353年在军中去世；治河官员与战争官员由此落在同一生涯。把他只写成水利英雄或起义导火索都过于单薄。更可靠的结论是：工程有效改变河道，同时进入了已高度紧张的社会环境。", ["v133_ys187_jialu", "v43y_ys041", "v43y_ys042"], ["v43y_redturban", "v133_jialu_labor"], ["y_toghto", "y_toghon_temur"]),
            ]
        ),
        "y_chaghan_temur": article(
            "y_chaghan_temur", "察罕帖木儿：地方武装怎样成为元廷主力", "从数百名乡里子弟到跨省统帅，他的成功既挽救北方战线，也改变中央与地方军队关系。", [
                section("v133_chaghan_s1", "科举经历与地方家世不能被军阀标签抹掉", "察罕帖木儿字廷瑞，家族早年由北方迁居河南沈丘一带。他幼年读书，曾参加进士考试，后来却以地方武装统帅知名。故宫资料称其畏兀儿人，《元史》写“系出北庭”，现代族属标签与十四世纪家世记载并不总能直接对应，因此应以可核的迁居、教育和仕历为主。他不是中央长期培养的职业大将，也不是完全脱离国家的乡间豪强。元末危机使熟悉地方人际、能够组织乡里子弟的人获得军事机会；科举知识、地方声望和家族资源在同一生涯中共同发挥作用。这样的复合身份比单一族属标签更能解释其崛起。", ["v133_dpm_chaghan", "v133_ys141_chaghan", "v133_ys044"], ["v133_chaghan_local_army"], ["y_toghon_temur"]),
                section("v133_chaghan_s2", "数百人的自保武装为何得到朝廷官职", "1352年察罕帖木儿与李思齐合兵，率沈丘等地数百人攻取罗山，随后获授汝宁府达鲁花赤。各地武装来会，队伍扩展至万人。中央军队无法及时控制广阔战区，朝廷便用官职、印信和军费吸收地方力量；地方统帅则借国家名义征募、调粮和扩大地盘。这种合作能迅速恢复战力，却把士兵忠诚更多系于具体统帅。所谓“义兵”是官修史的正统称呼，参与者可能包含地主武装、乡里子弟、流民及旧军，动机并不完全相同。对居民而言，红巾军与官军反复经过都可能带来征粮、守城和迁徙压力。", ["v133_dpm_chaghan", "v133_ys141_chaghan", "v133_ys044"], ["v133_chaghan_local_army"], ["y_koke_temur"]),
                section("v133_chaghan_s3", "从河南到关陕，胜利依赖多支军队", "察罕帖木儿此后转战河南、山西和关陕，逐步收复陕州、洛阳等地，并与李思齐及其他将领协作。正史把战功集中到主帅名下，实际作战还依赖地方驻军、降军、运输者和城中响应者。每夺回一地，接下来都要重新安排官员、粮税、城防和难民，军事地图上的颜色变化并不等于社会已经恢复。区域军队在连续胜利中积累自己的官属和补给网络，中央越来越依赖他们，同时越来越难直接调度。察罕帖木儿的能力确实改变北方战局；这种能力所依托的军权地方化，又成为元廷后期新的结构问题。", ["v133_ys141_chaghan", "v133_ys044", "v133_ys045"], ["v133_chaghan_local_army"], ["y_toghon_temur", "y_koke_temur"]),
                section("v133_chaghan_s4", "1359年攻取汴梁不是北方战争终点", "韩林儿、刘福通以汴梁为都后，察罕帖木儿于1359年组织围攻并破城，韩林儿等退往安丰。这次胜利削弱北方红巾军的重要中心，却没有消灭各地反元力量，也没有让江淮、四川和江南重新统一服从大都。汴梁守攻需要长期军粮、器械和外围据点，不能缩成一场城门决战。收复城市提高察罕帖木儿声望，也扩大其官职和军队。中央得到暂时安全，却更依赖一个掌握河南、山东与山西军事联系的统帅。把1359年当作“起义已经失败”会忽略安丰、山东及其他政权仍持续活动，城内居民还要面对围城损失、逃亡与恢复供给。", ["v133_dpm_chaghan", "v133_ys141_chaghan", "v133_ys045"], ["v133_kaifeng_recovery"], ["han", "y_koke_temur"]),
                section("v133_chaghan_s5", "接受降将为何最终带来益都刺杀", "进攻山东红巾军时，察罕帖木儿接受田丰、王士诚等归降，并继续围攻益都。招降能减少眼前抵抗、获得城情和兵力，也把刚刚改变阵营的人带入军中核心。1362年他进入田丰营帐时被刺杀，说明个人信任和快速收编存在巨大风险。官修史将其塑造成忠义殉国者，遇刺事实与军功可核，道德赞语仍要与战争中破坏、征发分开。其外甥兼养子扩廓帖木儿随后接掌主力并攻下益都，军权没有交还中央，而是沿亲属与军中网络继续。这既维持战线，也进一步证明元廷主力已区域化，个人死亡没有结束依附其家族的军事组织。", ["v133_dpm_chaghan", "v133_ys141_chaghan", "v133_ys046"], ["v133_yidu_assassination"], ["y_koke_temur", "y_toghon_temur"]),
            ]
        ),
        "y_koke_temur": article(
            "y_koke_temur", "扩廓帖木儿：从益都复仇到北元战线", "继承一支区域军队不等于继承所有盟友；他既保卫元廷，也深陷元廷自身内战。", [
                section("v133_koke_s1", "王保保与扩廓帖木儿是同一个人吗", "汉文材料常以王保保称呼扩廓帖木儿，并记他为察罕帖木儿的外甥、由舅父养为子。不同史书对本姓、名字来源和族属的解释并不完全一致，明朝招降叙事又喜欢强调“王”姓。可以确认的是，扩廓帖木儿在察罕军中成长，1362年主帅遇刺后由军中推举接掌主力。姓名差异不应被拆成两个人，也不能仅凭一个汉姓断定完整身份。养子和外甥关系提供继承资格，真正让他掌军的仍是将领承认、营伍控制和为养父复仇的共同目标。来源分歧本身也是元明易代留下的政治痕迹。", ["v133_ys141_chaghan", "v133_ms124_koke", "v133_dpm_chaghan"], ["v133_yidu_assassination"], ["y_chaghan_temur"]),
                section("v133_koke_s2", "攻下益都以后，为何旧盟友不肯听命", "扩廓帖木儿接掌军队后继续围攻益都，击败并处置刺杀察罕帖木儿的田丰、王士诚，完成军中期待的复仇。但李思齐、张良弼等原与察罕帖木儿地位相近，不愿自动接受年轻继承者统属。区域军队表面都受元廷官号，实际各有募兵地盘、将领关系和粮饷来源。亲属继承能保住核心部队，不能让所有同盟变成下属。此后关陕、山西诸军相互攻战，显示元廷“总天下兵”的诏令缺少稳定执行条件。益都胜利延续了战斗力，也暴露地方军事联盟的边界，胜利后的分配往往比共同作战更难。", ["v133_ys141_chaghan", "v133_ys046", "v133_ms124_koke"], ["v133_yidu_assassination"], ["y_chaghan_temur", "y_toghon_temur"]),
                section("v133_koke_s3", "孛罗帖木儿入大都，是谁在同谁作战", "扩廓帖木儿与驻大同的孛罗帖木儿争夺山西、河北，冲突又卷入顺帝、皇太子、皇后和中枢官员。1364年孛罗帖木儿一度进入大都，皇太子转往太原依靠扩廓帖木儿；次年孛罗帖木儿被杀，扩廓帖木儿进入中枢并获高位。这不是元军与反元军的简单战线，而是元廷内部用区域军队争夺首都和继承权。沿途居民面对的是同属朝廷名义的军队互相征粮与攻城。扩廓帖木儿帮助皇太子返回，也没有因此成为无条件服从的臣下；军权让他成为宫廷需要又难以控制的伙伴，首都安全也被地方统帅的选择左右。", ["v133_ys141_chaghan", "v43y_ys047", "v133_ms124_koke"], ["v133_koke_court_war"], ["y_toghon_temur"]),
                section("v133_koke_s4", "受命南征为何转成西北军阀混战", "元廷后来授扩廓帖木儿河南王等名号，要求他总兵南征，但李思齐、张良弼等拒绝统一节制，扩廓帖木儿也把大量力量用于关陕和山西内部冲突。皇太子及中枢先倚重他，继而削夺官爵、另设军府讨伐，命令反复显示皇权已难把封号转化为真实指挥。与此同时朱元璋已消灭陈友谅、张士诚并发动北伐。不能把元亡解释成扩廓帖木儿一人“拒不南征”，也不能忽略军阀内战确实消耗了仍具战斗力的北方军队。制度崩解常表现为每一方都保存部分资源，却没有人能把资源稳定汇合，地方士兵和居民则在相互矛盾的征调中反复承担成本。", ["v133_ys141_chaghan", "v43y_ys047", "v133_ms124_koke"], ["v133_koke_court_war", "v43y_yuan_exit"], ["y_toghon_temur", "yuanzhang"]),
                section("v133_koke_s5", "1368年以后为什么仍要继续讲他", "明军进入大都时，元廷北撤，扩廓帖木儿仍在山西等地组织抵抗，后来转入甘肃与漠北方向。明朝多次招降未果，双方继续战争；1372年明军北征也并非一路顺利。扩廓帖木儿继续服务北元，直到1375年去世。由此可以区分两个命题：1368年元朝失去中原首都和全国性统治，是明确王朝断点；元廷、蒙古诸部和原有将领网络仍存在，也同样是事实。《明史》强调朱元璋称许其不降，既塑造强敌也衬托明朝；北元材料又较零散。理解他需要同时保留战事、政治立场与来源不对称，而不是把后半生删成明朝开国的余波。", ["v133_ms124_koke", "v133_dpm_northern_yuan", "v43y_ys047"], ["v133_koke_northern_yuan", "v43y_yuan_exit"], ["y_toghon_temur", "yuanzhang"]),
            ]
        ),
    }

    for pid, value in articles.items():
        upsert_article(data["articles"], value)

    data["version"] = max(data.get("version", 0), 107)
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
