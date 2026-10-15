from pathlib import Path
import json
from collections import Counter
from PIL import Image
R=Path(__file__).resolve().parents[1];d=json.loads((R/'App/Resources/history.json').read_text())
people={p['id']:p for p in d['people']};sources={s['id']:s for s in d['sources']}
def image_path(name):
 for extension in ['jpg','png']:
  path=R/'App/Resources'/f'{name}.{extension}'
  if path.exists():return path
 raise FileNotFoundError(name)

assert len(people)==len(d['people'])
assert len(sources)==len(d['sources'])
for collection in ['events','objects','sequence','tombs']:
 assert len({x['id'] for x in d[collection]})==len(d[collection]),(collection,'duplicate identifier')
emperors={p['id'] for p in people.values() if p['kind']=='皇帝'}
ming_emperors={pid for pid in emperors if people[pid].get('dynasty','qing' if pid.startswith('q_') else 'ming')=='ming'}
qing_emperors={pid for pid in emperors if pid.startswith('q_')}
assert len(ming_emperors)==16
assert len(qing_emperors)==(12 if d['version']>=5 else 0)
legacy_emperors=ming_emperors|qing_emperors
expected_sequence_count = 313 if d['version']>=39 else 283 if d['version']>=37 else 254 if d['version']>=36 else 198 if d['version']>=35 else 142 if d['version']>=34 else 127 if d['version']>=33 else 116 if d['version']>=32 else 111 if d['version']>=31 else 85 if d['version']>=30 else 83 if d['version']>=25 else 29 if d['version']>=5 else 17
assert len(d['sequence'])==expected_sequence_count and {s['person'] for s in d['sequence']}==emperors
counts=Counter(s['person'] for s in d['sequence'])
repeated={'qizhen','t_zhongzong','t_ruizong','y_tugh_temur'} if d['version']>=25 else {'qizhen'}
assert all(counts[p]==2 for p in repeated) and all(v==1 for k,v in counts.items() if k not in repeated)
assert [s['years'] for s in d['sequence'] if s['person']=='qizhen']==['1435—1449','1457—1464']
for collection in ['people','events','objects','tombs']:
 for item in d[collection]:
  assert item['sources'],(collection,item['id'],'no sources')
  assert set(item['sources'])<=sources.keys(),item['id']
  for target in item.get('people',[]):assert target in people
for p in people.values():
 visited=set();cursor=p
 while cursor.get('parent'):
  assert cursor['id'] not in visited,('cycle',p['id']);visited.add(cursor['id'])
  assert cursor['parent'] in people
  cursor=people[cursor['parent']]
 if p.get('image'):
  Image.open(image_path(p['image'])).verify()
assert people['houcong']['parent']=='youyuan' and people['youyuan']['kind']!='皇帝'
assert people['yunwen']['parent']=='biao' and people['biao']['parent']=='yuanzhang'
assert people['gaoxu']['parent']==people['gaochi']['parent']=='di'
assert legacy_emperors<={t['person'] for t in d['tombs']}<=emperors
assert len({t['person'] for t in d['tombs']})==len(d['tombs'])
assert len([t for t in d['tombs'] if t['area']=='北京 · 明十三陵'])==13
assert next(t for t in d['tombs'] if t['person']=='yunwen')['area']=='尚无定论'
assert next(t for t in d['tombs'] if t['person']=='qiyu')['area']=='北京 · 景泰陵'
assert all(s['url'].startswith('https://') for s in sources.values())
Image.open(R/'App/Resources/ewer.jpg').verify()
print(f"PASS: {len(people)} 人物 / {len(emperors)} 帝 / {len(d['sequence'])} 在位段 / {len(d['events'])} 事件 / {len(d['tombs'])} 陵寝 / {len(sources)} 来源；图谱无环、引用完整、图片可解码。")
if d['version'] >= 2:
 import re
 articles={a['person']:a for a in d['articles']}
 assert emperors <= articles.keys(), ('missing emperor articles',emperors-articles.keys())
 for pid,a in articles.items():
  assert pid in people and a['sections']
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in a['sections'])
  assert chars >= (1200 if pid in legacy_emperors else 650 if pid in emperors else 500),(pid,'article too short',chars)
  assert len({s['id'] for s in a['sections']})==len(a['sections'])
  assert set(a['sources'])<=sources.keys()
  for s in a['sections']:
   assert s['sources'] and set(s['sources'])<=sources.keys(),(pid,s['id'])
   assert set(s.get('people',[]))<=people.keys(),(pid,s['id'],'chapter people')
   assert set(s.get('events',[]))<={e['id'] for e in d['events']},(pid,s['id'],'chapter events')
   assert not re.search(r'本应用|本版本|第一版|后续补充|开发进度|AI生成|用户要求',s['text']), (pid,'product process copy')
 portraits={p['person']:p for p in d['portraits']}
 assert legacy_emperors<=portraits.keys()
 for pid,portrait in portraits.items():
  assert pid in people and set(portrait['sourceIds'])<=sources.keys()
  assert people[pid].get('image')==portrait.get('image'),(pid,'portrait mapping')
  if portrait.get('image'):Image.open(image_path(portrait['image'])).verify()
 if d['version'] < 4: assert portraits['qiyu']['image'] is None and portraits['youjian']['image'] is None
 assert portraits['jianshen']['image']=='portrait_jianshen'
 links=d['familyLinks']
 for edge in links:
  assert edge['from'] in people and edge['to'] in people and edge['from']!=edge['to']
  assert edge['kind'] in ['father','mother','spouse','adoptive','ritual','adoptiveFather','adoptiveMother']
  assert edge['sources'] and set(edge['sources'])<=sources.keys()
 assert any(e['from']=='biao' and e['to']=='ma' and e['kind']=='mother' for e in links)
 assert any(e['from']=='xinglong' and e['to']=='chen' and e['kind']=='mother' for e in links)
 assert 'gaochi' not in next(e for e in d['events'] if e['id']=='hanwang')['people']
 assert len({e['id'] for e in d['events']})==len(d['events'])
 for e in d['events']:
  assert set(e.get('peopleRoles',{}))<=set(e['people'])
  assert e.get('category') in {'政治','军事','文化','经济','社会'}, (e['id'],'invalid or missing event category')
 for edge in d.get('associations',[]):
  assert edge['from'] in people and edge['to'] in people
  assert edge['period'] and edge['role'] and edge['inverse']
  assert edge['sources'] and set(edge['sources'])<=sources.keys()
 print(f"V2 PASS: {len(articles)} full articles / {sum(bool(p['image']) for pid,p in portraits.items() if pid in emperors)}/{len(emperors)} emperor portraits / {len(links)} family edges / {len(d.get('associations',[]))} contextual relationships")
if d['version'] >= 3:
 for pid in ming_emperors:
  assert any(s.get('events') for s in articles[pid]['sections']),(pid,'no chapter exploration')
 for pid in ['yuqian','esen','shiheng','wangzhen']:
  assert pid in people and pid in articles
  assert any(pid in e['people'] for e in d['events'])
  assert any(pid in [a['from'],a['to']] for a in d['associations'])
 assert len({(a['from'],a['to'],a['period']) for a in d['associations']})==len(d['associations'])
 assert 'di' not in next(e for e in d['events'] if e['id']=='cabinet')['people']
 print('V3 PASS: all 16 emperor articles have chapter event links; four new people have articles, events and relationships')

if d['version'] >= 4:
 for pid,order in [('shang',2),('gang',3),('su',5),('bai',12),('quan',17)]:
  assert people[pid]['parent']=='yuanzhang' and people[pid]['birthOrder']==order
  assert any(e['from']==pid and e['to']=='yuanzhang' and e['kind']=='father' for e in links)
  assert not any(e['from']==pid and e['kind']=='mother' for e in links), (pid,'mother requires a separately reviewed source')
  assert pid in articles and any(s.get('events') for s in articles[pid]['sections'])
  assert sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in articles[pid]['sections'])>=700
  assert any(pid in e['people'] for e in d['events'])
 for pid in ['yunwen','qiyu','youjian']:
  if portraits[pid]['image']:
   assert portraits[pid].get('displayLabel') and portraits[pid]['sourceURL'] and portraits[pid]['date']
 assert len({(e['from'],e['to'],e['kind']) for e in links})==len(links)
 print('V4 PASS: five selected princes have sourced father/order, full biographies and linked events; later portraits have visible qualification labels')

if d['version'] >= 5:
 expected_selectable = ['shang','qin','han','three_kingdoms','jin','northern_southern','sui','tang','five_dynasties','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=39 else ['qin','han','three_kingdoms','jin','northern_southern','sui','tang','five_dynasties','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=36 else ['qin','han','three_kingdoms','jin','northern_southern','sui','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=35 else ['qin','han','three_kingdoms','jin','sui','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=34 else ['qin','han','three_kingdoms','sui','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=33 else ['qin','han','sui','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=32 else ['qin','han','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=31 else ['qin','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=30 else ['tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=25 else ['ming','qing']
 assert [x['id'] for x in d['dynasties'] if x['selectable']]==expected_selectable
 assert len(d['dynasties'])>=15 and all(x['sources'] and set(x['sources'])<=sources.keys() for x in d['dynasties'])
 assert [s['person'] for s in d['sequence'] if s['person'].startswith('q_')]==[
  'q_nurhaci','q_hongtaiji','q_shunzhi','q_kangxi','q_yongzheng','q_qianlong',
  'q_jiaqing','q_daoguang','q_xianfeng','q_tongzhi','q_guangxu','q_xuantong']
 for pid in qing_emperors:
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in articles[pid]['sections'])
  assert 1200<=chars<=1600,(pid,'Qing article length',chars)
 assert {t['person'] for t in d['tombs'] if t['person'].startswith('q_')}==qing_emperors
 assert {t['area'] for t in d['tombs'] if t['person'].startswith('q_')}<= {'沈阳 · 盛京三陵','河北 · 清东陵','河北 · 清西陵','特殊安葬'}
 assert next(t for t in d['tombs'] if t['person']=='q_daoguang')['title'].find('慕陵')>=0
 assert '迁' in next(t for t in d['tombs'] if t['person']=='q_daoguang')['body']
 assert any(e['id']=='qev_qianlong_abdication_1796' for e in d['events'])
 assert any(e['id']=='qev_jiaqing_rule_1799' for e in d['events'])
 assert any(e['id']=='qev_manchukuo_1932' for e in d['events'])
 for pid in ['q_daishan','q_hongtaiji','q_dorgon','q_dodo','q_hoog','q_yinreng','q_yongzheng','q_yinsi','q_yinxiang','q_xianfeng','q_yixin','q_yixuan','q_guangxu','q_zaifeng','q_xuantong']:
  assert pid in people and pid in articles,(pid,'missing required Qing family person/article')
 assert people['q_zaifeng']['parent']=='q_yixuan' and people['q_xuantong']['parent']=='q_zaifeng'
 assert any(e['from']=='q_xuantong' and e['to']=='q_zaifeng' and e['kind']=='father' for e in links)
 assert {(e['to'],e['kind']) for e in links if e['from']=='q_xuantong'} >= {('q_tongzhi','ritual'),('q_guangxu','ritual')}
 forbidden=re.compile(r'本应用|本版本|开发中|敬请期待|占位|placeholder|AI生成')
 for collection in ['people','events','objects','tombs','articles']:
  for item in d[collection]: assert not forbidden.search(json.dumps(item,ensure_ascii=False)),(collection,item.get('id',item.get('person')))
 assert sum(1 for p in portraits.values() if p['person'] in qing_emperors and p.get('image'))==12
 print('V5 PASS: 15 dynasty chronology entries; Ming/Qing filtering data complete; 12 Qing rulers, articles, portraits and tombs verified; late-Qing biological and ritual succession links are distinct')

if d['version'] >= 7:
 kangxi_sons = [
  ('q_yinzhi_elder',1),('q_yinreng',2),('q_yinzhi_third',3),('q_yongzheng',4),
  ('q_yinsi',8),('q_yintang',9),('q_yine',10),('q_yinxiang',13),('q_yinti',14)
 ]
 for pid,order in kangxi_sons:
  assert people[pid]['birthOrder']==order,(pid,'wrong Kangxi-son order')
  assert any(e['from']==pid and e['to']=='q_kangxi' and e['kind']=='father' for e in links),(pid,'missing Kangxi father edge')
  assert pid in articles,(pid,'missing Kangxi-son article')
 assert all(any(pid in e['people'] for e in d['events']) for pid,_ in kangxi_sons)
 print('V7 PASS: nine key Kangxi sons have ranks, father edges, full articles and linked events')

if d['version'] >= 8:
 assert d['dynasties'][0]['id']=='prehistory'
 assert len(d['dynastyProfiles'])==len(d['dynasties'])==16
 assert {x['id'] for x in d['dynastyProfiles']}=={x['id'] for x in d['dynasties']}
 sites=d['prehistorySites']
 assert len(sites)>=15 and len({x['id'] for x in sites})==len(sites)
 assert {'yuanmou','lantian','zhoukoudian','hemudu','liangzhu','taosi','shimao'}<={x['id'] for x in sites}
 for item in d['dynastyProfiles']+sites:
  assert item['sources'] and set(item['sources'])<=sources.keys()
 for site in sites:
  assert 18<=site['latitude']<=54 and 73<=site['longitude']<=135
  assert site['summary'] and site['discovery'] and site['significance']
 assert not any('已收录' in x['note'] or '占位' in x['note'] for x in d['dynasties'])
 assert not any(re.search(r'本应用|开发进度|已收录|个人离线学习|未取得额外影像授权', json.dumps(x,ensure_ascii=False)) for x in d['portraits'])
 print('V8 PASS: every chronology row has an introduction; 15 sourced prehistoric sites have valid map coordinates and reader-facing copy')

if d['version'] >= 9:
 maps=d['territoryMaps']
 dynasty_ids={x['id'] for x in d['dynasties'] if x['id']!='prehistory'}
 assert len(maps)==15 and {x['id'] for x in maps}==dynasty_ids
 for item in maps:
  assert item['date'] and item['caption'] and item['regions']
  assert item['sources'] and set(item['sources'])<=sources.keys()
  for region in item['regions']:
   assert len(region['points'])>=4
   assert region['tone'] in {'ink','red','ochre','slate'}
   assert all(18<=p['latitude']<=56 and 70<=p['longitude']<=136 for p in region['points'])
 assert len(next(x for x in maps if x['id']=='three_kingdoms')['regions'])==3
 assert len(next(x for x in maps if x['id']=='song_liao_xia_jin')['regions'])==3
 print('V9 PASS: all 15 written-history stages have a dated, sourced territory or multi-state map')

if d['version'] >= 10:
 for profile in d['dynastyProfiles']:
  overview=profile['overview']
  assert len(re.findall(r'[\u4e00-\u9fff]',overview))>=150,(profile['id'],'overview too short')
  assert '\n\n' in overview,(profile['id'],'overview needs paragraph hierarchy')
  assert not re.search(r'本应用|开发中|收录状态|用户要求|AI生成',overview)
 print('V10 PASS: all 16 historical stages have sourced, multi-paragraph overview essays')

if d['version'] >= 11:
 event=next(e for e in d['events'] if e['id']=='v11_wanggongchang_1626')
 assert event['category']=='社会' and event['people']==['youxiao']
 assert {'v11_dpm_wanggongchang','v2l_ms22'}<=set(event['sources'])
 assert not re.search(r'二万|两万|陨石定论|外星',json.dumps(event,ensure_ascii=False))
 print('V11 PASS: social-history category and sourced Wanggongchang public-disaster event are present')

if d['version'] >= 12:
 expanded={e['id']:e for e in d['events'] if e['id'].startswith('v12_')}
 assert len(expanded)==18,('event expansion count',len(expanded))
 assert {e['category'] for e in expanded.values()}=={'文化','经济','社会'}
 assert all(e['sources'] and set(e['sources'])<=sources.keys() for e in expanded.values())
 required_links={
  'yuanzhang-4':'v12_hongwu_registers','di-5':'v12_yongle_dadian',
  'zhanji-5':'v12_xuande_kilns','youjian-4':'v12_chongzhen_crisis',
  'q-yongzheng-3':'v12_yongzheng_tax','q-qianlong-4':'v12_qianlong_siku',
  'q-guangxu-6':'v12_guangxu_exam'
 }
 for section_id,event_id in required_links.items():
  section=next(s for a in d['articles'] for s in a['sections'] if s['id']==section_id)
  assert event_id in (section.get('events') or []),(section_id,'missing event link')
 print('V12 PASS: 18 cultural, economic and social events are sourced and linked into long-form chapters')

if d['version'] >= 13:
 expanded={e['id']:e for e in d['events'] if e['id'].startswith('v13_')}
 assert set(expanded)=={
  'v13_jiajing_minglun','v13_nurhaci_sarhu','v13_hongtaiji_songjin',
  'v13_yongzheng_tushu','v13_xianfeng_zongli'
 }
 assert all(e['sources'] and set(e['sources'])<=sources.keys() for e in expanded.values())
 expected={
  'v2l_greatrites':'政治','v2l_release':'政治','v2l_altan':'军事',
  'v13_jiajing_minglun':'文化','v13_nurhaci_sarhu':'军事',
  'v13_hongtaiji_songjin':'军事','v13_yongzheng_tushu':'文化',
  'v13_xianfeng_zongli':'政治'
 }
 event_by_id={e['id']:e for e in d['events']}
 assert all(event_by_id[event_id]['category']==category for event_id,category in expected.items())
 required_links={
  'houcong-2':'v13_jiajing_minglun','q-nurhaci-4':'v13_nurhaci_sarhu',
  'q-hongtaiji-5':'v13_hongtaiji_songjin','q-yongzheng-7':'v13_yongzheng_tushu',
  'q-xianfeng-5':'v13_xianfeng_zongli'
 }
 for section_id,event_id in required_links.items():
  section=next(s for a in d['articles'] for s in a['sections'] if s['id']==section_id)
  assert event_id in (section.get('events') or []),(section_id,'missing V13 event link')
 print('V13 PASS: five sourced events fill key category gaps; three earlier events use clearer categories')

if d['version'] >= 14:
 expanded={e['id']:e for e in d['events'] if e['id'].startswith('v14_')}
 assert set(expanded)=={'v14_chenghua_doucai','v14_hongzhi_huidian','v14_wanli_worldmap'}
 assert all(e['category']=='文化' for e in expanded.values())
 assert all(e['sources'] and set(e['sources'])<=sources.keys() for e in expanded.values())
 required_links={
  'jianshen-7':'v14_chenghua_doucai',
  'youtang-3':'v14_hongzhi_huidian',
  'yijun-8':'v14_wanli_worldmap'
 }
 for section_id,event_id in required_links.items():
  section=next(s for a in d['articles'] for s in a['sections'] if s['id']==section_id)
  assert event_id in (section.get('events') or []),(section_id,'missing V14 event link')
 print('V14 PASS: Chenghua porcelain, Hongzhi institutions and Wanli world knowledge are sourced and linked')

if d['version'] >= 15:
 early_ids={'changyuchun','liwenzhong','liuji'}
 people={p['id']:p for p in d['people']}
 assert early_ids <= people.keys()
 articles={a['person']:a for a in d['articles']}
 assert all(len(articles[pid]['sections']) == 5 for pid in early_ids)
 expanded={e['id']:e for e in d['events'] if e['id'].startswith('v15_')}
 assert len(expanded)==15
 assert all(e['sources'] and set(e['sources'])<=sources.keys() for e in expanded.values())
 assert all(set(e['people'])<=people.keys() for e in expanded.values())
 for pid in early_ids:
  assert any(pid in e['people'] for e in expanded.values())
  assert any(pid in (a['from'],a['to']) for a in d['associations'])
 father=next(e for e in d['familyLinks'] if e['from']=='liwenzhong' and e['to']=='lijinglong')
 assert father['kind']=='father'
 section_events={s['id']:set(s.get('events') or []) for a in d['articles'] for s in a['sections']}
 assert 'v15_xuda_1372' in section_events['xuda-f3'] & section_events['liwenzhong-3']
 print('V15 PASS: three early-Ming figures, fifteen distinct events, relationships and chapter links verified')

if d['version'] >= 16:
 expanded={e['id']:e for e in d['events'] if e['id'].startswith('v26_')}
 assert len(expanded)==8
 articles={a['person']:a for a in d['articles']}
 assert len(articles['zhangjuzheng']['sections'])==4
 # Every new event must be discoverable from an emperor's long-read chapter.
 chapter_events={eid for a in d['articles'] if a['person'] in emperors for s in a['sections'] for eid in s.get('events',[])}
 assert expanded.keys() <= chapter_events
 whip=next(e for e in d['events'] if e['id']=='v2l_whip')
 assert 'zhangjuzheng' in whip['people']
 links=[a for a in d['associations'] if a['from']=='zhangjuzheng']
 assert {a['to'] for a in links}=={'yijun','zaihou'}
 assert next(a for a in links if a['to']=='yijun')['role']=='幼年即位的皇帝'
 print('V16 PASS: Zhang Juzheng biography, eight Ming/Qing events and emperor reading links verified')

# Time-map chronology must never silently assign a whole culture's span to a site.
for site in d['prehistorySites']:
 dating=site['dating']
 assert 0 < dating['younger'] <= dating['older']
 assert dating['isPoint'] == (dating['older'] == dating['younger'])
 assert dating['sources'] and set(dating['sources']) <= sources.keys()
assert next(s for s in d['prehistorySites'] if s['id']=='liangzhu')['dating']['older']==5250
assert next(s for s in d['prehistorySites'] if s['id']=='majiayao')['dating']['isPoint']
print('Time map PASS: fifteen dated sites distinguish ranges from approximate points')

if d['version'] >= 17:
 event_by_id={e['id']:e for e in d['events']}
 assert event_by_id['v17_yongle_mobei']['category']=='军事'
 assert event_by_id['v17_yongle_mobei']['people']==['di']
 assert {'v12_zhenghe_voyages','v12_yongle_dadian','v17_yongle_mobei'} <= event_by_id.keys()
 zhou=json.loads((R/'App/Resources/zhou_topics.json').read_text())
 topic_ids={x['id'] for x in zhou['topics']}
 assert {'confucius','laozi','hanfei','chu-zhuang','zhao-wuling'} <= topic_ids
 assert len(zhou['topics']) >= 15
 assert {'zhou-wu','duke-zhou','qi-huan-guanzhong','jin-wen','sun-wu','mozi','mencius','zhuangzi','xunzi','shang-yang'} <= topic_ids
 assert {x.get('period') for x in zhou['topics']} == {'西周','春秋','战国'}
 assert {x['category'] for x in zhou['topics']} <= {'建国与礼制','诸侯与争霸','变法与治理','思想'}
 assert all(len(x['sections'])>=3 and len(x['sources'])>=2 for x in zhou['topics'])
 assert all(source['url'].startswith('https://') for x in zhou['topics'] for source in x['sources'])
 print('V17 PASS: Zhu Di’s three signature projects are discoverable; fifteen Zhou topics span Western Zhou, Spring–Autumn and Warring States')
if d['version'] == 18:
 ideas={x['id']:x for x in d['objects'] if x.get('symbol')=='brain.head.profile'}
 required={'idea_confucian_tradition','idea_daoist_tradition','idea_wang_yangming','idea_self_strengthening'}
 assert required <= ideas.keys(),('missing idea topics',required-ideas.keys())
 assert {'ming','qing'} <= set(ideas['idea_confucian_tradition']['dynasties'])
 assert ideas['idea_wang_yangming']['dynasties']==['ming']
 assert ideas['idea_self_strengthening']['dynasties']==['qing']
 assert all(len(x['body'])>120 and x['sources'] for x in ideas.values())
 print('V18 PASS: four sourced thought-and-change topics are classified for Ming and Qing browsing')
if d['version'] >= 19:
 ideas={x['id']:x for x in d['objects'] if x.get('symbol')=='brain.head.profile'}
 required={
  'idea_ming_chengzhu','idea_wang_yangming','idea_ming_taizhou','idea_ming_xixue',
  'idea_qing_jingshi','idea_qing_kaozheng','idea_self_strengthening',
  'idea_qing_reform','idea_qing_new_policy'
 }
 ming_qing_ideas={key for key,x in ideas.items() if set(x.get('dynasties',[]))&{'ming','qing'}}
 assert required == ming_qing_ideas,('unexpected Ming/Qing thought topics',required ^ ming_qing_ideas)
 assert all(x['dynasties']==['ming'] for key,x in ideas.items() if key.startswith('idea_ming_') or key=='idea_wang_yangming')
 assert all(x['dynasties']==['qing'] for key,x in ideas.items() if key.startswith('idea_qing_') or key=='idea_self_strengthening')
 assert all(len(x['body'])>180 and x['sources'] and set(x['sources'])<=sources.keys() for x in ideas.values())
 q_transitions={x['id']:x['transition'] for x in d['sequence'] if x['id'].startswith('q_')}
 assert q_transitions['q_1']=='父 → 子' and q_transitions['q_9']=='父 → 子'
 assert q_transitions['q_10']=='堂兄 → 堂弟 · 嗣子入继'
 assert q_transitions['q_11']=='叔 → 侄 · 兼祧入继'
 print('V19 PASS: nine dynasty-specific thought topics and concise Qing succession relations are verified')
if d['version'] >= 20:
 people={p['id']:p for p in d['people']}
 assert people['q_taksi']['parent']=='q_giocangga'
 assert people['q_nurhaci'].get('birthOrder') is None
 expected_orders={
  'q_hongtaiji':8,'q_shunzhi':9,'q_kangxi':3,'q_qianlong':4,
  'q_daishan':2,'q_dorgon':14,'q_dodo':15,'q_hoog':1,
  'q_yixin':6,'q_yixuan':7
 }
 assert all(people[person_id]['birthOrder']==order for person_id,order in expected_orders.items())
 links={(x['from'],x['to'],x['kind']) for x in d['familyLinks']}
 assert ('q_nurhaci','q_taksi','father') in links and ('q_taksi','q_giocangga','father') in links
 print('V20 PASS: Qing founder ancestry and visible child-order labels are sourced and explicit')

if d['version'] >= 21:
 sons={'q_honghui','q_hongfen','q_hongyun','q_hongshi','q_qianlong','q_hongzhou','q_fuyi','q_fuhui','q_fupei','q_hongzhan'}
 biological={e['from'] for e in d['familyLinks'] if e['to']=='q_yongzheng' and e['kind']=='father'}
 assert sons == biological, ('Yongzheng sons',sons ^ biological)
 mother_map={'q_honghui':'q_ulanara','q_hongfen':'q_lishi','q_hongyun':'q_lishi','q_hongshi':'q_lishi','q_qianlong':'q_niuhuru','q_hongzhou':'q_gengshi','q_fuyi':'q_nianshi','q_fuhui':'q_nianshi','q_fupei':'q_nianshi','q_hongzhan':'q_liushi'}
 for pid,mother in mother_map.items():
  assert {(e['to'],e['kind']) for e in d['familyLinks'] if e['from']==pid} >= {('q_yongzheng','father'),(mother,'mother')}
 for pid in ['q_hongfen','q_fuyi','q_fuhui','q_fupei']:
  assert people[pid].get('birthOrder') is None and people[pid]['birthOrderNote']=='未列齿序'
 for pid,order in {'q_honghui':1,'q_hongyun':2,'q_hongshi':3,'q_qianlong':4,'q_hongzhou':5,'q_hongzhan':6}.items():assert people[pid]['birthOrder']==order
 assert ('q_hongzhan','q_yinli','adoptiveFather') in links
 for pid in ['q_yongzheng','q_yinti']:assert (pid,'q_wuya','mother') in links
 assert '1770' in people['q_hongzhou']['note'] and '纯懿' in people['q_gengshi']['call']
 new_readers={'q_hongshi','q_hongzhou','q_hongzhan','q_zhangtingyu','q_eertai','q_niangengyao','q_longkodo'}
 assert new_readers <= articles.keys()
 for pid in new_readers:
  assert len(articles[pid]['sections']) >= 3
  assert any(pid in e['people'] for e in d['events'])
  assert any(s.get('events') for s in articles[pid]['sections'])
 assert all('eventLinks' not in s for a in d['articles'] for s in a['sections']), 'obsolete chapter link key'
 for pid in qing_emperors:assert any(s.get('events') for s in articles[pid]['sections'])
 print('V21 PASS: ten Yongzheng sons, six mothers, separate adoptive father, seven new biographies and restored Qing chapter links')

if d['version'] >= 21:
 associates={(a['from'],a['to']):a for a in d['associations']}
 assert '皇兄' in associates['q_yinti','q_yongzheng']['role']
 assert '同母弟' in associates['q_yinti','q_yongzheng']['inverse']
 assert '皇弟' in associates['q_yinreng','q_yinsi']['role']
 assert '皇太后' in associates['q_yixin','q_cixi']['role']
 assert '姨母' not in associates['q_cixi','q_yixuan']['inverse']
 print('V21 PASS: Qing association labels describe the other person in both directions')

if d['version'] >= 22:
 contexts={c['person']:c for c in d['reignContexts']}
 events={e['id']:e for e in d['events']}
 assert len(contexts)==len(d['reignContexts']) and contexts.keys()==emperors
 assert len(articles)==len(d['articles']), 'duplicate person articles'
 assert len({(a['from'],a['to'],a['period']) for a in d['associations']})==len(d['associations']), 'duplicate relationship identity'
 for pid,c in contexts.items():
  assert len(c['people'])>=2 and len(c['people'])==len(set(c['people'])),(pid,'reign people')
  assert len(c['events'])>=2 and len(c['events'])==len(set(c['events'])),(pid,'reign events')
  assert c['sources'] and set(c['sources'])<=sources.keys(),(pid,'reign sources')
  expected=[]
  for seq in d['sequence']:
   if seq['person']==pid:
    years=[int(y) for y in re.findall(r'\d{1,4}',seq['years'])]
    expected.append({'label':seq['years'],'start':years[0],'end':years[-1]})
  assert [(p['start'],p['end']) for p in c['periods']]==[(p['start'],p['end']) for p in expected],(pid,'reign periods')
  assert all(p['label'] for p in c['periods']),(pid,'reign label')
  for actor in c['people']:
   assert actor in people and actor in articles,(pid,actor,'missing actor biography')
   assert any({a['from'],a['to']}=={pid,actor} for a in d['associations']),(pid,actor,'missing contextual relationship')
  for eid in c['events']:
   assert eid in events and pid in events[eid]['people'],(pid,eid,'reign event link')
   label=events[eid]['year']
   years=[] if '世纪' in label else [int(y) for y in re.findall(r'\d{1,4}',label)]
   if '年代' in label and years:years.append(max(years)+9)
   century=re.search(r'(\d{1,2})世纪',label)
   if not years and century:years=[(int(century[1])-1)*100+1,int(century[1])*100]
   assert years and any(min(years)<=max(p['start'],p['end']) and max(years)>=min(p['start'],p['end']) for p in c['periods']),(pid,eid,'outside reign')
 # Calendar-year overlap alone cannot distinguish an accession within that year.
 excluded={
  'gaochi':{'beijing'},'qizhen':{'v2e_changeheir'},'qiyu':{'v2e_jingrestore'},
  'changluo':{'v2l_crown','v2l_tingji','v2l_taichang','v2l_yigong'},
  'youxiao':{'v2l_yigong','v26_zhang_death'},'zaihou':{'v26_zhang_chief'},
  'q_qianlong':{'v39_miao_affairs','qev_white_lotus_1796'},
  'q_xuantong':{'qev_manchukuo_1932'}
 }
 for pid,ids in excluded.items():assert not ids.intersection(contexts[pid]['events']),(pid,'pre-accession or post-reign event')
 for pid,a in articles.items():
  if any(s.startswith('v40') for s in a['sources']):
   assert any(s.get('events') for s in a['sections']),(pid,'reviewed biography lacks event navigation')
 assert 'v39_qianlong_accession' not in events and 'qev_qianlong_accession_1735' in events
 assert all('改变了清廷的权力结构、疆域治理或对外处境' not in e['impact'] for e in d['events']), 'generic Qing impact'
 print('V22 PASS: all emperors have sourced reign periods, linked people and curated events; pre-accession and post-reign cases stay separate')

if d['version'] >= 23:
 names={p['name']:p['id'] for p in d['people']}
 added_names={'胡宗宪','俞大猷','谭纶','王崇古','宋应星','李时珍','梁启超','丁汝昌','刘锦棠','黄兴','曾纪泽','严复','王鼎','琦善'}
 assert added_names <= names.keys(), ('missing expanded figures',added_names-names.keys())
 for name in added_names:
  pid=names[name]
  assert pid in articles and len(articles[pid]['sections'])>=3,(pid,'missing layered biography')
  assert any(s.get('events') for s in articles[pid]['sections']),(pid,'missing chapter event')
  assert any(pid in e['people'] for e in d['events']),(pid,'no event relationship')
  assert any(pid in c['people'] for c in d['reignContexts']),(pid,'not discoverable in reign people')
 objects={o['id']:o for o in d['objects']}
 assert len(objects)==len(d['objects']), 'duplicate artifact ID'
 topic_people={
  'idea_wang_yangming':{'m40_wangshouren'},
  'idea_ming_xixue':{'m40_xuguangqi','m40_limadou'},
  'idea_self_strengthening':{'q_zengguofan','q_zuozongtang','q_lihongzhang','q_zhangzhidong'},
  'idea_qing_reform':{'q_kangyouwei',names['梁启超']},
  'idea_qing_new_policy':{'q_zhangzhidong','q_yuanshikai'}
 }
 for oid,required in topic_people.items():assert required <= set(objects[oid]['people']),(oid,'topic author links')
 for title,name in [('本草纲目','李时珍'),('天工开物','宋应星')]:
  books=[o for o in d['objects'] if title in o['title']]
  assert len(books)==1 and names[name] in books[0]['people'],(title,'book and author link')
  assert books[0]['symbol'] in ['book.closed','doc.text'] and books[0]['dynasties']==['ming']
 assert all('把它放入' not in o['body'] for o in d['objects']), 'editorial classification copy'
 print('V23 PASS: fourteen figures connect reigns, biographies and events; knowledge texts and thought topics link to their authors')

if d['version'] >= 24:
 names={p['name']:p['id'] for p in d['people']}
 required={'徐有贞','韩雍','余子俊','丘濬','马文升','靳辅','陈潢','于成龙','阿桂','松筠'}
 assert required <= names.keys(), ('missing governance figures',required-names.keys())
 for name in required:
  pid=names[name];article=articles[pid]
  assert len(article['sections']) >= 3,(pid,'layered biography')
  assert any(s.get('events') for s in article['sections']),(pid,'chapter event navigation')
  contexts_for_person=[c for c in d['reignContexts'] if pid in c['people']]
  assert contexts_for_person,(pid,'no reign entry')
  assert any(pid in events[eid]['people'] for c in contexts_for_person for eid in c['events']),(pid,'no linked in-reign event')
  for c in contexts_for_person:
   assert any({edge['from'],edge['to']}=={pid,c['person']} for edge in d['associations']),(pid,c['person'],'missing relationship description')
 assert names['松筠'] in contexts['q_jiaqing']['people']
 assert names['丘濬'] in contexts['youtang']['people']
 assert names['靳辅'] in contexts['q_kangxi']['people']
 assert '北溟' in people[names['于成龙']]['note'] and '振甲' in people[names['于成龙']]['note'], 'distinguish the two Yu Chenglongs'
 print('V24 PASS: ten governance figures have sourced biographies, in-reign events and contextual relationships; namesakes stay distinct')


if d['version'] >= 25:
 dynasty_ids={x['id'] for x in d['dynasties']}
 required={'tang':(22,24,45,10),'song_liao_xia_jin':((47,47,120,30) if d['version']>=37 else (18,18,40,13)),'yuan':(11,12,30,12)}
 for dynasty,(emperor_count,segment_count,event_count,other_count) in required.items():
  members={p['id'] for p in d['people'] if p.get('dynasty')==dynasty}
  rulers=members&emperors
  assert len(rulers)==emperor_count,(dynasty,'emperor coverage')
  assert len([x for x in d['sequence'] if x['person'] in rulers])==segment_count,(dynasty,'sequence coverage')
  assert len(members-emperors)>=other_count,(dynasty,'important people coverage')
  assert len([e for e in d['events'] if set(e['people'])&members])>=event_count,(dynasty,'events coverage')
  assert len([o for o in d['objects'] if dynasty in o.get('dynasties',[])])>=4,(dynasty,'heritage coverage')
  for pid in rulers:
   assert pid in articles and len(articles[pid]['sections'])>=3,(pid,'article structure')
   assert any(x.get('events') for x in articles[pid]['sections']),(pid,'chapter event discovery')
   assert any(x.get('people') for x in articles[pid]['sections']),(pid,'chapter people discovery')
 for p in d['people']:
  if p.get('dynasty'): assert p['dynasty'] in dynasty_ids,(p['id'],'unknown dynasty')
 core={'t_gaozu','t_taizong','t_gaozong','t_wuzetian','t_xuanzong','t_suzong','t_dezong','t_xianzong',
       's_taizu','s_taizong','s_zhenzong','s_renzong','s_shenzong','s_huizong','s_gaozong','s_xiaozong',
       'y_kublai','y_temur','y_ayurbarwada','y_toghon_temur'}
 for pid in core:
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in articles[pid]['sections'])
  assert chars>=1200,(pid,'core biography depth',chars)
 for pid in ['y_genghis','y_ogedei','y_guyuk','y_mongke']:
  assert pid in people and pid in articles and pid not in emperors,(pid,'Mongol forehistory')
 if d['version']>=37:
  assert {'s_liao_shengzong','s_xia_jingzong','s_jin_taizu'}<=emperors
 else:
  assert all(pid not in emperors for pid in ['s_liao_shengzong','s_xia_jingzong','s_jin_taizu'])
 for pid in ['m_zhengchenggong','q_wusangui','q_huangzongxi','q_guyanwu','q_wangfuzhi']:
  assert pid in people and pid in articles,(pid,'Ming Qing transition expansion')
  assert any(pid in c['people'] for c in d['reignContexts']),(pid,'reign entry missing')
  assert any(pid in e['people'] for e in d['events']),(pid,'event entry missing')
 assert any(e['from']=='s_xiaozong' and e['to']=='s_gaozong' and e['kind']=='adoptiveFather' for e in d['familyLinks']), 'Song adoption must not become biological lineage'
 assert people['s_xiaozong'].get('parent')!='s_gaozong'
 assert people['y_kublai'].get('parent')!='y_mongke'
 for pid in ['t_wuzetian','t_shangdi','t_aidi','s_gongdi','s_zhaobing']:
  assert people[pid]['temple']=='无庙号',(pid,'common or posthumous title is not a temple name')
 for pid,a in articles.items():
  if people[pid].get('dynasty') in {'tang','song_liao_xia_jin','yuan'}:
   assert not re.search(r'人物页|留在页面|本轮|数据包|不能写成|不赋予儿童',json.dumps(a,ensure_ascii=False)),(pid,'editorial instruction leaked')
 chapter_event_ids={eid for a in d['articles'] for sec in a['sections'] for eid in sec.get('events',[])}
 for event in d['events']:
  if event['id'].startswith('v43'):
   assert event['people'] or event['id'] in chapter_event_ids,(event['id'],'unreachable event')
 for obj in d['objects']:
  if obj['id'].startswith('v43'):
   assert len(re.findall(r'[\u4e00-\u9fff]',obj['body']))>=180,(obj['id'],'new heritage topic too thin')
 print('V25 PASS: complete Tang/Song/Yuan imperial coverage, core biographies, reign context, cross-linked heritage and Ming/Qing transition figures')

if d['version'] >= 26:
 for event in d['events']:
  explicit = re.match(r'^(\d{3,4})(?!\d|世纪)', event['year'])
  placement = event.get('sortYear')
  assert explicit or placement is not None, (event['id'], 'period label needs chronology placement')
  if placement is not None:
   minimum_year = -2000 if d['version'] >= 39 else -230 if d['version'] >= 30 else 600
   assert type(placement) is int and minimum_year <= placement <= 2000, (event['id'], 'invalid chronology placement')
   century = re.match(r'^(\d+)世纪', event['year'])
   if century:
    n = int(century[1]); assert (n-1)*100 < placement <= n*100, (event['id'], 'placement outside century')
 print('V26 PASS: every event has a usable chronology key; period labels retain their display precision')

if d['version'] >= 27:
 tang_portraits={'t_gaozu','t_taizong','t_xuanzong'}
 song_portraits={
  's_taizu','s_taizong','s_zhenzong','s_renzong','s_yingzong',
  's_shenzong','s_zhezong','s_huizong','s_qinzong','s_gaozong',
  's_xiaozong','s_guangzong','s_ningzong','s_lizong','s_duzong'
 }
 for pid in tang_portraits:
  assert portraits[pid]['image'] and portraits[pid]['displayLabel']=='后世宫廷像'
  assert '真容原迹' in portraits[pid]['description']
 for pid in song_portraits:
  assert portraits[pid]['image'] and portraits[pid]['displayLabel']=='南薰殿旧藏'
  assert '乾隆十三年' in portraits[pid]['description']
 assert not ({'s_gongdi','s_duanzong','s_zhaobing'} & portraits.keys())
 assert all(people[pid].get('image')==portraits[pid]['image'] for pid in tang_portraits|song_portraits)
 print('V27 PASS: three qualified later Tang portraits and fifteen NPM Song imperial portraits are mapped; unsupported late-Song child-emperor images stay absent')

if d['version'] >= 28:
 assert all(p.get('dynasty') in {x['id'] for x in d['dynasties']} for p in d['people']), 'every person needs an explicit valid dynasty'
 expanded={
  't_zhongzong','t_ruizong','t_daizong','t_shunzong','t_muzong','t_jingzong','t_wenzong','t_wuzong',
  't_xuanzong_late','t_yizong','t_xizong','t_zhaozong','s_yingzong','s_zhezong','s_qinzong',
  's_guangzong','s_ningzong','s_lizong','s_duzong','y_kulug','y_gegeen','y_yesun_temur','y_tugh_temur'
 }
 for pid in expanded:
  article=articles[pid]
  section=next((x for x in article['sections'] if x['id']=='v46-depth'),None)
  assert section and section.get('sources') and section.get('people') and section.get('events'),(pid,'missing sourced depth section')
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in article['sections'])
  assert chars>=850,(pid,'expanded article is still thin',chars)
 assert all(not re.search(r'本轮|补充内容|数据缺口|页面需要',json.dumps(articles[pid],ensure_ascii=False)) for pid in expanded), 'editorial language leaked into product copy'
 print(f'V28 PASS: 23 Tang, Song and Yuan imperial readings exceed the depth floor; all {len(people)} people have explicit dynasty ownership')

if d['version'] >= 29:
 target_dynasties={'tang','song_liao_xia_jin','yuan'}
 categories={'政治','军事','文化','经济','社会'}
 def item_dynasties(item):
  return set(item.get('dynasties') or [])|{people[pid]['dynasty'] for pid in item.get('people',[]) if pid in people}
 for dynasty in target_dynasties:
  counts=Counter(e['category'] for e in d['events'] if dynasty in item_dynasties(e))
  assert all(counts[category]>=5 for category in categories),(dynasty,'category floor',counts)
  assert sum(dynasty in item_dynasties(obj) for obj in d['objects'])>=8,(dynasty,'heritage floor')
 additions={'v47t_bingtian','v47t_war_displacement','v47t_famine_rebellion','v47s_yellow_river','v47s_futian','v47s_yingzao','v47s_qianli'}
 events={e['id']:e for e in d['events']}
 assert additions<=events.keys()
 assert all(events[eid]['sources'] and events[eid].get('peopleRoles') for eid in additions)
 for pid in {'s_lijie','s_wangximeng'}:
  assert pid in articles and len(articles[pid]['sections'])>=4
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',section['text'])) for section in articles[pid]['sections'])
  assert chars>=850,(pid,'new full reading below depth floor',chars)
  assert all(section['sources'] for section in articles[pid]['sections'])
 for pid in {'t_xuanzong','t_xizong','s_renzong','s_huizong'}:
  section=next((x for x in articles[pid]['sections'] if x['id'].startswith('v47-')),None)
  assert section and section.get('events') and section.get('people') and section.get('sources'),(pid,'missing contextual chapter')
 assert not re.search(r'本轮(?:新增|补充|修改|开发)|补充内容|数据缺口|高标准|验收线',json.dumps(d['articles'],ensure_ascii=False)), 'editorial language leaked into product copy'
 print('V29 PASS: Tang, Song and Yuan each have five event lenses and eight heritage entries; Li Jie and Wang Ximeng have sourced full readings')

if d['version'] >= 30:
 qin_people={p['id'] for p in d['people'] if p.get('dynasty')=='qin'}
 required_people={
  'qin_zhuangxiang','qin_zhaoji','qin_shihuang','qin_fusu','qin_er_shi','qin_ziying',
  'qin_lvbuwei','qin_lisi','qin_zhaogao','qin_mengtian','qin_wangjian','qin_chen_sheng',
  'qin_wuguang','qin_xiangyu','qin_liubang','qin_xi'
 }
 assert qin_people==required_people,('Qin people coverage',qin_people^required_people)
 assert {p['id'] for p in d['people'] if p.get('dynasty')=='qin' and p['kind']=='皇帝'}=={'qin_shihuang','qin_er_shi'}
 assert people['qin_shihuang']['temple']=='' and people['qin_er_shi']['temple']=='', 'Qin imperial titles are not temple names'
 assert [x['person'] for x in d['sequence'] if x['person'] in qin_people]==['qin_shihuang','qin_er_shi']
 assert all(x['person']!='qin_ziying' for x in d['sequence']) and people['qin_ziying']['kind']=='秦王'
 qin_events=[e for e in d['events'] if e['id'].startswith('v48q_')]
 counts=Counter(e['category'] for e in qin_events)
 assert len(qin_events)>=25 and all(counts[c]>=5 for c in {'政治','军事','文化','经济','社会'}),counts
 assert all(e['sources'] and e.get('peopleRoles') and e.get('sortYear') is not None for e in qin_events)
 qin_objects=[o for o in d['objects'] if 'qin' in o.get('dynasties',[])]
 assert len(qin_objects)>=9 and all(o['sources'] and o['people'] for o in qin_objects)
 assert any(t['person']=='qin_shihuang' for t in d['tombs'])
 qin_articles={pid:articles[pid] for pid in required_people if pid in articles}
 assert {'qin_shihuang','qin_er_shi','qin_lisi','qin_zhaogao','qin_mengtian','qin_wangjian','qin_lvbuwei','qin_fusu','qin_ziying','qin_chen_sheng','qin_wuguang','qin_xiangyu','qin_liubang','qin_xi'}<=qin_articles.keys()
 for pid,a in qin_articles.items():
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in a['sections'])
  assert len(a['sections'])>=4 and chars>=(650 if pid in {'qin_shihuang','qin_er_shi'} else 500),(pid,'Qin reading depth',chars)
  assert all(s['sources'] and (s.get('events') or s.get('people')) for s in a['sections']),(pid,'chapter lacks evidence or exploration')
 assert {c['person'] for c in d['reignContexts'] if c['person'] in qin_people}=={'qin_shihuang','qin_er_shi'}
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in qin_people]+qin_events+qin_objects+list(qin_articles.values()),ensure_ascii=False))
 print('V30 PASS: Qin has a bounded two-emperor sequence, sixteen sourced people, five event lenses, nine heritage entries, a tomb and fourteen full readings')

if d['version'] >= 31:
 han_people={p['id'] for p in d['people'] if p.get('dynasty')=='han'}
 han_emperors={p['id'] for p in d['people'] if p.get('dynasty')=='han' and p['kind']=='皇帝'}
 assert len(han_people)>=60 and len(han_emperors)==26,(len(han_people),len(han_emperors))
 han_sequence=[x for x in d['sequence'] if x['person'] in han_people]
 assert len(han_sequence)==26 and {x['person'] for x in han_sequence}==han_emperors
 assert [x['person'] for x in han_sequence[2:4]]==['han_qianshao','han_houshao']
 assert 'han_wangmang' not in {x['person'] for x in han_sequence} and people['han_wangmang']['kind']=='新朝皇帝'
 assert '名讳' in people['han_qianshao']['note'] and '名讳' in people['han_houshao']['note']
 han_events=[e for e in d['events'] if e['id'].startswith('v49h_')]
 counts=Counter(e['category'] for e in han_events)
 assert len(han_events)>=75 and all(counts[c]>=6 for c in {'政治','军事','文化','经济','社会'}),counts
 assert all(e['sources'] and e.get('peopleRoles') and e.get('sortYear') is not None for e in han_events)
 han_objects=[o for o in d['objects'] if 'han' in o.get('dynasties',[])]
 assert len(han_objects)>=12 and all(o['sources'] and o['people'] for o in han_objects)
 assert len([t for t in d['tombs'] if t['person'] in han_emperors])>=6
 for pid in han_people:
  assert pid in articles,(pid,'missing Han reading')
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in articles[pid]['sections'])
  assert chars>=(650 if pid in han_emperors else 500),(pid,'Han reading depth',chars)
  assert any(s.get('events') for s in articles[pid]['sections']),(pid,'Han reading has no event navigation')
 assert {c['person'] for c in d['reignContexts'] if c['person'] in han_people}==han_emperors
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in han_people]+han_events+han_objects+[articles[p] for p in han_people],ensure_ascii=False))
 print('V31 PASS: Han has twenty-six bounded reigns, sixty people, five event lenses, twelve heritage entries, six tombs and full linked readings')

if d['version'] >= 32:
 sui_people={p['id'] for p in d['people'] if p.get('dynasty')=='sui'}
 sui_emperors={p['id'] for p in d['people'] if p.get('dynasty')=='sui' and p['kind']=='皇帝'}
 assert len(sui_people)>=25 and sui_emperors=={'sui_wendi','sui_yangdi','sui_gongdi_you','sui_yanghao','sui_gongdi_tong'}
 sui_sequence=[x for x in d['sequence'] if x['person'] in sui_people]
 assert [x['person'] for x in sui_sequence]==['sui_wendi','sui_yangdi','sui_gongdi_you','sui_yanghao','sui_gongdi_tong']
 assert any('争议' in people[p]['note'] for p in {'sui_yangdi','sui_yanghao','sui_gongdi_tong'})
 sui_events=[e for e in d['events'] if e['id'].startswith('v50s_')]
 counts=Counter(e['category'] for e in sui_events)
 assert len(sui_events)>=40 and all(counts[c]>=8 for c in {'政治','军事','文化','经济','社会'}),counts
 assert all(e['sources'] and e.get('peopleRoles') and e.get('sortYear') is not None for e in sui_events)
 sui_objects=[o for o in d['objects'] if 'sui' in o.get('dynasties',[])]
 assert len(sui_objects)>=12 and all(o['sources'] and o['people'] for o in sui_objects)
 assert len([t for t in d['tombs'] if t['person'] in sui_people])>=2
 for pid in sui_people:
  assert pid in articles,(pid,'missing Sui reading')
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in articles[pid]['sections'])
  assert chars>=(700 if pid in sui_emperors else 520),(pid,'Sui reading depth',chars)
  assert all(s['sources'] and s.get('events') and s.get('people') for s in articles[pid]['sections']),(pid,'Sui chapter lacks evidence or navigation')
 assert {c['person'] for c in d['reignContexts'] if c['person'] in sui_people}==sui_emperors
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in sui_people]+sui_events+sui_objects+[articles[p] for p in sui_people],ensure_ascii=False))
 print('V32 PASS: Sui includes five explicitly bounded claimants, twenty-five people, five event lenses, twelve heritage entries, two securely identified imperial tombs and full linked readings')

if d['version'] >= 33:
 three_people={p['id'] for p in d['people'] if p.get('dynasty')=='three_kingdoms'}
 three_emperors={p['id'] for p in d['people'] if p.get('dynasty')=='three_kingdoms' and p['kind']=='皇帝'}
 expected_emperors={
  'tk_caopi','tk_caorui','tk_caofang','tk_caomao','tk_caohuan',
  'tk_liubei','tk_liushan','tk_sunquan','tk_sunliang','tk_sunxiu','tk_sunhao'
 }
 assert len(three_people)>=50 and three_emperors==expected_emperors,(len(three_people),three_emperors^expected_emperors)
 three_sequence=[x for x in d['sequence'] if x['person'] in three_people]
 assert len(three_sequence)==11 and {x['person'] for x in three_sequence}==three_emperors
 assert Counter(x.get('polity') for x in three_sequence)=={'曹魏':5,'蜀汉':2,'孙吴':4}
 assert all(x.get('polity') for x in three_sequence), 'parallel sequence needs an explicit polity'
 three_events=[e for e in d['events'] if e['id'].startswith('v51tk_')]
 counts=Counter(e['category'] for e in three_events)
 assert len(three_events)>=50 and all(counts[c]>=10 for c in {'政治','军事','文化','经济','社会'}),counts
 assert all(e['sources'] and e.get('peopleRoles') and e.get('sortYear') is not None for e in three_events)
 three_objects=[o for o in d['objects'] if 'three_kingdoms' in o.get('dynasties',[])]
 assert len(three_objects)>=12 and all(o['sources'] and o['people'] for o in three_objects)
 assert {'tk_liubei','tk_sunquan'}<={t['person'] for t in d['tombs']},'documented tomb traditions need explicit confidence boundaries'
 for pid in three_people:
  assert pid in articles,(pid,'missing Three Kingdoms reading')
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in articles[pid]['sections'])
  assert chars>=(750 if pid in three_emperors else 520),(pid,'Three Kingdoms reading depth',chars)
  assert len(articles[pid]['sections'])>=4 and all(s['sources'] and s.get('events') and s.get('people') for s in articles[pid]['sections']),(pid,'chapter lacks evidence or navigation')
 assert {c['person'] for c in d['reignContexts'] if c['person'] in three_people}==three_emperors
 assert all(len(c['people'])>=3 and len(c['events'])>=2 for c in d['reignContexts'] if c['person'] in three_emperors)
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in three_people]+three_events+three_objects+[articles[p] for p in three_people],ensure_ascii=False))
 print('V33 PASS: Three Kingdoms has eleven rulers in three parallel sequences, fifty-one people, five event lenses, twelve heritage entries, bounded tomb evidence and full linked readings')


if d['version'] >= 34:
 jin_people={p['id'] for p in d['people'] if p.get('dynasty')=='jin'}
 jin_emperors={p['id'] for p in d['people'] if p.get('dynasty')=='jin' and p['kind']=='皇帝'}
 expected={'jin_wudi','jin_huidi','jin_huaidi','jin_mindi','jin_yuandi','jin_mingdi','jin_chengdi','jin_kangdi','jin_mudi','jin_aidi','jin_feidi','jin_jianwendi','jin_xiaowudi','jin_andi','jin_gongdi'}
 assert len(jin_people)>=40 and jin_emperors==expected,(len(jin_people),jin_emperors^expected)
 seq=[x for x in d['sequence'] if x['person'] in jin_people]
 assert len(seq)==15 and {x['person'] for x in seq}==expected
 assert Counter(x.get('polity') for x in seq)=={'西晋':4,'东晋':11}
 ev=[e for e in d['events'] if e['id'].startswith('v52j_') and e['kind']=='历史事件']
 counts=Counter(e['category'] for e in ev)
 assert len(ev)>=50 and all(counts[c]>=10 for c in {'政治','军事','文化','经济','社会'}),counts
 assert all(e['sources'] and e.get('peopleRoles') and e.get('sortYear') is not None for e in ev)
 obj=[o for o in d['objects'] if 'jin' in o.get('dynasties',[])]
 assert len(obj)>=12 and all(o['sources'] and o['people'] for o in obj)
 assert len([t for t in d['tombs'] if t['person'] in jin_emperors])>=2
 for pid in jin_people:
  assert pid in articles,(pid,'missing Jin reading')
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in articles[pid]['sections'])
  assert chars>=(750 if pid in jin_emperors else 520),(pid,'Jin reading depth',chars)
  assert len(articles[pid]['sections'])>=4 and all(x['sources'] and x.get('events') and x.get('people') for x in articles[pid]['sections'])
 assert {c['person'] for c in d['reignContexts'] if c['person'] in jin_people}==jin_emperors
 assert all(len(c['people'])>=3 and len(c['events'])>=2 for c in d['reignContexts'] if c['person'] in jin_emperors)
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in jin_people]+ev+obj+[articles[p] for p in jin_people],ensure_ascii=False))
 print('V34 PASS: Jin has fifteen rulers in Western and Eastern sequences, forty-one people, five event lenses, twelve heritage entries, bounded tomb evidence and full linked readings')


if d['version'] >= 35:
 ns_people={p['id'] for p in d['people'] if p.get('dynasty')=='northern_southern'}
 ns_emperors={p['id'] for p in d['people'] if p.get('dynasty')=='northern_southern' and p['kind']=='皇帝'}
 assert len(ns_people)>=90 and len(ns_emperors)==56,(len(ns_people),len(ns_emperors))
 seq=[x for x in d['sequence'] if x['person'] in ns_people]
 assert len(seq)==56 and {x['person'] for x in seq}==ns_emperors
 assert Counter(x.get('polity') for x in seq)=={'南朝宋':8,'南齐':7,'梁':6,'陈':5,'北魏':15,'东魏':1,'西魏':3,'北齐':6,'北周':5}
 assert people['ns_yuan_girl']['kind']!='皇帝' and '争议' in people['ns_yuan_girl']['call']
 ev=[e for e in d['events'] if e['id'].startswith('v53ns_')]
 counts=Counter(e['category'] for e in ev)
 assert len(ev)>=200 and all(counts[c]>=20 for c in {'政治','军事','文化','经济','社会'}),counts
 thematic=[e for e in ev if re.fullmatch(r'v53ns_[pmces]\d{2}',e['id'])]
 assert len(thematic)==100 and all(e.get('impact') and not e['impact'].startswith(e.get('body','')) for e in thematic)
 assert all(e['sources'] and e.get('peopleRoles') and e.get('sortYear') is not None for e in ev)
 obj=[o for o in d['objects'] if 'northern_southern' in o.get('dynasties',[])]
 assert len(obj)>=16 and all(o['sources'] and o['people'] for o in obj)
 assert len([t for t in d['tombs'] if t['person'] in ns_emperors])>=4
 for pid in ns_people:
  assert pid in articles,(pid,'missing Northern-Southern reading')
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in articles[pid]['sections'])
  assert chars>=(750 if pid in ns_emperors else 520),(pid,'Northern-Southern reading depth',chars)
  assert len(articles[pid]['sections'])>=5 and all(x['sources'] and x.get('events') and x.get('people') for x in articles[pid]['sections'])
 assert {c['person'] for c in d['reignContexts'] if c['person'] in ns_people}==ns_emperors
 assert all(len(c['people'])>=3 and len(c['events'])>=2 for c in d['reignContexts'] if c['person'] in ns_emperors)
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in ns_people]+ev+obj+[articles[p] for p in ns_people],ensure_ascii=False))
 print('V35 PASS: Northern and Southern Dynasties has fifty-six rulers in nine parallel sequences, ninety-four people, five event lenses, sixteen heritage entries, four bounded tombs and full linked readings')


if d['version'] >= 36:
 fd_people={p['id'] for p in d['people'] if p.get('dynasty')=='five_dynasties'}
 fd_rulers={p['id'] for p in d['people'] if p.get('dynasty')=='five_dynasties' and p['kind']=='皇帝'}
 assert len(fd_people)>=73 and len(fd_rulers)==56,(len(fd_people),len(fd_rulers))
 seq=[x for x in d['sequence'] if x['person'] in fd_people]
 assert len(seq)==56 and {x['person'] for x in seq}==fd_rulers
 assert Counter(x.get('polity') for x in seq)=={'中原五代':14,'吴':4,'南唐':3,'荆南':5,'闽':7,'楚':6,'前蜀':2,'后蜀':2,'吴越':5,'南汉':4,'北汉':4}
 assert len({people[p]['name'] for p in fd_people})==len(fd_people),'duplicate Five Dynasties historical identities'
 ev=[e for e in d['events'] if e['id'].startswith('v54_')]
 thematic=[e for e in ev if re.fullmatch(r'v54_[pmces]\d{2}',e['id'])]
 assert len(thematic)==50 and Counter(e['category'] for e in thematic)=={'政治':10,'军事':10,'文化':10,'经济':10,'社会':10}
 assert all(e['sources'] and e.get('peopleRoles') and e.get('impact') for e in ev)
 obj=[o for o in d['objects'] if 'five_dynasties' in o.get('dynasties',[])]
 assert len(obj)>=12 and all(o['sources'] and o['people'] for o in obj)
 for pid in fd_people:
  assert pid in articles,(pid,'missing Five Dynasties reading')
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in articles[pid]['sections'])
  assert chars>=620,(pid,'Five Dynasties reading depth',chars)
  assert len(articles[pid]['sections'])>=5 and all(x['sources'] and x.get('events') and x.get('people') for x in articles[pid]['sections'])
 assert {c['person'] for c in d['reignContexts'] if c['person'] in fd_people}==fd_rulers
 assert all(len(c['people'])>=3 and len(c['events'])>=2 for c in d['reignContexts'] if c['person'] in fd_rulers)
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in fd_people]+ev+obj+[articles[p] for p in fd_people],ensure_ascii=False))
 print('V36 PASS: Five Dynasties and Ten Kingdoms has fifty-six rulers in eleven parallel sequences, linked biographies, five event lenses and twelve heritage entries')


if d['version'] >= 37:
 stage={p['id'] for p in d['people'] if p.get('dynasty')=='song_liao_xia_jin'}
 rulers={p['id'] for p in d['people'] if p.get('dynasty')=='song_liao_xia_jin' and p['kind']=='皇帝'}
 assert len(rulers)==47 and len(stage-rulers)>=60,(len(rulers),len(stage-rulers))
 seq=[x for x in d['sequence'] if x['person'] in rulers]
 assert len(seq)==47 and Counter(x.get('polity') for x in seq)=={'北宋':9,'南宋':9,'辽':9,'西夏':10,'金':10}
 parallel={p for p in rulers if p.startswith(('s_liao_','s_xia_','s_jin_'))}
 assert len(parallel)==29
 ev=[e for e in d['events'] if e['id'].startswith('v55_')]
 thematic=[e for e in ev if re.fullmatch(r'v55_[pmces]\d{2}',e['id'])]
 assert len(thematic)==50 and Counter(e['category'] for e in thematic)=={'政治':10,'军事':10,'文化':10,'经济':10,'社会':10}
 assert all(e['sources'] and e.get('peopleRoles') and e.get('impact') for e in ev)
 obj=[o for o in d['objects'] if o['id'].startswith('v55_obj_')]
 assert len(obj)==12 and all(len(re.findall(r'[\u4e00-\u9fff]',o['body']))>=55 for o in obj)
 for pid in parallel|{p['id'] for p in d['people'] if p['id'].startswith(('s_liao_','s_xia_','s_jin_')) and p['id'] not in articles}:
  assert pid in articles,(pid,'missing Liao-Xia-Jin reading')
 for pid in parallel:
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in articles[pid]['sections'])
  assert chars>=700,(pid,'parallel ruler reading depth',chars)
  assert len(articles[pid]['sections'])>=5 and all(x['sources'] and x.get('events') and x.get('people') for x in articles[pid]['sections'])
 contexts={c['person']:c for c in d['reignContexts'] if c['person'] in parallel}
 assert set(contexts)==parallel and all(len(c['people'])>=3 and len(c['events'])>=2 for c in contexts.values())
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in stage]+ev+obj,ensure_ascii=False))
 print('V37 PASS: Song, Liao, Western Xia and Jin has forty-seven rulers in five parallel sequences, twenty-nine non-Song rulers, five event lenses and twelve new heritage entries')


if d['version'] >= 38:
 added={
  's_liao_yelubei','s_liao_xiaotalin','s_liao_xiaoguanyin','s_liao_yeluyixin','s_liao_liuliufu','s_liao_zhangjian',
  's_xia_mozangtaihou','s_xia_mozange','s_xia_xiaoliangtaihou','s_xia_liangyimai','s_xia_liangyibu','s_xia_renduobaozhong','s_xia_wodaochong',
  's_jin_wanyanxiyin','s_jin_wanyanzonggan','s_jin_hanqixian','s_jin_wanyanhada','s_jin_yilapua','s_jin_puxianwannu'
 }
 assert added<=people.keys() and added<=articles.keys()
 assert 's_xia_weiminganquan' not in people
 assert all('s_xia_weiminganquan' not in json.dumps(x,ensure_ascii=False) for k in ['events','articles','associations','reignContexts'] for x in d[k])
 assert people['s_xia_liangtaihou']['name']=='大梁太后'
 assert people['s_xia_xiaoliangtaihou']['name']=='小梁太后'
 assert '惠宗生母' in people['s_xia_liangtaihou']['summary'] and '崇宗生母' in people['s_xia_xiaoliangtaihou']['summary']
 events=[e for e in d['events'] if e['id'].startswith('v56_')]
 assert len(events)==35 and Counter(e['category'] for e in events)=={'政治':7,'军事':7,'文化':7,'经济':7,'社会':7}
 assert all(e['sources'] and e.get('peopleRoles') and e.get('impact') for e in events)
 curated=added|{'s_liao_xiaochuo','s_liao_shengzong','s_xia_renzong','s_jin_shizong','s_jin_zhangzong','s_xia_liangtaihou'}
 for pid in curated:
  article=articles[pid]
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in article['sections'])
  assert chars>=700,(pid,'V38 curated reading depth',chars)
  assert len(article['sections'])==5 and all(x['sources'] and x.get('events') and x.get('people') for x in article['sections'])
 for ruler,figures in {
  's_liao_daozong':{'s_liao_xiaoguanyin','s_liao_yeluyixin'},
  's_xia_huizong':{'s_xia_liangtaihou','s_xia_liangyimai'},
  's_xia_chongzong':{'s_xia_xiaoliangtaihou','s_xia_liangyibu'},
  's_jin_aizong':{'s_jin_wanyanhada','s_jin_yilapua'},
 }.items():
  context=next(c for c in d['reignContexts'] if c['person']==ruler)
  assert figures<=set(context['people']),(ruler,'missing newly surfaced court figures')
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in added]+events+[articles[p] for p in curated],ensure_ascii=False))
 print('V38 PASS: nineteen key Liao-Xia-Jin figures, two distinct Liang regencies, thirty-five balanced events and twenty-five curated readings verified')


if d['version'] >= 39:
 shang={p['id'] for p in d['people'] if p.get('dynasty')=='shang'}
 kings={p for p in shang if people[p]['kind']=='皇帝'}
 assert len(kings)==30 and len(shang-kings)==16,(len(kings),len(shang-kings))
 seq=[x for x in d['sequence'] if x['person'] in shang]
 assert len(seq)==30 and {x['person'] for x in seq}==kings
 assert seq[0]['person']=='sh_tang' and seq[-1]['person']=='sh_dixin'
 assert all('个人在位年待考' in x['years'] for x in seq)
 assert people['sh_taiding']['kind']!='皇帝' and '未即位' in people['sh_taiding']['summary']
 events=[e for e in d['events'] if e['id'].startswith('v57_')]
 thematic=[e for e in events if re.fullmatch(r'v57_[pmces]\d{2}',e['id'])]
 assert len(thematic)==50 and Counter(e['category'] for e in thematic)=={'政治':10,'军事':10,'文化':10,'经济':10,'社会':10}
 assert all(e['sources'] and e.get('peopleRoles') and e.get('impact') for e in events)
 objects=[o for o in d['objects'] if o['id'].startswith('v57_obj_')]
 assert len(objects)==14 and all(o['sources'] and o['people'] and 'shang' in o.get('dynasties',[]) for o in objects)
 assert all(len(re.findall(r'[\u4e00-\u9fff]',o['body']))>=80 for o in objects)
 assert next(x for x in d['dynasties'] if x['id']=='shang')['selectable'] is True
 for pid in shang:
  assert pid in articles,(pid,'missing Shang reading')
  article=articles[pid]
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in article['sections'])
  assert chars>=700,(pid,'Shang reading depth',chars)
  assert len(article['sections'])==5 and all(x['sources'] and x.get('events') and len(x.get('people',[]))>=3 for x in article['sections'])
 contexts={c['person']:c for c in d['reignContexts'] if c['person'] in shang}
 assert set(contexts)==kings and all(len(c['people'])>=3 and len(c['events'])>=2 for c in contexts.values())
 assert all('商王' in people[p]['call'] or p=='sh_tang' for p in kings)
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in shang]+events+objects+[articles[p] for p in shang],ensure_ascii=False))
 print('V39 PASS: Shang has thirty bounded kings, sixteen linked figures, five event lenses, fourteen heritage entries and evidence-qualified full readings')
