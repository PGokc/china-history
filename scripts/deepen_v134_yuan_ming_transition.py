#!/usr/bin/env python3
"""Deepen the Yuan-Ming transition through eight competing political paths."""

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
            "id": "v134_dpm_liufutong",
            "title": "故宫博物院：刘福通",
            "url": "https://www.dpm.org.cn/lemmas/243198.html",
            "note": "故宫博物院人物资料，概述颍州起事、拥立韩林儿、三路北伐及退守安丰；其简明年表须同本纪、列传互证。",
        },
        {
            "id": "v134_dpm_red_turbans",
            "title": "故宫博物院：红巾军",
            "url": "https://www.dpm.org.cn/lemmas/245117.html",
            "note": "故宫博物院概述北方与南方多支红巾军，适合辨认并非单一组织；宗教与阶级定性仍需结合具体地区和同时代材料。",
        },
        {
            "id": "v134_ms122_han_song",
            "title": "《明史》卷122｜韩林儿传",
            "url": "https://zh.wikisource.org/zh-hans/明史/卷122",
            "note": "清修《明史》的开放转录，保存韩山童、刘福通、韩林儿和北伐等叙述；妖言、贼等称谓及朱元璋相关段落具有胜利王朝立场。",
        },
        {
            "id": "v134_ms123_rivals",
            "title": "《明史》卷123｜陈友谅、张士诚、方国珍、明玉珍传",
            "url": "https://zh.wikisource.org/zh-hans/明史/卷123",
            "note": "清修《明史》的开放转录，集中记录元末区域政权；人物性格褒贬、兵力数字和动机判断须与实物及其他材料互证。",
        },
        {
            "id": "v134_dpm_zhang_shicheng",
            "title": "故宫博物院：张士诚",
            "url": "https://www.dpm.org.cn/lemmas/241421.html",
            "note": "故宫博物院人物资料，提供白驹场盐业背景、高邮与平江政权等基本节点；不能据此把江南治理简化为个人性格。",
        },
        {
            "id": "v134_dpm_fang_guozhen",
            "title": "故宫博物院：方国珍",
            "url": "https://www.dpm.org.cn/lemmas/241422.html",
            "note": "故宫博物院人物资料，记录方国珍控制浙东沿海、接受元廷官号并同朱元璋往来的过程。",
        },
        {
            "id": "v134_dpm_chen_youliang",
            "title": "故宫博物院：陈友谅",
            "url": "https://www.dpm.org.cn/lemmas/241420.html",
            "note": "故宫博物院人物资料，提供由县吏进入天完军、建立汉政权及鄱阳湖战死等节点；胜负原因仍需拆解围城、船队和补给。",
        },
        {
            "id": "v134_nmc_han_song_seal",
            "title": "中国国家博物馆：管军万户府印",
            "url": "https://www.chnmuseum.cn/zp/zpml/kgfjp/202111/t20211116_252350.shtml",
            "note": "国家博物馆藏龙凤五年军印，铭文可证韩宋中书礼部造印、军事官署与纪年；一方印不能证明全部六部均完整运作。",
        },
        {
            "id": "v134_nopss_yuan_ming_jiangnan",
            "title": "全国哲学社会科学工作办公室：元、明前期江南政策与社会发展脉络",
            "url": "https://www.nopss.gov.cn/n1/2024/0523/c373410-40242022.html",
            "note": "国家社科基金成果介绍，提示元明江南应结合户籍、赋役、海商、军户、市镇与地方文书研究，而非只读政权胜负。",
        },
    ]:
        upsert(data["sources"], source)

    people = [
        {
            "id": "y_han_shantong", "name": "韩山童", "call": "元末起事组织者", "temple": "—", "era": "顺帝至正时期",
            "reign": "生年不详—1351", "summary": "利用白莲教等宗教网络与复宋话语组织起事，尚未举兵即被捕杀；石人故事的形成层次须谨慎辨析。",
            "kind": "起事者", "note": "自称宋徽宗后裔属于政治动员主张，不可当作已证世系。", "sources": ["v134_ms122_han_song", "v43y_ys042", "v134_dpm_red_turbans"], "dynasty": "yuan",
        },
        {
            "id": "y_liu_futong", "name": "刘福通", "call": "北方红巾军统帅", "temple": "—", "era": "龙凤（韩宋）",
            "reign": "约1321—约1363", "summary": "颍州起事后重组北方红巾军，拥立韩林儿并发动多路北伐；安丰陷落后的结局存在材料分歧。",
            "kind": "起事者", "note": "死亡时间与地点不可写成无争议定论。", "sources": ["v134_dpm_liufutong", "v134_ms122_han_song", "v134_nmc_han_song_seal"], "dynasty": "yuan",
        },
        {
            "id": "y_xu_shouhui", "name": "徐寿辉", "call": "天完政权首领", "temple": "—", "era": "治平、太平等（天完）",
            "reign": "生年不详—1360", "summary": "1351年在蕲水被推为天完政权皇帝，势力一度扩展至湖广、江西和江浙；后受部将控制并被陈友谅杀害。",
            "kind": "政权首领", "note": "《明史》以陈友谅前史收录其事，传记篇幅与称谓反映明朝正统立场。", "sources": ["v134_ms123_rivals", "v134_dpm_red_turbans"], "dynasty": "yuan",
        },
        {
            "id": "y_fang_guozhen", "name": "方国珍", "call": "浙东海上势力首领", "temple": "—", "era": "顺帝至正时期",
            "reign": "1319—1374", "summary": "依靠浙东海岛、船队和港口网络起家，多次接受元廷官号并同各方议和，1367年向朱元璋投降。",
            "kind": "政权首领", "note": "反复受官与纳贡是弱中央下的政治策略，不宜只写作个人反复无常。", "sources": ["v134_dpm_fang_guozhen", "v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan"], "dynasty": "yuan",
        },
        {
            "id": "y_ming_yuzhen", "name": "明玉珍", "call": "大夏政权建立者", "temple": "—", "era": "天统（大夏）",
            "reign": "1331—1366", "summary": "由徐寿辉部将进入四川，控制重庆和成都后于1362年建立大夏；其子明昇在1371年向明朝投降。",
            "kind": "政权首领", "note": "四川地区的恢复与控制程度须区分政权法令、城市据点和地方实际。", "sources": ["v134_ms123_rivals", "v134_dpm_red_turbans"], "dynasty": "yuan",
        },
    ]
    for person in people:
        upsert(data["people"], person)

    rewrites = {
        "han": {
            "name": "韩林儿", "call": "韩宋政权首领", "temple": "—", "era": "龙凤（韩宋）", "reign": "约1340—1366",
            "summary": "1355年被刘福通等拥立，韩宋以龙凤纪年并建立官署；1366年渡江遇难，是否受朱元璋授意没有无争议定论。",
            "kind": "政权首领", "note": "所谓宋徽宗后裔是韩宋政治主张，不是可核实世系。", "sources": ["v134_ms122_han_song", "v134_nmc_han_song_seal", "226244"], "dynasty": "yuan",
        },
        "zhang": {
            "name": "张士诚", "call": "大周、吴政权首领", "temple": "—", "era": "天祐（大周）", "reign": "1321—1367",
            "summary": "由白驹场盐运劳动者起事，守住高邮后控制苏州及江南富庶地区；1367年平江陷落后身亡。",
            "kind": "政权首领", "note": "降元、称吴王和江南治理处于不同阶段，不能压成单一“割据”。", "sources": ["v134_dpm_zhang_shicheng", "v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan"], "dynasty": "yuan",
        },
        "chenyou": {
            "name": "陈友谅", "call": "汉政权建立者", "temple": "—", "era": "大义（汉）", "reign": "1320—1363",
            "summary": "由天完军文书与将领崛起，1360年杀徐寿辉并建立汉政权；1363年洪都—鄱阳湖战争中身亡。",
            "kind": "政权首领", "note": "《明史》性格评价来自胜利王朝，须与其资源、组织和战局分开。", "sources": ["v134_dpm_chen_youliang", "v134_ms123_rivals", "v2f_ms123"], "dynasty": "yuan",
        },
    }
    for pid, values in rewrites.items():
        original = next(person for person in data["people"] if person["id"] == pid)
        values = {**original, **values, "id": pid}
        upsert(data["people"], values)

    events = [
        {"id": "v134_yingzhou_uprising", "year": "1351", "title": "韩山童计划受挫与刘福通颍州起事", "category": "社会", "body": "韩山童等以宗教网络、复宋主张组织聚众，计划泄露后韩山童被捕杀；刘福通随后在颍州起兵，红巾标识扩散。", "impact": "河工征役提供了不满与人员汇集环境，但灾荒、税役、钞法、地方冲突和宗教网络共同作用，不能归结为一则石人传说。", "kind": "历史事件", "people": ["y_han_shantong", "y_liu_futong", "y_jia_lu"], "sources": ["v134_ms122_han_song", "v43y_ys042", "v134_dpm_red_turbans"]},
        {"id": "v134_tianwan_founding", "year": "1351", "title": "蕲水起兵与天完政权建立", "category": "政治", "body": "彭莹玉、邹普胜等在蕲黄地区组织起事并推徐寿辉为主，建立天完政权，势力向湖广、江西和江浙扩展。", "impact": "南方红巾军并非北方韩宋的一支地方分队，而是由不同网络、将领和区域资源组成的政治军事力量。", "kind": "历史事件", "people": ["y_xu_shouhui", "chenyou", "y_ming_yuzhen"], "sources": ["v134_ms123_rivals", "v134_dpm_red_turbans"]},
        {"id": "v134_gaoyou_salt_uprising", "year": "1353", "title": "白驹场盐运劳动者起事", "category": "社会", "body": "张士诚与弟兄及同伴从白驹场起事，参与者与私盐运输、盐业劳动及地方冲突关系密切，随后攻取泰州、兴化和高邮。", "impact": "国家盐政、地方豪强与运输劳动者之间的矛盾进入战争，起事并非抽象贫困自动造成。", "kind": "历史事件", "people": ["zhang"], "sources": ["v134_dpm_zhang_shicheng", "v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan"]},
        {"id": "v134_gaoyou_defense", "year": "1354", "title": "高邮守城与脱脱前线被罢", "category": "军事", "body": "脱脱组织大军围攻张士诚控制的高邮，城防承受巨大压力；朝廷在战事未决时罢免脱脱，军队协调迅速瓦解。", "impact": "张士诚获得生存和扩张窗口，也显示元廷仍能集结重兵，却难以让宫廷决策与前线组织保持稳定。", "kind": "历史事件", "people": ["zhang", "y_toghto", "y_toghon_temur"], "sources": ["v134_dpm_zhang_shicheng", "v134_ms123_rivals", "v43y_ys043"]},
        {"id": "v134_han_song_founding", "year": "1355", "title": "亳州拥立韩林儿与龙凤纪年", "category": "政治", "body": "刘福通等迎韩林儿至亳州，称皇帝、小明王，国号宋、年号龙凤，并设置中枢与军事官号。", "impact": "复宋世系和明王信仰提供政治合法性，实际军政则由刘福通等将领和官署网络持续运作。", "kind": "历史事件", "people": ["y_liu_futong", "han", "y_han_shantong"], "sources": ["v134_dpm_liufutong", "v134_ms122_han_song", "v134_nmc_han_song_seal"]},
        {"id": "v134_han_song_northern_campaigns", "year": "1357—1359", "title": "韩宋三路北伐与进入汴梁", "category": "军事", "body": "韩宋将领分路进入山东、山西、关中、辽东等地，部分军队逼近上都与大都；刘福通一方进入汴梁并迁置政权中心。", "impact": "远距离推进牵制元军，却也拉长补给并分散指挥；各路战果不能等同于韩宋稳定控制大片行政区。", "kind": "历史事件", "people": ["y_liu_futong", "han", "y_chaghan_temur"], "sources": ["v134_dpm_liufutong", "v134_ms122_han_song", "v133_ys045"]},
        {"id": "v134_han_song_seal_offices", "year": "1359", "title": "龙凤五年军印所见韩宋官署", "category": "文化", "body": "国家博物馆藏铜印铭有“管军万户府印”“中书礼部造”和龙凤五年纪年，显示韩宋能够制造、编号并颁发军事官印。", "impact": "实物把政权名号连接到官署实践，但一方军印不能证明所有中央部门都持续、完整地运行。", "kind": "历史事件", "people": ["han", "y_liu_futong"], "sources": ["v134_nmc_han_song_seal", "v134_ms122_han_song"]},
        {"id": "v134_tianwan_takeover", "year": "1357—1360", "title": "倪文俊、陈友谅与天完军权转移", "category": "政治", "body": "天完丞相倪文俊控制徐寿辉未果后被陈友谅所杀，陈友谅接收其部众、夺取江西湖广要地，最终杀徐寿辉自立。", "impact": "共同反元没有消除政权内部对军队、城市和名号的争夺，部将网络能够反过来控制被推戴的首领。", "kind": "历史事件", "people": ["y_xu_shouhui", "chenyou"], "sources": ["v134_dpm_chen_youliang", "v134_ms123_rivals"]},
        {"id": "v134_fang_maritime_network", "year": "1352—1367", "title": "方国珍控制浙东港口与海运通道", "category": "经济", "body": "方国珍依靠海岛、船队和浙东港口立足，多次接受元廷官号并向不同势力输诚，维持沿海控制与贸易运输资源。", "impact": "海上力量既能截断航运，也能成为朝廷和新政权争取的运输伙伴；反复谈判是多方竞争下的策略。", "kind": "历史事件", "people": ["y_fang_guozhen", "yuanzhang"], "sources": ["v134_dpm_fang_guozhen", "v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan"]},
        {"id": "v134_daxia_sichuan", "year": "1362—1371", "title": "明玉珍建立大夏与四川政权交接", "category": "经济", "body": "明玉珍控制重庆、成都后建立大夏，设置官署并试图恢复农业与地方秩序；1366年去世后由幼子明昇继承，1371年降明。", "impact": "四川不是元明战争的边缘空白，大夏治理和后续接收影响人口、赋役、交通与地方官员的延续。", "kind": "历史事件", "people": ["y_ming_yuzhen", "y_xu_shouhui", "yuanzhang"], "sources": ["v134_ms123_rivals", "v134_dpm_red_turbans"]},
        {"id": "v134_anfeng_relief", "year": "1363", "title": "安丰陷落、朱元璋救援与韩宋收缩", "category": "军事", "body": "张士诚部将吕珍攻安丰，韩林儿向朱元璋求援；朱军抵达前后城池失守，刘福通结局的具体记载不一，韩林儿被安置于滁州。", "impact": "援救既牵制张士诚扩张，也使朱元璋进一步掌握韩宋政治名号；不能据结果反推所有参与者一开始已有同一计划。", "kind": "历史事件", "people": ["han", "y_liu_futong", "zhang", "yuanzhang"], "sources": ["v134_ms122_han_song", "ms1", "226244"]},
        {"id": "v134_hongdu_poyang_system", "year": "1363—1364", "title": "洪都守城、鄱阳湖决战与汉政权后续", "category": "军事", "body": "陈友谅围洪都未克，朱元璋援军到来后双方转战鄱阳湖；持续交战、火攻、湖口封锁和粮食压力共同改变战局，陈友谅身亡。", "impact": "陈理仍在武昌继位，至1364年才投降；战役结果不能缩成一次火攻或一位统帅的个人神机。", "kind": "历史事件", "people": ["chenyou", "yuanzhang", "xuda", "changyuchun"], "sources": ["v134_dpm_chen_youliang", "v134_ms123_rivals", "v2f_ms123"]},
        {"id": "v134_pingjiang_siege_society", "year": "1366—1367", "title": "平江长期围城与江南政权终结", "category": "社会", "body": "朱元璋军分割湖州、杭州等外围后围攻平江，修筑长围并使用炮石；长期封锁使城内军民面对粮食紧张与持续破坏。", "impact": "1367年城破、张士诚身亡，江南富庶并未自动转化为持久军事优势，接收税粮与人口还需要新的行政整合。", "kind": "历史事件", "people": ["zhang", "yuanzhang", "xuda", "changyuchun"], "sources": ["v134_dpm_zhang_shicheng", "v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan"]},
    ]
    for event in events:
        upsert(data["events"], event)

    upsert(data["objects"], {
        "id": "v134_obj_han_song_seal", "title": "韩宋管军万户府印", "subtitle": "龙凤五年 · 从政治名号到军政文书",
        "symbol": "seal.fill", "body": "中国国家博物馆藏铜印为韩宋龙凤五年制造。印文为“管军万户府印”，印背和印侧另刻“中书礼部造”、制造年月及编号。它说明韩宋不只使用复宋口号，还以自己的纪年、中央官署名义制造并颁发军职印信。\n\n军印能证明特定官署实践，不能据此想象一套与元朝完全相同、始终完整运行的六部制度。把铭文、传世史书与各路军队活动合读，才能判断名号怎样转化为实际命令。",
        "note": "馆方对铭文和年代有明确说明；印章的具体出土与使用者经历不宜在无材料时补写。", "people": ["han", "y_liu_futong"], "sources": ["v134_nmc_han_song_seal", "v134_ms122_han_song"], "dynasties": ["yuan"],
    })

    for association in [
        {"from": "y_han_shantong", "to": "han", "role": "儿子、死后被拥立为韩宋皇帝", "inverse": "父亲、其复宋主张成为政权合法性资源", "period": "1351—1366", "note": "父子关系可核，所谓宋徽宗后裔不可当作已证世系。", "sources": ["v134_ms122_han_song", "v134_nmc_han_song_seal"]},
        {"from": "y_han_shantong", "to": "y_liu_futong", "role": "共同组织起事者", "inverse": "共同组织起事者与死后政治象征", "period": "1351", "note": "计划泄露后韩山童被杀，刘福通继续组织颍州起事。", "sources": ["v134_ms122_han_song", "v43y_ys042"]},
        {"from": "y_liu_futong", "to": "han", "role": "被其拥立并提供政治名号的韩宋首领", "inverse": "拥立者与主要军政主持者", "period": "1355—1363", "note": "韩林儿并非所有军政决策的实际发起者，刘福通也不能完全控制各路北伐军。", "sources": ["v134_dpm_liufutong", "v134_ms122_han_song"]},
        {"from": "y_xu_shouhui", "to": "chenyou", "role": "部将、后来的夺权与杀害者", "inverse": "早期君主、后被其挟持并杀害", "period": "1351—1360", "note": "陈友谅先经倪文俊部掌军，不能写成起事之初即独立建汉。", "sources": ["v134_ms123_rivals", "v134_dpm_chen_youliang"]},
        {"from": "y_xu_shouhui", "to": "y_ming_yuzhen", "role": "派往西征的部将、后来的四川政权建立者", "inverse": "早期所属天完政权首领", "period": "1350年代", "note": "明玉珍进入四川后逐渐形成独立资源基础。", "sources": ["v134_ms123_rivals", "v134_dpm_red_turbans"]},
        {"from": "yuanzhang", "to": "han", "role": "曾提供政治名号、后被安置于滁州的韩宋首领", "inverse": "曾使用龙凤年号、后来掌握其处境的地方首领", "period": "1355—1366", "note": "韩林儿溺亡事实可核，朱元璋是否直接授意存在史料分歧。", "sources": ["v134_ms122_han_song", "ms1", "226244"]},
        {"from": "yuanzhang", "to": "zhang", "role": "争夺江南税粮与城市的对手", "inverse": "争夺江南税粮与城市的对手", "period": "1356—1367", "note": "竞争包含外围城市、漕运、降将和长期围城，不只有平江一战。", "sources": ["v134_ms123_rivals", "v134_dpm_zhang_shicheng"]},
        {"from": "yuanzhang", "to": "y_fang_guozhen", "role": "反复谈判、最终投降的浙东海上首领", "inverse": "长期受其输诚、最终接受投降的新政权首领", "period": "1358—1367", "note": "双方关系随浙东战局和海运资源改变。", "sources": ["v134_ms123_rivals", "v134_dpm_fang_guozhen"]},
        {"from": "chenyou", "to": "y_ming_yuzhen", "role": "天完分裂后在四川自立的大夏首领", "inverse": "天完分裂后互不统属的汉政权首领", "period": "1360—1363", "note": "两人同出徐寿辉系统，但分别依托长江中游与四川资源。", "sources": ["v134_ms123_rivals"]},
    ]:
        upsert_association(data["associations"], association)

    articles = {
        "y_han_shantong": article("y_han_shantong", "韩山童：一场尚未举兵便失败的动员", "从宗教网络、复宋话语到河工社会，区分可核组织与后来传奇。", [
            section("v134_hanshan_s1", "关于他的材料为何总与传说相连", "韩山童生年不详，活动中心在颍州、河北栾城等说法之间需谨慎处理。较稳定的信息是，他与刘福通、杜遵道、罗文素等利用白莲教及相关信仰网络筹划起事，1351年计划泄露后被官府捕杀。关于其外貌、异兆和神秘法术的叙述，多来自官修史对“妖人”的定型或后世传奇，不宜当作个人传记事实。史料几乎没有留下他的日常生活、职业和自述，这种沉默并不等于他只有一句口号。可靠写法应从组织方式和政治语言入手，同时承认我们无法重建其全部经历。", ["v134_ms122_han_song", "v43y_ys042", "v134_dpm_red_turbans"], ["v134_yingzhou_uprising"], ["y_liu_futong", "han"]),
            section("v134_hanshan_s2", "“宋徽宗八世孙”是一项政治主张", "韩山童一方宣称他是宋徽宗八世孙，并把复宋、明王出世和弥勒降生等语言结合起来。现有材料不能把这套世系核实为家谱事实，它首先是元末动员的合法性主张：宋朝记忆为反元行动提供熟悉的王朝名称，宗教预言则把现实困苦解释成秩序即将翻转。参与者未必以完全相同方式理解这些符号，有人可能相信救劫预言，有人更关心赋役、治安或报复地方官。把起事只叫宗教暴动，会抹掉社会条件；把宗教全部解释成伪装，也会误读组织者与信众共享的意义世界。", ["v134_ms122_han_song", "v134_dpm_red_turbans", "v134_dpm_liufutong"], ["v134_yingzhou_uprising", "v134_han_song_founding"], ["y_liu_futong", "han"]),
            section("v134_hanshan_s3", "河工人群提供条件，却不是唯一原因", "1351年黄河工程调集大量民夫和军士，沿线承担粮食、运输与离家服役。韩山童、刘福通的组织活动与河工社会相遇，使不满、流动人口和秘密联络更容易汇集。后世最熟悉的独眼石人故事，能说明政治传播如何借预言和物件制造冲击，却缺少足够同时代证据来证明全部细节。更不能由此推出“挖出石人就引发起义”。灾荒、钞法贬值、税役、地方豪强冲突、治安失控和宗教网络共同形成危机；河工是其中重要场景，而非包办一切的按钮。", ["v43y_ys042", "v133_ys187_jialu", "v134_ms122_han_song"], ["v133_jialu_labor", "v134_yingzhou_uprising"], ["y_jia_lu", "y_liu_futong"]),
            section("v134_hanshan_s4", "杀白马黑牛之后，聚会为何迅速败露", "《明史》等记韩山童一方举行盟誓、准备聚众时，消息被地方官掌握，韩山童被捕杀，妻子杨氏和儿子韩林儿逃脱。这个节点说明秘密网络并非没有漏洞，官府基层侦察也未完全失效。计划失败并没有终止更广泛危机：刘福通随后在颍州起兵，徐州、蕲黄、濠州等地又出现不同队伍。各支红巾军共享部分颜色、信仰和反元语言，却没有一个始终统一的指挥中心。韩山童本人未能统率后来的战争，把所有红巾军行动都归到他的预先计划，是把结果倒写成开端。", ["v134_ms122_han_song", "v43y_ys042", "v134_dpm_red_turbans"], ["v134_yingzhou_uprising", "v134_tianwan_founding"], ["y_liu_futong", "y_xu_shouhui"]),
            section("v134_hanshan_s5", "死者怎样成为韩宋政权的合法性资源", "韩山童死后四年，刘福通等迎立其子韩林儿，国号宋、年号龙凤。父亲的复宋主张由一次失败聚会变成国家名号，母亲杨氏也被尊为皇太后。韩宋发行官印、设置官署和发动北伐，说明政治记忆可以转化为制度实践；这并不证明韩山童生前已设计好后来全部政权结构。明朝官修史把他置于太祖开国前史，常以“妖言”压缩其思想。今天既不需要把他塑成预知王朝更替的先知，也不能因资料稀少把他删去。他的重要性正在于：一个被迅速镇压的组织者，仍通过家族、符号与幸存网络影响了此后十五年。", ["v134_ms122_han_song", "v134_nmc_han_song_seal", "226244"], ["v134_han_song_founding", "v134_han_song_seal_offices"], ["han", "y_liu_futong"]),
        ]),
        "y_liu_futong": article("y_liu_futong", "刘福通：从颍州起事到多路北伐", "他能组织跨区域战争，却不能把所有红巾军变成一支服从中央的军队。", [
            section("v134_liufutong_s1", "韩山童被捕后，颍州为何仍能起兵", "刘福通是颍州人，早期经历留下的可靠细节有限。1351年韩山童计划败露并被杀后，他没有等待重新推戴首领，而是在颍州发动起事。红巾、红旗和焚香等标识让分散参与者能够识别同道，地方不满与宗教网络提供扩张条件。元廷记载把参与者称为贼，后来的革命叙事又容易把他们写成目标完全一致的整体。实际队伍包含教众、河工、农民、流民和地方武装，各自进入战争的原因不一。刘福通的组织能力可从持续扩军和建立据点看出，却不能据此假定每名参与者都受他直接指挥。", ["v134_dpm_liufutong", "v134_ms122_han_song", "v43y_ys042"], ["v134_yingzhou_uprising"], ["y_han_shantong", "han"]),
            section("v134_liufutong_s2", "1355年拥立韩林儿解决了什么问题", "1355年，起事四年后，刘福通等在亳州迎立韩林儿，国号宋、年号龙凤。韩山童的儿子把最初复宋主张与幸存组织连接起来，使各地将领可以在共同纪年和官号下行动。刘福通获平章等职位，是主要军政主持者；但韩林儿并非毫无意义的傀儡，其身份、诏命和宫廷构成政权合法性的一部分。官署能否深入各地、军粮能否稳定征集，仍取决于将领和地方控制。政治名号解决“为谁而战”的表达，不能自动解决不同队伍之间的纪律、补给与利益分配。", ["v134_dpm_liufutong", "v134_ms122_han_song", "v134_nmc_han_song_seal"], ["v134_han_song_founding", "v134_han_song_seal_offices"], ["han", "y_han_shantong"]),
            section("v134_liufutong_s3", "三路北伐走得很远，为何难以形成稳定统治", "1357年前后韩宋发动三路北伐：东路进入山东并向大都方向活动，西路进入关中，中路经山西逼近上都，另有军队到达辽东。广阔推进迫使元廷分兵，显示北方政权承受真实压力；然而距离越远，粮食、马匹、军令和后援越难保持。不同将领有自己的部众和路线，战报中的“攻取”可能只是短期进入，不能全部涂成稳定行政区。把北伐只用成败评判，会漏掉沿路城镇反复易手、居民逃亡和运输负担。刘福通能发起战略性扩张，却没有建立足以持续整合所有远征军的后勤体系。", ["v134_dpm_liufutong", "v134_ms122_han_song", "v133_ys045"], ["v134_han_song_northern_campaigns"], ["han", "y_chaghan_temur"]),
            section("v134_liufutong_s4", "汴梁既是胜利中心，也是容易被围困的目标", "韩宋军进入汴梁后将韩林儿迁入，旧都的宋朝记忆增强了政权象征，城市位置也便于联系河南诸路。但大型城市需要持续粮食和防御，远征诸军分散后，察罕帖木儿逐步清理外围并于1359年围破汴梁。刘福通护送韩林儿退往安丰，韩宋失去最显眼的政治中心。汴梁失守不等于所有红巾军同时结束，却暴露象征都城与实际补给之间的张力。国家博物馆所藏同年军印又显示，即使军事受挫，韩宋仍在制造官印和维持某些制度。败退与行政实践可以同时存在。", ["v134_dpm_liufutong", "v134_ms122_han_song", "v134_nmc_han_song_seal"], ["v134_han_song_northern_campaigns", "v133_kaifeng_recovery"], ["han", "y_chaghan_temur"]),
            section("v134_liufutong_s5", "安丰陷落以后，他的结局为何不能写死", "1363年张士诚部将吕珍攻安丰，韩林儿向朱元璋求援。部分材料说城破时刘福通被杀，另一些较晚或不同系统记录使其下落出现歧义。可以确认的是，安丰政权遭到毁灭性打击，韩林儿随后处在朱元璋控制范围，刘福通不再作为独立统帅活动。史料分歧不应被一条确定死亡场景抹平，也不意味着所有说法同样可靠。写他的终点，最好把“约1363年失去活动记录”和具体遇害说分开。刘福通的历史作用也不只是一位失败将领：他让元廷北方战线多年承压，并把宗教动员转成了有纪年、官署与远征战略的政权。", ["v134_ms122_han_song", "v134_dpm_liufutong", "226244"], ["v134_anfeng_relief"], ["han", "yuanzhang", "zhang"]),
        ]),
        "han": article("han", "韩林儿：被拥立者也构成一种政治秩序", "不把他写成有完整自主权的皇帝，也不把他删成刘福通或朱元璋的道具。", [
            section("v134_hanliner_s1", "父亲的世系主张如何落到儿子身上", "韩林儿是韩山童之子，父亲在1351年筹划起事时被杀，他与母亲杨氏得以逃离。所谓宋徽宗后裔没有可核连续家谱，是韩山童集团提出的复宋政治主张。1355年刘福通等迎立韩林儿时，父亲之死、宋室名号与“明王”信仰共同构成他的身份。称他小明王既有宗教象征，也有现实政治功能。若只说“冒充宋室”，会忽略名号为什么能被接受；若把世系照录为事实，又会混淆宣传与证据。韩林儿个人早年言行几乎没有独立记录，这种史料限制应直接告诉读者。", ["v134_ms122_han_song", "v134_dpm_liufutong", "v134_dpm_red_turbans"], ["v134_yingzhou_uprising", "v134_han_song_founding"], ["y_han_shantong", "y_liu_futong"]),
            section("v134_hanliner_s2", "龙凤政权不是一句口号", "韩林儿在亳州被称帝，国号宋、年号龙凤，母亲为皇太后，刘福通等获得中枢和军事职位。国家博物馆藏龙凤五年“管军万户府印”，印背刻有中书礼部制造信息和编号，证明政权能够制作军印、授予官号并使用自己的纪年。实物比后世概括更接近行政动作，但也有边界：一方印章不能证明六部全部齐备，更不能说明各路远征军都每日服从同一文书系统。韩林儿提供的是制度中心和合法性，实际命令能走多远仍取决于刘福通、地方将领、交通与军粮。", ["v134_nmc_han_song_seal", "v134_ms122_han_song", "v134_dpm_liufutong"], ["v134_han_song_founding", "v134_han_song_seal_offices"], ["y_liu_futong", "y_han_shantong"]),
            section("v134_hanliner_s3", "朱元璋为什么曾使用龙凤纪年", "朱元璋在江淮发展时曾接受韩宋官号并使用龙凤年号，这使自己的军事行动可以置于更广泛反元合法性之下，也避免过早与其他红巾力量争夺皇帝名号。双方并非现代意义的中央与地方行政关系：朱元璋拥有独立军队、根据地和官僚网络，服从程度随实力变化。韩林儿不是明朝皇帝，却真实进入明朝开国时间线；龙凤纪年也不是无意义装饰。后来朱元璋在1364年称吴王、1367年改用吴元年，显示政治名号随着力量对比逐步改变，而不是1352年投军时就已预定建立明朝。", ["v134_ms122_han_song", "ms1", "226244"], ["v134_han_song_founding", "hanend"], ["yuanzhang", "y_liu_futong"]),
            section("v134_hanliner_s4", "从汴梁到安丰，他能决定多少事务", "1358年前后韩宋进入汴梁，旧都身份放大韩林儿的象征地位；1359年察罕帖木儿攻破城市，他与刘福通退往安丰。迁都与逃亡都由军事力量和补给条件推动，现有材料很少记录韩林儿个人意见。1363年吕珍围攻安丰，韩林儿向朱元璋告急，朱军救援后把他安置到滁州。他从一个区域政权中心转为处在另一位首领保护和控制之下。把这一过程称作“挟天子”可以提示权力不对称，却不能替代具体说明：谁掌军、谁供粮、谁控制居所，才决定政治名号还能如何使用。", ["v134_ms122_han_song", "v133_ys045", "226244"], ["v133_kaifeng_recovery", "v134_anfeng_relief"], ["y_liu_futong", "y_chaghan_temur", "yuanzhang"]),
            section("v134_hanliner_s5", "1366年溺亡：事实与幕后推断要分开", "1366年朱元璋派廖永忠迎韩林儿前往应天，船行至瓜步附近覆没，韩林儿死亡。关于事故、廖永忠擅自加害或朱元璋授意，不同材料和后世史家判断不一；目前不能把幕后命令视为无争议事实。韩林儿死后，朱元璋结束对龙凤名号的使用，次年称吴元年，政治收益客观存在，但“谁受益”并不自动证明“谁下令”。对韩林儿最公允的阅读，不是替他虚构自主决策，也不是因其受制于人而抹去。他所代表的韩宋纪年、官印和联盟框架，曾真实组织元末政治，死亡才使这一合法性中心彻底退出。", ["v134_ms122_han_song", "ms1", "226244"], ["hanend", "v134_han_song_seal_offices"], ["yuanzhang", "y_liu_futong"]),
        ]),
        "y_xu_shouhui": article("y_xu_shouhui", "徐寿辉：天完政权与被部将控制的首领", "从蕲黄扩张到汉阳内斗，南方红巾军不能只作为陈友谅的前传。", [
            section("v134_xushouhui_s1", "贩布者为何会被推到政权中心", "《明史》称徐寿辉是罗田人，名真一，从事贩布；彭莹玉、邹普胜等在蕲黄组织起事时，因其相貌和群众号召力而推为首领。传记中的异相说属于政治神化与官修转述，不能当作崛起原因。更重要的是，他连接了宗教组织者、地方参与者和需要共同名号的军队。1351年队伍攻取蕲水、黄州后，他称帝，国号天完。个人出身显示元末政治机会不只向旧官僚开放，但“贫民领袖”也不能替代分析其身边掌握组织、军队和文书的合作者。", ["v134_ms123_rivals", "v134_dpm_red_turbans", "v43y_ys042"], ["v134_tianwan_founding"], ["chenyou", "y_ming_yuzhen"]),
            section("v134_xushouhui_s2", "天完扩张为什么既迅速又松散", "天完军从蕲黄向湖广、江西和江浙推进，一度攻取饶州、信州、杭州等许多城市。各路将领借红巾标识和政权名号行动，却依赖自己的部众和地方补给；城市被攻下后，守备与征收未必能稳定维持。元军反攻时，一些据点又迅速失去。地图上大片颜色容易造成统一行政区的错觉，真实控制更像由城市、交通线和将领辖区拼成。普通居民要面对政权更替、征粮、城防和逃难，也可能利用新权力解决旧有地方冲突。天完的力量真实而广泛，组织松散同样真实。", ["v134_ms123_rivals", "v134_dpm_red_turbans", "v43y_ys043"], ["v134_tianwan_founding"], ["chenyou", "y_ming_yuzhen"]),
            section("v134_xushouhui_s3", "皇帝名号为何挡不住倪文俊掌军", "天完失去蕲水等早期中心后转向汉阳，丞相倪文俊掌握主要军队，徐寿辉越来越受其控制。1357年倪文俊谋杀徐寿辉未成，逃往黄州，陈友谅趁机杀倪文俊并接收部众。这个转折说明，被拥立为皇帝不等于垄断武力；将领掌握营伍、城市与粮源时，宫廷名号反而可能成为其争夺的资源。正史常用“挟制”概括关系，但需要进一步追问军队听谁调度、官职由谁分配。徐寿辉仍能提供天完合法性，正因如此，掌军者没有立即废除他，而是先借其名义扩张。", ["v134_ms123_rivals", "v134_dpm_chen_youliang", "v134_dpm_red_turbans"], ["v134_tianwan_takeover"], ["chenyou"]),
            section("v134_xushouhui_s4", "陈友谅扩张时为何仍暂时奉他为主", "陈友谅接收倪文俊军队后，攻取安庆、龙兴、瑞州及江西多地，成为天完最强将领。他一面需要徐寿辉的政权名号整合旧部，一面逐步建立自己的官属和地盘。徐寿辉希望迁都龙兴等安排与陈友谅利益发生冲突，最终被移置江州。两人的关系不是突然发生的一次背叛，而是军权、都城和名号逐步分离。与此同时明玉珍在西线进入四川，也形成较独立基础。天完看似仍有皇帝，内部已经出现长江中游与四川等不同权力中心，政权分裂早于正式改国号。", ["v134_ms123_rivals", "v134_dpm_chen_youliang", "v134_dpm_red_turbans"], ["v134_tianwan_takeover", "v134_daxia_sichuan"], ["chenyou", "y_ming_yuzhen"]),
            section("v134_xushouhui_s5", "采石遇害以后，为什么仍应单独记住他", "1360年陈友谅挟徐寿辉东攻，军至采石后杀死徐寿辉，随即称帝建汉。明朝史书把徐寿辉放在陈友谅传中，使他容易被读成过渡人物；但天完在九年间形成的军队、官号和区域网络，是陈友谅、明玉珍等后来政权的共同基础。徐寿辉本人能够独立决策多少，材料并不充分，也不能因此说他毫无作用。被推戴、被将领控制和被杀害，揭示元末新政权如何在动员成功后面对军权集中难题。记住天完，才能理解长江流域竞争不是从朱元璋与陈友谅决战才突然开始。", ["v134_ms123_rivals", "v134_dpm_chen_youliang", "v134_dpm_red_turbans"], ["v134_tianwan_takeover", "v134_hongdu_poyang_system"], ["chenyou", "y_ming_yuzhen"]),
        ]),
        "chenyou": article("chenyou", "陈友谅：从天完将领到长江汉帝", "水军规模是真实优势，夺权路径、洪都消耗和鄱阳湖补给共同限定了它。", [
            section("v134_chenyou_s1", "县吏与文书经验怎样进入军队", "陈友谅生于沔阳渔家，曾任县中小吏，略通文字。徐寿辉起兵后，他投到倪文俊麾下，先任簿掾，后来因战功掌兵。小吏经验可能帮助处理文书、粮饷与官号，但现有材料不足以把他的全部军事才能归于读书。1357年倪文俊谋害徐寿辉失败，陈友谅杀倪并接收其军，成为天完内部权力转移的受益者。这个起点不同于独立起兵：他的核心资源来自既有红巾军网络、降附将领和夺取的城市。胜利王朝史书强调其权术，具体军政积累比性格标签更能解释崛起。", ["v134_ms123_rivals", "v134_dpm_chen_youliang", "v2f_ms123"], ["v134_tianwan_takeover"], ["y_xu_shouhui"]),
            section("v134_chenyou_s2", "杀赵普胜、杀徐寿辉与汉政权建立", "陈友谅在江西湖广扩张时，先除掉骁将赵普胜，再把徐寿辉控制于江州。1360年东进采石时，他杀徐寿辉，称帝，国号汉、年号大义。连续夺权减少潜在竞争者，也让部分旧部对其缺乏信任；但不能用“猜忌”一词解释所有政治选择。汉政权拥有官属、江西湖广城市和水军，并非一支临时叛军。徐寿辉名号被替换后，各地将领需要重新选择效忠。陈友谅的强势建立了更集中统帅权，也付出联盟破裂和降将流失的组织成本。", ["v134_ms123_rivals", "v134_dpm_chen_youliang", "v134_dpm_red_turbans"], ["v134_tianwan_takeover"], ["y_xu_shouhui", "y_ming_yuzhen"]),
            section("v134_chenyou_s3", "长江上游、江西粮区与大型楼船", "汉政权控制武昌、江州和江西多地，能够利用长江水路调动军队与物资。陈友谅建造多层大型楼船，铁裹橹箱并容纳军士、官属，体现组织和资源能力。巨舰在开阔水面有防护与高度优势，进入浅水、狭窄湖道或遭火攻时也可能转向困难。船只不是脱离社会的武器：造船需要木材、铁料、工匠和粮食，长期战争会把征发压力传给沿江居民。把汉军失败归咎于“船太大”过于简单，优势能否发挥取决于地形、队形、风向、补给和指挥。", ["v134_ms123_rivals", "v134_dpm_chen_youliang", "v2f_ms123"], ["poyang", "v134_hongdu_poyang_system"], ["yuanzhang", "changyuchun"]),
            section("v134_chenyou_s4", "洪都三个月为何改变鄱阳湖决战条件", "1363年陈友谅集中力量围攻洪都，朱文正等守军坚持数月，使汉军在城下消耗时间、人员和物资。朱元璋援军到达后，双方转入鄱阳湖。连续多日交战、火船、风向、舰队机动和湖口封锁共同压缩汉军选择；陈友谅突围时中箭身亡。单讲火攻妙计，会删掉洪都守城和后续封锁；单比兵力或船高，也无法解释战局。双方都依赖大量无名船工、运粮者和守城居民。鄱阳湖是一个战争系统的结果，不是一位英雄在一天内独自决定。", ["v134_ms123_rivals", "v134_dpm_chen_youliang", "v2f_ms123"], ["poyang", "v134_hongdu_poyang_system"], ["yuanzhang", "xuda", "changyuchun"]),
            section("v134_chenyou_s5", "陈理继续在位，提醒我们胜负并非瞬间完成", "陈友谅死后，张定边护送其子陈理返回武昌，陈理继位并改元，汉政权没有在鄱阳湖当天消失。朱元璋继续围攻，至1364年陈理才投降，后来被迁往高丽。这个尾声说明战场击杀首领与接收城市、军队和人口是不同阶段。《明史》赞扬朱元璋宽宥幼主，又以奢侈、猜忌贬斥陈友谅，叙述服务于胜利者形象。可核的疆域、官属和后续处置，应与道德评语分开。陈友谅代表过一种真实的长江政权可能，理解其失败也要看到资源优势怎样在组织裂痕和持久战中被消耗。", ["v134_ms123_rivals", "v134_dpm_chen_youliang", "v2f_ms123"], ["v134_hongdu_poyang_system"], ["yuanzhang", "y_ming_yuzhen"]),
        ]),
        "y_fang_guozhen": article("y_fang_guozhen", "方国珍：海岛、船队与反复谈判", "浙东海上势力不是陆地王朝边缘，它掌握了各方都需要的港口与运输能力。", [
            section("v134_fang_s1", "从黄岩海民到被追捕的船队首领", "方国珍生于黄岩，熟悉浙东海路。至正年间因仇告与官府追捕等冲突入海，聚集兄弟和船众，利用岛屿、港湾与航海经验活动。史书常以“海盗”概括早期行为，这能反映袭击与劫掠，却不足以说明其后来为何能控制沿海城市、接受官号并组织赋运。海上队伍可能包含亲族、船户、渔盐劳动者和亡命者，行动依靠船只、导航和岸上补给。元廷水师多次不能消灭他，显示沿海地理与地方网络能抵消中央名义上的兵力优势。", ["v134_dpm_fang_guozhen", "v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan"], ["v134_fang_maritime_network"], ["yuanzhang"]),
            section("v134_fang_s2", "为何多次接受元廷官号又再次扩张", "元廷对方国珍反复使用招安、授官和征讨。方氏接受行省、海运等元廷官号后仍保留自己的船队与地盘，局势变化时又扩张或重新谈判。把这种行为简单叫反复无常，会漏掉弱中央的统治方式：朝廷需要他保障海运、牵制其他势力，方氏则借官号取得合法征收和发展空间。双方都没有能力一次解决对方，名义归附成为暂时交换。受官不等于军队被国家收编，拒命也不等于此前所有官职完全虚假；政治关系在文书服从与实际自治之间摇摆。", ["v134_dpm_fang_guozhen", "v134_ms123_rivals", "v133_ys044"], ["v134_fang_maritime_network"], ["y_toghon_temur"]),
            section("v134_fang_s3", "港口和海运为何比占有大片内陆更重要", "方国珍控制庆元、台州、温州等浙东节点时，影响的不只是海岸线。港口连接粮食、盐货、木材、船舶和跨区域商人，也关系元廷南粮北运与各政权军需。海上力量可以截断航路、收取资源，也能以输送粮食换取官位和安全。地方居民既可能从贸易与治安恢复中受益，也承担造船、征粮和军事冲突。元明江南研究提示，应把海商、出海军、户籍和赋役放在一起。方氏没有建立覆盖全国的制度，却掌握了足以让大都、张士诚和朱元璋都认真谈判的运输网络。", ["v134_dpm_fang_guozhen", "v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan"], ["v134_fang_maritime_network"], ["zhang", "yuanzhang"]),
            section("v134_fang_s4", "在张士诚与朱元璋之间如何维持空间", "朱元璋取得婺州后与方国珍控制区接近，方氏开始输诚纳贡，同时仍观察元廷和张士诚局势。他既不是朱元璋从一开始的忠实部属，也没有与张士诚组成固定联盟。不同阶段的贡物、书信、扣留和军事行动，反映各方用时间换取资源。朱元璋先处理陈友谅、张士诚，再集中压力于浙东；战略顺序减少了方氏继续周旋的对象。把最终投降倒推为早已归附，会抹掉近十年的自主政治；把谈判全写成欺骗，也会忽略互通物资和避免全面战争的现实功能。", ["v134_dpm_fang_guozhen", "v134_ms123_rivals", "226244"], ["v134_fang_maritime_network", "pingjiang"], ["zhang", "yuanzhang"]),
            section("v134_fang_s5", "1367年投降以后，海上网络怎样被新王朝接收", "平江陷落后，方国珍失去主要回旋空间，朱元璋军进入浙东，他在1367年底投降。方氏被迁置并获名义官职，部分部属、船户和地方行政逐步纳入明朝。投降避免了像平江那样的长期围城，但不等于沿海立刻安定；新政权还要处理户籍、海防、岛民和贸易控制。方国珍后于1374年去世。《明史》用反复和畏惧刻画他，海运能力却贯穿其政治价值。以“降将”作结会看不见明朝接收的其实是一套港口、船舶、人员与地方知识网络，这些资源继续影响东南治理。", ["v134_dpm_fang_guozhen", "v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan"], ["v134_fang_maritime_network", "founding"], ["yuanzhang"]),
        ]),
        "zhang": article("zhang", "张士诚：盐场起事与江南政权", "从白驹场、高邮到平江，富庶地区的统治仍需军队、税粮与地方合作。", [
            section("v134_zhang_s1", "白驹场盐业怎样塑造起事网络", "张士诚生于泰州白驹场，从事盐运相关劳动。官盐制度、私盐运输、地方富户和关卡冲突，使盐场社会形成既熟悉水路又能互相联络的人群。1353年他与弟兄及同伴起事，先后攻取泰州、兴化、高邮。后世把起事写成受盐商欺压后的个人复仇，可能保存地方冲突线索，却不能单独解释数千人为何加入。盐业劳动、税制、治安失灵和战争机会共同构成条件。张士诚不是抽象的“农民领袖”，其早期力量带有明显盐运和水网地区特征。", ["v134_dpm_zhang_shicheng", "v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan"], ["v134_gaoyou_salt_uprising"], ["y_toghto"]),
            section("v134_zhang_s2", "高邮守住以后，胜利为何来自朝廷自乱", "张士诚在高邮建立大周并使用天祐年号。1354年脱脱调集大军围城，元军有能力形成巨大压力，张氏并非凭一次正面决战击败所有官军。顺帝受中枢斗争影响，在前线胜负未定时罢免脱脱，统帅、将领与粮饷体系骤然失去协调，围城军队瓦解。张士诚因此获得喘息并向江南扩张。高邮既显示守城韧性，也显示元廷政治如何破坏自己的军事能力。若把结果全算作张士诚神机，会遗漏对手制度失灵；若说只是偶然，又无法解释他为何能把窗口转成持续政权。", ["v134_dpm_zhang_shicheng", "v134_ms123_rivals", "v43y_ys043"], ["v134_gaoyou_defense", "v43y_toghto_dismiss"], ["y_toghto", "y_toghon_temur"]),
            section("v134_zhang_s3", "进入平江后，江南富庶怎样转成政权资源", "张士诚取得平江并以苏州为中心，控制太湖水网、粮区和繁荣城市。税粮、商业、工匠和水运为军队提供资源，他也延揽部分文士、恢复地方官署。与此同时军费、将领分封、豪强关系和生活奢侈等问题消耗财政。元末江南不是等待新王朝接收的完整钱袋，战争造成迁徙、田地荒废和重复征收，不同城市控制强度也不相同。王蒙等文人曾进入张氏政权，说明文化生活与政治选择并非只围绕未来的明朝。富庶提供竞争资格，却不保证行政整合和军事胜利。", ["v134_ms123_rivals", "v134_dpm_zhang_shicheng", "v134_nopss_yuan_ming_jiangnan"], ["v134_gaoyou_salt_uprising", "v134_pingjiang_siege_society"], ["yuanzhang"]),
            section("v134_zhang_s4", "降元、称吴王与攻安丰不是同一阶段", "面对元军压力和江南竞争，张士诚一度接受元廷官号，承担海运等任务，同时保留军队和地盘。后来他又称吴王，不再满足于名义臣属。1363年其部将吕珍攻安丰，打击韩宋并扩大淮南空间；朱元璋出兵救援，双方关系进一步恶化。受元官号不意味着成为元廷普通地方官，称王也不代表全新建立一套从零开始的制度。张氏在不同政治名义间转换，是保存实力和争夺资源的策略。其对手也同样借韩宋、吴王等名号逐步改变位置，不能只用忠叛道德解释。", ["v134_ms123_rivals", "v134_dpm_zhang_shicheng", "v134_ms122_han_song"], ["v134_anfeng_relief", "v134_fang_maritime_network"], ["han", "y_liu_futong", "yuanzhang"]),
            section("v134_zhang_s5", "平江围城为什么持续近一年", "朱元璋在击败陈友谅后，先切断湖州、杭州等外围，再由徐达、常遇春围攻平江。攻方修长围、筑台并使用炮石，守方依赖城防与水网抵抗，长期封锁造成粮食紧张和军民伤亡。1367年城破，张士诚被俘后身亡。富庶城市的财富不能在包围中自动变成外援，地方将领和外围据点的丧失逐步压缩选择。胜利后明朝仍需接收户籍、税粮、工匠和旧官员。把平江只当北伐前的最后障碍，会让江南社会成本消失；把张士诚只写成失败者，也看不见他经营十余年的区域政权。", ["v134_dpm_zhang_shicheng", "v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan"], ["pingjiang", "v134_pingjiang_siege_society"], ["yuanzhang", "xuda", "changyuchun"]),
        ]),
        "y_ming_yuzhen": article("y_ming_yuzhen", "明玉珍：从天完西征到四川大夏", "四川并非元明易代的空白后方，大夏尝试把军事占领转成区域治理。", [
            section("v134_ming_s1", "乡里武装如何进入徐寿辉体系", "明玉珍是随州人，元末地方动乱时组织乡里自保，后来归入徐寿辉天完政权。材料称他在战斗中伤失一目，外貌细节不应盖过其组织位置：他带着相对独立部众加入，既接受天完官号，也保存自己的指挥网络。徐寿辉军向西扩张时，明玉珍承担进入四川的任务。与陈友谅从倪文俊部内夺权不同，他的资源基础逐渐转移到长江上游。天完能够把不同地方武装纳入共同名号，却无法确保他们永远由中心直接控制，这为后来大夏独立埋下制度条件。", ["v134_ms123_rivals", "v134_dpm_red_turbans", "v134_dpm_chen_youliang"], ["v134_tianwan_founding", "v134_daxia_sichuan"], ["y_xu_shouhui", "chenyou"]),
            section("v134_ming_s2", "重庆为什么成为进入四川的支点", "明玉珍军由峡江进入重庆，利用元廷地方将领不和与守备薄弱取得城市，随后向成都及四川其他地区扩张。重庆控制长江与川东通道，既是军事据点，也是粮食、船只和人员汇集点。取得一座城市不等于控制全部盆地，山区、州县和地方豪强需要逐步协商或征服。战争也打断运输、造成迁徙。明玉珍能在远离天完中心的地区立足，说明四川有自己的官员、士人和生产基础可被重新组织；其成功不是简单因为中原政权“顾不上”，而是本地条件与外来军队结合。", ["v134_ms123_rivals", "v134_dpm_red_turbans", "v134_nopss_yuan_ming_jiangnan"], ["v134_daxia_sichuan"], ["y_xu_shouhui"]),
            section("v134_ming_s3", "与陈友谅断开后，为何建立大夏", "陈友谅杀徐寿辉并建立汉政权后，明玉珍不愿归附，四川力量与长江中游中心正式分离。1362年他称帝，国号夏、年号天统，以重庆为都，设置官署并任用地方士人。建立新国号既是与陈友谅争夺正统，也是把西征军转成区域政府的需要。法令中可见减轻赋役、恢复生产和整顿官制的意图，但传记容易把新政美化为一人仁德。政策能否深入不同州县、地方执行有多均匀，材料并不足。大夏不是现代四川疆界内完全一致的国家，也不是没有行政能力的割据营寨。", ["v134_ms123_rivals", "v134_dpm_red_turbans", "v134_ms123_rivals"], ["v134_daxia_sichuan", "v134_tianwan_takeover"], ["y_xu_shouhui", "chenyou"]),
            section("v134_ming_s4", "恢复农业与维持军队为何必须同时进行", "长期战争使四川部分地区人口流动、田地荒芜，政权需要安置军民、征收粮赋并修复交通。明玉珍以轻赋、劝农等政策建立名声，也必须供养守军、官署和对外防线。这两面不能只留一面：恢复生产是政权生存条件，军事征发又会消耗恢复成果。四川盐、粮和水路使大夏具备独立资源，却也受峡江交通与周边势力限制。普通人的经历更多隐藏在户籍、赋役和地方文书中，正史主要记君臣决策。评价治理时，应区分颁布政策、城市控制和乡村实际，而不是把“保境安民”当作自动实现的结果。", ["v134_ms123_rivals", "v134_nopss_yuan_ming_jiangnan", "v134_dpm_red_turbans"], ["v134_daxia_sichuan"], ["y_xu_shouhui"]),
            section("v134_ming_s5", "幼主明昇投降，为什么不是大夏历史的附注", "明玉珍于1366年去世，年幼的明昇继位，由母后和大臣辅政。此后明朝完成长江下游、北方和云南以外多地整合，1371年派军入川，大夏在军事压力与内部选择下投降。明昇后来被迁往高丽，政权结束不等于四川原有官员、军民和制度全部消失；明朝需要接收城市、人口和赋税网络。把大夏写到明玉珍去世即止，会忽略幼主政治和区域整合过程。它曾是元末多种秩序之一，既继承天完网络又发展四川治理，为理解明初如何纳入西南提供必要前史。", ["v134_ms123_rivals", "v134_dpm_red_turbans", "226244"], ["v134_daxia_sichuan", "founding"], ["yuanzhang", "y_xu_shouhui"]),
        ]),
    }

    addenda = {
        "v134_hanshan_s1": "因此，页面以可定位的1351年筹划和被捕为骨架，不替材料空白编造童年、师承或秘密头衔。",
        "v134_hanshan_s2": "这些观念能够跨村落传播，正因为它们同时回答苦难从何而来、谁有资格带来新秩序。",
        "v134_hanshan_s3": "分析动员还要区分传说出现的年代，否则后来的生动故事会反过来冒充起事现场记录。",
        "v134_hanshan_s4": "官府提前行动与各地随后爆发并不矛盾，反而说明危机已经超出捕杀少数首领所能控制。",
        "v134_hanshan_s5": "这种死后影响不是个人神秘力量，而是幸存者继续使用共同记忆、亲属身份和政治语言的结果。",
        "v134_liufutong_s1": "颍州靠近河淮交通与灾区，人员和消息能够流动，也使新队伍很快面对元军与地方武装夹击。",
        "v134_liufutong_s2": "龙凤纪年进入公文和军印后，时间本身也成为政治边界，使用哪一种年号就是在表达归属。",
        "v134_liufutong_s3": "远征军彼此难以救援时，局部胜利也可能扩大整体脆弱性，尤其在元军恢复外围据点之后。",
        "v134_liufutong_s4": "对城内家庭而言，迁都带来官署与军队，也带来粮价、役使和围城风险，政治象征有具体生活成本。",
        "v134_liufutong_s5": "史料能确定的下限和后世推测应分层展示，让不确定性成为理解战争混乱的一部分。",
        "v134_hanliner_s1": "他的年龄也只能约计，不宜为追求叙述整齐而给出缺乏原始依据的精确出生年月。",
        "v134_hanliner_s2": "印章的重量、文字和编号让抽象政权落到一件可观察物上，也提醒制度研究不能只靠帝王称号。",
        "v134_hanliner_s3": "这段关系介于联盟、名义臣属与实力自治之间，用后世成熟朝廷的上下级框架会产生误导。",
        "v134_hanliner_s4": "居所转移也是权力转移：失去自己的护卫和财政后，皇帝称号能调动的资源随之缩小。",
        "v134_hanliner_s5": "把争议公开并不会削弱叙事，反而能训练读者区分事件、动机、受益关系与直接证据。",
        "v134_xushouhui_s1": "“天完”名号的确切构词解释存在讨论，页面不把流行拆字说当成已证的建国纲领。",
        "v134_xushouhui_s2": "将领辖区之间既合作又竞争，中央称号提供联系，却未形成一套随时可核的统一财政账册。",
        "v134_xushouhui_s3": "这也解释了宫廷迁移为何频繁：首领所在城市必须依靠当时最强军队保护，反过来又受其约束。",
        "v134_xushouhui_s4": "观察官号、军队和都城三者何时分离，比用忠臣与叛将的道德标签更接近权力变化。",
        "v134_xushouhui_s5": "天完的遗产后来分别进入汉与大夏，两条路径说明政权解体不等于组织资源当场消失。",
        "v134_chenyou_s1": "从簿掾到元帅的变化也提示，元末军队需要能处理文字和财赋的人，并非只有冲锋者能够上升。",
        "v134_chenyou_s2": "旧天完官员是否继续任职、军队是否承认新年号，都是建国能否越过称帝仪式的现实检验。",
        "v134_chenyou_s3": "舰队规模还受水位季节影响，适合长江干流的船阵进入湖区后，操作条件不会保持不变。",
        "v134_chenyou_s4": "战后材料偏重统帅决策，守城百姓、伤员和船工的损失难以量化，不能因此从解释中删除。",
        "v134_chenyou_s5": "陈理的存在还校正了常见时间线：1363年是决定性转折，1364年才是汉政权的制度终点。",
        "v134_fang_s1": "船队的机动性使官军难以迫其决战，岸上家属、修船点和贸易关系则是它无法脱离的固定基础。",
        "v134_fang_s2": "同一封授官文书，在大都眼中是臣属证明，在浙东可能只是暂时停战和资源交换的凭据。",
        "v134_fang_s3": "因此评估势力范围不能只数州县，还要看船只何处补给、哪些港口愿意提供人员和仓储。",
        "v134_fang_s4": "书信中的谦卑称谓属于谈判语言，不能直接换算成实际服从程度，军事部署提供了另一层证据。",
        "v134_fang_s5": "沿海经验随后被纳入更严格的海防秩序，延续与重组同时发生，不是简单换一面旗帜。",
        "v134_zhang_s1": "水网交通帮助队伍快速移动，也让盐税、关卡和地方市场成为起事后必须争夺的治理节点。",
        "v134_zhang_s2": "围城解除后的武器、降卒和声望被张氏吸收，才把一次幸存转化为进入江南的实际能力。",
        "v134_zhang_s3": "文人出仕既可能追求秩序和生计，也可能基于地方关系，不能全部解释成对某位首领的道德认同。",
        "v134_zhang_s4": "安丰战事把韩宋、张氏与朱氏三套政治网络直接交叉，元末竞争远不止元军与起义军两方。",
        "v134_zhang_s5": "围城后的饥馑数字和惨烈故事来源层次不一，正文保留可核过程，不用夸张细节制造戏剧性。",
        "v134_ming_s1": "带兵加入而非孤身投奔，使他在新体系中拥有谈判能力，也解释后来为何能在西线自行决策。",
        "v134_ming_s2": "四川内部并非同质空间，盆地水路、川东山地和边缘区域对政权命令的回应速度并不相同。",
        "v134_ming_s3": "政权名称和年号可核，具体法令的覆盖面则必须降格表达，避免把传记赞语直接写成社会实效。",
        "v134_ming_s4": "恢复秩序的证据若只来自统治者传记，往往看不见未服从地区，因此结论必须保留空间边界。",
        "v134_ming_s5": "明军入川后的接收也不是纯军事尾声，而是元末多套地方秩序重新编入全国政权的过程。",
    }
    for value in articles.values():
        for item in value["sections"]:
            item["text"] += addenda[item["id"]]

    for pid, value in articles.items():
        upsert_article(data["articles"], value)

    data["version"] = max(data.get("version", 0), 108)
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
