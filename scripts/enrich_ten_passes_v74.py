#!/usr/bin/env python3
"""Ten audited passes from chronology repair to multi-state reign depth."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'App/Resources/history.json'
d=json.loads(PATH.read_text())
events={e['id']:e for e in d['events']}; contexts={c['person']:c for c in d['reignContexts']}

def add(item,rulers):
 if item['id'] not in events:d['events'].append(item);events[item['id']]=item
 for pid in rulers:
  c=contexts[pid]
  if item['id'] not in c['events']:c['events'].append(item['id'])
  for sid in item['sources']:
   if sid not in c['sources']:c['sources'].append(sid)

new=[
# Pass 2 / v0.98: Song
({"id":"v98s_zhenzong_society","year":"1008—1015","sortYear":1008,"title":"封禅、宫观营建与地方进献","body":"澶渊之盟后，真宗推动泰山封禅、汾阴祭祀和宫观营建，各地官员竞献祥瑞与方物。大型礼仪需要道路、供给和人员组织，正史多从皇帝与官僚角度记载，普通家庭实际承担的差役和费用难以完整统计。","impact":"礼仪强化了太平政治的象征，却也增加财政与地方动员压力，并助长祥瑞政治。它说明和平时期的社会成本不只来自战争，也可能来自国家仪式与官僚竞争。","people":["s_zhenzong"],"sources":["v43s_ss007","v43s_ss173","v55_zztj"],"kind":"礼仪与社会","category":"社会"},['s_zhenzong']),
# Pass 3 / v0.99: Liao and Jin
({"id":"v99s_liao_jingzong_economy","year":"969—982","sortYear":972,"title":"南京道财赋与辽朝南部治理","body":"景宗时期辽朝继续经营燕云农业州县，南京道的田赋、手工业和市场为宫廷与军队提供资源。草原行营、辽东城镇和南部州县采用不同征收与管理方式，现存材料不足以还原统一预算。","impact":"南部财赋增强了辽朝持续与北宋对峙的能力，也要求皇权协调多套地方制度。理解景宗朝复兴，不能只看军事和萧绰辅政，还要看到稳定资源网络。","people":["s_liao_jingzong"],"sources":["v55_liaoshi","v55_kaogu"],"kind":"区域财政","category":"经济"},['s_liao_jingzong']),
({"id":"v99s_jin_xizong_economy","year":"1135—1150","sortYear":1138,"title":"征服地区赋税与金朝财政转型","body":"熙宗朝金已控制华北大片农业区，需要接收辽宋旧有户籍、田赋、盐税和仓运制度，并调整猛安谋克人口与州县居民的负担。制度并非整齐替换，旧官吏和多种文书传统仍被利用。","impact":"财政转型让金朝从征服联盟进一步走向跨区域国家，也带来身份、税役和土地占有差异。它为海陵王以后中央制度改革提供了物质与行政基础。","people":["s_jin_xizong"],"sources":["v55_jinshi","v55_songshi","v55_kaogu"],"kind":"财政与征服","category":"经济"},['s_jin_xizong']),
({"id":"v99s_jin_yellow_river","year":"1194","sortYear":1194,"title":"黄河改道与沿线社会压力","body":"明昌五年黄河发生重大改道，河道南徙影响淮河水系与沿线州县。治河、赈济、迁徙和田地损失并非只发生在一年，且不同记载对具体决口与流路描述有差异，需要结合后续水文变化理解。","impact":"改道长期改变金、宋边界附近的交通、农业和防务环境，也让灾害治理成为跨地区问题。它提醒读者，章宗朝的繁荣叙事之外仍有巨大的环境风险。","people":["s_jin_zhangzong"],"sources":["v55_jinshi","v55_songshi"],"kind":"环境与社会","category":"社会"},['s_jin_zhangzong']),
({"id":"v99s_jin_mongol_war","year":"1213—1214","sortYear":1213,"title":"蒙古攻势、守中都与迁南京","body":"蒙古军大举进入金境后，中都周边州县反复遭受战事。宣宗即位后与蒙古议和，1214年迁都南京开封；次年中都失守。迁都包含安全和资源判断，却也动摇北方军民信心，并加剧运输和安置压力。","impact":"军事危机使金朝统治重心南移，华北地方控制快速削弱。迁都并非单一的怯战决定，而是军力、粮运、宫廷安全和区域资源共同作用的结果。","people":["s_jin_xuanzong"],"sources":["v55_jinshi","v55_songshi","v56_jinshi_112"],"kind":"战争与迁都","category":"军事"},['s_jin_xuanzong']),
# Pass 4 / v1.00: Western Xia and Yuan
({"id":"v100s_xia_yizong_war","year":"1048—1067","sortYear":1055,"title":"幼主时期的宋夏边境冲突","body":"谅祚幼年即位后，没藏氏与后来的梁氏掌握宫廷重要权力，宋夏边境在和议框架下仍有堡寨争夺、部族归属和小规模军事行动。战争与谈判经常交替，不能只按某次胜负概括。","impact":"边境冲突消耗兵力与财政，也推动西夏朝廷在亲宋、联辽和内部权力之间调整。幼主名义下的决策更应区分皇帝、外戚和军政官员的责任。","people":["s_xia_yizong"],"sources":["v55_xixia","v55_songshi","v56_xixia_14"],"kind":"边境与权力","category":"军事"},['s_xia_yizong']),
({"id":"v100s_xia_yizong_trade","year":"1048—1067","sortYear":1058,"title":"榷场、贡赐与边境交换","body":"宋夏关系缓和时，榷场和使节往来提供茶、布帛、马匹等交换渠道；冲突升级时市场又可能关闭。官方贸易、贡赐和民间走私并存，史料记录的额度不能等同边境经济全貌。","impact":"交换网络既补充西夏物资，也成为外交施压工具。边境居民的生计随战争与开市反复波动，经济关系因此与军事决策紧密相连。","people":["s_xia_yizong"],"sources":["v55_xixia","v55_songshi"],"kind":"边贸与外交","category":"经济"},['s_xia_yizong']),
({"id":"v100s_xia_huanzong_economy","year":"1193—1206","sortYear":1198,"title":"宋夏互市与河西交通","body":"桓宗时期西夏仍通过宋夏互市、贡赐和河西交通取得茶叶、布帛及其他物资，也输出马匹、盐和地方产品。市场受边境政策影响，官方记录偏重禁令与额度，不能完全覆盖民间交换。","impact":"贸易为西夏财政和城市生活提供支撑，也使政权对宋金关系变化十分敏感。蒙古势力兴起前，河西交通仍是西夏连接周边世界的重要基础。","people":["s_xia_huanzong"],"sources":["v55_xixia","v55_songshi","v55_kaogu"],"kind":"边贸与交通","category":"经济"},['s_xia_huanzong']),
({"id":"v100s_xia_huanzong_society","year":"1205—1206","sortYear":1205,"title":"蒙古袭扰与西夏北部居民","body":"成吉思汗势力兴起后，蒙古军开始袭扰西夏边地。早期行动规模和路线在不同史料中存在差异，但边境堡寨、牧地和居民已承受军事侦察、掠夺与防御动员。","impact":"北部安全压力改变了西夏对蒙古与金宋关系的判断，也把战争成本传递给边地人口。桓宗退位前后的宫廷变化，需放在这一外部压力中理解。","people":["s_xia_huanzong"],"sources":["v55_xixia","v56_xixia_19"],"kind":"边疆社会","category":"社会"},['s_xia_huanzong']),
({"id":"v100y_chagatai_war","year":"1314—1320","sortYear":1314,"title":"元与察合台汗国的西北战争","body":"仁宗朝，察合台汗也先不花与元朝关系恶化，双方在阿尔泰、天山和河西以西发生军事行动。战线遥远，调兵、驿站和军粮运输成为重要负担，具体战果在不同叙事中并不完全一致。","impact":"战争显示大元皇权与西部蒙古诸汗国并非天然统一，也牵动西北交通和财政。仁宗朝的文治与科举恢复，需要和同时存在的边疆军事压力并读。","people":["y_ayurbarwada"],"sources":["v43y_ys024","v43y_ys026","v43y_ys093"],"kind":"汗国关系与战争","category":"军事"},['y_ayurbarwada']),
# Pass 5 / v1.01: Eastern Han
({"id":"v101h_guangwu_taixue","year":"29—57","sortYear":29,"title":"洛阳太学与东汉经学重建","body":"光武帝在洛阳设置太学、立博士弟子，并征召经学人才。战后学校规模和教学并非立即稳定，各家章句仍有差异，但国家教育与官员选拔重新取得制度场所。","impact":"太学帮助东汉重建礼制与政治语言，也为士人形成共同网络提供条件。它不是单纯的文化装饰，而与新王朝确认正统、培养官僚直接相关。","people":["han_guangwu"],"sources":["v49h_houhanshu","v49h_cambridge"],"kind":"教育与经学","category":"文化"},['han_guangwu']),
({"id":"v101h_zhang_agriculture","year":"76—88","sortYear":80,"title":"劝农、减赋与边郡供给","body":"章帝朝诏令持续强调劝农、赈贷和灾害减免，同时边郡驻军与西域经营需要粮食运输。帝纪中的宽政语言不能证明赋役普遍轻缓，却显示农业恢复和军费供给之间的张力。","impact":"稳定农业与户籍是“明章之治”的物质基础，边疆行动又不断消耗资源。经济视角能纠正只从白虎观会议评价章帝朝的偏狭。","people":["han_zhang"],"sources":["v49h_houhanshu","v49h_cambridge"],"kind":"农业与财政","category":"经济"},['han_zhang']),
({"id":"v101h_huan_qiang","year":"159—168","sortYear":159,"title":"羌乱、边将与长期军费","body":"桓帝后期，张奂、段颎等将领参与镇压羌乱，朝廷在招抚和强攻之间反复。冲突与边政腐败、迁徙、徭役及地方生计相连，不宜写成固定族群无缘由的持续反叛。","impact":"多年战争造成军费和人口损失，也提高边将及地方武装的重要性。它与宦官政治、党锢和财政紧张共同构成东汉中后期危机。","people":["han_huan"],"sources":["v49h_houhanshu","v49h_cambridge"],"kind":"边疆与军费","category":"军事"},['han_huan']),
# Pass 6 / v1.02: Three Kingdoms and Jin
({"id":"v102tk_sunhao_finance","year":"264—280","sortYear":266,"title":"宫室营建、征发与吴末财政","body":"孙皓在位时继续战争动员，并有营建宫室、迁都和加重征发的记载。传统史书对亡国之君褒贬强烈，具体数字需谨慎使用，但官民负担上升和财政紧张可以从多条记录互证。","impact":"高额动员削弱吴国社会承受力，也加深地方与宫廷矛盾。吴亡不能只归因于君主性格，人口、资源和晋军压力同样重要。","people":["tk_sunhao"],"sources":["v51tk_sgz48","v51tk_sgz61","v51tk_zztj"],"kind":"财政与亡国","category":"经济"},['tk_sunhao']),
({"id":"v102j_western_jin_culture","year":"290—306","sortYear":295,"title":"洛阳士人、文学与玄学论辩","body":"惠帝时期虽政治混乱，洛阳士人仍进行文学创作、清谈和经典解释。陆机、潘岳等人的作品与仕途都卷入权力斗争，文化活动并未脱离八王之乱的政治环境。","impact":"这一时期保存的文章和思想展示西晋精英如何面对秩序崩解，也影响东晋以后的文学与玄学。不能因皇帝能力有限就把整段文化史写成空白。","people":["jin_huidi"],"sources":["v52j_js4","v52j_zztj","v52j_dpm"],"kind":"文学与思想","category":"文化"},['jin_huidi']),
({"id":"v102j_jiankang_culture","year":"325—342","sortYear":330,"title":"建康礼制、侨姓士族与文化重建","body":"成帝时期东晋立足建康，王导等重臣维系朝廷礼制，北来士族与江南地方家族在政治、书写和宗教生活中持续互动。现存名家作品多经后世摹刻，不能都当作当时原迹。","impact":"文化重建帮助流亡王朝塑造正统，也形成门第、地域和官职紧密结合的格局。它为稍后书法、玄学与佛教的兴盛提供制度和社会环境。","people":["jin_chengdi"],"sources":["v52j_js7","v52j_njm","v52j_dpm"],"kind":"礼制与士族","category":"文化"},['jin_chengdi']),
# Pass 7 / v1.03: Southern dynasties
({"id":"v103ns_song_xiaowu_war","year":"454","sortYear":454,"title":"刘义宣起兵与长江中游战争","body":"孝武帝即位不久，南郡王刘义宣与臧质等起兵，战事沿长江中游展开，最终被朝廷平定。冲突既是宗室权力斗争，也涉及荆州军力、地方官员和水路运输。","impact":"胜利加强皇帝对强藩的控制，却未消除宗室互疑和军事化问题。战争对沿线州县的征发与破坏，是理解刘宋中央集权代价的重要部分。","people":["ns_song_xiaowu"],"sources":["v53ns_songshu","v53ns_nanshi","v53ns_zztj"],"kind":"宗室战争","category":"军事"},['ns_song_xiaowu']),
({"id":"v103ns_song_coinage","year":"454—464","sortYear":455,"title":"四铢钱、铸币与市场秩序","body":"孝武帝时期继续整顿铸币并使用四铢钱，官府希望维持币值与交易秩序，但盗铸、轻钱和地区差异仍存在。货币政策与军费、宫廷支出和地方征收互相影响。","impact":"铸币问题反映南朝商品交换活跃，也显示中央控制金属货币的能力有限。经济史不能只从建康繁华推断普通居民普遍富足。","people":["ns_song_xiaowu"],"sources":["v53ns_songshu","v53ns_nanshi"],"kind":"货币与市场","category":"经济"},['ns_song_xiaowu']),
({"id":"v103ns_song_households","year":"453—464","sortYear":458,"title":"宗王出镇、州郡征发与户籍压力","body":"刘宋宗王掌握州镇军政，朝廷在削弱强藩的同时仍依靠地方征兵、运输和税役。孝武帝强化中央控制，官民却可能面对重复征发与官员更替。正史对普通家庭的记载零散，需要从诏令和战争间接观察。","impact":"中央集权并不自动减少基层负担，反而可能把宫廷与地方竞争的成本传给州县居民。它解释了刘宋后期政治暴力为何与社会压力相互放大。","people":["ns_song_xiaowu"],"sources":["v53ns_songshu","v53ns_nanshi"],"kind":"州郡与社会","category":"社会"},['ns_song_xiaowu']),
({"id":"v103ns_qi_border","year":"484—493","sortYear":487,"title":"南齐与北魏边境攻防","body":"齐武帝时期南北边境仍有军事摩擦，淮汉州镇承担守备、侦察与粮运。双方也通过使节往来维持间歇性和平，边境不是持续全面战争，而是攻防、外交与地方控制交替。","impact":"长期守边消耗财政并强化州镇将领地位，也影响边民迁徙和农业恢复。齐武帝朝相对稳定，仍建立在高成本的南北对峙之上。","people":["ns_qi_wu"],"sources":["v53ns_nanqishu","v53ns_beishi","v53ns_zztj"],"kind":"南北对峙","category":"军事"},['ns_qi_wu']),
({"id":"v103ns_qi_registration","year":"482—493","sortYear":485,"title":"检籍、却籍与户籍冲突","body":"南齐整顿户籍时核查白籍、黄籍和侨置人口，部分被认定造假的户籍遭“却籍”，影响赋役身份。政策意在扩大财政与徭役基础，却触动士族、地方官和普通家庭的既有利益。","impact":"户籍核查显示南朝国家试图把流动人口纳入制度，也引发抗议与社会冲突。它把门第政治、财政需要和家庭负担连接在一起。","people":["ns_qi_wu"],"sources":["v53ns_nanqishu","v53ns_nanshi"],"kind":"户籍与社会","category":"社会"},['ns_qi_wu']),
# Pass 8 / v1.04: Northern dynasties
({"id":"v104ns_daowu_war","year":"395—398","sortYear":395,"title":"参合陂之战与北魏定都平城","body":"拓跋珪在参合陂击败后燕军，随后进取中原北部并于398年定都平城。战争利用骑兵、部族联盟和对手内部矛盾，胜利后仍需控制新占城镇与人口。","impact":"这场扩张奠定北魏成为北方强国的基础，也把政权从部族联盟推向拥有固定都城和州郡的国家。军事胜利随即带来治理转型。","people":["ns_wei_daowu"],"sources":["v53ns_weishu","v53ns_beishi","v53ns_zztj"],"kind":"战争与建国","category":"军事"},['ns_wei_daowu']),
({"id":"v104ns_daowu_school","year":"398—409","sortYear":399,"title":"平城礼制与太学建设","body":"北魏定都平城后设置官署、礼仪与教育机构，吸纳中原士人处理文书和制度。儒家礼制并未立即取代鲜卑政治传统，而是在皇权、部族和州郡治理之间逐步结合。","impact":"学校和礼仪为新都培养官员、表达正统，也为后来的制度改革准备文化资源。北魏国家形成不能只从军事征服解释。","people":["ns_wei_daowu"],"sources":["v53ns_weishu","v53ns_beishi"],"kind":"礼制与教育","category":"文化"},['ns_wei_daowu']),
({"id":"v104ns_daowu_economy","year":"398—409","sortYear":401,"title":"平城供给与农牧资源整合","body":"平城成为都城后需要稳定粮食、牲畜和手工业供给。北魏利用牧业资源，也迁徙和组织农业人口，在新占地区设置官吏。具体赋税数字有限，但都城和军队使资源调度规模显著扩大。","impact":"农牧资源整合支持北魏扩张，也增加迁徙、运输和地方征收压力。经济转型与定都、战争是同一国家建设过程的不同侧面。","people":["ns_wei_daowu"],"sources":["v53ns_weishu","v53ns_kaogu"],"kind":"都城与经济","category":"经济"},['ns_wei_daowu']),
({"id":"v104ns_daowu_migration","year":"398—409","sortYear":402,"title":"迁徙人口与平城社会重组","body":"北魏扩张后把部分山东、河北等地人口迁往平城及其周边，工匠、士人、农户和战俘进入新的社会环境。迁徙既服务都城建设和生产，也包含强制与身份差异。","impact":"人口重组加速不同文化与技术汇集，同时制造离土、依附和管理问题。平城社会的形成，是征服者与被迁徙者共同经历的复杂过程。","people":["ns_wei_daowu"],"sources":["v53ns_weishu","v53ns_kaogu"],"kind":"迁徙与社会","category":"社会"},['ns_wei_daowu']),
({"id":"v104ns_mingyuan_culture","year":"409—423","sortYear":415,"title":"崔浩参政与经史知识进入北魏决策","body":"明元帝时期崔浩等汉人士人参与军政咨询、历法和文书工作，中原经史知识与北魏统治经验结合。士人影响不等于文官完全主导，皇帝、宗室和部族贵族仍掌握核心权力。","impact":"多种知识传统进入国家决策，为太武帝时期扩张和制度建设提供人才，也埋下士族、国史与皇权关系的长期张力。","people":["ns_wei_mingyuan"],"sources":["v53ns_weishu","v53ns_beishi"],"kind":"知识与政治","category":"文化"},['ns_wei_mingyuan']),
({"id":"v104ns_wencheng_border","year":"452—465","sortYear":458,"title":"柔然边防与北方军事动员","body":"文成帝时期北魏继续防备柔然，并组织北部边地巡行和军事行动。北方草原关系包含战争、互市、降附和使节往来，不能只写成固定民族之间的永久敌对。","impact":"边防维持了平城安全，也消耗军马、粮食和沿边人口。它与恢复佛教、减轻内部政治清洗共同构成文成帝朝的统治调整。","people":["ns_wei_wencheng"],"sources":["v53ns_weishu","v53ns_beishi"],"kind":"草原边防","category":"军事"},['ns_wei_wencheng']),
({"id":"v104ns_wencheng_recovery","year":"452—465","sortYear":455,"title":"太武末年之后的生产与赋役恢复","body":"太武帝末年政治震荡后，文成帝调整刑政、赈恤灾害并维持农业生产。恢复并非普遍减负，军队、都城和边防仍需要大量资源，但政策语气显示朝廷试图稳定户籍与州郡。","impact":"经济恢复为献文、孝文时期进一步改革提供基础，也让宗教政策转向能够落实。所谓休养需要与持续征发和地区差异一并观察。","people":["ns_wei_wencheng"],"sources":["v53ns_weishu","v53ns_beishi"],"kind":"恢复与赋役","category":"经济"},['ns_wei_wencheng']),
# Pass 9 / v1.05: Five Dynasties
({"id":"v105fd_liang_exams","year":"913—923","sortYear":916,"title":"后梁末年的贡举与文官延续","body":"朱友贞时期虽然战争不断，后梁仍维持贡举、官署和文书制度，士人通过考试、荐举和幕府进入政治。战乱影响考试频率与公平，制度延续不等于形成稳定文治。","impact":"文官体系让短命王朝能够处理日常行政，也把唐代制度带入后唐。五代文化并未随政权更替完全中断。","people":["fd_youzheng"],"sources":["v54_old","v54_wudaihuiyao","v54_new"],"kind":"选举与文官","category":"文化"},['fd_youzheng']),
({"id":"v105fd_wu_culture","year":"908—920","sortYear":914,"title":"江淮幕府、文书与地方文化","body":"杨隆演时期军政实权多由徐温掌握，江淮幕府仍吸纳文士、处理外交与州县文书。文化活动依附政治网络，却也保存晚唐以来的诗文、礼制和行政经验。","impact":"幕府人才后来继续服务南唐等区域政权，显示知识和官僚经验能够跨越君主更替流动。杨吴不应只作为南唐前奏被一笔带过。","people":["fd_wu_longyan"],"sources":["v54_old","v54_new","v54_npm"],"kind":"幕府与文化","category":"文化"},['fd_wu_longyan']),
({"id":"v105fd_min_coup","year":"935","sortYear":935,"title":"宫廷政变与王延钧之死","body":"王延钧晚年宫廷矛盾激化，禁军将领与宗室卷入政变，他在935年被杀。事件材料多集中于宫廷人物，具体过程有叙述差异，但亲军政治和继承失序十分明确。","impact":"政变使闽国统治进一步碎片化，军事集团更频繁介入君位更替，并把不稳定传导到州县。它说明区域贸易繁荣无法抵消核心权力失控。","people":["fd_min_yanjun"],"sources":["v54_new","v54_zztj"],"kind":"宫廷军事","category":"军事"},['fd_min_yanjun']),
]
for item,rulers in new:add(item,rulers)

# Pass 10 / v1.06: deepen ten consequential but short Five-Dynasties readings.
extra={
 'fd_zhuwen':('从唐末军阀到后梁皇帝','朱温的经历连接黄巢军、唐廷节度使和后梁皇权。阅读他的生平，既要看到军事选择和残酷清洗，也要观察宣武军财政、汴州交通及唐代官僚制度如何被新王朝接收。后世史书多在唐宋正统框架中评价其篡位，事实核对与道德褒贬应分开。'),
 'fd_cunxu':('胜利为何迅速转为危机','李存勖灭后梁、恢复“唐”号取得巨大军事成功，但都城供给、军队赏赐、伶官近侍和地方控制很快形成压力。兴亡之速不能只归结为个人爱好，应同时考察长期战争后的财政、军人期待和政权整合能力。'),
 'fd_siyuan':('在短暂稳定中看制度延续','李嗣源以军人身份即位，却依靠枢密、三司、州县和文官处理日常国家事务。他的相对稳定并非五代战争暂停，而是在军镇权力、民生恢复与契丹压力间维持平衡。相关“仁厚”评价需要与赋役、灾荒和地方执行并读。'),
 'fd_jingtang':('燕云问题之外的国家选择','石敬瑭借契丹力量建后晋并割让燕云，是理解其统治的核心，却不是全部。新政权还要接管后唐州县、供应军队并处理对契丹称臣的政治成本。后世强烈批评应与当时军力对比、联盟选择和地方社会后果分别讨论。'),
 'fd_zhiyuan':('从河东军镇到后汉政权','刘知远在契丹北撤后进入开封，依靠河东军力和地方响应建立后汉。短暂在位使许多制度只能承接前朝，军队奖赏、财政恢复和权力交接都十分仓促。不能因王朝短命就忽略它在后周兴起中的承接作用。'),
 'fd_guowei':('兵变、改朝与减轻负担','郭威由枢密使和军队统帅成为后周皇帝，政权建立仍带有五代军人拥立特征。他整顿赋役、减少部分苛敛的记载构成后世善政评价，但执行程度需结合州县材料。制度恢复为柴荣改革提供了现实起点。'),
 'fd_chairong':('改革与战争是一套资源安排','柴荣整军、整顿财政、限制寺院经济并发动北伐，这些政策共同服务于增强国家动员能力。显德改革不能拆成互不相关的政绩，也不能忽略征发和战争成本。其早逝使很多计划的长期效果只能从宋初延续中间接判断。'),
 'fd_wy_qianliu':('区域建设与统治资源','钱镠维护吴越独立，修筑海塘、经营水利并向中原王朝称臣。地方建设既保护农业与城市，也是政权取得税收和政治声望的方式。后世“保境安民”记忆应与军镇竞争、劳役负担和家族统治一并衡量。'),
 'fd_min_shenzhi':('港口、移民与福建区域化','王审知治闽与福州港口、北方移民和地方文教发展相连。海上贸易并非由一位统治者从无到有创造，而是在既有航路、商人和地方社会基础上被政权保护与利用。稳定评价仍需保留对赋役和权力继承的观察。'),
 'fd_nt_yu':('文学名声不能遮住亡国政治','李煜的词作塑造了极强的后世记忆，但南唐后主首先面对宋朝压力、财政军备和内部用人问题。作品中的亡国感受不能直接当成事件记录，政治失败也不能抹去文学创造；两条材料链应互相参照而不相互替代。'),
}
articles={a['person']:a for a in d['articles']}
for pid,(title,text) in extra.items():
 article=articles[pid]
 sid=f'v106-{pid}-context'
 if not any(s['id']==sid for s in article['sections']):
  article['sections'].append({'id':sid,'title':title,'kind':'延伸阅读','text':text,'people':[pid]+contexts[pid]['people'][:2],'events':contexts[pid]['events'][:3],'sources':article['sources'][:3]})

d['version']=74;d['reviewed']='2026-10-19'
PATH.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(f"history v74: {len(new)} events and {len(extra)} deepened ruler readings")
