#!/usr/bin/env python3
"""One-time, reviewable migration for the V123 Five Dynasties biography cleanup."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "App/Resources/history.json"


POLITY_CONTEXT = {
    "中原五代": (
        "中原王朝以开封、洛阳为政治中心，却不能把诏令直接等同于对所有州县的有效控制。禁军、侍卫亲军、地方节度使和枢密机构共同分配兵权，皇位更替往往由军队拥立、宫廷政变与外部战争交织推动。",
        "河北与河东的军事集团、契丹力量和黄河交通始终影响朝局。城池易手不仅改变国号，也会带来军粮征调、人口迁徙和官员重新归属；文官、礼仪与财政制度则在频繁改朝换代中保持相当连续性。",
    ),
    "吴": (
        "杨吴控制淮南和江东，名义上的杨氏王权与徐温集团掌握的军政实权并不完全重合。扬州、金陵及长江水运把粮食、盐业和军队调动连在一起，使这一政权既与中原争衡，也成为南唐建立的制度基础。",
        "理解吴国不能只看宫廷禅代，还要观察地方州镇、河道交通和士人流动。937年的政权转换改变了国号与统治家族，但许多官僚、赋税网络和区域经营并没有在同一天重新开始。",
    ),
    "南唐": (
        "南唐以金陵为中心经营江淮，曾趁闽、楚内乱扩大控制，后来又在后周进攻下割让江北并去帝号。它的词、绘画和宫廷文化十分醒目，却建立在农业税收、长江运输、州县治理和持续军事支出之上。",
        "975年金陵陷落是政权终点，不是江南社会突然中断。官僚与艺术人才向宋廷流动，旧有城市、生产和文化网络继续变化；亡国叙事若只围绕君主才情，便会遮蔽战争和财政对普通人的影响。",
    ),
    "荆南": (
        "荆南疆域不大，却控制江陵这一长江中游交通节点。高氏向相邻强权反复称臣、接待使者并维持转运，不应简单理解为反复无常，而是小国在后梁、后唐、楚、南唐和宋之间求存的现实策略。",
        "江陵的价值来自水陆交通、商旅和信息汇集，也意味着军队借道与大国施压会迅速传到本地。963年高继冲归宋减少了全面攻城的破坏，但权力、军队和税收体系仍经历重新编组。",
    ),
    "闽": (
        "闽国立足福建多山地形和福州港口，海路贸易、地方豪族与州镇军权同时塑造政局。王审知时期形成的相对秩序并未自动延续，后来宗室分裂、亲军介入和福州建州对立逐渐消耗统治能力。",
        "945年南唐灭闽并不等于福建从此完全安定，福州一带随后仍有李仁达等势力。港口贸易和佛道活动可以与宫廷暴力并存，因此不能用繁荣器物掩盖征敛、兵变及地方社会承受的压力。",
    ),
    "楚": (
        "楚以潭州为中心控制湖南，茶叶生产、商路和向周边政权输送物资构成财政的重要部分。马殷经营出的区域网络为政权提供基础，但宫廷营建、军费与宗室分权也持续消耗这些资源。",
        "马殷死后诸子争位，950至951年的内战使军队和地方势力直接介入继承。南唐进入长沙终结马氏政权，却没有立刻消除地方竞争；把这一过程写成单纯家族伦理失败，会漏掉财政和军镇结构。",
    ),
    "前蜀": (
        "前蜀依托成都平原和山地关隘，在中原战争频仍时维持西南政权。农业、盐井、手工业与成都城市文化为王氏统治提供资源，而宫廷消费和边防军费也不断争夺同一套财政能力。",
        "925年后唐军越过险阻后，前蜀迅速瓦解，说明天然屏障不能代替军政组织。政权灭亡以后，四川的生产、人口和文化网络仍延续，并成为后蜀及宋接收西南时必须面对的基础。",
    ),
    "后蜀": (
        "后蜀承接后唐在四川的军政体系，又依靠成都平原、山川防线和地方官僚维持较长统治。孟昶时期的城市文化与相对安定值得重视，但不能由都城景象推断所有州县都同样富足。",
        "965年宋军入蜀后，财政仓储、军队与地方官员被重新接收。史书关于府库丰厚的记录能说明国家积累，却不能直接证明民众普遍生活优裕；税役、运输和战争成本需要另行考察。",
    ),
    "吴越": (
        "吴越以杭州和两浙为核心，水网、海塘、港口与山地州县共同构成区域治理。钱氏长期奉中原王朝正朔，同时保有实际统治，这既是外交策略，也减少了与北方强权持续正面战争的风险。",
        "水利、佛教造像和海上往来留下丰富物证，但这些成果依赖赋税、劳役、技术与地方组织，不能只写成君主个人功德。978年纳土避免大规模攻城，随后仍有官员、军队和制度整合，并非毫无成本的瞬间交接。",
    ),
    "南汉": (
        "南汉以广州为中心控制岭南，海上交通、内陆州县和南方物产为政权提供资源。宫廷能够接触远方物品，不表示财富平均分布；宦官政治、宗室清洗和地方征敛同样是统治结构的一部分。",
        "971年宋军南下使南汉灭亡，边界变化随后落实为军队裁并、州县接收与财政重组。传统史书偏重宫廷逸事，阅读时应把猎奇叙述与可以核实的制度、战争和区域社会事实分开。",
    ),
    "北汉": (
        "北汉以太原和河东军事网络为根基，在后周、宋的持续压力下依靠与辽的关系维持。它延续后汉名号，却不是简单把中原王朝原样搬到山西；山地防御、边境军镇和外援共同限定其选择。",
        "979年太原投降后，五代以来的一个割据中心被纳入宋朝，但宋辽对峙并未结束。围城、粮运和兵役给地方社会造成的代价，不应被“统一完成”的结论遮蔽。",
    ),
}


ROLE_CONTEXT = {
    "fd_li_keyong": ("中原五代", "李克用虽然没有建立后唐，却以河东军镇和沙陀军事集团为李存勖留下核心力量；他与朱温的竞争把晚唐藩镇战争延续到五代政治。"),
    "fd_gu_cheng": ("吴越", "顾全武的意义主要在钱镠扩张两浙的军事过程；将领行动须放回杭州政权形成、州镇兼并和战后处置之中。"),
    "fd_xuwen": ("吴", "徐温从吴国将领上升为实际决策者，并让养子徐知诰进入权力核心；杨氏仍保留名号时，军政实权已经发生转移。"),
    "fd_fengdao": ("中原五代", "冯道历仕多个中原政权，既被后世批评失节，也显示文官、文书和官学事业能够跨越短促王朝延续；评价不应替代对其具体职务的分析。"),
    "fd_jing_yanguang": ("中原五代", "景延广与石重贵朝对契丹称孙不称臣的强硬政策相关，争端随后进入战争；把后晋覆亡全归于一人，同样会忽略军力、外交和内部决策结构。"),
    "fd_sang_weihan": ("中原五代", "桑维翰参与劝进石敬瑭并处理后晋对契丹关系，燕云割让与援兵条件是其政治生涯无法绕开的背景；其后失势也反映宫廷派系变化。"),
    "fd_wang_pu": ("中原五代", "王朴在后周参与制度规划、历法修订与用兵谋划，他的《平边策》体现的是分步骤整合诸国的战略判断。"),
    "fd_zhao_kuangyin": ("中原五代", "赵匡胤由后周禁军将领成为宋朝皇帝，陈桥兵变既延续军队拥立的五代逻辑，也开启重新安排禁军与地方军权的新阶段。"),
    "fd_han_xizai": ("南唐", "韩熙载的政治经历与《韩熙载夜宴图》的图像传统必须分开：现存画卷通常被视为宋摹本，不能当作顾闳中在场写真的无条件证据。"),
    "fd_gu_hongzhong": ("南唐", "顾闳中与《韩熙载夜宴图》的传统归属十分重要，但作品流传、摹写与后世题跋构成复杂证据链；画面不能直接替代人物传记。"),
    "fd_huang_quan": ("后蜀", "黄筌服务于西蜀宫廷，精细设色的花鸟传统后来进入宋代宫廷评价体系；所谓画派标签是后世概括，不等于当时只有一种创作方法。"),
    "fd_xu_xi": ("南唐", "徐熙被后世用来代表江南花鸟传统，并常与黄筌并举；传世归属和风格描述多经宋人整理，不能把后来的“黄家富贵、徐熙野逸”当作同时代原话。"),
    "fd_guan_tong": ("中原五代", "关仝应放在五代北方山水画的师承与作品流传中理解；传世作品题名也需要区分原作、旧传与后世鉴定。"),
    "fd_jing_hao": ("中原五代", "荆浩与《笔法记》及北方山水传统相关，太行山活动的叙述影响深远；文本作者、作品归属和后世画史记载仍应分别衡量。"),
    "fd_zhou_wenju": ("南唐", "周文矩作为南唐画院人物，宫廷生活题材帮助观察服饰、陈设和观看方式；画面经过流传摹写，不能自动当成社会全景。"),
    "fd_tan_qiao": ("闽", "谭峭及《化书》提供了五代思想史的另一条线索，但其生平记载有限，作品成书和传承问题也不能由后世传说填满。"),
    "fd_he_ning": ("中原五代", "和凝历仕后梁至后周，参与典章文书并以文学知名；他的经历呈现多朝更替中文官知识与行政实践的连续性。"),
}


EVENT_FIXES = {
    "fd_gu_cheng": ("v123_gu_quanwu", ["fd_gu_cheng", "fd_wy_qianliu"]),
    "fd_xuwen": ("v123_xu_wen", ["fd_xuwen", "fd_wu_longyan", "fd_nt_bian"]),
    "fd_jing_yanguang": ("v123_jing_yanguang", ["fd_jing_yanguang", "fd_chonggui", "fd_sang_weihan"]),
    "fd_sang_weihan": ("v123_sang_weihan", ["fd_sang_weihan", "fd_jingtang", "fd_chonggui"]),
    "fd_wang_pu": ("v123_wang_pu", ["fd_wang_pu", "fd_chairong", "fd_zhao_kuangyin"]),
    "fd_guan_tong": ("v123_guan_tong", ["fd_guan_tong", "fd_jing_hao"]),
    "fd_he_ning": ("v123_he_ning", ["fd_he_ning", "fd_fengdao"]),
}


NEW_EVENTS = [
    {
        "id": "v123_gu_quanwu", "year": "896—897", "title": "顾全武与两浙军镇整合", "category": "军事",
        "body": "钱镠与董昌决裂后，顾全武参与攻取越州。战争结果使杭州集团扩大到浙东，但胜利不等于地方秩序自然恢复，州镇接收、军队安置和赋役调整仍需持续进行。",
        "impact": "这场战争促使杭州集团扩展到浙东，并把军镇接收、军队安置和赋役调整推到吴越政权形成的核心位置。",
        "people": ["fd_gu_cheng", "fd_wy_qianliu"], "peopleRoles": {"fd_gu_cheng": "吴越将领", "fd_wy_qianliu": "杭州集团首领"},
        "sources": ["v54_new", "v54_zztj"],
    },
    {
        "id": "v123_xu_wen", "year": "905—927", "title": "徐温掌握杨吴军政", "category": "政治",
        "body": "杨行密死后，吴国内部权力重组。徐温在诛除张颢后逐步掌握军政，并让养子徐知诰居于金陵；杨氏君主保留名号，实际决策中心却已转移。",
        "impact": "这段长期权力转移改变了杨吴的决策中心，也为937年徐知诰建立南唐准备了政治与人员基础。",
        "people": ["fd_xuwen", "fd_wu_longyan", "fd_nt_bian"], "peopleRoles": {"fd_xuwen": "吴国权臣", "fd_wu_longyan": "名义君主", "fd_nt_bian": "徐温养子与继承者"},
        "sources": ["v54_new", "v54_zztj"],
    },
    {
        "id": "v123_jing_yanguang", "year": "942—946", "title": "景延广与后晋对辽关系转硬", "category": "政治",
        "body": "石重贵即位后，后晋对契丹的礼仪和外交立场转趋强硬，景延广是重要推动者。双方随后反复交战，但后晋覆亡还涉及兵力、将领倒戈和辽军南下，不能归结为一句失言。",
        "impact": "礼仪称谓在这里连接真实权力关系，却不是解释战争全部原因的唯一钥匙。",
        "people": ["fd_jing_yanguang", "fd_chonggui", "fd_sang_weihan"], "peopleRoles": {"fd_jing_yanguang": "强硬政策推动者", "fd_chonggui": "后晋皇帝", "fd_sang_weihan": "主张谨慎处理对辽关系"},
        "sources": ["v54_old", "v54_zztj"],
    },
    {
        "id": "v123_sang_weihan", "year": "936—947", "title": "桑维翰与后晋建国及外交", "category": "政治",
        "body": "桑维翰参与劝进石敬瑭，并在后晋处理军政和对契丹关系。燕云割让及向契丹求援构成建国条件；石重贵朝路线改变后，他的政治位置也随之变化。",
        "impact": "个人谋划必须与后唐内战、契丹军力和后晋内部派系一并考察。",
        "people": ["fd_sang_weihan", "fd_jingtang", "fd_chonggui"], "peopleRoles": {"fd_sang_weihan": "后晋宰相", "fd_jingtang": "建国者", "fd_chonggui": "继任皇帝"},
        "sources": ["v54_old", "v54_zztj"],
    },
    {
        "id": "v123_wang_pu", "year": "954—959", "title": "王朴参与后周制度与用兵规划", "category": "政治",
        "body": "柴荣时期，王朴参与制度、历法和对外战略规划。《平边策》以分步骤削弱周边政权为思路，与后周整军、征南唐和北取关南的实践相互参照。",
        "impact": "这些规划把制度建设、财政能力与分阶段用兵连在一起，显示后周整合周边政权并非只有战场决胜。",
        "people": ["fd_wang_pu", "fd_chairong", "fd_zhao_kuangyin"], "peopleRoles": {"fd_wang_pu": "后周官员", "fd_chairong": "决策者", "fd_zhao_kuangyin": "后周将领"},
        "sources": ["v54_old", "v54_new"],
    },
    {
        "id": "v123_guan_tong", "year": "10世纪前期", "sortYear": 930, "title": "关仝与北方山水画传统", "category": "文化",
        "body": "北宋画史将关仝与荆浩联系，并把他置于北方山水传统中。今天讨论其作品时，需要区分画史记载、旧题归属和后世递藏，不能把题名直接当成作者身份的充分证明。",
        "impact": "关仝与荆浩在后世画史中共同构成北方山水传统的重要坐标，其意义主要见于作品归属、摹写与风格谱系。",
        "people": ["fd_guan_tong", "fd_jing_hao"], "peopleRoles": {"fd_guan_tong": "山水画家", "fd_jing_hao": "前辈画家与理论传统"},
        "sources": ["v54_new"],
    },
    {
        "id": "v123_he_ning", "year": "936—959", "title": "和凝与多朝文官连续性", "category": "文化",
        "body": "和凝历仕后梁、后唐、后晋、后汉和后周，参与诏令、礼制与文书工作。频繁改朝换代没有让官僚知识每次归零，典章、文字和人才在新政权中被重新使用。",
        "impact": "他的经历说明五代文化不只存在于绘画，也存在于维持行政运转的文书实践。",
        "people": ["fd_he_ning", "fd_fengdao"], "peopleRoles": {"fd_he_ning": "官员与文学家", "fd_fengdao": "同时期多朝文官"},
        "sources": ["v54_old", "v54_new", "v54_wudaihuiyao"],
    },
]


def polity_for(pid: str, sequence: dict[str, str]) -> tuple[str, str]:
    if pid in ROLE_CONTEXT:
        return ROLE_CONTEXT[pid]
    polity = sequence[pid]
    return polity, ""


def cleaned_reading(person: dict, polity: str, specific: str) -> str:
    name = person["name"]
    reign = person.get("reign") or ""
    summary = person["summary"].rstrip("。")
    first, second = POLITY_CONTEXT[polity]
    identity = f"{name}不能只由“{summary}”这一句概括。"
    if reign:
        identity += f"其统治时段标作{reign}，这是定位政权先后的坐标，不表示当时全中国只有一条共同帝序。"
    else:
        identity += "其活动处在多个政权并立、人员与技术跨区域流动的环境，身份标签不能替代具体经历。"
    if specific:
        anchor = specific
    elif person["kind"] == "皇帝":
        anchor = f"对{name}的评价应先核对即位方式、实际控制范围和权力终结，再讨论道德褒贬；{summary}只是其中最醒目的节点。"
    else:
        anchor = f"{name}作为{person['kind']}留下的影响，需要从任职、作品或军事行动的证据出发；{summary}只是进入问题的线索。"
    method = (
        f"把{name}放回区域社会，还要区分三层后果：宫廷和军队怎样作出选择，州县与地方家族怎样执行或抵抗，税役、迁徙和战争又怎样落到普通人身上。"
        "正史擅长记录废立、征伐和君臣言论，却很少连续呈现家庭生计；器物、墓葬、碑刻与地方材料可以补充观察，也不能由一件精美遗物反推整个社会繁荣。"
    )
    boundary = (
        f"因此，{name}的长期意义不在给{polity}贴上“兴”或“亡”的单一标签，而在辨认个人选择受到哪些军政结构约束，又给既有区域网络带来什么改变。"
        "能够确认的事实、基于多种材料的解释与后世形成的评价应分层陈述；材料没有回答的部分，应保留空白而不是用传说补齐。"
    )
    return "\n\n".join([identity + anchor, first + second, method, boundary])


def main() -> None:
    data = json.loads(DATA_PATH.read_text())
    people = {person["id"]: person for person in data["people"]}
    sequence = {item["person"]: item["polity"] for item in data["sequence"] if item.get("polity")}
    data["events"] = [event for event in data["events"] if event["id"] != "v123_gu_quanwuu"]
    for event in NEW_EVENTS:
        event.setdefault("kind", "历史事件")
    new_by_id = {event["id"]: event for event in NEW_EVENTS}
    data["events"] = [new_by_id.get(event["id"], event) for event in data["events"]]
    event_ids = {event["id"] for event in data["events"]}
    for event in NEW_EVENTS:
        if event["id"] not in event_ids:
            data["events"].append(event)

    changed = []
    for article in data["articles"]:
        pid = article["person"]
        if not pid.startswith("fd_"):
            continue
        repeated_section = None
        for section in article["sections"]:
            sentences = [part.strip() for part in re.split(r"[。！？]", section["text"]) if len(part.strip()) >= 12]
            if len(sentences) != len(set(sentences)):
                repeated_section = section
                break
        if repeated_section is None:
            continue
        polity, specific = polity_for(pid, sequence)
        repeated_section["title"] = "把人物放回区域社会"
        repeated_section["text"] = cleaned_reading(people[pid], polity, specific)
        repeated_section["sources"] = list(dict.fromkeys(article["sources"] + ["v54_wudaihuiyao", "v122_cssn_military"]))
        changed.append(pid)

    assert len(changed) in {0, 73}, len(changed)
    for article in data["articles"]:
        pid = article["person"]
        if pid not in EVENT_FIXES:
            continue
        event_id, related_people = EVENT_FIXES[pid]
        for section in article["sections"]:
            if section["id"].startswith(pid + "-v54-"):
                section["events"] = [event_id]
                section["people"] = related_people
                section["sources"] = list(dict.fromkeys(section["sources"] + ["v54_wudaihuiyao"]))
        article["sources"] = list(dict.fromkeys(article["sources"] + ["v54_wudaihuiyao"]))

    # The legacy generator rotated the fourth section onto a later ruler's event.
    # Re-anchor the rewritten regional reading to the subject's reviewed lead event.
    for article in data["articles"]:
        if not article["person"].startswith("fd_"):
            continue
        lead = next((section for section in article["sections"] if section["id"].endswith("-v54-1")), None)
        regional = next((section for section in article["sections"] if section["id"].endswith("-v54-4")), None)
        if lead and regional:
            regional["events"] = lead["events"]
            regional["people"] = lead["people"]

    data["version"] = 97
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"rewrote {len(changed)} repeated Five Dynasties readings and corrected {len(EVENT_FIXES)} event mappings")


if __name__ == "__main__":
    main()
