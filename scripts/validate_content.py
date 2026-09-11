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
emperors={p['id'] for p in people.values() if p['kind']=='皇帝'}
ming_emperors={pid for pid in emperors if not pid.startswith('q_')}
qing_emperors={pid for pid in emperors if pid.startswith('q_')}
assert len(ming_emperors)==16
assert len(qing_emperors)==(12 if d['version']>=5 else 0)
assert len(d['sequence'])==(29 if d['version']>=5 else 17) and {s['person'] for s in d['sequence']}==emperors
counts=Counter(s['person'] for s in d['sequence']);assert counts['qizhen']==2 and all(v==1 for k,v in counts.items() if k!='qizhen')
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
assert {t['person'] for t in d['tombs']}==emperors and len(d['tombs'])==(28 if d['version']>=5 else 16)
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
  assert chars >= (1200 if pid in emperors else 500),(pid,'article too short',chars)
  assert len({s['id'] for s in a['sections']})==len(a['sections'])
  assert set(a['sources'])<=sources.keys()
  for s in a['sections']:
   assert s['sources'] and set(s['sources'])<=sources.keys(),(pid,s['id'])
   assert set(s.get('people',[]))<=people.keys(),(pid,s['id'],'chapter people')
   assert set(s.get('events',[]))<={e['id'] for e in d['events']},(pid,s['id'],'chapter events')
   assert not re.search(r'本应用|本版本|第一版|后续补充|开发进度|AI生成|用户要求',s['text']), (pid,'product process copy')
 portraits={p['person']:p for p in d['portraits']}
 assert emperors<=portraits.keys()
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
 assert [x['id'] for x in d['dynasties'] if x['selectable']]==['ming','qing']
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
 assert required == ideas.keys(),('unexpected thought topics',required ^ ideas.keys())
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
    years=[int(y) for y in re.findall(r'\d{4}',seq['years'])]
    expected.append({'label':seq['years'],'start':years[0],'end':years[-1]})
  assert c['periods']==expected,(pid,'reign periods')
  for actor in c['people']:
   assert actor in people and actor in articles,(pid,actor,'missing actor biography')
   assert any({a['from'],a['to']}=={pid,actor} for a in d['associations']),(pid,actor,'missing contextual relationship')
  for eid in c['events']:
   assert eid in events and pid in events[eid]['people'],(pid,eid,'reign event link')
   label=events[eid]['year']
   years=[int(y) for y in re.findall(r'\d{4}',label)]
   if '年代' in label and years:years.append(max(years)+9)
   century=re.search(r'(\d{1,2})世纪',label)
   if not years and century:years=[(int(century[1])-1)*100+1,int(century[1])*100]
   assert years and any(min(years)<=p['end'] and max(years)>=p['start'] for p in c['periods']),(pid,eid,'outside reign')
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
 print('V22 PASS: all 28 emperors have sourced reign periods, linked people and curated events; pre-accession and post-reign cases stay separate')

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
