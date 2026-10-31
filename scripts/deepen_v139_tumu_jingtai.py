#!/usr/bin/env python3
"""Deepen the Tumu crisis, Beijing defence, Jingtai recovery and restoration."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "App/Resources/history.json"
NARRATION = ROOT / "App/Resources/narration_manifest.json"


def upsert(items, item, key="id"):
    for i, old in enumerate(items):
        if old.get(key) == item[key]:
            items[i] = item
            return
    items.append(item)


def main():
    data = json.loads(DATA.read_text())
    source_notes = {
        "v2e_ms11": "清修《明史》景帝本纪开放转录，核对监国、即位、通州粮入京、各地军队入卫、北京保卫、上皇归京、团营与灾赈。纪年材料保留朝廷视角，不能独自代表士卒、居民和瓦剌内部经验。",
        "v2e_ms12": "清修《明史》英宗后纪开放转录，核对夺门复位、于谦案、论功授官、石亨失势与罢宫妃殉葬。其赞语属于官修评价，不能抵消复位清洗的政治责任。",
        "v3n_ms170": "清修《明史》于谦传开放转录，核对河南山西赈务、北京防御部署、团营、迎还英宗与遇害。传记赞颂色彩鲜明，兵力、战果和人物言语不作为逐字现场记录。",
        "v3n_ms328": "清修《明史》瓦剌传开放转录，用于核对也先、脱脱不花、朝贡贸易、土木之变及英宗送还。材料主要从明廷观察草原政治，不能把瓦剌写成没有内部关系与目标的单一敌人。",
        "v3n_ms304": "清修《明史》宦官传开放转录，核对王振掌司礼监、压制异议、亲征路线与败后清算。列传以宦官祸政为编纂框架，皇帝授权和外朝参与不能被推给王振一人。",
    }
    for source in data["sources"]:
        if source["id"] in source_notes:
            source["note"] = source_notes[source["id"]]

    events = [
        {"id":"v139_tongzhou_grain","year":"1449年八月","title":"败报到京后，通州粮食与各地军队转入首都防御","category":"经济","body":"英宗被俘后，监国郕王命把通州粮运入北京，并征调两京、山东、河南的备倭军和运粮军入卫。粮仓、漕运节点与原本承担其他任务的部队被迅速改作守城资源。","impact":"北京能够继续作战，不只依靠城墙和将领，也依靠粮食及时转移、道路仍可通行以及地方军户承担新的征调。军队数字与运输损耗难以精确复原，不把本纪记载当作现代统计。","people":["qiyu","yuqian","shiheng"],"sources":["v2e_ms11","v3n_ms170"],"kind":"粮运与战时动员"},
        {"id":"v139_city_residents","year":"1449年十月","title":"北京城门外作战中，居民也进入防御现场","category":"社会","body":"于谦部署诸将守九门，也先军转战德胜、西直、彰义等门。官军阵线一度混乱，史传记录城外居民登屋呼喊、投掷砖石，援军随后赶到。","impact":"北京保卫不是少数名臣的独角戏。军士、运输者、城内外居民都承受戒严、迁入城内、房屋战场化与伤亡风险；零散记载无法统计其人数，却足以提醒我们不要让普通人从胜利叙事中消失。","people":["yuqian","qiyu","shiheng","esen"],"sources":["v2e_ms11","v3n_ms170"],"kind":"城市与战争"},
        {"id":"v139_battlefield_burials","year":"1449—1454","title":"朝廷多次祭奠并收瘗土木、关隘与京城战场遗骸","category":"文化","body":"景泰本纪记载祭土木阵亡将士、在西直门外祭官军，后来又收瘗土木、大同和紫荆关暴露遗骸；天顺复位后仍再次处理土木遗骸。","impact":"纪念仪式为国家重建忠烈秩序，也说明败战留下的尸骸多年未能完全安葬。姓名、籍贯和家庭损失大量缺失，不能用祭典替代对实际伤亡及抚恤执行的追问。","people":["qiyu","qizhen","yuqian"],"sources":["v2e_ms11","v2e_ms12"],"kind":"死亡与国家记忆"},
        {"id":"v139_jingtai_relief","year":"1449—1456","title":"边战未止时，景泰朝持续处理被寇、饥荒与逋赋","category":"社会","body":"北京解围后，瓦剌仍多次进犯大同、宣府、宁夏等地。本纪同时记录赈济山东、畿内、大同受灾受寇军民，免山西及多府县税粮，暂停部分民运。","impact":"所谓战后恢复并非某日恢复正常，而是边防、饥荒、运输与税收反复拉扯。诏令证明朝廷承认负担，不等于粮食必然及时到户，地方差异与执行缺口仍需保留。","people":["qiyu","yuqian","esen"],"sources":["v2e_ms11","v3n_ms170"],"kind":"赈济与恢复"},
        {"id":"v139_ten_battalions","year":"1452年","title":"团营把京军重新编为跨旧营调度的训练体系","category":"军事","body":"土木损失后，京军原有五军、三千、神机诸营分属不同系统。于谦提出选精锐分十营团操，景泰三年正式设团营，由将领与内臣共同节制。","impact":"团营回应的是败战后兵员、训练和指挥碎片化，而非一项孤立发明。共同节制也没有消除权力竞争；石亨、曹吉祥后来参与夺门，说明军制修复可能反过来提供政治行动资源。","people":["qiyu","yuqian","shiheng"],"sources":["v2e_ms11","v3n_ms170","v3n_ms304"],"kind":"军制重建"},
        {"id":"v139_restoration_rewards","year":"1457年","title":"夺门复位以授爵、升官和清洗迅速重排功罪","category":"政治","body":"石亨、徐有贞、曹吉祥等迎英宗复位后，于谦、王文被下狱处死，多位景泰大臣贬谪；参与夺门者获封爵，三千余名官舍旗军晋级，随后又清理冒功。","impact":"复位并非单纯恢复旧秩序，而是用奖赏和案件制造新联盟。后来徐有贞被逐、石亨下狱、曹吉祥集团叛乱，证明夺门集团也不是稳定整体；于谦案须保留英宗最终裁决的责任。","people":["qizhen","yuqian","shiheng","m42_xuyouzhen"],"sources":["v2e_ms12","v3n_ms170","v3n_ms173","v3n_ms304"],"kind":"复位与政治清洗"},
    ]
    for event in events:
        upsert(data["events"], event)

    additions = {
        "yuqian-n1":"地方赈务并不是北京保卫的序章装饰：核定仓粮、安排运输、让无力偿还者获得减免，正是危机中把命令变成供给的能力。史传所称二十余万流民是旧史口径，不作精确人口统计。",
        "yuqian-n2":"败报后还要把通州粮移入城内、征各地军入卫并安定朝班。迁都争论固然醒目，真正使守议成立的，是粮、兵、城门和新的皇权中心能够同时被组织。",
        "yuqian-n3":"居民投掷砖石、各地援军逼近也进入战局。胜利应归于一套临时形成的协作，而非把二十二万等史书记数当成精确兵力，或把所有行动压缩成于谦一人的英雄时刻。",
        "yuqian-n4":"指控由夺门集团推动，但英宗听取“不杀于谦，此举无名”后作出裁决。把责任只归徐有贞、石亨，会再次让最高权力从叙事中消失。",
        "yuqian-n5":"恢复名誉经历成化赐祭、后世追赠与改谥多个阶段；它纠正冤案，却不能补回本人生命，也不能证明制度已建立防止下一次政治清洗的约束。",
        "wangzhen-n1":"内书堂教育使部分宦官具备文字和典章能力，但王振的权势仍来自英宗授权；把识字本身视为祸源，是《明史》宦官传的编纂偏见。",
        "wangzhen-n2":"太皇太后与三杨在世时，王振仍受约束；他们凋零后，奏报、刑狱与人事更易围绕近侍运转。变化说明问题在权力通道，而不只是个人性格。",
        "wangzhen-n3":"马价争端只是长期边境关系的一环，不能作为也先出兵的唯一原因。亲征、反复改道、粮道和军令混乱共同扩大风险，皇帝本人对拒绝劝阻承担责任。",
        "wangzhen-n4":"败后族诛、籍产把责任集中于王振家族，无法解释为何制度允许其压制不同意见，也让大量未参与决策的亲属承受连坐。",
        "wangzhen-n5":"英宗复位后为王振招魂、赐祭并在智化寺立祠，说明私人感情与官方记忆可以逆转。寺院遗存可证明 patronage 和纪念，却不能证明王振政治行为合理。",
        "esen-n1":"脱脱不花为可汗、也先掌握强大军政资源，二者既合作又竞争；用“瓦剌首领”概括便于识别，却不能抹掉草原内部多中心结构。",
        "esen-n2":"朝贡人数、马价和赏赐争议连接贸易、声望与边境安全，但《明史》主要记录明廷对使团的判断。不能把减价一事写成战争的单一开关。",
        "esen-n3":"携英宗到北京既是军事施压，也是谈判资源。明廷另立皇帝、拒绝以首都交换人质后，人质价值改变；也先撤退还受城防、援军与补给影响。",
        "esen-n4":"送还英宗并非无条件善意：明使往返、草原内部关系和明朝已经稳定的新君位共同改变谈判。回京后的南宫隔离又说明外交解决没有消除继承冲突。",
        "esen-n5":"也先后来称汗，打破原有名分安排，旋即在内部冲突中被杀。土木胜利没有自动生成稳定帝国，草原政治也不能只作为明朝兴衰的外部变量。",
    }
    changed = set()
    for article in data["articles"]:
        touched = False
        for section in article["sections"]:
            extra = additions.get(section["id"])
            if extra and extra not in section["text"]:
                section["text"] += "\n\n" + extra
                touched = True
        if touched:
            changed.add(article["person"])
            article["sources"] = list(dict.fromkeys(article.get("sources", []) + [s for sec in article["sections"] for s in sec.get("sources", [])]))

    data["version"] = 113
    data["reviewed"] = "2026-10-31"
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    narration = json.loads(NARRATION.read_text())
    narration["entries"] = [e for e in narration["entries"] if e["articleID"] not in changed]
    NARRATION.write_text(json.dumps(narration, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
