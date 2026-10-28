#!/usr/bin/env python3
"""Replace the four remaining V54 template sections with subject-specific readings."""

from __future__ import annotations

import json
from pathlib import Path

from rewrite_v123_five_dynasties import POLITY_CONTEXT, ROLE_CONTEXT


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "App/Resources/history.json"

ARTISTS = {
    "fd_gu_hongzhong", "fd_huang_quan", "fd_xu_xi", "fd_guan_tong",
    "fd_jing_hao", "fd_zhou_wenju",
}
NIGHT_FIGURES = {"fd_han_xizai", "fd_gu_hongzhong"}
THINKERS = {"fd_tan_qiao"}

MATERIAL = {
    "中原五代": "开封与洛阳城址、墓葬材料、钱币和制度文书",
    "吴": "扬州与金陵城址、淮南钱币、瓷器和长江沿线考古材料",
    "南唐": "金陵遗址、南唐二陵、钱币、陶瓷和传世书画",
    "荆南": "江陵城址、水陆交通遗迹、墓葬和区域出土器物",
    "闽": "福州城址、闽国墓葬、钱币、瓷器与海路贸易遗存",
    "楚": "长沙及湖南州县遗址、钱币、墓葬和茶业交通材料",
    "前蜀": "成都城址、前蜀帝陵、墓葬器物与四川地区考古材料",
    "后蜀": "成都城址、后蜀墓葬、陶瓷和西蜀绘画著录",
    "吴越": "杭州城址、海塘遗迹、钱氏墓葬、越窑器和佛教造像",
    "南汉": "广州城址、南汉陵墓、陶瓷和海上交通遗物",
    "北汉": "太原城址、河东墓葬、边防遗迹和宋辽战争考古材料",
}

EVENT_IMPACTS = {
    "v123_gu_quanwu": "这场战争促使杭州集团扩展到浙东，并把军镇接收、军队安置和赋役调整推到吴越政权形成的核心位置。",
    "v123_xu_wen": "这段长期权力转移改变了杨吴的决策中心，也为937年徐知诰建立南唐准备了政治与人员基础。",
    "v123_wang_pu": "这些规划把制度建设、财政能力与分阶段用兵连在一起，显示后周整合周边政权并非只有战场决胜。",
    "v123_guan_tong": "关仝与荆浩在后世画史中共同构成北方山水传统的重要坐标，其意义主要见于作品归属、摹写与风格谱系。",
}

REGIONAL_REPLACEMENTS = {
    "不能误接到后唐灭前蜀": "需要放回后周制度建设与分阶段用兵的同一脉络",
    "而非误接徐熙江南花鸟画": "也呈现多朝更替中文官知识与行政实践的连续性",
}


def polity_for(pid: str, sequence: dict[str, str]) -> str:
    if pid in ROLE_CONTEXT:
        return ROLE_CONTEXT[pid][0]
    return sequence[pid]


def position_text(person: dict, polity: str) -> str:
    name, summary = person["name"], person["summary"].rstrip("。")
    call = person.get("call", "").strip()
    reign = person.get("reign", "").strip()
    if reign:
        identity = f"{name}在{reign}进入{polity}的统治序列"
        if call:
            identity += f"，史籍常以“{call}”标识其身份"
        return (
            identity + f"。现有资料最醒目的线索是“{summary}”。这段在位时间只表示{name}在本政权内部的先后位置，"
            f"不等于同一时期各地都承认{polity}的君主名号。阅读{name}时，应同时核对实际控制范围、"
            "对外称号和向其他政权使用的礼仪，避免把称帝、称王或节度使名义混成一种权力。"
        )
    return (
        f"{name}以“{person['kind']}”进入五代十国史，核心线索是：{summary}。"
        f"{name}并非独立于政权结构的孤立名人，其活动与{polity}的人员流动、资源组织或文化网络相连。"
        f"{name}所处年代往往只能由任职、交往和作品著录约略定位，材料不能支持的生卒年与行踪不作补写。"
    )


def power_text(person: dict, event: dict, polity: str) -> str:
    pid, name = person["id"], person["name"]
    role = (event.get("peopleRoles") or {}).get(person["id"], person["kind"])
    when = event["year"] + ("的" if "世纪" in event["year"] or event["year"].endswith("年") else "年的")
    if pid in ARTISTS or pid in NIGHT_FIGURES:
        mechanism = f"{name}的影响要经过创作、摹写、收藏、题跋和画史著录才被后世看见，不能套用君主下令便直接执行的模型"
    elif pid in THINKERS:
        mechanism = f"{name}的思想影响依靠文本写定、抄传和后世阐释扩散，作品流传不等于生平细节都可以复原"
    else:
        mechanism = f"{name}的个人决定要经过{polity}的军队、宫廷或官僚网络才会产生后果"
    return (
        f"与{name}直接相关的节点是{when}“{event['title']}”。{event['body'].rstrip('。')}。"
        f"在这项变化中，{name}的可确认身份是{role}；{mechanism}。"
        f"{name}所对应的结果是：{event['impact']} 因此，解释{name}既不能把结果全归于性格，也不能用制度二字抹去个人在具体时刻的选择。"
    )


def evidence_text(person: dict, polity: str) -> tuple[str, list[str]]:
    pid, name = person["id"], person["name"]
    if pid in NIGHT_FIGURES:
        return (
            f"讨论{name}必须区分画史记载、传世画卷与人物生平。故宫所藏《韩熙载夜宴图》现存本通常按宋摹本说明，"
            f"画面能帮助观察后世如何塑造{name}及南唐宫廷生活，却不能直接证明每个场景都由画家现场记录。"
            f"对{name}而言，题跋、递藏与摹写过程本身也是历史证据，作品年代和作者归属应保留限定。",
            ["v54_dpm", "v54_night"],
        )
    if pid in ARTISTS:
        return (
            f"认识{name}主要依靠后世画史著录、旧传作品、题跋与收藏记录。国立故宫和故宫博物院的五代书画资料能够说明作品流传与风格判断，"
            f"但署名为{name}不自动等于真迹，摹本也不是毫无价值的赝品。应把作者归属、创作年代、后世摹写和今天的鉴定意见分开陈述，"
            f"不由署名{name}的一幅画复原整个五代社会。",
            ["v54_dpm", "v54_npm"],
        )
    if pid in THINKERS:
        return (
            f"认识{name}主要依靠传世文本及后世目录、序跋和思想史著录。《化书》的概念可以分析五代知识世界，"
            f"却不能把书中每句话直接还原为{name}在某年某地的个人经历。版本传承与生平传说属于不同证据链，"
            "文本能够证明思想表达，不足以填补所有行踪空白。",
            ["v54_new", "v54_wudaihuiyao"],
        )
    material = MATERIAL[polity]
    return (
        f"与{name}同时代的证据包括{material}。这些材料能够检验城市、财政、交通、信仰和消费环境，"
        f"但多数并非{name}本人使用或下令制作的遗物。把文献中的{name}行动与考古层位、器物年代相互校核时，"
        f"只能说明彼此支持到什么程度；没有出土地点或可靠递藏的器物，不能仅凭风格附会到{name}。",
        ["v54_chnm", "v54_kaogu"],
    )


def source_text(person: dict, polity: str) -> str:
    pid, name = person["id"], person["name"]
    if pid in ARTISTS or pid in NIGHT_FIGURES:
        return (
            f"{name}的记载常由后世画史、作品题跋和收藏著录层层累积，信息产生时间可能晚于人物生活年代。"
            f"本篇把涉及{name}的馆藏定名写成“传、旧传或宋摹”等可见限定，不把艺术史归属改写成无争议传记。关于{name}的风格评价可作为接受史，"
            f"对{name}的风格判断不能反向证明失载的宫廷活动；不同机构意见不一致时保留分歧。"
        )
    if pid in THINKERS:
        return (
            f"关于{name}，传世著作、正史零散材料和后世道教传记的目的不同。文本内容可以讨论思想，神异故事则首先反映后世信仰与人物记忆。"
            f"本篇不因{name}生平材料稀少便把传说补成连续年谱，也不由现代概念替古人预设完整学派身份。"
        )
    if polity in {"中原五代", "北汉"}:
        return (
            f"{name}的基本年代以《旧五代史》《新五代史》和《资治通鉴》互校。《旧五代史》保存较多五代朝廷材料，"
            f"就{name}而言，《新五代史》带有鲜明褒贬义例，《资治通鉴》便于核对事件先后；三者共享材料时不算三份独立证据。阅读{name}时，"
            f"涉及{name}的事实记载、史家评论和后世道德标签分别处理。"
        )
    return (
        f"{name}所属的{polity}主要依靠《新五代史》十国世家、《资治通鉴》及相关制度、考古材料互校。中原王朝编成的史书常从统一后的正统秩序回看地方政权，"
        f"对{name}的称号、礼仪和兴亡评价可能带有立场。关于{name}，本文保留可核对的年代与行动，把史家评论视为解释对象，"
        "不将亡国结局倒推成所有早期选择都必然失败。"
    )


def cultural_regional_text(person: dict, polity: str) -> str:
    pid, name = person["id"], person["name"]
    summary = person["summary"].rstrip("。")
    if pid in THINKERS:
        medium = "文本的写定、抄传、重编和后世注释"
        evidence = "《化书》的版本、目录著录与道教传记"
    else:
        medium = "画院或私人赞助、工作坊协作、摹写收藏和后世画史"
        evidence = "传世作品、题跋、递藏记录与机构鉴定"
    return "\n\n".join([
        f"{name}不能只由“{summary}”这一句概括。作为{person['kind']}，{name}没有像君主那样留下连续帝纪，今天能够看到的形象主要经过{medium}形成；材料越晚，越需要说明它与人物生活年代的距离。",
        f"{name}所处的{polity}并非只有战争和改朝换代。城市消费、宗教活动、文书教育和跨区域人才流动，为作品或思想提供了产生与传播条件。赞助者、工匠、抄手、收藏者和观看者都参与其中，因此文化成果不能简化为孤立天才的个人创造，也不能反过来证明当地居民普遍富足。",
        f"观察{name}的社会影响，应追踪作品或文本如何离开最初环境。政权灭亡后，人员与藏品可能进入宋廷或其他地区，旧有题材也会被重新摹写和解释；后世建立的风格谱系有助于理解接受史，却未必等同五代人自己的分类。",
        f"这也提醒我们，{name}留下的是一条有缺口的传播链，而不是覆盖整个时代的社会统计。宫廷与城市中的书画、著述和收藏活动，可以呈现特定赞助网络与知识趣味；它们不能替代乡村生产、普通家庭生活或其他地区经验。把文化材料放回具体媒介和受众，才能既看见{name}的历史作用，又不夸大材料所能代表的范围。",
        f"关于{name}，{evidence}分别回答不同问题。能够确认的作品或文字、基于风格与文献的归属判断、后世形成的故事必须分层；没有可靠材料的生卒、师承细节与创作现场保持未知，不用完整传说填补证据空白。",
    ])


def main() -> None:
    data = json.loads(PATH.read_text())
    people = {person["id"]: person for person in data["people"]}
    events = {event["id"]: event for event in data["events"]}
    for event_id, impact in EVENT_IMPACTS.items():
        events[event_id]["impact"] = impact
    sequence = {item["person"]: item["polity"] for item in data["sequence"] if item.get("polity")}
    changed = 0
    for article in data["articles"]:
        pid = article["person"]
        if not pid.startswith("fd_"):
            continue
        sections = {section["id"].rsplit("-", 1)[-1]: section for section in article["sections"] if "-v54-" in section["id"]}
        if not all(key in sections for key in ["1", "2", "3", "4", "5"]):
            continue
        person = people[pid]
        polity = polity_for(pid, sequence)
        lead_event = events[sections["1"]["events"][0]]
        evidence, evidence_sources = evidence_text(person, polity)
        replacements = {
            "1": ("身份、时间与政权", position_text(person, polity)),
            "2": ("决定发生在什么结构中", power_text(person, lead_event, polity)),
            "3": ("哪些材料能够作证", evidence),
            "5": ("史书如何塑造人物", source_text(person, polity)),
        }
        for key, (title, text) in replacements.items():
            section = sections[key]
            section["title"] = title
            section["text"] = text
            section["events"] = [lead_event["id"]]
            section["people"] = lead_event["people"]
            section["sources"] = list(dict.fromkeys(article["sources"] + lead_event["sources"] + (["v54_wudaihuiyao"] if key in {"1", "2", "5"} else evidence_sources)))
        sections["4"]["events"] = [lead_event["id"]]
        sections["4"]["people"] = lead_event["people"]
        if pid in ARTISTS or pid in THINKERS:
            sections["4"]["text"] = cultural_regional_text(person, polity)
        else:
            for old, new in REGIONAL_REPLACEMENTS.items():
                sections["4"]["text"] = sections["4"]["text"].replace(old, new)
        article["sources"] = list(dict.fromkeys(article["sources"] + lead_event["sources"] + evidence_sources + ["v54_wudaihuiyao"]))
        changed += 1
    assert changed == 73, changed
    data["version"] = 98
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"rewrote four legacy sections and all section relations for {changed} Five Dynasties people")


if __name__ == "__main__":
    main()
