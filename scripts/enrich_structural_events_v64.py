#!/usr/bin/env python3
"""Add evidence-bounded structural events and repair BCE/CE context links."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'App/Resources/history.json'
d=json.loads(PATH.read_text())
events={e['id']:e for e in d['events']}
contexts={c['person']:c for c in d['reignContexts']}

# These were period-search false positives: the Arabic number matched an
# Eastern-Han reign even though the label explicitly says BCE.
wrong={
 'han_guangwu':{'v49h_yuan_theme'},
 'han_zhang':{'v49h_saltiron'},
 'han_huan':{'v49h_jing_theme'},
}
for pid,ids in wrong.items():
 contexts[pid]['events']=[eid for eid in contexts[pid]['events'] if eid not in ids]

def add(item,rulers):
 if item['id'] not in events:
  d['events'].append(item);events[item['id']]=item
 for pid in rulers:
  c=contexts[pid]
  if item['id'] not in c['events']:c['events'].append(item['id'])
  for sid in item['sources']:
   if sid not in c['sources']:c['sources'].append(sid)

items=[
({"id":"v96s_song_fiscal","year":"963—976","sortYear":963,"title":"统一进程中的财赋接收与转运","body":"宋在削平荆湖、后蜀、南汉和南唐的过程中，逐步接收州县户籍、仓储与赋税网络，并把地方财货转入中央控制。这个过程并非一次完成：新占地区仍需留用官吏、重定税额、保障水陆运输，战争征发与战后恢复也同时存在。","impact":"开国财政扩张支撑禁军和中央官僚体系，却也把东京供给建立在跨区域转运之上。理解宋初集权，需要同时观察兵权调整和财赋流向，而不能只讲杯酒释兵权。","people":["s_taizu"],"sources":["v43s_ss001","v43s_ss173","v55_songshi"],"kind":"财政与统一","category":"经济"},['s_taizu']),
({"id":"v96s_song_local_order","year":"963—976","sortYear":965,"title":"统一战争后的州县接管与社会安顿","body":"宋军进入南方诸国后，朝廷需要接管州县、约束军队、处理原政权官员，并使逃散人口和农业生产重新进入地方行政。正史多保存诏令与官员行动，普通家庭的经历较少，因此不能把“平定”理解为社会立即恢复。","impact":"地方接管减少了长期割据，却也伴随征服、迁徙和制度转换。把战后安顿纳入叙事，能看见统一不只是地图变化，而是基层权力和生活秩序的重组。","people":["s_taizu"],"sources":["v43s_ss001","v43s_ss250","v55_songshi"],"kind":"统一与社会","category":"社会"},['s_taizu']),
({"id":"v96s_taizong_transport","year":"976—997","sortYear":980,"title":"东京供给、河运与地方财赋","body":"太宗朝疆域扩大后，中央需要把东南粮食、钱帛和地方税收持续运往东京。河道、仓场和转运官体系承担连接产粮区与首都的任务，北方战争和庞大禁军又提高了供给压力。史料记录制度与命令，实际损耗和地方差异仍难完整量化。","impact":"转运能力成为中央集权能够长期运转的物质条件，也使漕河安全、地方征收和首都消费彼此牵动。北伐成败之外，这套财政交通网络同样塑造了宋初国家。","people":["s_taizong"],"sources":["v43s_ss002","v43s_ss173","v55_zztj"],"kind":"财政与交通","category":"经济"},['s_taizong']),
({"id":"v96s_liao_bohai","year":"925—926","sortYear":925,"title":"契丹攻灭渤海与东丹设置","body":"耶律阿保机晚年出兵渤海，926年攻取其都城，并设置东丹国，由耶律倍主持。行动把辽东与渤海人口、城镇和交通纳入契丹皇帝权力范围；东丹的制度安排仍保留对当地治理传统的利用。","impact":"这场战争扩大了契丹国家的东部版图，也带来多族群、多城市治理的新问题。东丹并非简单的地方改名，而是早期辽朝处理征服地区的一种政治安排。","people":["s_liao_taizu","s_liao_yelubei"],"sources":["v55_liaoshi","v55_songshi"],"kind":"征服与建置","category":"军事"},['s_liao_taizu']),
({"id":"v96s_liao_dual_economy","year":"916—926","sortYear":921,"title":"捺钵、城郭与农牧资源调度","body":"辽初统治者仍以季节性行营和牧业资源为重要基础，同时经营上京等城郭，并吸纳汉地农业、手工业与赋税。不同人群承担的生产和贡纳方式并不相同，不能用单一的游牧或农业模式概括早期契丹国家。","impact":"多种经济形态共同支撑皇权、军队和贵族网络，也推动辽朝形成适应不同地区的治理方式。资源调度与政治制度的并行变化，是理解南北面治理的重要前提。","people":["s_liao_taizu"],"sources":["v55_liaoshi","v55_kaogu"],"kind":"区域经济","category":"经济"},['s_liao_taizu']),
({"id":"v96s_liao_yanyun","year":"936—947","sortYear":936,"title":"援立后晋与燕云地区的军事控制","body":"耶律德光援助石敬瑭取得后唐政权，后晋割让燕云十六州并称臣。辽由此获得长城内外的重要州城与交通线。后来辽军南下开封，虽因补给和反抗北撤，却显示其已能深度介入中原王朝更替。","impact":"燕云的取得改变了辽宋之间长期的战略边界，也让辽朝直接治理更多农业州县。军事同盟、领土转移和地方控制在此连成一体，其影响远超一次战役。","people":["s_liao_taizong"],"sources":["v55_liaoshi","v55_songshi"],"kind":"战争与边界","category":"军事"},['s_liao_taizong']),
({"id":"v96s_muzong_border","year":"951—969","sortYear":954,"title":"应历时期的边防与内部军事约束","body":"穆宗时期辽与后周、北宋相继对峙，边境州军和贵族军事力量仍需维持。帝纪同时留下近侍、宗室叛乱与处置记录，说明皇权面临的军事风险既来自南部边界，也来自宫廷和部族权力网络内部。","impact":"这一时期缺少大规模制度创新，却不能视为没有军事史。边防消耗和内部不稳定削弱统治弹性，并为景宗、圣宗时期重新整顿朝政提供背景。","people":["s_liao_muzong"],"sources":["v55_liaoshi"],"kind":"边防与宫廷","category":"军事"},['s_liao_muzong']),
({"id":"v96s_muzong_culture","year":"951—969","sortYear":956,"title":"多文字文书与佛教文化延续","body":"辽朝在契丹大字、小字之外继续使用汉文处理不同类型的政务与文化活动，佛教寺院和经典传播也在各地延续。穆宗本人并非这些文化体系的创始者，现存材料亦不足以把具体成果都归功于皇帝。","impact":"文字并用与宗教网络使不同地区、族群能够进入同一政权的沟通体系。把它列作同期背景，是为了呈现辽代文化连续性，而不是制造“穆宗主持文化建设”的结论。","people":["s_liao_muzong"],"sources":["v55_liaoshi","v55_dpm"],"kind":"文字与宗教","category":"文化"},['s_liao_muzong']),
({"id":"v96s_muzong_economy","year":"951—969","sortYear":958,"title":"南京道农业州县与草原资源并存","body":"应历年间的辽朝同时控制草原、辽东和燕云农业州县，税赋、贡纳、畜产与手工业品通过不同制度进入统治网络。史料难以提供统一财政数字，但地理、食货和制度材料能确认区域生产方式长期并存。","impact":"多区域资源支撑宫廷和军队，也增加转运、官员配置与地方差异管理的难度。辽代经济不能只用牛羊或燕云赋税中的一项来概括。","people":["s_liao_muzong"],"sources":["v55_liaoshi","v55_kaogu"],"kind":"区域经济","category":"经济"},['s_liao_muzong']),
({"id":"v96s_muzong_society","year":"951—969","sortYear":960,"title":"行营秩序、部族与州县居民","body":"辽朝社会包含随四时捺钵移动的宫廷与部族人口，也包含城郭、农州和被迁徙安置的居民。各群体面对的法律、赋役和政治联系并不一致。穆宗时期的本纪材料偏重宫廷惩罚，普通生活需借制度与考古资料补充。","impact":"多种生活方式并存，是辽朝能够跨越不同生态区统治的基础，也造成身份和负担差异。社会史视角可以防止把辽代缩减为皇帝与战争的单线叙事。","people":["s_liao_muzong"],"sources":["v55_liaoshi","v55_kaogu"],"kind":"社会结构","category":"社会"},['s_liao_muzong']),
({"id":"v96s_jin_writing","year":"1123—1135","sortYear":1125,"title":"女真文字、诏令与征服后的文书治理","body":"女真大字创制于太祖时期，太宗朝继续在扩张中的金朝使用并发展女真文字，同时大量接触契丹、汉文文书传统。随着辽、北宋旧地纳入统治，命令传达、户籍财赋和官僚办事需要多种语言文字协作。","impact":"文字制度帮助新政权保存命令与培养官员，但实际行政并未由单一文字取代其他传统。把它放入太宗朝，应理解为制度延续和扩展，而非再次宣称创制。","people":["s_jin_taizong","s_jin_wanyanxiyin"],"sources":["v55_jinshi","v56_jinshi_73"],"kind":"文字与治理","category":"文化"},['s_jin_taizong']),
({"id":"v96h_guangwu_relief","year":"30—57","sortYear":35,"title":"释放奴婢诏令与战后社会恢复","body":"光武帝统一过程中及其后多次颁布释放奴婢、限制杀伤奴婢的诏令，并减省刑徒与徭役。诏令并不证明依附人口问题已经消失，豪强庄园和债务关系仍影响普通家庭，但它显示朝廷试图修复长期战争造成的人身控制与人口流散。","impact":"社会恢复与重新编户共同构成东汉初年秩序重建。评价这些措施需要区分法令目标、执行范围和长期结构，不能只用“柔道治国”代替具体制度。","people":["han_guangwu"],"sources":["v49h_houhanshu","v49h_cambridge"],"kind":"身份与社会","category":"社会"},['han_guangwu']),
({"id":"v96h_ming_education","year":"59—75","sortYear":59,"title":"辟雍礼仪与经学教育","body":"明帝时期举行辟雍礼仪，皇帝讲论经义，并以太学、博士等制度连接礼制和官员教育。东汉经学内部学派众多，朝廷礼仪不等于形成完全统一的解释，更不能把后世所有儒学发展归于一朝。","impact":"国家礼仪和学校强化了皇权对经典秩序的表达，也为士人进入政治提供共同语言。它与稍后的白虎观会议一起，显示东汉前期经学与制度相互塑造。","people":["han_ming"],"sources":["v49h_houhanshu","v49h_cambridge"],"kind":"礼制与教育","category":"文化"},['han_ming']),
({"id":"v96h_ming_chu_case","year":"70","sortYear":70,"title":"楚王英案与株连","body":"楚王刘英被告发谋反后自杀，案件继续追查并牵连多人。记载中还出现与方术、佛教信仰相关的词语，但材料主要来自政治案件，不能据此把所有受牵连者视为同一宗教组织。","impact":"案件显示宗室控制、告发制度和思想活动可能在司法中交叠，也给地方官民带来株连风险。它比单讲白马寺传说更能呈现明帝朝可核查的社会张力。","people":["han_ming"],"sources":["v49h_houhanshu"],"kind":"宗室与司法","category":"社会"},['han_ming']),
({"id":"v96h_zhang_relief","year":"76—88","sortYear":78,"title":"灾害赈恤与刑政宽简","body":"章帝本纪多次记载水旱、地震、蝗灾后的赈贷、减免和巡察，也有宽刑与察举官吏的诏令。帝纪的政策宣示不等于各地执行一致，但这些记录能说明朝廷如何把灾异、民生和官员责任联系起来。","impact":"赈恤和刑政构成章帝朝社会治理的重要面向，并与后世所谓“明章之治”的评价相连。阅读治世叙事时，仍需保留对地区差异和史书褒贬的判断。","people":["han_zhang"],"sources":["v49h_houhanshu"],"kind":"灾害与治理","category":"社会"},['han_zhang']),
({"id":"v96h_shun_qiang","year":"126—144","sortYear":129,"title":"羌地冲突与西北军费","body":"顺帝时期西北羌乱与边郡军事压力延续，朝廷在征讨、招抚、官员更替之间反复调整。战争并非单一族群持续反叛的简单故事，边政失当、徭役负担、迁徙与地方利益都影响冲突。","impact":"长期边患消耗财政并扰动沿线居民，也暴露中央对地方军政的控制困难。它帮助解释东汉中后期财政、宦官政治和地方武装问题为何相互缠绕。","people":["han_shun"],"sources":["v49h_houhanshu","v49h_cambridge"],"kind":"边疆与军费","category":"军事"},['han_shun']),
({"id":"v96h_huan_students","year":"166—168","sortYear":166,"title":"太学生议政与党锢冲突","body":"桓帝后期，太学生和地方士人以清议评价官员，与依附宦官的政治网络发生冲突。李膺等人遭捕形成第一次党锢。所谓士人与宦官都不是完全一致的集团，具体案件还涉及地方纠纷和官僚派系。","impact":"清议把名誉、教育与政治动员联系起来，党锢则压缩了官僚批评空间。它不仅是宫廷斗争，也影响士人共同体和地方社会对朝廷的信任。","people":["han_huan"],"sources":["v49h_houhanshu","v49h_cambridge"],"kind":"士人与政治文化","category":"文化"},['han_huan']),
({"id":"v96h_ling_hongdu","year":"178","sortYear":178,"title":"鸿都门学与文艺取士争议","body":"灵帝设置鸿都门学，招收擅长辞赋、书画等艺能者，并授予官职。传统士人批评它绕开太学经学和常规选官路径，史书的负面评价也带有这一立场，不能简单等同学校毫无文化价值。","impact":"鸿都门学显示晚汉宫廷艺术、教育与政治任用之间的新联系，也暴露不同知识标准的竞争。它为理解灵帝朝文化提供了超出卖官和黄巾起事的另一条线索。","people":["han_ling"],"sources":["v49h_houhanshu"],"kind":"教育与文艺","category":"文化"},['han_ling']),
({"id":"v96h_jianan_culture","year":"196—220","sortYear":200,"title":"战乱中的建安文学与知识流动","body":"献帝迁许以后，曹操集团聚集文士，诗赋、奏议和史论在长期战争与政权重组中发展。建安文学不是献帝主持的宫廷工程，作者经历和作品保存也各不相同，应作为同一时期的文化背景阅读。","impact":"文学记录了战争、离乱、生命感受与政治抱负，并影响后世对“建安风骨”的概括。明确它与献帝的关系边界，可以同时保留时代联系和个人责任的区别。","people":["han_xian"],"sources":["v49h_houhanshu","v49h_cambridge"],"kind":"文学与时代","category":"文化"},['han_xian']),
({"id":"v96fd_wu_society","year":"908—920","sortYear":912,"title":"杨吴权臣政治下的州县社会","body":"杨隆演在位时徐温掌握军政，杨吴仍需依靠江淮州县维持赋税、农业和军队。中央名义、权臣幕府与地方官员并行，使政治命令的来源并不单一；战争间隙的生产恢复也有明显地区差异。","impact":"这一结构解释了杨吴政权能够延续，同时又逐步转入徐氏控制。社会秩序来自州县、军镇和地方资源的共同维持，不能只按君主年表理解。","people":["fd_wu_longyan"],"sources":["v54_old","v54_new","v54_zztj"],"kind":"权力与社会","category":"社会"},['fd_wu_longyan']),
({"id":"v96fd_fujian_culture","year":"909—925","sortYear":915,"title":"闽地文教与中原士人南迁","body":"王审知统治福建期间延揽士人、经营学校与礼制，唐末以来南迁人口也带来文书、教育和技术传统。传世记载多突出统治者德政，具体规模不宜夸大，但福建文化资源在相对稳定环境中积累可以确认。","impact":"文教建设与港口贸易共同增强福州的区域中心地位，也为宋代福建科举和文化发展提供前史。它不能被简化成一位统治者独自创造地方繁荣。","people":["fd_min_shenzhi"],"sources":["v54_new","v54_zztj","v54_kaogu"],"kind":"文教与迁徙","category":"文化"},['fd_min_shenzhi']),
({"id":"v96fd_min_court","year":"926—935","sortYear":930,"title":"闽国宫廷军事化与地方社会压力","body":"王延钧从王位走向称帝，宫廷宗教活动、亲军和权力竞争相互交织。统治末期政变与杀戮说明核心军政集团高度不稳，地方社会还要承担宫廷、军队与区域贸易体系的资源需求。","impact":"宫廷军事化削弱了稳定继承，也使闽国内部冲突不断向州县和家族扩散。它提示思想与贸易繁荣并不能自动消除政治暴力。","people":["fd_min_yanjun"],"sources":["v54_new","v54_zztj"],"kind":"宫廷与社会","category":"社会"},['fd_min_yanjun']),
({"id":"v96fd_shu_culture","year":"907—918","sortYear":910,"title":"成都宫廷、书写与蜀中文化延续","body":"前蜀建立后，成都继续吸纳唐末流离的士人、艺匠与宗教人物，宫廷礼制和地方文化在相对独立的政治空间中延续。传世作品与后世著录存在真伪、年代问题，不能把所有蜀中艺术都直接归于王建。","impact":"人口与知识流动使成都成为五代文化中心之一，也说明分裂时期并非只有战争和制度断裂。区域政权能够保存、重组并传播晚唐文化资源。","people":["fd_fs_wangjian"],"sources":["v54_old","v54_new","v54_dpm"],"kind":"区域文化","category":"文化"},['fd_fs_wangjian']),
]
for item,rulers in items:add(item,rulers)
d['version']=64;d['reviewed']='2026-10-19'
PATH.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(f"history v64: added {len(items)} structural events and removed {sum(map(len,wrong.values()))} BCE/CE false links")
