#!/usr/bin/env python3
"""Tighten chronology, primary-source precision, and reading depth after the v74 audit."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "App/Resources/history.json"
d = json.loads(PATH.read_text())

sources = {s["id"]: s for s in d["sources"]}
events = {e["id"]: e for e in d["events"]}
contexts = {c["person"]: c for c in d["reignContexts"]}
articles = {a["person"]: a for a in d["articles"]}

new_sources = [
    {"id":"v107_liaoshi_6","title":"《辽史》卷六·穆宗上","url":"https://zh.wikisource.org/zh-hans/遼史/卷6","note":"穆宗应历前期帝纪；用于核对应历年间宫廷、边防和朝会记录。元修史成书仓促，具体事件仍需互校。"},
    {"id":"v107_liaoshi_7","title":"《辽史》卷七·穆宗下","url":"https://zh.wikisource.org/zh-hans/遼史/卷7","note":"穆宗应历后期帝纪；用于核对叛乱处置、出行与南部边境活动。"},
    {"id":"v107_xixiaji_26","title":"《西夏纪》卷二十六","url":"https://zh.wikisource.org/zh-hant/西夏紀/26","note":"桓宗朝编年材料汇编；用于核对克烈部流亡者、蒙古压力与西夏北部局势。该书成于清代，引用宋、辽、金、元材料，须注明其汇编性质。"},
    {"id":"v107_nanqishu_34","title":"《南齐书》卷三十四·虞玩之传","url":"https://zh.wikisource.org/zh-hant/南齊書_(四庫全書本)/卷34","note":"记载建元二年检籍的发端、却籍积弊及永明八年诏令，是区分高帝始行与武帝调整处置的直接材料。"},
    {"id":"v107_houhanshu_79a","title":"《后汉书》卷七十九上·儒林列传","url":"https://zh.wikisource.org/wiki/後漢書/卷79上","note":"记载光武帝建武五年修起太学，为洛阳太学复建的明确纪年材料。"},
    {"id":"v107_weishu_2","title":"《魏书》卷二·太祖纪、太宗纪","url":"https://zh.wikisource.org/zh-hant/魏書/卷2","note":"记载北魏道武帝定都平城、建台省、置百官、迁徙人口及明元帝时期政务。采用时保留魏收叙事立场。"},
    {"id":"v107_beishi_1","title":"《北史》卷一·魏本纪第一","url":"https://zh.wikisource.org/zh-hans/北史/卷001","note":"道武帝、明元帝本纪材料；与《魏书》互校北魏初年战争、制度和迁徙。"},
    {"id":"v107_jinshi_4","title":"《金史》卷四·熙宗本纪","url":"https://zh.wikisource.org/zh-hans/金史/卷4","note":"熙宗朝帝纪；用于限定华北统治制度转型的时段与政治背景。财政结构仍需结合食货志理解。"},
    {"id":"v107_jinshi_14","title":"《金史》卷十四·宣宗本纪上","url":"https://zh.wikisource.org/zh-hans/金史/卷14","note":"宣宗即位、中都危局与贞祐年间军政记录。"},
    {"id":"v107_jinshi_101","title":"《金史》卷一百一·仆散端等传","url":"https://zh.wikisource.org/zh/金史/卷101","note":"保存贞祐二年迁都南京前后的廷议，可与宣宗本纪互证决策过程。"},
]
for source in new_sources:
    if source["id"] not in sources:
        d["sources"].append(source)
        sources[source["id"]] = source

def revise(eid, *, year=None, sort_year=None, title=None, body=None, impact=None, add_sources=()):
    event = events[eid]
    if year is not None: event["year"] = year
    if sort_year is not None: event["sortYear"] = sort_year
    if title is not None: event["title"] = title
    if body is not None: event["body"] = body
    if impact is not None: event["impact"] = impact
    for sid in add_sources:
        if sid not in event["sources"]:
            event["sources"].append(sid)
    for pid in event["people"]:
        context = contexts.get(pid)
        if context:
            for sid in add_sources:
                if sid not in context["sources"]:
                    context["sources"].append(sid)

for eid in ("v96s_muzong_border", "v96s_muzong_culture", "v96s_muzong_economy", "v96s_muzong_society"):
    revise(eid, add_sources=("v107_liaoshi_6", "v107_liaoshi_7"))

revise(
    "v100s_xia_huanzong_society",
    title="蒙古势力兴起与西夏北部压力",
    body="桓宗后期，克烈部败亡后的流亡者进入西夏边境，蒙古势力也开始向河西周边推进。关于1205年前后行动的路线和规模，现存材料多为后出的编年汇录，细节不能写成完全确定；但北部堡寨、牧地与居民面临的新安全压力已经出现。",
    impact="外部力量重组改变了西夏对蒙古、金和宋关系的判断，也把侦察、防御与接纳流亡人口的成本传给边地。桓宗退位前后的宫廷变化，应放在这一逐步加重、但材料并不完整的压力中理解。",
    add_sources=("v107_xixiaji_26",),
)

revise(
    "v103ns_qi_registration",
    year="490",
    sort_year=490,
    title="永明八年调整却籍处置",
    body="南齐检籍始于高帝建元二年，并非齐武帝新创。到永明八年，因却籍积压、执行苛急与民间怨望，武帝下诏调整处置：宋升明以前的旧籍准许恢复登记，部分被谪戍者得还本乡，同时限制此后继续冒籍。",
    impact="这一转折显示户籍整顿既服务赋役控制，也会因执行成本和社会反弹而被修正。它把高帝朝启动的政策与武帝朝的纠偏分开，避免把延续多年的检籍冲突笼统归给一位皇帝。",
    add_sources=("v107_nanqishu_34",),
)

revise(
    "v101h_guangwu_taixue",
    year="29",
    title="建武五年修起洛阳太学",
    body="建武五年，光武帝在洛阳修建太学。战后学校规模和教学秩序并非立即完备，朝廷还通过征召经学人才、设置博士及弟子逐步恢复国家教育；各家章句仍有差异，太学也不是官员入仕的唯一渠道。",
    impact="太学为东汉重建礼制、经学传授和官僚培养提供了制度场所。把起建年份落实到29年，可以区分一次明确建置与此后三十年持续发展的教育网络。",
    add_sources=("v107_houhanshu_79a",),
)

revise(
    "v104ns_daowu_school",
    title="平城官署、礼制与文人任用",
    body="北魏定都平城后建立台省、设置百官，并任用中原文人处理诏令、文书和制度事务。现有本纪足以支持官署建设与文人任用，却不足以把这一整段概括为已有完备太学；儒家礼制是在皇权、部族传统和州郡治理之间逐步进入国家运作。",
    impact="官署、文书与礼仪为新都形成日常行政能力，也为后来的制度改革积累人才。这样的表述把有明确史料的国家建设与尚待专门材料证明的学校规模分开。",
    add_sources=("v107_weishu_2", "v107_beishi_1"),
)
for eid in ("v104ns_daowu_war", "v104ns_daowu_economy", "v104ns_daowu_migration", "v104ns_mingyuan_culture"):
    revise(eid, add_sources=("v107_weishu_2", "v107_beishi_1"))

revise(
    "v99s_jin_xizong_economy",
    body="熙宗朝金已控制华北大片农业区，国家需要接收并重组辽宋旧有的州县、户籍和赋税网络，同时处理猛安谋克人口与州县居民并存的负担体系。帝纪能界定政治进程，具体田赋、盐课与仓运仍须结合食货材料，不能从一次诏令推成统一制度。",
    impact="这场转型使金朝从征服联盟进一步走向跨区域国家，也留下身份、税役与土地占有的差异。这里描述的是多种制度逐步拼接的过程，而非熙宗一次完成的整齐改革。",
    add_sources=("v107_jinshi_4",),
)
revise("v99s_jin_mongol_war", add_sources=("v107_jinshi_14", "v107_jinshi_101"))

# Replace the short v106 additions with substantial readings that separate evidence,
# interpretation and later reputation. These are still overview layers, not biographies.
expanded = {
"fd_zhuwen":"朱温的经历连接黄巢军、唐廷招抚、宣武军节度使与后梁皇权。他先以军镇控制汴州和交通要地，再逐步干预唐廷、迁都洛阳并最终代唐。阅读这一过程，既要看到军事选择、政治清洗和对宿敌的强硬手段，也要观察宣武军财政、漕运网络与唐代官僚制度如何被新王朝接收。正史关于他晚年宫廷暴力的记载很集中，却多出自后唐、宋代编纂体系；具体细节应与基本年表分层使用。后世常以“篡唐”作为全部评价，但王朝转换并不是一次仪式就完成：州县是否输税、将领是否效忠、文官能否继续处理政务，才决定后梁能否运转。把事实核对、制度承接与道德评价分开，才能说明朱温为何既终结唐朝，又没有建立足够稳定的继承秩序。",
"fd_cunxu":"李存勖从河东集团出发，经过长期征战灭后梁，恢复“唐”号，并取得显著军事声望。胜利之后，原先依靠共同敌人与战利品维系的军政关系必须转化为都城供给、常态俸赏和州县治理；洛阳宫廷、伶官近侍、旧梁官员与沙陀将领之间的资源分配迅速紧张。传统叙事常用个人沉迷声色解释败亡，这能反映宫廷用人问题，却不足以替代对财政、军人期待和地方控制的分析。征蜀带来新的土地和人口，也拉长了运输与驻军负担；欠饷和谣言则直接影响军队忠诚。兴亡之速因此不是“会打仗而不会治国”一句话可以概括，而是战争型联盟在胜利后未能及时建立可持续分配规则的结果。把同光年间放进五代财政与军政连续性中，结论会比个人逸事更可靠。",
"fd_siyuan":"李嗣源以军人身份在兵变中即位，却必须依靠枢密、三司、州县与文官处理日常国家事务。他减少部分宫廷奢费、整顿吏治并关注灾荒的记载，构成后世“明宗小康”的基础；这些诏令表达了治理方向，却不等于各地赋役都已减轻。朝廷仍面对契丹压力、军镇将领和继承安排，地方秩序也会因兵变、饥荒与官员更替而波动。理解他的相对稳定，应观察军人皇帝如何借用晚唐以来的行政机器，也要看到稳定依赖个人威望和关键将领合作。晚年储位冲突暴露制度化继承仍很薄弱。所谓仁厚评价可以保留，但需要同财政承受、州县执行和宫廷权力结构一起阅读。材料中的赈恤诏令与地方实际效果，也应继续分开核对。",
"fd_jingtang":"石敬瑭借契丹力量建立后晋并割让燕云，是理解其统治的核心事实，却不是全部历史。起兵时后唐中央与河东军镇矛盾已激化，契丹援助改变了军事均势；即位后，新政权还要接管后唐州县、供应军队、维持漕运，并承担对契丹称臣和岁输的政治经济成本。燕云移交影响北方防线和人口治理，其长期后果不应简化为一位君主的单次“失地”。后世批评非常强烈，其中有清楚的价值判断，也包含宋代面对北方压力后的历史回望。较可靠的读法是分别讨论当时军力对比、联盟条件、地方居民处境和此后边防变化，再评价他的选择。这样既不回避责任，也避免用后来结局替代当时复杂的决策环境。",
"fd_zhiyuan":"刘知远以河东军镇为基础，在契丹灭后晋又北撤的权力真空中进入开封，建立后汉。地方响应并非自动发生，各州将领、原后晋官员和军队都在判断新的效忠对象；政权必须以任命、赏赐和军事压力迅速重建秩序。短暂在位使许多制度只能承接前朝，军费、税收恢复和权力交接都十分仓促。史书容易因后汉寿命短而把它压缩成过渡，但这种过渡本身说明中原行政网络仍有连续性：都城易主之后，州县文书、仓储与官僚仍决定国家能否运行。刘知远之死留下幼主和强将并存的局面，最终为郭威取代后汉创造条件。把建国过程与继承危机放在一起，才能理解后周为何紧接着出现，也能看清短命政权仍然拥有值得研究的行政史。",
"fd_guowei":"郭威由枢密使和军队统帅成为后周皇帝，政权建立仍带有五代军人拥立与宫廷冲突的特征。他减省部分苛敛、处理逃户与田赋、约束宫廷支出的记载，为后世善政评价提供依据；诏令是否在各州同样落实，则需要保持谨慎。经历连续战争后，恢复生产并不只是降低一个税率，还包括让流散人口重新登记、使运输与市场恢复，并控制军队额外征取。郭威沿用了前朝官署和专业官僚，没有从头创造一套制度，这种连续性反而是短期稳定的重要条件。他的改革为柴荣提供现实起点，但继承依然通过收养关系与军政支持维系。评价其治绩，应同时看政策意图、执行范围和为下一朝积累的行政能力。",
"fd_chairong":"柴荣整军、整顿财政、限制寺院经济、修治水运并发动对南唐和辽的战争，这些措施共同服务于增强国家动员能力。显德改革若拆成互不相关的政绩，就会看不见其资源逻辑：军队需要稳定饷粮，扩张需要道路和漕运，铸钱与寺院政策又关系铜料、户口与税源。传统记载称赞他的进取，也记录征战和征发带来的成本；两面必须同时保留。北伐取得进展后因病撤军，早逝使长期计划无法在后周内部完成，很多影响只能从宋初制度承接中间接观察。说他为宋统一“奠基”有道理，却不能把后来结果倒推成每项政策的唯一目的。更准确的理解是，他在有限时间内提高了中原政权的组织能力，也把更高强度的国家动员留给了继承者。",
"fd_wy_qianliu":"钱镠在唐末军镇竞争中控制两浙，修筑海塘、经营水利、保护港口，并持续向中原王朝称臣。海塘与河渠并非单一工程，而是长期维护体系，需要地方官、技术人员和大量劳役；它们既保护农业与城市，也是政权取得税收、交通便利和政治声望的资源。吴越避免大规模北进，不能简单解释为天生“保境安民”，还与周边强敌、区域经济和家族统治策略有关。官方记忆常突出恩惠，普通居民承担的征发与工程风险在材料中更分散。对外称臣也不是放弃自主，而是用名号、贡赐和外交承认换取生存空间。把环境治理、海上贸易、军镇政治和家族继承合在一起，才能解释吴越为何在五代频繁改朝中保持较长稳定。",
"fd_min_shenzhi":"王审知治闽与福州港口、北方移民、山海交通和地方文教发展相连。唐末以来的人口迁入带来官僚经验和生产技术，海上贸易则依靠既有航路、商人、港口设施及周边政权关系，并非由一位统治者从无到有创造。政权能够做的是降低部分阻碍、保护交通并把贸易收益纳入财政。后世常以“开闽”概括其贡献，这一称号有地方记忆价值，却容易遮住更早的社会积累以及山地州县之间的差异。相对稳定也不代表没有赋役、军镇和家族权力问题；王审知死后的继承冲突很快暴露制度脆弱。评价他时，应把个人政策放回移民社会、港口网络与王氏家族统治的共同作用中，并区分地方传说、后世纪念与可核查的当时记录。",
"fd_nt_yu":"李煜的词作塑造了极强的后世记忆，但南唐后主首先面对宋朝扩张、江南防务、财政供给和内部用人。即位时南唐已去帝号、国势受限，后续称臣与贡输是力量差距下的政治选择；同时，是否整军、如何处理将相意见以及对宋判断失误，仍属于统治责任。文学作品中的亡国感受提供情绪与自我表达，却不能直接当作战争和外交的逐日记录。反过来，政治失败也不应抹去其在词体语言和抒情方式上的创造。宋代以后关于他的叙述常把才情与误国并置，形成鲜明人物模板。阅读时最好分开宫廷文书、正史战事记录和后世词作接受史，再讨论它们如何共同塑造“亡国之君”的形象。如此才不会用词人的自我书写代替南唐社会与战争的完整历史。",
}
for pid, text_value in expanded.items():
    section_id = f"v106-{pid}-context"
    section = next(s for s in articles[pid]["sections"] if s["id"] == section_id)
    section["text"] = text_value

d["version"] = 75
d["reviewed"] = "2026-10-19"
PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print(f"history v75: {len(new_sources)} precise sources, 7 evidence corrections, {len(expanded)} expanded readings")
