#!/usr/bin/env python3
"""Five-pass reign-context enrichment for history.json.

The script is intentionally idempotent.  It adds a small set of sourced Tang
events where the corpus had no suitable material, then links already reviewed
events to rulers whose reigns overlap them.  A linked event remains period
context unless the ruler is explicitly present in ``event.people``; the UI
discloses that distinction.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "App/Resources/history.json"
data = json.loads(PATH.read_text())
people = {item["id"]: item for item in data["people"]}
events = {item["id"]: item for item in data["events"]}
contexts = {item["person"]: item for item in data["reignContexts"]}
CATEGORIES = ["政治", "军事", "文化", "经济", "社会"]


def add_event(item, rulers):
    if item["id"] not in events:
        data["events"].append(item)
        events[item["id"]] = item
    for ruler in rulers:
        context = contexts[ruler]
        if item["id"] not in context["events"]:
            context["events"].append(item["id"])
        for source in item["sources"]:
            if source not in context["sources"]:
                context["sources"].append(source)


TANG_EVENTS = [
    ({"id":"v91t_taizong_fiscal","year":"627—649","sortYear":627,"title":"均田、租庸调与贞观户籍恢复","body":"隋末战争造成户口流散与州县残破。贞观朝在既有均田、租庸调制度框架内重整户籍、核定赋役，并多次因水旱、霜蝗减免租调。制度并非由唐太宗一人创制，也未在各地整齐落实，但中央把轻徭、节用与恢复编户视为战后治理的重要尺度。","impact":"财政恢复依赖把流民重新纳入州县、让农业生产与赋役秩序逐步接续。它支持了贞观时期的军政运转，也提示所谓“治世”背后仍有地区差异、灾害冲击与基层执行问题。","people":["t_taizong"],"sources":["v43t_jts2","v43t_jts3","v43t_jts48"],"kind":"制度与社会","category":"经济"}, ["t_taizong"]),
    ({"id":"v91t_taizong_relief","year":"628—649","sortYear":628,"title":"赈恤、减役与战后人口安顿","body":"贞观本纪反复记载旱灾、蝗灾、饥馑后的赈给、免租与遣使巡察，也记有释放宫女、减省徭役等措施。这些诏令不能直接等同于所有地方都获得充分救济，却能看出朝廷把灾害响应、刑罚宽简和人口休养放在评价政治得失的同一框架中。","impact":"救灾与减役帮助战后家庭恢复生产，也塑造了后世对贞观政治的记忆。阅读时需要同时看诏令目标和执行边界，避免只用“轻徭薄赋”概括复杂的地方社会。","people":["t_taizong"],"sources":["v43t_jts2","v43t_jts3","v43t_jts48"],"kind":"社会治理","category":"社会"}, ["t_taizong"]),
    ({"id":"v91t_exam_expansion","year":"690—705","sortYear":690,"title":"制举、殿试与官僚入口扩张","body":"武周时期延续并扩大科举与制举取士，传统记载又把亲策贡士、开武举等举措与武则天联系起来。科举尚未取代门荫、荐举和胥吏等入仕路径，但扩大考试与文学才能的政治意义，有助于朝廷从既有高门之外吸纳可用官员。","impact":"取士方式的变化重塑了官僚竞争与政治表达，也为中宗、睿宗复位后的官场留下持续影响。所谓“殿试首创”等细节在后世叙述中常被简化，页面把它放回多种选官方式并存的背景。","people":["t_wuzetian"],"sources":["v43t_jts6","v43t_jts7"],"kind":"教育与选官","category":"文化"}, ["t_wuzetian","t_zhongzong"]),
    ({"id":"v91t_zhou_capital_fiscal","year":"690—705","sortYear":692,"title":"神都营建与武周财政调度","body":"武周以洛阳为神都，宫城、礼仪工程、军费与官僚机构共同增加财政调度压力。与此同时，关东漕运和地方赋税支撑两京体系。史书多从朝廷命令与支出评价这些措施，难以完整量化地方负担，因此不能把繁盛景象直接等同于普遍富足。","impact":"两京政治强化了洛阳的全国性枢纽地位，也显示都城、交通和财政彼此牵动。中宗、睿宗时期仍需面对这一空间格局和支出结构留下的问题。","people":["t_wuzetian"],"sources":["v43t_jts6","v43t_jts7","v43t_jts48"],"kind":"财政与都城","category":"经济"}, ["t_wuzetian","t_zhongzong"]),
    ({"id":"v91t_zhou_social_control","year":"690—705","sortYear":694,"title":"告密、酷吏与武周社会控制","body":"武周政权在重组政治联盟时使用告密、制狱和酷吏侦讯，周兴、来俊臣等人的活动在史书中留下集中记载。材料带有唐室复辟后的评价立场，但大规模政治审讯、官员恐惧和株连风险仍是理解当时社会气氛不可回避的证据。","impact":"高压侦讯帮助新政权打击反对者，也破坏了正常司法边界。它影响官僚行为和家庭安全感，并解释为什么中宗复位后的政治清算、平反与派系重组如此激烈。","people":["t_wuzetian"],"sources":["v43t_jts6","v43t_jts50"],"kind":"司法与社会","category":"社会"}, ["t_wuzetian","t_zhongzong"]),
    ({"id":"v91t_post_rebellion_households","year":"762—779","sortYear":763,"title":"安史乱后流民、户籍与赋役重建","body":"安史之乱结束并不意味着社会立即复原。大量人口迁徙、户籍脱漏、田地荒废与地方军镇坐大，使旧有租庸调基础持续收缩。代宗朝一面处理河北藩镇与吐蕃压力，一面依靠盐利、转运和地方征收维持军政，普通家庭则面对重新编户与多重负担。","impact":"战后重建改变了国家取得资源的方式，并为德宗时期推行两税法准备了财政背景。把流民与户籍问题纳入叙事，可以看见战争结束后的长期社会成本。","people":["t_daizong"],"sources":["v43t_jts11","v43t_jts48","v43t_jts49"],"kind":"战后社会","category":"社会"}, ["t_daizong"]),
    ({"id":"v91t_shence_ganlu","year":"835","sortYear":835,"title":"神策军控制与甘露之变","body":"文宗试图借李训、郑注等人削弱宦官集团，计划在甘露之变中诛除掌握神策军的宦官。谋划泄露后，宦官调兵反击，参与者及许多官员遭杀。事件既是宫廷政变，也是禁军指挥权长期变化的集中爆发。","impact":"失败使文宗进一步受制于宦官与神策军，中央决策的信任结构遭到重创。它说明晚唐军事问题不仅发生在边疆和藩镇，也深嵌于宫城内部的禁军体系。","people":["t_wenzong"],"sources":["v43t_jts17a","v43t_jts17b","v43t_xts207"],"kind":"宫廷与禁军","category":"军事"}, ["t_wenzong"]),
    ({"id":"v91t_dazhong_recovery","year":"847—859","sortYear":847,"title":"大中政局与会昌政策调整","body":"宣宗即位后贬逐李德裕集团，并对会昌灭佛后的若干措施作出调整，恢复部分寺院与僧尼活动；朝廷同时强调吏治、纳谏与旧章。传统史书因此形成“大中之治”的称誉，但党争、宦官和藩镇结构并未消失。","impact":"政策转向缓和了会昌时期急剧变化带来的冲突，也重组了朝廷人事与文化空间。评价这一时期应区分史书的治世叙事与晚唐结构性困境。","people":["t_xuanzong_late"],"sources":["v43t_jts18b","v43t_jts174"],"kind":"政策与文化","category":"文化"}, ["t_xuanzong_late"]),
    ({"id":"v91t_dazhong_finance","year":"847—859","sortYear":850,"title":"盐利、漕运与大中财政","body":"晚唐中央财政高度依赖盐铁与江淮转运。宣宗朝在维持边防、官俸和宫廷开支时，仍需通过盐政与漕运连接东南财赋区和关中。正史留下制度与任官线索，却难以给出全国一致的收支图景，私盐与地方截留也长期存在。","impact":"财政对专卖和远距离运输的依赖，使中央稳定与东南市场、河道安全紧密相连；它也加重了基层征管冲突，为稍后的社会动荡埋下条件。","people":["t_xuanzong_late"],"sources":["v43t_jts18b","v43t_jts48","v43t_jts49"],"kind":"财政与交通","category":"经济"}, ["t_xuanzong_late"]),
    ({"id":"v91t_late_tang_displacement","year":"875—904","sortYear":880,"title":"战争、迁都与晚唐人口流离","body":"黄巢战争及其后的军阀混战使长安、洛阳和多地州县反复遭受破坏。僖宗奔蜀、昭宗受藩镇挟持并最终迁往洛阳，宫廷移动背后是粮运中断、城市居民逃散和地方秩序重组。史书以朝廷行程为主，普通人的损失只能从饥荒、屠掠与户口记载间接重建。","impact":"人口流离和城市衰败削弱了唐廷最后的财政、军事与象征基础，也推动人才、技术和经济活动向区域政权分散，为五代十国格局提供社会背景。","people":["t_xizong","t_zhaozong"],"sources":["v43t_jts19b","v43t_jts20a","v43t_jts200b"],"kind":"战争与社会","category":"社会"}, ["t_xizong","t_zhaozong"]),
    ({"id":"v91t_late_tang_revenue","year":"880—904","sortYear":883,"title":"财赋断裂与地方截留","body":"黄巢战争后，中央难以稳定取得两税、盐利和漕运收入。许多节度使掌握本地军政财赋，贡赋时断时续；朝廷迁徙与禁军开支又增加临时征敛。相关数字并不完整，但本纪和食货材料共同显示中央可支配资源持续萎缩。","impact":"财赋断裂使皇帝更依赖近臣、军阀与临时性索取，加速了中央权威空心化。它解释了晚唐政治危机为何不仅是宫廷斗争，也是国家资源网络的崩解。","people":["t_xizong","t_zhaozong"],"sources":["v43t_jts19b","v43t_jts20a","v43t_jts48","v43t_jts49"],"kind":"财政危机","category":"经济"}, ["t_xizong","t_zhaozong"]),
]

for item, rulers in TANG_EVENTS:
    add_event(item, rulers)


def event_year(event):
    value = event.get("sortYear")
    if isinstance(value, (int, float)):
        return int(value)
    match = re.search(r"(?<!\d)(\d{3,4})", event.get("year", ""))
    return int(match.group(1)) if match else None


def event_bounds(event):
    label = event.get("year", "")
    century_range = re.search(r"(\d{1,2})[—–-](\d{1,2})世纪", label)
    if century_range:
        return (int(century_range.group(1)) - 1) * 100 + 1, int(century_range.group(2)) * 100
    years = [] if "世纪" in label else [int(value) for value in re.findall(r"\d{1,4}", label)]
    if "年代" in label and years:
        years.append(max(years) + 9)
    century = re.search(r"(\d{1,2})世纪", label)
    if not years and century:
        years = [(int(century.group(1)) - 1) * 100 + 1, int(century.group(1)) * 100]
    return (min(years), max(years)) if years else None


def add_overlapping_context(dynasties):
    """Fill a missing lens with one reviewed event inside the reign span.

    This is deliberately broad for multi-state stages: the item is presented as
    contemporaneous stage context, never as an action by the ruler.
    """
    for person_id, context in contexts.items():
        if people[person_id].get("dynasty") not in dynasties:
            continue
        start = min(period["start"] for period in context["periods"])
        end = max(period["end"] for period in context["periods"])
        periods = [(min(period["start"], period["end"]), max(period["start"], period["end"])) for period in context["periods"]]
        if end - start < 9:
            continue
        have = {events[event_id]["category"] for event_id in context["events"]}
        for category in CATEGORIES:
            if category in have:
                continue
            candidates = []
            for event in data["events"]:
                year = event_year(event)
                bounds = event_bounds(event)
                event_is_bce = event.get("year", "").startswith("前") and "世纪—" not in event.get("year", "")
                reign_is_bce = all(period.get("label", "").startswith("前") for period in context["periods"])
                same_stage = any(
                    people[target].get("dynasty") == people[person_id].get("dynasty")
                    for target in event.get("people", []) if target in people
                )
                if event.get("category") == category and event_is_bce == reign_is_bce and year is not None and bounds is not None and any(bounds[0] <= b and bounds[1] >= a for a, b in periods) and same_stage:
                    candidates.append(event)
            candidates.sort(key=lambda event: (abs(event_year(event) - (start + end) / 2), event["id"]))
            if candidates:
                chosen = candidates[0]
                context["events"].append(chosen["id"])
                for source in chosen["sources"]:
                    if source not in context["sources"]:
                        context["sources"].append(source)
                have.add(category)


# Pass 2: Tang; pass 3: Song/Liao/Xia/Jin and Yuan; pass 4: Qin-Han to
# Northern/Southern dynasties and Sui; pass 5: Five Dynasties plus early stages.
add_overlapping_context({"tang"})
add_overlapping_context({"song_liao_xia_jin", "yuan"})
add_overlapping_context({"qin", "han", "three_kingdoms", "jin", "northern_southern", "sui"})
add_overlapping_context({"xia", "shang", "zhou", "five_dynasties"})

data["version"] = 63
data["reviewed"] = "2026-10-19"
PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(f"history v{data['version']}: {len(data['events'])} events; five-pass reign context enrichment applied")
