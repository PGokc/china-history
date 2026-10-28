from pathlib import Path
import json
import hashlib
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
expected_sequence_count = 367 if d['version']>=41 else 350 if d['version']>=40 else 313 if d['version']>=39 else 283 if d['version']>=37 else 254 if d['version']>=36 else 198 if d['version']>=35 else 142 if d['version']>=34 else 127 if d['version']>=33 else 116 if d['version']>=32 else 111 if d['version']>=31 else 85 if d['version']>=30 else 83 if d['version']>=25 else 29 if d['version']>=5 else 17
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
 narration=json.loads((R/'App/Resources/narration_manifest.json').read_text())
 narration_people={pid for pid,p in people.items() if p.get('dynasty') in {'ming','qing'}}
 expected_narration={
  (a['person'],section['id'])
  for a in d['articles'] if a['person'] in narration_people
  for section in a['sections']
 }
 actual_narration={(entry['articleID'],entry['sectionID']) for entry in narration['entries']}
 assert len(actual_narration)==len(narration['entries']),("narration manifest",'duplicate entry')
 assert actual_narration<=expected_narration,(
  "narration manifest contains stale sections",
  actual_narration-expected_narration,
 )
 emperor_narration={
  (a['person'],section['id'])
  for a in d['articles'] if a['person'] in legacy_emperors
  for section in a['sections']
 }
 assert emperor_narration<=actual_narration,(
  "published emperor narration is incomplete",emperor_narration-actual_narration,
 )
 narration_entries={(entry['articleID'],entry['sectionID']):entry for entry in narration['entries']}
 digits=str.maketrans('0123456789','零一二三四五六七八九')
 for article in d['articles']:
  if article['person'] not in narration_people: continue
  for section in article['sections']:
   spoken=f"{section['title']}。{section['text']}".replace('—','至')
   spoken=re.sub(r'(?<!\d)(\d{4})(?=年)',lambda match:match.group(1).translate(digits),spoken)
   expected_hash=hashlib.sha256(spoken.encode()).hexdigest()
   entry=narration_entries.get((article['person'],section['id']))
   if entry is None: continue
   assert entry['textHash']==expected_hash,(article['person'],section['id'],'stale narration hash')
 assert narration['baseURL'].startswith('https://') and narration['version']>=1
 assert 'tos-cn-shanghai.volces.com' in narration['baseURL']
 if narration['published']:
  assert all(re.fullmatch(r'[0-9a-f]{64}',entry.get('audioHash','')) for entry in narration['entries'])
 for pid,a in articles.items():
  assert pid in people and a['sections']
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in a['sections'])
  assert chars >= (1200 if pid in legacy_emperors else 650 if pid in emperors else 500),(pid,'article too short',chars)
  assert len({s['id'] for s in a['sections']})==len(a['sections'])
  assert set(a['sources'])<=sources.keys()
  for s in a['sections']:
   assert s['kind'].strip(),(pid,s['id'],'missing section kind')
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
 expected_selectable = ['xia','shang','zhou','qin','han','three_kingdoms','jin','northern_southern','sui','tang','five_dynasties','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=41 else ['shang','zhou','qin','han','three_kingdoms','jin','northern_southern','sui','tang','five_dynasties','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=40 else ['shang','qin','han','three_kingdoms','jin','northern_southern','sui','tang','five_dynasties','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=39 else ['qin','han','three_kingdoms','jin','northern_southern','sui','tang','five_dynasties','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=36 else ['qin','han','three_kingdoms','jin','northern_southern','sui','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=35 else ['qin','han','three_kingdoms','jin','sui','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=34 else ['qin','han','three_kingdoms','sui','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=33 else ['qin','han','sui','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=32 else ['qin','han','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=31 else ['qin','tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=30 else ['tang','song_liao_xia_jin','yuan','ming','qing'] if d['version']>=25 else ['ming','qing']
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
if d['version'] >= 49:
 zhou=json.loads((R/'App/Resources/zhou_topics.json').read_text())
 topics={x['id']:x for x in zhou['topics']}
 expanded={
  'duke-shao','liwang-republic','pingwang-eastward','qin-mugong','wu-yue-rivalry',
  'wu-qi','li-kui','suqin-zhangyi','qu-yuan','li-bing-dujiangyan'
 }
 assert len(topics)==25 and expanded <= topics.keys()
 assert {topics[x]['period'] for x in expanded} == {'西周','春秋','战国'}
 assert all(len(topics[x]['summary']) >= 70 and len(topics[x]['sections']) == 3 for x in expanded)
 assert all(len(section['text']) >= 75 for x in expanded for section in topics[x]['sections'])
 assert all(len(topics[x]['sources']) >= 2 for x in expanded)
 assert '材料并不一致' in topics['liwang-republic']['summary'] and '并未形成' in topics['liwang-republic']['sections'][1]['text']
 assert '不能说成' in topics['li-bing-dujiangyan']['summary']
 assert all('非官方古籍电子本' in source['title'] for x in expanded for source in topics[x]['sources'] if 'ctext.org' in source['url'])
 print('V49 PASS: twenty-five Zhou guide topics expose the missing royal, diplomatic, reform, literary and engineering threads')
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
    if years:
     expected.append({'label':seq['years'],'start':years[0],'end':years[-1]})
  if people[pid].get('dynasty')=='xia':
   assert c['periods']==[{'label':'传统王序 · 个人王年不详','start':2070,'end':1600}],(pid,'Xia evidence envelope')
  else:
   assert [(p['start'],p['end']) for p in c['periods']]==[(p['start'],p['end']) for p in expected],(pid,'reign periods')
  assert all(p['label'] for p in c['periods']),(pid,'reign label')
  for actor in c['people']:
   assert actor in people and actor in articles,(pid,actor,'missing actor biography')
   assert any({a['from'],a['to']}=={pid,actor} for a in d['associations']),(pid,actor,'missing contextual relationship')
  for eid in c['events']:
   assert eid in events and (pid in events[eid]['people'] or d['version']>=58),(pid,eid,'reign event link')
   if people[pid].get('dynasty')=='xia': continue
   label=events[eid]['year']
   century_range=re.search(r'(\d{1,2})[—–-](\d{1,2})世纪',label)
   years=[(int(century_range[1])-1)*100+1,int(century_range[2])*100] if century_range else ([] if '世纪' in label else [int(y) for y in re.findall(r'\d{1,4}',label)])
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
   minimum_year = -2100 if d['version'] >= 41 else -2000 if d['version'] >= 39 else -230 if d['version'] >= 30 else 600
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

if d['version'] >= 40:
 zhou={p['id'] for p in d['people'] if p.get('dynasty')=='zhou'}
 kings={p for p in zhou if people[p]['kind']=='皇帝'}
 figures=zhou-kings
 assert len(kings)==37 and len(figures)==26,(len(kings),len(figures))
 seq=[x for x in d['sequence'] if x['person'] in zhou]
 assert len(seq)==37 and {x['person'] for x in seq}==kings
 assert Counter(x['polity'] for x in seq)=={'西周':12,'东周':25}
 assert seq[0]['person']=='z_wuwang' and seq[-1]['person']=='z_nanwang'
 western=[x for x in seq if x['polity']=='西周'];eastern=[x for x in seq if x['polity']=='东周']
 assert all('断代方案' in x['years'] for x in western[:9]) and all('断代方案' not in x['years'] for x in western[9:]+eastern)
 assert people['z_gongbohe']['kind']!='皇帝' and '共和行政' in people['z_gongbohe']['summary']
 events=[e for e in d['events'] if e['id'].startswith('v58_')]
 thematic=[e for e in events if re.fullmatch(r'v58_[pmces]\d{2}',e['id'])]
 assert len(thematic)==50 and Counter(e['category'] for e in thematic)=={'政治':10,'军事':10,'文化':10,'经济':10,'社会':10}
 assert all(e['sources'] and e.get('peopleRoles') and e.get('impact') for e in events)
 objects=[o for o in d['objects'] if o['id'].startswith('v58_obj_')]
 assert len(objects)==14 and all(o['sources'] and o['people'] and o.get('dynasties')==['zhou'] for o in objects)
 assert all(len(re.findall(r'[\u4e00-\u9fff]',o['body']))>=55 for o in objects)
 assert next(x for x in d['dynasties'] if x['id']=='zhou')['selectable'] is True
 for pid in zhou:
  assert pid in articles,(pid,'missing Zhou reading')
  article=articles[pid]
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in article['sections'])
  assert chars>=700,(pid,'Zhou reading depth',chars)
  assert len(article['sections'])==5 and all(x['sources'] and x.get('events') and len(x.get('people',[]))>=3 for x in article['sections'])
  if pid in kings:
   assert article['title'] != f"{people[pid]['name']}：{people[pid]['call']}",(pid,'repeated Zhou reading title')
 contexts={c['person']:c for c in d['reignContexts'] if c['person'] in zhou}
 assert set(contexts)==kings and all(len(c['people'])>=3 and len(c['events'])>=2 for c in contexts.values())
 assert any(e['title']=='厉王出奔与共和行政' and 'z_gongbohe' in e['people'] for e in thematic)
 assert all(e.get('note') for e in d['familyLinks'] if e['from'] in zhou)
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in zhou]+events+objects+[articles[p] for p in zhou],ensure_ascii=False))
 print('V40 PASS: Zhou has twelve Western Zhou and twenty-five Eastern Zhou kings, twenty-six linked figures, five event lenses and fourteen evidence-rich heritage entries')

if d['version'] >= 41:
 xia={p['id'] for p in d['people'] if p.get('dynasty')=='xia'}
 kings={p for p in xia if people[p]['kind']=='皇帝'}
 figures=xia-kings
 assert len(kings)==17 and len(figures)==11,(len(kings),len(figures))
 seq=[x for x in d['sequence'] if x['person'] in xia]
 assert len(seq)==17 and [x['person'] for x in seq]==['xia_yu','xia_qi','xia_taikang','xia_zhongkang','xia_xiang','xia_shaokang','xia_zhu','xia_huai','xia_mang','xia_xie','xia_bujiang','xia_jiong','xia_jin','xia_kongjia','xia_gao','xia_fa','xia_jie']
 assert all(x['years']=='传统王序 · 具体年代不详' and x['eraLabel']=='传统王名 · 无可核年号' for x in seq)
 assert all('同时代文字' in people[p]['note'] for p in kings)
 events=[e for e in d['events'] if e['id'].startswith('v59_')]
 thematic=[e for e in events if re.fullmatch(r'v59_[pmces]\d{2}',e['id'])]
 assert len(thematic)==40 and Counter(e['category'] for e in thematic)=={'政治':8,'军事':8,'文化':8,'经济':8,'社会':8}
 assert len([e for e in events if e['id'].startswith('v59_king_')])==17
 assert all(e['sources'] and e.get('impact') and e.get('peopleRoles') is not None for e in events)
 objects=[o for o in d['objects'] if o['id'].startswith('v59_obj_')]
 assert len(objects)==16 and all(o['sources'] and o.get('dynasties')==['xia'] for o in objects)
 assert all(len(re.findall(r'[\u4e00-\u9fff]',o['body']))>=55 and '不等于' in o['note'] for o in objects)
 assert next(x for x in d['dynasties'] if x['id']=='xia')['selectable'] is True
 for pid in xia:
  assert pid in articles,(pid,'missing Xia reading')
  article=articles[pid]
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in article['sections'])
  assert chars>=700,(pid,'Xia reading depth',chars)
  assert len(article['sections'])==5 and all(x['sources'] and x.get('events') and len(x.get('people',[]))>=3 for x in article['sections'])
 contexts={c['person']:c for c in d['reignContexts'] if c['person'] in xia}
 assert set(contexts)==kings and all(c['periods'][0]['label']=='传统王序 · 个人王年不详' and c['events'] for c in contexts.values())
 assert not any(p in portraits and portraits[p].get('image') for p in kings)
 nonofficial={'v59_oxford_xia','v59_cambridge_debate','v59_shiji_xia','v59_zhushu','v59_shangshu_gan'}
 assert all('非官方' in sources[s]['note'] for s in nonofficial)
 assert any(e['title']=='女性人物的文本可见度' and {'xia_tushan','xia_houmin','xia_nuai','xia_meixi'}<=set(e['people']) for e in thematic)
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in xia]+events+objects+[articles[p] for p in xia],ensure_ascii=False))
 print('V41 PASS: Xia has seventeen explicitly received kings, eleven bounded figures, five balanced evidence lenses and sixteen archaeology topics without invented personal reign dates')

if d['version'] >= 42:
 tang_v60={
  't_changsun_empress','t_wencheng_princess','t_shangguan_waner','t_yang_guifei',
  't_gaolishi','t_yangguozhong','t_libi','t_yanzhenqing','t_duyou','t_liuzongyuan',
  't_baijuyi','t_luyu','t_jianzhen','t_sunsimiao','t_yanliben','t_liugongquan'
 }
 assert tang_v60<={p['id'] for p in d['people'] if p.get('dynasty')=='tang'}
 events=[e for e in d['events'] if e['id'].startswith('v60t_')]
 assert len(events)==30 and Counter(e['category'] for e in events)=={'政治':6,'军事':6,'文化':6,'经济':6,'社会':6}
 assert all(e['sources'] and e.get('impact') and e.get('peopleRoles') for e in events)
 objects=[o for o in d['objects'] if o['id'].startswith('v60_obj_')]
 assert len(objects)==12 and all(o['sources'] and o.get('dynasties')==['tang'] for o in objects)
 assert all(len(re.findall(r'[\u4e00-\u9fff]',o['body']))>=150 for o in objects)
 for pid in tang_v60:
  assert pid in articles and any(pid in e['people'] for e in events),(pid,'missing article or event')
  article=articles[pid]
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',x['text'])) for x in article['sections'])
  assert chars>=650,(pid,'Tang figure reading depth',chars)
  assert len(article['sections'])==5 and all(x['sources'] and x.get('events') and len(x.get('people',[]))>=2 for x in article['sections'])
  assert any(pid in c['people'] for c in d['reignContexts']),(pid,'missing imperial context')
 open_texts={'v60_jts51','v60_xts76','v60_jts106','v60_jts184','v60_jts130','v60_jts128','v60_jts147','v60_jts160','v60_jts166','v60_xts196','v60_jts191','v60_jts77','v60_jts165'}
 assert all('非官方' in sources[s]['note'] for s in open_texts)
 assert '未找到稳定的考古院原始网页' in next(o for o in objects if o['id']=='v60_obj_shangguan')['note']
 assert any(o['id']=='v60_obj_bunian' and '学术分歧' in o['note'] for o in objects)
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',json.dumps([people[p] for p in tang_v60]+events+objects+[articles[p] for p in tang_v60],ensure_ascii=False))
 print('V42 PASS: sixteen Tang figures, thirty balanced events, twelve evidence-bounded heritage topics and sourced five-part readings deepen court, social and material history')

if d['version'] >= 43:
 tang_emperors={p['id'] for p in d['people'] if p.get('dynasty')=='tang' and p['kind']=='皇帝'}
 tombs=[t for t in d['tombs'] if t['id'].startswith('v61_tomb_')]
 assert len(tombs)==10 and all(t['person'] in tang_emperors and t['sources'] for t in tombs)
 assert {'昭陵','桥陵','泰陵','景陵'}<={t['title'] for t in tombs}
 assert any(t['title']=='乾陵' and t['person']=='t_gaozong' for t in d['tombs'])
 assert all('未' in (t['body']+t['note']) or '不' in (t['body']+t['note']) for t in tombs), 'tomb evidence limits required'
 objects=[o for o in d['objects'] if o['id'].startswith('v61_obj_')]
 assert len(objects)==12 and all(o['sources'] and o['people'] and o.get('dynasties')==['tang'] for o in objects)
 assert all(len(re.findall(r'[\u4e00-\u9fff]',o['body']+o['note']))>=110 for o in objects)
 events=[e for e in d['events'] if e['id'].startswith('v61t_')]
 assert len(events)==25 and Counter(e['category'] for e in events)=={'政治':5,'军事':5,'文化':5,'经济':5,'社会':5}
 assert all(e['sources'] and e.get('impact') and e.get('peopleRoles') for e in events)
 required={'v61_shaanxi_tombs','v61_zhaoling_conservation','v61_nopss_changan','v61_nopss_county','v61_nopss_clerks','v61_nopss_markets','v61_nlc_dunhuang_admin','v61_nlc_sogdian','v61_nmc_silkroad'}
 assert required<=sources.keys()
 assert '不是逐陵考古报告' in sources['v61_shaanxi_tombs']['note']
 corpus=json.dumps(tombs+objects+events,ensure_ascii=False)
 assert all(term in corpus for term in ['唐十八陵','里坊','胥吏','敦煌','吐鲁番','粟特','驿传','墓志'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V43 PASS: ten evidence-bounded Tang imperial tombs, twelve urban and documentary topics, and twenty-five balanced events connect court history with local administration and ordinary life')

if d['version'] >= 44:
 song={p['id'] for p in d['people'] if p.get('dynasty')=='song_liao_xia_jin'}
 tombs=[t for t in d['tombs'] if t['id'].startswith('v62_tomb_')]
 assert len(tombs)==14 and len({t['person'] for t in tombs})==14
 assert all(t['person'] in song and t['sources'] and t['note'] for t in tombs)
 assert Counter(t['area'] for t in tombs)=={'河南 · 巩义北宋皇陵':7,'浙江 · 绍兴宋六陵':7}
 assert {'永昌陵','永熙陵','永定陵','永昭陵','永厚陵','永裕陵','永泰陵'}=={t['title'] for t in tombs if t['area'].startswith('河南')}
 assert {'永祐陵','永思陵','永阜陵','永崇陵','永茂陵','永穆陵','永绍陵'}=={t['title'] for t in tombs if t['area'].startswith('浙江')}
 assert all(any(x in t['body']+t['note'] for x in ['不能','不可','不作','不把','不得','仍需']) for t in tombs)
 objects=[o for o in d['objects'] if o['id'].startswith('v62_obj_')]
 assert len(objects)==10 and all(o['sources'] and o['people'] and o.get('dynasties')==['song_liao_xia_jin'] for o in objects)
 assert all(len(re.findall(r'[\u4e00-\u9fff]',o['body']+o['note']))>=110 for o in objects)
 events=[e for e in d['events'] if e['id'].startswith('v62s_')]
 assert len(events)==20 and Counter(e['category'] for e in events)=={'政治':4,'军事':4,'文化':4,'经济':4,'社会':4}
 assert all(e['sources'] and e.get('impact') and e.get('peopleRoles') for e in events)
 required={'v62_zzww_songling','v62_gongyi_plan','v62_zzww_archaeology','v62_henan_museum','v62_shaoxing_six','v62_shaoxing_exhibit','v62_shaoxing_gazetteer'}
 assert required<=sources.keys()
 corpus=json.dumps(tombs+objects+events,ensure_ascii=False)
 assert all(x in corpus for x in ['巩义','宋六陵','上宫','下宫','攒宫','梓宫','石刻','盗毁','复原'])
 assert '各陵绝对位置仍存在推测' in sources['v62_shaoxing_six']['note']
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V44 PASS: fourteen evidence-bounded Song imperial tombs, ten mausoleum-system topics and twenty balanced events distinguish Gongyi imperial tombs from Shaoxing temporary mausoleums')

if d['version'] >= 45:
 v63_sources={s['id']:s for s in d['sources'] if s['id'].startswith('v63_')}
 assert len(v63_sources)==11 and all(s['url'].startswith('https://') and len(s['note'])>=25 for s in v63_sources.values())
 tombs=[t for t in d['tombs'] if t['id'].startswith('v63_tomb_')]
 assert len(tombs)==11 and len({t['person'] for t in tombs})==11
 assert Counter('liao' if t['person'].startswith('s_liao_') else 'xia' if t['person'].startswith('s_xia_') else 'jin' for t in tombs)=={'liao':9,'xia':1,'jin':1}
 assert all(t['sources'] and t['note'] and len(re.findall(r'[\u4e00-\u9fff]',t['body']+t['note']))>=90 for t in tombs)
 assert all(any(term in t['body']+t['note']+t['status'] for term in ['不能','不应','不表示','不提供','不展示','尚不','尚缺','仍须','仍需','有待','推测','并非']) for t in tombs)
 assert next(t for t in tombs if t['id']=='v63_tomb_jin_ruiling')['title']=='睿陵'
 assert '传统推测' in next(t for t in tombs if t['id']=='v63_tomb_xixia_no3')['title']
 objects=[o for o in d['objects'] if o['id'].startswith('v63_obj_')]
 assert len(objects)==15 and all(o['sources'] and o['people'] and o.get('dynasties') for o in objects)
 assert all(len(re.findall(r'[\u4e00-\u9fff]',o['body']+o['note']))>=95 for o in objects)
 assert Counter(x for o in objects for x in o['dynasties'])=={'song_liao_xia_jin':13,'yuan':3}
 corpus=json.dumps(tombs+objects,ensure_ascii=False)
 assert all(term in corpus for term in ['九帝五陵','祖州','医巫闾山','九座帝陵','防洪','睿陵','数字编号','秘密归葬','起辇谷'])
 assert '目前仅太祖睿陵经考古确认' in v63_sources['v63_jinling_boundary']['note']
 assert '只是研究判断' in v63_sources['v63_yuan_research']['note']
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V45 PASS: eleven evidence-graded Liao, Xixia and Jin tomb links plus fifteen burial-system topics preserve numbered sites, confirmed tombs and unresolved Yuan locations')

if d['version'] >= 46:
 v64_sources={s['id']:s for s in d['sources'] if s['id'].startswith('v64_')}
 assert len(v64_sources)==16 and all(s['url'].startswith('https://') and len(s['note'])>=25 for s in v64_sources.values())
 objects=[o for o in d['objects'] if o['id'].startswith('v64_obj_')]
 assert len(objects)==16 and all(o['sources'] and o['people'] and o.get('dynasties') for o in objects)
 assert all(len(re.findall(r'[\u4e00-\u9fff]',o['body']+o['note']))>=100 for o in objects)
 assert Counter(x for o in objects for x in o['dynasties'])=={'qing':10,'ming':8}
 def object_category(o):
  if o['symbol']=='brain.head.profile': return 'ideas'
  if o['symbol'] in ['book.closed','music.note','doc.text']: return 'texts'
  if o['symbol'].startswith('building.columns'): return 'architecture'
  return 'objects'
 for dynasty,minimum in [('ming',{'architecture':6,'objects':2}),('qing',{'architecture':6,'objects':4})]:
  current=Counter(object_category(o) for o in d['objects'] if dynasty in (o.get('dynasties') or []))
  assert all(current[k]>=v for k,v in minimum.items())
 corpus=json.dumps(objects,ensure_ascii=False)
 assert all(term in corpus for term in ['紫禁城','天坛','南京明城墙','明长城','武当山','御窑','永宣青花','宣德炉','沈阳故宫','圆明园','避暑山庄','样式雷','金瓯永固杯','大禹治水','瓷胎画珐琅','铜版战图'])
 assert '不应写成已经正式列入世界遗产名录' in corpus
 assert '不能把所有粉彩瓷都归入这一门类' in corpus
 assert '不是中立的战场摄影' in corpus
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V46 PASS: sixteen sourced Ming-Qing architecture and object topics fill both empty collection categories while preserving reconstruction, attribution and image-bias boundaries')

if d['version'] >= 47:
 v65_sources={s['id']:s for s in d['sources'] if s['id'].startswith('v65_')}
 assert len(v65_sources)==11 and all(s['url'].startswith('https://') and len(s['note'])>=25 for s in v65_sources.values())
 events=[e for e in d['events'] if e['id'].startswith('v65')]
 assert len(events)==8 and Counter(e['category'] for e in events)=={'经济':4,'社会':4}
 assert all(e['sources'] and e.get('impact') and e.get('peopleRoles') and len(re.findall(r'[\u4e00-\u9fff]',e['body']+e['impact']))>=120 for e in events)
 assert {'q_zhantianyou','q_wuliande'}<=people.keys()
 for pid in ['q_zhantianyou','q_wuliande']:
  article=articles[pid]
  assert len(article['sections'])==4 and all(s['sources'] and s.get('events') and s.get('people') for s in article['sections'])
  assert sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in article['sections'])>=500
  assert any(pid in e['people'] for e in events)
 ming={p['id'] for p in d['people'] if p.get('dynasty')=='ming'}
 qing={p['id'] for p in d['people'] if p.get('dynasty')=='qing'}
 for dynasty_people in [ming,qing]:
  counts=Counter(e['category'] for e in d['events'] if dynasty_people.intersection(e['people']))
  assert counts['经济']>=15 and counts['社会']>=10
 required_links={
  'jianshen-7':'v65m_silver','houcong-8':'v65m_customs','yijun-8':'v65m_urban',
  'q-tongzhi-3':'v65q_shipping','q-guangxu-2':'v65q_famine','q-xuantong-3':'v65q_plague'
 }
 for section_id,event_id in required_links.items():
  section=next(s for a in d['articles'] for s in a['sections'] if s['id']==section_id)
  assert event_id in (section.get('events') or []),(section_id,'missing V47 event link')
 required_reign_events={
  'jianshen':{'v65m_silver','v65m_shecang'},'youtang':{'v65m_silver','v65m_shecang'},
  'houcong':{'v65m_silver','v65m_customs','v65m_shecang','v65m_urban'},
  'zaihou':{'v65m_silver','v65m_urban'},'yijun':{'v65m_silver','v65m_urban'},
  'q_tongzhi':{'v65q_shipping'},'q_guangxu':{'v65q_famine','v65q_jingzhang'},
  'q_xuantong':{'v65q_jingzhang','v65q_plague'}
 }
 contexts={x['person']:x for x in d['reignContexts']}
 assert all(ids<=set(contexts[pid]['events']) for pid,ids in required_reign_events.items())
 corpus=json.dumps(events+[people['q_zhantianyou'],people['q_wuliande'],articles['q_zhantianyou'],articles['q_wuliande']],ensure_ascii=False)
 assert all(term in corpus for term in ['白银','钞关','社仓','城市','丁戊奇荒','轮船招商局','京张铁路','肺鼠疫'])
 assert '不是中国境内第一条铁路' in corpus and '不能写成一人独自指挥整个东北' in corpus
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V47 PASS: eight sourced Ming-Qing economic and social events plus Zhan Tianyou and Wu Lien-teh readings deepen markets, relief, infrastructure and public health')

if d['version'] >= 48:
 v66_sources={s['id']:s for s in d['sources'] if s['id'].startswith('v66_')}
 assert len(v66_sources)==11 and all(s['url'].startswith('https://') and len(s['note'])>=25 for s in v66_sources.values())
 events=[e for e in d['events'] if e['id'].startswith('v66')]
 assert len(events)==8 and Counter(e['category'] for e in events)=={'文化':4,'社会':4}
 assert all(e['sources'] and e.get('impact') and e.get('peopleRoles') and len(re.findall(r'[\u4e00-\u9fff]',e['body']+e['impact']))>=180 for e in events)
 for pid in ['m_tanyunxian','q_wangzhenyi','q_qiujin']:
  assert pid in people
  article=articles[pid]
  assert len(article['sections'])==4 and all(s['sources'] and s.get('events') and s.get('people') for s in article['sections'])
  assert sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in article['sections'])>=550
  assert any(pid in e['people'] for e in events)
 required_reign_people={'houzhao':{'m_tanyunxian'},'q_qianlong':{'q_wangzhenyi'},'q_guangxu':{'q_qiujin'}}
 required_reign_events={
  'houzhao':{'v66m_tan_cases'},'houcong':{'v66m_women_work'},
  'q_yongzheng':{'v66q_xingke_records'},'q_qianlong':{'v66q_wang_science','v66q_xingke_records'},
  'q_jiaqing':{'v66q_xingke_records'},'q_daoguang':{'v66q_xingke_records'},
  'q_xianfeng':{'v66q_xingke_records'},'q_tongzhi':{'v66q_xingke_records'},
  'q_guangxu':{'v66q_xingke_records','v66q_women_schools','v66q_womens_journal','v66q_women_normal','v66q_ningbo_charity'},
  'q_xuantong':{'v66q_women_normal','v66q_ningbo_charity'}
 }
 contexts={x['person']:x for x in d['reignContexts']}
 assert all(ids<=set(contexts[pid]['people']) for pid,ids in required_reign_people.items())
 assert all(ids<=set(contexts[pid]['events']) for pid,ids in required_reign_events.items())
 required_links={
  'houzhao-8':'v66m_tan_cases','houcong-8':'v66m_women_work','q-yongzheng-7':'v66q_xingke_records',
  'q-qianlong-4':'v66q_wang_science','q-guangxu-6':'v66q_women_schools','q-xuantong-2':'v66q_women_normal'
 }
 for section_id,event_id in required_links.items():
  section=next(s for a in d['articles'] for s in a['sections'] if s['id']==section_id)
  assert event_id in (section.get('events') or []),(section_id,'missing V48 event link')
 corpus=json.dumps(events+[people[x] for x in ['m_tanyunxian','q_wangzhenyi','q_qiujin']]+[articles[x] for x in ['m_tanyunxian','q_wangzhenyi','q_qiujin']],ensure_ascii=False)
 assert all(term in corpus for term in ['女医杂言','三十一则','稳婆','王贞仪','刑科题本','女子教育','中国女报','京师女子师范','宁波'])
 assert '不是宫廷女官' in corpus and '只出版两期' in corpus and '不能把卷宗当作完整透明的日常生活实录' in corpus
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V48 PASS: eight sourced Ming-Qing topics and three full readings add women physicians, science, education, press, justice records and local charity with explicit evidence boundaries')

if d['version'] >= 50:
 v68_sources={s['id']:s for s in d['sources'] if s['id'].startswith('v50y_')}
 assert len(v68_sources)==10 and all(s['url'].startswith('https://') and len(s['note'])>=25 for s in v68_sources.values())
 yuan_people={'y_chabi','y_guan_daosheng','y_huang_daopo','y_ma_zhiyuan','y_jamal_al_din','y_ahmad_fanakati'}
 assert yuan_people<=people.keys()
 events=[e for e in d['events'] if e['id'].startswith('v50y_')]
 assert len(events)==12 and Counter(e['category'] for e in events)=={'经济':5,'文化':3,'社会':2,'政治':2}
 assert all(e['sources'] and e.get('peopleRoles') and e.get('impact') and len(re.findall(r'[\u4e00-\u9fff]',e['body']+e['impact']))>=120 for e in events)
 for pid in yuan_people:
  article=articles[pid]
  assert len(article['sections'])==4 and all(s['sources'] and s.get('events') and s.get('people') for s in article['sections'])
  assert sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in article['sections'])>=550
  assert any(pid in e['people'] for e in events)
 objects=[o for o in d['objects'] if o['id'].startswith('v50y_')]
 assert len(objects)==4 and all(o['sources'] and o['people'] and len(re.findall(r'[\u4e00-\u9fff]',o['body']+o['note']))>=120 for o in objects)
 five=[e for e in d['events'] if re.fullmatch(r'v54_[es]\d{2}',e['id'])]
 assert len(five)==20 and all(e.get('peopleRoles') and len(re.findall(r'[\u4e00-\u9fff]',e['body']+e['impact']))>=120 for e in five)
 contexts={x['person']:x for x in d['reignContexts']}
 assert {'y_chabi','y_jamal_al_din','y_ahmad_fanakati','y_huang_daopo'}<=set(contexts['y_kublai']['people'])
 assert {'v50y_late_currency','v50y_salt_revenue'}<=set(contexts['y_toghon_temur']['events'])
 corpus=json.dumps([people[x] for x in yuan_people]+events+objects+[articles[x] for x in yuan_people]+five,ensure_ascii=False)
 assert all(term in corpus for term in ['秋深帖','黄道婆','泉州','扎马鲁丁','阿合马','站赤','四等人','盐课','马致远'])
 assert '不能把整个江南棉业归为她一人发明' in corpus
 assert '不等于存在一部整齐统一' in corpus
 assert '正文实为赵孟頫代书' in corpus
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V50 PASS: six full Yuan readings, twelve institutional and social events, four evidence-bounded objects, and twenty rewritten Five Dynasties economy/social entries')

if d['version'] >= 51:
 added_people={'t_wangbo','t_gaopian','s_zhangjie','s_chenyizhong'}
 assert added_people<=people.keys()
 added_event_ids={'v51t_wangbo_salt','v51t_wuzong_property','v51t_annam_recovery','v51t_annam_relief','v51t_changan_damage','v51s_pingxia','v51s_duzong_lectures','v51s_linan_daily'}
 added_events=[e for e in d['events'] if e['id'] in added_event_ids]
 assert len(added_events)==8 and Counter(e['category'] for e in added_events)=={'经济':3,'军事':2,'社会':2,'文化':1}
 assert all(e['sources'] and e.get('peopleRoles') and e.get('impact') and len(re.findall(r'[\u4e00-\u9fff]',e['body']+e['impact']))>=80 for e in added_events)
 for pid in added_people:
  article=articles[pid]
  assert len(article['sections'])==4 and all(s['sources'] and s.get('events') and len(s.get('people',[]))>=2 for s in article['sections'])
  assert sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in article['sections'])>=600
  assert any(pid in e['people'] for e in added_events)
 source_ids={'v51t_jts164','v51t_jts182','v51s_ss328','v51s_menglianglu'}
 source_map={s['id']:s for s in d['sources'] if s['id'] in source_ids}
 assert source_ids==source_map.keys() and all('非官方平台' in s['title'] and len(s['note'])>=40 for s in source_map.values())
 contexts={x['person']:x for x in d['reignContexts']}
 required_people={'t_jingzong':{'t_wangbo'},'t_yizong':{'t_gaopian'},'t_xizong':{'t_gaopian'},'s_zhezong':{'s_zhangjie'},'s_duzong':{'s_chenyizhong'}}
 required_events={
  't_jingzong':{'v51t_wangbo_salt'},'t_wuzong':{'v51t_wuzong_property'},
  't_yizong':{'v60t_s06','v51t_annam_recovery','v51t_annam_relief'},
  't_xizong':{'v47t_famine_rebellion','v51t_changan_damage'},
  's_yingzong':{'v47s_futian'},'s_zhezong':{'v47s_yingzao','v51s_pingxia'},
  's_duzong':{'v43s_gongtian','v51s_duzong_lectures','v51s_linan_daily'}
 }
 assert all(ids<=set(contexts[pid]['people']) for pid,ids in required_people.items())
 assert all(ids<=set(contexts[pid]['events']) for pid,ids in required_events.items())
 required_links={'v43t_yizong_s2':'v51t_annam_recovery','v43t_xizong_s2':'v51t_changan_damage','v43s_zhezong_2':'v51s_pingxia','v43s_duzong_5':'v51s_duzong_lectures'}
 for section_id,event_id in required_links.items():
  section=next(s for a in d['articles'] for s in a['sections'] if s['id']==section_id)
  assert event_id in (section.get('events') or []),(section_id,'missing V51 event link')
 corpus=json.dumps([people[x] for x in added_people]+added_events+[articles[x] for x in added_people],ensure_ascii=False)
 assert all(term in corpus for term in ['羡余','安南','纪年相差一年','平夏城','奏捷','字民','梦粱录','追忆故都'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V51 PASS: four full late-Tang and Song readings, eight events, and seven repaired reign-context links preserve explicit evidence boundaries')

if d['version'] >= 52:
 assert 'han_liangna' in people and people['han_liangna']['name']=='梁妠'
 liang_article=articles['han_liangna']
 assert len(liang_article['sections'])==5
 assert sum(len(re.findall(r'[\u4e00-\u9fff]',s['text'])) for s in liang_article['sections'])>=700
 assert all(s['sources'] and s.get('events') and s.get('people') for s in liang_article['sections'])
 events={e['id']:e for e in d['events']}
 assert events['v49h_jing_theme']['year']=='前154'
 assert events['v49h_zhao_theme']['year']=='前81'
 assert events['v49h_huan_theme']['year']=='166' and 'han_liangji' not in events['v49h_huan_theme']['people']
 assert events['v49h_ling_theme']['year']=='184' and 'han_chenfan' not in events['v49h_ling_theme']['people']
 assert 'han_zhangheng' not in events['v49h_chong_accession']['people']+events['v49h_chong_theme']['people']
 assert 'han_chenfan' not in events['v49h_zhi_accession']['people']+events['v49h_zhi_theme']['people']
 assert {'han_liangna','han_chong','han_zhi','han_huan','han_liangji'}==set(events['v52h_liang_dowager_regency']['people'])
 contexts={x['person']:x for x in d['reignContexts']}
 required_events={
  'han_gaozu':{'v49h_baideng'},'han_wen':{'v49h_rest'},'han_jing':{'v49h_seven'},
  'han_wu':{'v49h_tui_en','v49h_hexi','v49h_wuzhu','v49h_taixue','v49h_shiji'},
  'han_zhao':{'v49h_saltiron'},'han_xuan':{'v49h_protectorate'},'han_guangwu':{'v49h_land'},
  'han_he':{'v49h_western','v49h_paper','v49h_hanbook'},'han_an':{'v49h_disaster'},
  'han_chong':{'v52h_liang_dowager_regency'},'han_zhi':{'v52h_liang_dowager_regency'},
  'han_huan':{'v52h_liang_dowager_regency'},
  'han_ling':{'v49h_partisan','v49h_epidemics','v49h_yellow'},
  'han_xian':{'v49h_dongzhuo','v49h_xutian'}
 }
 assert all(ids<=set(contexts[pid]['events']) for pid,ids in required_events.items())
 assert 'han_liangna' in contexts['han_shun']['people']
 assert contexts['han_chong']['people']==['han_liangna','han_liangji']
 assert contexts['han_zhi']['people']==['han_liangna','han_liangji'] and 'han_liangna' in contexts['han_huan']['people']
 assert any(x['from']=='han_liangna' and x['to']=='han_shun' and x['kind']=='spouse' for x in d['familyLinks'])
 assert all('han_zhi' not in {x['from'],x['to']} or 'han_chenfan' not in {x['from'],x['to']} for x in d['associations'])
 assert all(set(s.get('events',[]))=={'v49h_huan_theme','v49h_partisan'} for s in articles['han_chenfan']['sections'])
 corpus=json.dumps([people['han_liangna'],liang_article,events['v52h_liang_dowager_regency']],ensure_ascii=False)
 assert all(term in corpus for term in ['皇太后临朝','连续拥立','归政','制度权力','不能混成一个行动主体'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V52 PASS: Han reign pages recover twenty existing event links, correct four chronology errors, and distinguish Empress Dowager Liang from Liang Ji across three short reigns')

if d['version'] >= 53:
 portraits={p['person']:p for p in d['portraits']}
 for pid,page in [('qiyu','page=20'),('youjian','page=32')]:
  portrait=portraits[pid]
  assert portrait['title'].startswith('《明史通俗演义》第')
  assert portrait['sourceIds']==['v4portrait-mingshi-cnts','v4portrait-mingshi-tokyo']
  assert 'commons.wikimedia.org' in portrait['sourceURL'] and page in portrait['sourceURL']
  assert 'hdslb.com' not in portrait['imageURL'] and portrait['displayLabel']=='后世绣像'
  with Image.open(image_path(portrait['image'])) as image:
   assert image.width>=1000 and image.height>=2000,(pid,image.size)
 assert not any('bilibili.com' in source['url'] for source in d['sources'])
 assert sources['portrait-jianwen-editions']['url'].startswith('https://rbook.ncl.edu.tw/')
 puyi=next(t for t in d['tombs'] if t['id']=='tomb_q_xuantong')
 assert puyi['sources']==['v73_puyi_cppcc','v5qn_puyi_burial']
 assert '未找到陵园或民政部门公开的原始迁葬档案' in puyi['note']
 assert sources['v73_puyi_cppcc']['url'].startswith('https://www.cppcc.gov.cn/')
 print('V53 PASS: Jingtai and Chongzhen use verified full book pages; Jianwen edition and Puyi burial evidence expose their source boundaries')

if d['version'] >= 54:
 key_readings={
  'm40_wangshouren':{'v2l_ningwang'},
  'm40_qijiguang':{'v2l_coastal','v40m2_jizhen_training_1568'},
  'm41_lishizhen':{'v41m_bencao_draft','v41m_bencao_print'},
  'm40_xuguangqi':{'v40m2_geometry_1607','v40m2_calendar_1629'},
  'q_linzexu':{'v40q_humen','qev_opium_war_1840','v40q_haiguo'},
  'q_zengguofan':{'v40q_xiang_army','v40q_tianjing_fall'},
  'q_lihongzhang':{'qev_self_strengthening_1860s','qev_sino_japanese_war_1894','v26_boxer_protocol'},
  'q_zuozongtang':{'v40q_fuzhou_shipyard','v40q_xinjiang_campaign','v41q_xinjiang_province'},
 }
 all_event_ids={event['id'] for event in d['events']}
 for pid,required_events in key_readings.items():
  article=articles[pid]
  linked_events={event_id for section in article['sections'] for event_id in section.get('events',[])}
  assert len(article['sections'])==5,(pid,'expected five-layer reading')
  assert sum(len(re.findall(r'[\u4e00-\u9fff]',section['text'])) for section in article['sections'])>=880,(pid,'reading remains too short')
  assert required_events<=linked_events<=all_event_ids,(pid,'missing or invalid event links')
  assert len(article['sources'])>=1 and all(source_id in sources for source_id in article['sources'])
 museum_source=sources['v54q_chnmuseum_humen']
 assert museum_source['url'].startswith('https://www.chnmuseum.cn/') and len(museum_source['note'])>=40
 corpus=json.dumps([articles[pid] for pid in key_readings],ensure_ascii=False)
 assert all(term in corpus for term in ['知行合一不是成功学口号','鸳鸯阵','金陵胡承龙刊本','团队工程','责任不能倒置','地方权力','签约者','后勤线'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V54 PASS: eight central Ming-Qing figures now have five-layer readings with event links, institutional context and explicit evidence boundaries')

if d['version'] >= 55:
 key_readings={
  'm40_yansong':{'v2l_gengxu','v40m2_yansong_removed_1562'},
  'm40_hairui':{'v40m2_hairui_memorial_1566','v2l_release','v40m2_hairui_land_1569'},
  'm40_yuanchonghuan':{'v40m2_sun_liaoxi_1622','v2l_ningyuan','v2l_yuan'},
  'q_weiyuan':{'v40q_haiguo'},
  'q_kangyouwei':{'qev_hundred_days_1898','v41q_shiwu'},
  'q_liangqichao':{'v41q_shiwu','qev_hundred_days_1898','v41q_tianyan','v41q_xinmin'},
 }
 for pid,required_events in key_readings.items():
  article=articles[pid]
  linked_events={event_id for section in article['sections'] for event_id in section.get('events',[])}
  linked_people={person_id for section in article['sections'] for person_id in section.get('people',[])}
  assert len(article['sections'])==5,(pid,'expected five-layer reading')
  assert sum(len(re.findall(r'[\u4e00-\u9fff]',section['text'])) for section in article['sections'])>=900,(pid,'reading remains too short')
  assert required_events<=linked_events,(pid,'missing event context')
  assert linked_people<=people.keys() and linked_people,(pid,'missing or invalid people links')
  assert len(article['sources'])>=2 and all(source_id in sources for source_id in article['sources'])
 corpus=json.dumps([articles[pid] for pid in key_readings],ensure_ascii=False)
 assert all(term in corpus for term in ['最终任免和裁断','清官救济','通敌罪证不足','来源链越长','是否真正上达存在研究争议','思想变化不是简单反复'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成',corpus)
 print('V55 PASS: six pivotal Ming-Qing readings separate personal agency from institutions, networks, source limits and later memory')

if d['version'] >= 56:
 key_readings={
  'm40_xujie':{'v2l_gengxu','v40m2_yansong_removed_1562','v2l_release','v40m2_hairui_land_1569'},
  'm40_weizhongxian':{'v40m2_yang_accuses_1624','v2l_prisons','v2l_weifall'},
  'm40_lizicheng':{'v40m2_dashun_1644','v2l_beijing1644'},
  'q_hongxiuquan':{'qev_taiping_1851','v40q_tianjing_capital','v40q_tianjing_fall'},
  'q_zhangzhidong':{'v40q_new_policy_memorial','v12_guangxu_exam'},
  'q_yanfu':{'v41q_tianyan'},
 }
 for pid,required_events in key_readings.items():
  article=articles[pid]
  linked_events={event_id for section in article['sections'] for event_id in section.get('events',[])}
  linked_people={person_id for section in article['sections'] for person_id in section.get('people',[])}
  assert len(article['sections'])==5,(pid,'expected five-layer reading')
  assert sum(len(re.findall(r'[\u4e00-\u9fff]',section['text'])) for section in article['sections'])>=900,(pid,'reading remains too short')
  assert required_events<=linked_events,(pid,'missing event context')
  assert linked_people<=people.keys() and linked_people,(pid,'missing or invalid people links')
  assert len(article['sources'])>=2 and all(source_id in sources for source_id in article['sources'])
 corpus=json.dumps([articles[pid] for pid in key_readings],ensure_ascii=False)
 assert all(term in corpus for term in ['最终任免仍由皇帝决定','暴力并非只由一个宦官','死亡地点和过程存在不同记载','纲领文本不等于全国范围的完整实施','不能只按“创办第一”评价','赫胥黎'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V56 PASS: six Ming-Qing readings connect political actors to institutions, social costs, contested sources and later memory')

if d['version'] >= 57:
 sites={site['id']:site for site in d['prehistorySites']}
 required={'shangchen','nihewan','yuanmou','lantian','zhoukoudian','dingcun','jinniushan','tianyuan','shandingdong','xianrendong','shangshan','jiahu','hemudu','banpo','chengtoushan','dawenkou','niuheliang','majiayao','liangzhu','taosi','shimao'}
 assert required==sites.keys() and len(sites)==21
 assert sites['zhoukoudian']['name']=='北京人遗址（周口店第一地点）'
 assert {'北京人','周口店北京人','北京猿人'}<=set(sites['zhoukoudian']['aliases'])
 for site in sites.values():
  sections=site.get('sections') or []
  corpus=''.join([site['summary'],site['discovery'],site['significance'],site.get('evidenceNote','')]+[section['text'] for section in sections])
  assert len(sections)>=4,(site['id'],'insufficient reading layers')
  assert len(re.findall(r'[\u4e00-\u9fff]',corpus))>=450,(site['id'],'site reading remains too short')
  assert len(site.get('aliases',[]))>=2 and site.get('evidenceNote')
  assert len(site['sources'])>=3 and set(site['sources'])<=sources.keys()
 official_sources={'v57_nmc_human_history','v57_ivpp_origins','v57_cass_jiahu','v57_cass_chengtoushan'}
 assert official_sources<=sources.keys()
 assert sources['v57_nmc_human_history']['url'].startswith('https://www.chnmuseum.cn/')
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='prehistory')
 assert len(profile['sections'])==5 and len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=300
 corpus=json.dumps([profile]+list(sites.values()),ensure_ascii=False)
 assert all(term in corpus for term in ['北京人遗址（周口店第一地点）','战前发现的多件重要化石原件在转移中失踪','制造者种属不能由石器直接确定','不能直接称为成熟文字','城市定义'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V57 PASS: the prehistory overview and 21 layered site readings expose landmark discoveries, methods and evidence boundaries')

if d['version'] >= 58:
 assert set(people)==articles.keys(),('people without layered readings',set(people)-articles.keys())
 new_readings=[article for article in d['articles'] if any(section['id'].endswith('-e1') for section in article['sections'])]
 assert len(new_readings)==43
 for article in new_readings:
  chars=sum(len(re.findall(r'[\u4e00-\u9fff]',section['text'])) for section in article['sections'])
  assert len(article['sections'])==5 and chars>=500,(article['person'],'new reading remains too short',chars)
  assert article['sources'] and set(article['sources'])<=sources.keys()
 events={event['id']:event for event in d['events']}
 deep_events={event_id:event for event_id,event in events.items() if event_id.startswith('v90_')}
 assert len(deep_events)==24
 for event in deep_events.values():
  chars=len(re.findall(r'[\u4e00-\u9fff]',event['body']+event['impact']))
  assert chars>=145,(event['id'],'event reading remains too short',chars)
  assert event['category'] in {'政治','军事','文化','经济','社会'}
 contexts={context['person']:context for context in d['reignContexts']}
 categories=['政治','军事','文化','经济','社会']
 for dynasty in ['ming','qing']:
  for pid in {item['person'] for item in d['sequence'] if people[item['person']]['dynasty']==dynasty}:
   if pid=='changluo': continue  # one-month reign: do not manufacture five categories
   actual={events[event_id].get('category','政治') for event_id in contexts[pid]['events']}
   assert set(categories)<=actual,(pid,'reign category gap',set(categories)-actual)
 corpus=json.dumps(new_readings+list(deep_events.values()),ensure_ascii=False)
 assert all(term in corpus for term in ['不表示每位亲属都参与同一政治事件','追封属于身后礼制','迁都北京背后的供给与人口流动','圈地、投充与逃人问题'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V58 PASS: every person has a layered reading; durable Ming-Qing reigns cover five event lenses with evidence-bounded context')

if d['version'] >= 59:
 context_only=[(c['person'],eid) for c in d['reignContexts'] for eid in c['events'] if c['person'] not in events[eid]['people']]
 assert context_only and len(context_only)>=190
 assert all(any(min([int(y) for y in re.findall(r'\d{1,4}',events[eid]['year'])] or [10**9])<=max(p['start'],p['end']) and max([int(y) for y in re.findall(r'\d{1,4}',events[eid]['year'])] or [-10**9])>=min(p['start'],p['end']) for p in contexts[pid]['periods']) for pid,eid in context_only if '世纪' not in events[eid]['year'])
 print('V59 PASS: period-context links remain distinct from direct personal participation and overlap the displayed reign')

def durable_coverage(dynasties):
 complete=total=0
 categories={'政治','军事','文化','经济','社会'}
 for pid,c in contexts.items():
  if people[pid].get('dynasty') not in dynasties:continue
  start=min(p['start'] for p in c['periods']);end=max(p['end'] for p in c['periods'])
  if end-start<9:continue
  total+=1
  if categories<={events[eid]['category'] for eid in c['events']}:complete+=1
 return complete,total

if d['version'] >= 60:
 added=[e for e in d['events'] if e['id'].startswith('v91t_')]
 assert len(added)==11 and all(e['sources'] and e['impact'] for e in added)
 assert all(len(re.findall(r'[\u4e00-\u9fff]',e['body']+e['impact']))>=105 for e in added)
 assert durable_coverage({'tang'})==(14,14)
 print('V60 PASS: eleven sourced Tang structural-history readings give every durable reign all five event lenses')

if d['version'] >= 61:
 complete,total=durable_coverage({'song_liao_xia_jin','yuan'})
 assert complete>=24 and total==38
 print('V61 PASS: twenty-four of thirty-eight durable Song-Liao-Xia-Jin-Yuan reigns now expose all five lenses; unsupported gaps remain explicit')

if d['version'] >= 62:
 complete,total=durable_coverage({'qin','han','three_kingdoms','jin','northern_southern','sui'})
 assert complete>=24 and total==39
 print('V62 PASS: twenty-four of thirty-nine durable Qin-to-Sui reigns now expose all five lenses using chronologically overlapping reviewed material')

if d['version'] >= 63:
 complete,total=durable_coverage({'xia','shang','zhou','five_dynasties'})
 assert complete>=16 and total==21
 assert d['reviewed'] in {'2026-10-19','2026-10-28'}
 print('V63 PASS: early-state and Five-Dynasties contexts complete a five-pass audit without inventing evidence for the remaining gaps')

if d['version'] >= 64:
 added=[event for event in d['events'] if event['id'].startswith('v96')]
 assert len(added)==23
 assert all(event['sources'] and event['impact'] and len(re.findall(r'[\u4e00-\u9fff]',event['body']+event['impact']))>=105 for event in added)
 assert not {'v49h_yuan_theme'}&set(contexts['han_guangwu']['events'])
 assert not {'v49h_saltiron'}&set(contexts['han_zhang']['events'])
 assert not {'v49h_jing_theme'}&set(contexts['han_huan']['events'])
 assert durable_coverage({'song_liao_xia_jin','yuan'})[0]>=30
 assert durable_coverage({'qin','han','three_kingdoms','jin','northern_southern','sui'})[0]>=28
 assert durable_coverage({'xia','shang','zhou','five_dynasties'})[0]>=18
 corpus=json.dumps(added,ensure_ascii=False)
 assert all(term in corpus for term in ['不能只讲杯酒释兵权','不能据此把所有受牵连者视为同一宗教组织','不是献帝主持的宫廷工程','不能把所有蜀中艺术都直接归于王建'])
 assert not re.search(r'本轮|补充内容|数据缺口|开发进度|AI生成|fallback',corpus,re.I)
 print('V64 PASS: twenty-three structural events repair BCE/CE false links and deepen Song-Liao-Jin, Eastern Han and regional Five-Dynasties history')

if d['version'] >= 65:
 for pid,c in contexts.items():
  if people[pid].get('dynasty')!='han':continue
  reign_bce=all(period['label'].startswith('前') for period in c['periods'])
  for eid in c['events']:
   label=events[eid]['year']
   event_bce=label.startswith('前') and not re.search(r'前\d+世纪[—–-]\d+世纪',label)
   assert event_bce==reign_bce or ('世纪' in label and '—' in label),(pid,eid,'BCE/CE direction mismatch')
 print('V65 PASS: Han reign links distinguish BCE dates from CE dates before category coverage is counted')

def assert_deep_prefix(prefix,count):
 selected=[event for event in d['events'] if event['id'].startswith(prefix)]
 assert len(selected)==count,(prefix,len(selected))
 assert all(event['sources'] and event['impact'] and len(re.findall(r'[\u4e00-\u9fff]',event['body']+event['impact']))>=105 for event in selected)
 return selected

if d['version'] >= 66:
 assert_deep_prefix('v98',1)
 print('V66 PASS: Northern Song ritual mobilization adds a sourced social lens to Zhenzong’s reign')
if d['version'] >= 67:
 assert_deep_prefix('v99',4)
 print('V67 PASS: Liao and Jin fiscal, environmental and military contexts close four durable-reign gaps')
if d['version'] >= 68:
 assert_deep_prefix('v100',5)
 print('V68 PASS: Western Xia border trade and Yuan-Chagatai war complete evidence-bounded western-polity lenses')
if d['version'] >= 69:
 assert_deep_prefix('v101',3)
 print('V69 PASS: Eastern Han education, agriculture and Qiang-war readings replace broad or misplaced context')
if d['version'] >= 70:
 assert_deep_prefix('v102',3)
 print('V70 PASS: Wu finance and Western/Eastern Jin cultural contexts preserve agency and source boundaries')
if d['version'] >= 71:
 assert_deep_prefix('v103',5)
 print('V71 PASS: Liu-Song and Southern-Qi military, monetary, household and registration history is exposed')
if d['version'] >= 72:
 assert_deep_prefix('v104',7)
 print('V72 PASS: Northern-Wei state formation now connects war, education, economy, migration and border recovery')
if d['version'] >= 73:
 assert_deep_prefix('v105',3)
 print('V73 PASS: Later-Liang, Yang-Wu and Min retain cultural and military history beyond succession lists')
if d['version'] >= 74:
 assert durable_coverage({'tang'})==(14,14)
 assert durable_coverage({'song_liao_xia_jin','yuan'})==(38,38)
 assert durable_coverage({'qin','han','three_kingdoms','jin','northern_southern','sui'})==(39,39)
 assert durable_coverage({'xia','shang','zhou','five_dynasties'})==(21,21)
 deepened=['fd_zhuwen','fd_cunxu','fd_siyuan','fd_jingtang','fd_zhiyuan','fd_guowei','fd_chairong','fd_wy_qianliu','fd_min_shenzhi','fd_nt_yu']
 for pid in deepened:
  article=articles[pid]
  assert len(article['sections'])==6 and any(section['id'].startswith('v106-') for section in article['sections'])
  assert sum(len(re.findall(r'[\u4e00-\u9fff]',section['text'])) for section in article['sections'])>=740
 print('V74 PASS: all durable reigns expose five historical lenses; ten consequential Five-Dynasties rulers gain a sixth evidence-bounded reading layer')
if d['version'] >= 75:
 precise_sources={
  'v107_liaoshi_6','v107_liaoshi_7','v107_xixiaji_26','v107_nanqishu_34',
  'v107_houhanshu_79a','v107_weishu_2','v107_beishi_1','v107_jinshi_4',
  'v107_jinshi_14','v107_jinshi_101'
 }
 assert precise_sources <= set(sources)
 assert all(sources[sid]['url'].startswith('https://') for sid in precise_sources)
 qi_registration=events['v103ns_qi_registration']
 assert qi_registration['year']=='490' and qi_registration['sortYear']==490
 assert '始于高帝建元二年' in qi_registration['body'] and '永明八年' in qi_registration['body']
 assert 'v107_nanqishu_34' in qi_registration['sources']
 taixue=events['v101h_guangwu_taixue']
 assert taixue['year']=='29' and '建武五年' in taixue['body']
 assert 'v107_houhanshu_79a' in taixue['sources']
 daowu=events['v104ns_daowu_school']
 assert '太学建设' not in daowu['title'] and '官署' in daowu['title']
 assert {'v107_weishu_2','v107_beishi_1'} <= set(daowu['sources'])
 assert {'v107_jinshi_14','v107_jinshi_101'} <= set(events['v99s_jin_mongol_war']['sources'])
 assert 'v107_xixiaji_26' in events['v100s_xia_huanzong_society']['sources']
 for pid in deepened:
  article=articles[pid]
  section=next(section for section in article['sections'] if section['id']==f'v106-{pid}-context')
  assert len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=240,(pid,'short audited section')
  assert sum(len(re.findall(r'[\u4e00-\u9fff]',section['text'])) for section in article['sections'])>=900,(pid,'short article')
 print('V75 PASS: corrected chronology and attribution; precise primary-source chapters support audited events; ten Five-Dynasties readings exceed 900 Chinese characters')
three_kingdoms_passes={
 76:('江东奠基',['tk_sunjian','tk_sunce']),
 77:('赤壁联盟',['tk_zhouyu','tk_lusu']),
 78:('荆州攻守',['tk_lvmeng','tk_luxun']),
 79:('蜀汉建立',['tk_liubei','tk_guanyu']),
 80:('蜀汉将领',['tk_zhangfei','tk_zhaoyun']),
 81:('益州与托孤',['tk_zhugeliang','tk_pangtong']),
 82:('曹魏建国',['tk_caopi','tk_caorui']),
 83:('司马氏掌权',['tk_simayi','tk_simashi']),
 84:('魏灭蜀',['tk_dengai','tk_zhonghui']),
 85:('文学与名教',['tk_caozhi','tk_jikang']),
}
for version,(label,pids) in three_kingdoms_passes.items():
 if d['version']>=version:
  for pid in pids:
   article=articles[pid]
   titles={section['title'] for section in article['sections']}
   assert len(article['sections'])==7,(pid,'requires seven specific layers')
   assert not titles & {'时代位置','选择、制度与代价','人物关系与实物证据'},(pid,'templated title remains')
   total=sum(len(re.findall(r'[\u4e00-\u9fff]',section['text'])) for section in article['sections'])
   assert total>=580,(pid,total,'short bespoke reading')
   assert all(section['events'] and section['sources'] for section in article['sections'])
  print(f'V{version} PASS: {label} pair has seven person-specific reading layers and no legacy template headings')
if d['version']>=85:
 assert {'v108_sgz46','v108_jinshu1','v108_jinshu2','v108_jinshu49'} <= set(sources)
 assert articles['tk_sunjian']['sources']==['v108_sgz46']
 assert articles['tk_sunce']['sources']==['v108_sgz46']
 for eid in ['v108_sunjian_coalition','v108_sunce_jiangdong','v108_zhangfei_yizhou','v108_pangtong_yizhou']:
  event=events[eid]
  assert len(re.findall(r'[\u4e00-\u9fff]',event['body']+event['impact']))>=100
 assert '孙权称帝' not in ''.join(section['text'] for section in articles['tk_sunce']['sections'])
 print('V85 DETAIL PASS: four missing person-events and exact primary biographies replace the Sun-Ce source mismatch')

if d['version']>=86:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='prehistory')
 assert [section['id'] for section in profile['sections']]==['human','modern','settlement','regions','method']
 for section in profile['sections']:
  assert len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=180,(section['id'],'macro prehistory reading remains too short')
 corpus=''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['古地磁','古DNA','混合生计','调动劳力','复原图不是现场照片'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V86 PASS: five discoverable macro readings connect prehistoric evidence, population, subsistence and social complexity')

if d['version']>=87:
 for dynasty,ids in {
  'xia':['xia-three-layers','xia-king-list','xia-erlitou','xia-debate','xia-people'],
  'shang':['shang-evidence','shang-capitals','shang-network','shang-society','shang-writing'],
 }.items():
  profile=next(profile for profile in d['dynastyProfiles'] if profile['id']==dynasty)
  assert [section['id'] for section in profile['sections']]==ids
  assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=200 for section in profile['sections'])
  assert len(profile['sources'])>=5 and set(profile['sources'])<=sources.keys()
 corpus=''.join(next(profile for profile in d['dynastyProfiles'] if profile['id']==dynasty)['overview']+''.join(section['text'] for section in next(profile for profile in d['dynastyProfiles'] if profile['id']==dynasty)['sections']) for dynasty in ['xia','shang'])
 assert all(term in corpus for term in ['循环证明','不虚构个人公历年','发掘只占很小部分','王朝命名','档案视角并不等于全社会视角'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V87 PASS: Xia and Shang each expose five evidence-led long readings without conflating archaeology, king lists and later interpretation')

if d['version']>=88:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='zhou')
 assert [section['id'] for section in profile['sections']]==['zhou-evidence','zhou-network','zhou-eastward','zhou-states','zhou-society']
 assert len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=300
 assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=200 for section in profile['sections'])
 assert {'v58_nmc_bronze','v58_nopss_zhou','v114_nmc_eastern_zhou','v114_nopss_reform'}<=set(profile['sources'])<=sources.keys()
 corpus=profile['overview']+''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['前841年','固定国界','尊王','郡县治理','礼器和长篇铭文'])
 assert '“五霸”名单' in corpus and '不完全相同' in corpus
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V88 PASS: Zhou macro reading separates chronology, investiture networks, eastward transition, state formation and lives beyond ritual bronzes')

if d['version']>=89:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='qin')
 assert [section['id'] for section in profile['sections']]==['qin-from-state','qin-documents','qin-law','qin-standards','qin-collapse']
 assert len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=300
 assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=220 for section in profile['sections'])
 assert {'v48q_shiji6','v48q_hubei_slips','v115_nmc_liye_exhibition','v115_nopss_village'}<=set(profile['sources'])<=sources.keys()
 corpus=profile['overview']+''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['不是制度从无到有的起点','一个县代表全国','不能等同现代法治','持续推行的过程','大雨误期当斩'])
 assert all(term in corpus for term in ['喜','迁陵县','半两钱','扶苏','陈胜、吴广'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V89 PASS: Qin macro reading connects Warring States state formation, county archives, law, standards and collapse without textbook shortcuts')

if d['version']>=90:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='han')
 assert [section['id'] for section in profile['sections']]==['han-rebuilding','han-expansion','han-knowledge','han-society','han-interruption']
 assert len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=300
 assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=220 for section in profile['sections'])
 assert {'v49h_hanshu','v49h_houhanshu','v49h_nmc_qinhan','v49h_hunan_mawangdui','v115_nopss_village','v116_nopss_xuanquan'}<=set(profile['sources'])<=sources.keys()
 corpus=profile['overview']+''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['汉承秦制','不是一条没有断口的帝序','不能代表普通编户','不能一律画成与内地郡县相同','不能压缩成武帝一句“独尊儒术”'])
 assert all(term in corpus for term in ['郡国并行','悬泉置','盐铁会议','马王堆','王莽','黄巾起事'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V90 PASS: Han macro reading connects reconstruction, fiscal expansion, knowledge, registered households and dynastic interruption')

if d['version']>=91:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='three_kingdoms')
 assert [section['id'] for section in profile['sections']]==['tk-formation','tk-logistics','tk-documents','tk-society','tk-transition']
 assert len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=300
 assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=220 for section in profile['sections'])
 assert {'v51tk_sgz2','v51tk_sgz32','v51tk_sgz47','v51tk_wujian','v117_changsha_wujian','v117_nmc_medieval'}<=set(profile['sources'])<=sources.keys()
 corpus=profile['overview']+''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['不是从赤壁之战同时诞生','不能排成一条前后相继','不能据此推定曹魏、蜀汉或孙吴所有郡县完全相同','不是现实社会的完整缩影','不能反向当作三世纪事实'])
 assert all(term in corpus for term in ['220年','229年','走马楼','军粮','九品官人法','280年'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V91 PASS: Three Kingdoms macro reading connects parallel state formation, logistics, local archives, social life and the Jin transition')

if d['version']>=92:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='jin')
 assert [section['id'] for section in profile['sections']]==['jin-western','jin-north','jin-migration','jin-power','jin-life']
 assert len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=300
 assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=220 for section in profile['sections'])
 assert {'v52j_js3','v52j_js4','v52j_js5','v52j_js6','v117_nmc_medieval','v118_nopss_qiaozhi','v118_njm_sixdynasties'}<=set(profile['sources'])<=sources.keys()
 corpus=profile['overview']+''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['不能只归结为一句“外族入侵”','不能把一个政权等同为单一、固定的现代民族','不是一次完成','不是法律规定的两家共治','不能当作东晋原迹'])
 assert all(term in corpus for term in ['八王之乱','十六国','白籍','土断','淝水','北府兵','420年'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V92 PASS: Jin macro reading connects fragile reunification, northern regimes, migration administration, power networks and social life')

if d['version']>=93:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='northern_southern')
 assert [section['id'] for section in profile['sections']]==['ns-parallel','ns-wei','ns-south','ns-belief','ns-reunification']
 assert len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=350
 assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=230 for section in profile['sections'])
 assert {'v53ns_songshu','v53ns_weishu','v53ns_zhoushu','v53ns_yungang','v53ns_longmen','v119_cssn_capitals','v119_cssn_beiwei','v119_nmc_buddhist','v119_nanjing_gate'}<=set(profile['sources'])<=sources.keys()
 corpus=profile['overview']+''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['同一年并没有全国一致的皇帝与年号','不能证明每户都实际足额受田','都过于简单','不能据一个门址复原整座城市','赞助者不止皇帝','不能把西魏军制直接等同成熟的唐代府兵制','不能倒推为地理或制度必然'])
 assert all(term in corpus for term in ['439年','均田','三长制','493年','六镇','侯景之乱','云冈','龙门','574年','577年','589年'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V93 PASS: Northern and Southern Dynasties macro reading connects parallel courts, Northern Wei reform, Jiankang society, religious patrons and contingent reunification')

if d['version']>=94:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='sui')
 assert [section['id'] for section in profile['sections']]==['sui-unification','sui-governance','sui-network','sui-frontier','sui-collapse']
 assert len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=350
 assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=230 for section in profile['sections'])
 assert {'v50s_suishu1','v50s_suishu4','v50s_suishu5','v50s_suishu24','v50s_suishu67','v120_unesco_canal','v120_cssn_land','v120_nmc_hanjia','v120_nopss_goguryeo'}<=set(profile['sources'])<=sources.keys()
 corpus=profile['overview']+''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['不是地图在589年瞬间变成同一种社会','不能直接等同人口突然倍增','人人足额受田不可能成立','不是某一年从北京到杭州一次挖成同一条直线','不能代表所有居民都参与同等规模的“丝路生活”','把它写成现代两个民族国家之间的战争同样失真','不是全国在同一天完成交接'])
 assert all(term in corpus for term in ['580年','589年','大索貌阅','输籍定样','义仓','584年','605年','608年','610年','612至614年','杨玄感','619年'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V94 PASS: Sui macro reading connects staged reunification, registered households, canal logistics, frontier relations and multi-centred collapse')

if d['version']>=95:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='tang')
 assert [section['id'] for section in profile['sections']]==['tang-foundation','tang-government','tang-wuzhou','tang-world','tang-transformation']
 assert len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=400
 assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=230 for section in profile['sections'])
 assert {'v43t_jts1','v43t_jts2','v43t_jts6','v43t_jts9','v43t_jts10','v43t_jts48','v43t_law_source','v43t_jts200b','v121_cssn_finance','v121_cssn_transition','v121_cssn_heshuo','v121_nmc_silkroad','v121_nopss_family'}<=set(profile['sources'])<=sources.keys()
 corpus=profile['overview']+''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['不能把建国写成太宗一人的事业','不能当作现代部委','不能直接等同现代公平考试','并不等于门第影响消失或所有女性地位普遍提高','不是街头人口统计','不能代表所有藩镇','不是一条由“盛”必然滑向“衰”的直线'])
 assert all(term in corpus for term in ['617年','628年','626年','690至705年','755至763年','780年','875年','907年','两税法','神策军','河朔三镇'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V95 PASS: Tang macro reading connects contested foundation, implemented institutions, Wu Zhou, unequal mobility and post-An Lushan transformation')

if d['version']>=96:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='five_dynasties')
 assert [section['id'] for section in profile['sections']]==['fd-polities','fd-military-state','fd-regions','fd-society','fd-transition']
 assert len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=400
 assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=230 for section in profile['sections'])
 assert {'v54_old','v54_new','v54_zztj','v54_wudaihuiyao','v122_cssn_military','v122_cssn_memory','v122_cssn_geopolitics','v122_cssn_wuyue','v122_nmc_wuyue'}<=set(profile['sources'])<=sources.keys()
 corpus=profile['overview']+''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['不是当时一套整齐的国家名单','不能机械理解为始终恰好十国并立','不能只用“武将跋扈”解释','吴越经验不能代表整个南方','不能当作全社会的生活快照','不是简单反武','“统一”必须说明范围'])
 assert all(term in corpus for term in ['907年','923年','936年','947年','951年','960年','965年','971年','975年','978年','979年','枢密院','投龙银简','北汉'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V96 PASS: Five Dynasties macro reading connects parallel states, military governance, regional economies, ordinary life and staged Song integration')

if d['version']>=97:
 fd_people={p['id'] for p in d['people'] if p.get('dynasty')=='five_dynasties'}
 fd_articles=[articles[pid] for pid in fd_people]
 legacy_phrase='生活在唐宋之间多政权并立的时期'
 for article in fd_articles:
  for section in article['sections']:
   substantial=[part.strip() for part in re.split(r'[。！？]',section['text']) if len(part.strip())>=12]
   repeated=[sentence for sentence,count in Counter(substantial).items() if count>1]
   assert not repeated,(article['person'],section['id'],'repeated substantial sentence',repeated)
  lead=next((section for section in article['sections'] if section['id'].endswith('-v54-1')),None)
  regional=next((section for section in article['sections'] if section['id'].endswith('-v54-4')),None)
  if regional:
   assert regional['title']=='把人物放回区域社会',(article['person'],'stale regional reading')
   assert len(re.findall(r'[\u4e00-\u9fff]',regional['text']))>=430,(article['person'],'regional reading too thin')
   assert legacy_phrase not in regional['text'],(article['person'],'legacy filler survived in regional reading')
   assert lead and regional['events']==lead['events'] and regional['people']==lead['people'],(article['person'],'rotated legacy relation')
 corrected={
  'fd_gu_cheng':'v123_gu_quanwu','fd_xuwen':'v123_xu_wen','fd_jing_yanguang':'v123_jing_yanguang',
  'fd_sang_weihan':'v123_sang_weihan','fd_wang_pu':'v123_wang_pu','fd_guan_tong':'v123_guan_tong','fd_he_ning':'v123_he_ning'
 }
 new_events={event['id']:event for event in d['events'] if event['id'].startswith('v123_')}
 assert set(new_events)==set(corrected.values())
 for pid,event_id in corrected.items():
  article=articles[pid]
  assert all(section['events']==[event_id] for section in article['sections'] if section['id'].startswith(pid+'-v54-')),(pid,'stale event mapping')
  assert pid in new_events[event_id]['people'] and new_events[event_id]['sources']
 if d['version']==97:
  assert '971年宋灭南汉没有直接关系' in next(section['text'] for section in articles['fd_guan_tong']['sections'] if section['id'].endswith('-v54-4'))
 print('V97 PASS: seventy-three Five Dynasties readings contain no repeated filler; rotated and seven false person-event mappings are corrected')

if d['version']>=98:
 fd_people={p['id'] for p in d['people'] if p.get('dynasty')=='five_dynasties'}
 expected_titles=['身份、时间与政权','决定发生在什么结构中','哪些材料能够作证','把人物放回区域社会','史书如何塑造人物']
 old_phrases=[
  '生活在唐宋之间多政权并立的时期','器物、城址与传世作品分别',
  '这段经历由军队、官僚、宗族','本篇以《旧五代史》《新五代史》《资治通鉴》互校'
 ]
 seen={}
 for pid in fd_people:
  article=articles[pid]
  sections=[section for section in article['sections'] if section['id'].startswith(pid+'-v54-')]
  assert [section['title'] for section in sections]==expected_titles,(pid,'legacy section order or title')
  lead_event=sections[0]['events']
  assert len(lead_event)==1,(pid,'ambiguous lead event')
  assert all(section['events']==lead_event for section in sections),(pid,'section-event drift')
  assert all(pid in section['people'] for section in sections),(pid,'subject absent from section relations')
  corpus=''.join(section['text'] for section in sections)
  assert len(re.findall(r'[\u4e00-\u9fff]',corpus))>=900,(pid,'reading below 900 Chinese characters')
  assert not any(phrase in corpus for phrase in old_phrases),(pid,'legacy template survived')
  assert not re.search(r'误接|纠正关联|没有直接人物关系',corpus),(pid,'editorial repair note leaked')
  for section in (sections[0],sections[2],sections[4]):
   for sentence in re.split(r'(?<=[。；！？])',section['text']):
    sentence=sentence.strip()
    if len(sentence)<24: continue
    assert sentence not in seen or seen[sentence]==pid,(pid,'cross-person template sentence',seen.get(sentence),sentence)
    seen[sentence]=pid
 guan=''.join(section['text'] for section in articles['fd_guan_tong']['sections'] if '-v54-' in section['id'])
 guan_sections=[section for section in articles['fd_guan_tong']['sections'] if '-v54-' in section['id']]
 assert guan_sections[1]['events']==['v123_guan_tong'] and '创作、摹写、收藏' in guan_sections[1]['text']
 assert '宋军攻入广州' not in guan and '971年宋灭南汉' not in guan
 yougui_sections=[section for section in articles['fd_yougui']['sections'] if '-v54-' in section['id']]
 assert '开封与洛阳城址' in yougui_sections[2]['text'] and '南唐山水画' not in yougui_sections[2]['text']
 assert not any(re.search(r'误接|纠正关联|没有直接人物关系',event['impact']) for event in d['events'] if event['id'].startswith('v123_'))
 print('V98 PASS: all seventy-three Five Dynasties readings use person-specific identity, mechanism, evidence and historiography layers')

if d['version']>=99:
 profile=next(profile for profile in d['dynastyProfiles'] if profile['id']=='song_liao_xia_jin')
 assert [section['id'] for section in profile['sections']]==['slxj-world','slxj-governance','slxj-networks','slxj-society','slxj-transition']
 assert len(re.findall(r'[\u4e00-\u9fff]',profile['overview']))>=450
 assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=320 for section in profile['sections'])
 required_sources={
  'v55_songshi','v55_liaoshi','v55_jinshi','v55_zztj','v125_nopss_cities',
  'v125_cssn_song_military','v125_cssn_liao_capitals','v125_nopss_liao_capitals',
  'v125_cssn_xixia_documents','v125_cssn_jin_mengan','v125_nopss_shipbuilding',
  'v125_nopss_underwater','v50y_quanzhou','v63_xixia_unesco'
 }
 assert required_sources<=set(profile['sources'])<=sources.keys()
 assert all(sources[source_id]['url'].startswith('https://') for source_id in required_sources)
 corpus=profile['overview']+''.join(section['text'] for section in profile['sections'])
 assert all(term in corpus for term in ['960年','1005年','1038年','1044年','1115年','1125年','1127年','1141年','1227年','1234年','1276年','1279年'])
 assert all(term in corpus for term in ['五京','捺钵','头下军州','天盛改旧新定律令','猛安谋克','交子','榷场','市舶','南海一号'])
 assert all(term in corpus for term in ['不能把它概括成“谁向谁屈服”','不等于辽代始终存在五个整齐行政区','不能写成全国同时进入现代纸币时代','不能代表全部乡村','不是地图颜色在某一年整齐替换'])
 assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback',corpus,re.I)
 print('V99 PASS: Song, Liao, Western Xia and Jin macro reading connects parallel courts, plural governance, exchange, ordinary lives and staged conquest')

if d['version']>=100:
 liao_ids=['s_liao_taizu','s_liao_taizong','s_liao_shizong','s_liao_muzong','s_liao_jingzong','s_liao_shengzong','s_liao_xingzong','s_liao_daozong','s_liao_tianzuo']
 liao_terms={
  's_liao_taizu':['916年','契丹大字','东丹国','耶律倍'],
  's_liao_taizong':['936年','燕云十六州','后晋','开封'],
  's_liao_shizong':['947年','述律太后','火神淀','耶律察割'],
  's_liao_muzong':['951年','后周','北宋','近侍'],
  's_liao_jingzong':['969年','萧绰','高梁河','南京道'],
  's_liao_shengzong':['982年','雍熙北伐','澶渊之盟','中京'],
  's_liao_xingzong':['1031年','关南','重熙增币','西夏'],
  's_liao_daozong':['1063年','萧观音','耶律濬','耶律乙辛'],
  's_liao_tianzuo':['1114年','海上之盟','五京','1125年'],
 }
 forbidden=['处于宋、辽、西夏、金及蒙古势力先后并立的时代','同一事件在宋、辽、夏、金材料中的称谓','这一时期不是宋朝单方面面对“边患”','本节只陈述可以落到年代','金代帝陵与迁葬历史']
 seen_titles=set()
 seen_sentences={}
 for pid in liao_ids:
  article=articles[pid]
  sections=article['sections']
  assert len(sections)==5 and all(section['id']==f'{pid}-v126-{index}' for index,section in enumerate(sections,1)),(pid,'wrong section structure')
  assert all(section['title'] not in seen_titles for section in sections),(pid,'cross-person repeated title')
  seen_titles.update(section['title'] for section in sections)
  assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=170 for section in sections),(pid,'thin section')
  corpus=''.join(section['text'] for section in sections)
  assert len(re.findall(r'[\u4e00-\u9fff]',corpus))>=900,(pid,'reading below 900 Chinese characters')
  assert all(term in corpus for term in liao_terms[pid]),(pid,'missing ruler-specific chronology or institution')
  assert not any(phrase in corpus for phrase in forbidden),(pid,'legacy template survived')
  assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback|误接|纠正关联',corpus,re.I)
  for section in sections:
   assert pid in section['people'] and len(section['events'])==1 and section['events'][0] in events,(pid,section['id'],'broken relation')
   assert len(section['sources'])>=5 and set(section['sources'])<=sources.keys(),(pid,section['id'],'broken source')
   for sentence in re.split(r'(?<=[。！？；])',section['text']):
    sentence=sentence.strip()
    if len(sentence)<30: continue
    assert sentence not in seen_sentences or seen_sentences[sentence]==pid,(pid,'cross-ruler template sentence',seen_sentences.get(sentence),sentence)
    seen_sentences[sentence]=pid
 endings={event_id:events[event_id]['body'] for event_id in [f'v55_reign_{pid}_b' for pid in liao_ids]}
 assert all('去世、被废、被俘或政权覆亡' not in body and len(re.findall(r'[\u4e00-\u9fff]',body))>=35 for body in endings.values())
 assert '火神淀' in endings['v55_reign_s_liao_shizong_b'] and '西辽' in endings['v55_reign_s_liao_tianzuo_b']
 print('V100 PASS: nine Liao rulers have person-specific chronology, institutions, material evidence, relationships and source boundaries')

if d['version']>=101:
 early_xia_ids=['s_xia_jingzong','s_xia_yizong','s_xia_huizong','s_xia_chongzong','s_xia_renzong']
 early_xia_terms={
  's_xia_jingzong':['1038年','三川口','1044年','西夏文','宁令哥'],
  's_xia_yizong':['1048年','没藏太后','没藏讹庞','1061年','榷场'],
  's_xia_huizong':['1067年','大梁太后','1081年','灵州','永乐城'],
  's_xia_chongzong':['1086年','小梁太后','1115年','1125年','感通塔碑'],
  's_xia_renzong':['1139年','科举','天盛改旧新定律令','任得敬','1193年'],
 }
 forbidden=['处于宋、辽、西夏、金及蒙古势力先后并立的时代','同一事件在宋、辽、夏、金材料中的称谓','这一时期不是宋朝单方面面对“边患”','本节只陈述可以落到年代','女真文字和国家文书']
 seen_titles=set()
 seen_sentences={}
 for pid in early_xia_ids:
  sections=articles[pid]['sections']
  assert len(sections)==5 and all(section['id']==f'{pid}-v127-{index}' for index,section in enumerate(sections,1)),(pid,'wrong section structure')
  assert all(section['title'] not in seen_titles for section in sections),(pid,'cross-person repeated title')
  seen_titles.update(section['title'] for section in sections)
  assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=170 for section in sections),(pid,'thin section')
  corpus=''.join(section['text'] for section in sections)
  assert len(re.findall(r'[\u4e00-\u9fff]',corpus))>=900,(pid,'reading below 900 Chinese characters')
  assert all(term in corpus for term in early_xia_terms[pid]),(pid,'missing ruler-specific chronology or institution')
  assert not any(phrase in corpus for phrase in forbidden),(pid,'legacy or cross-polity template survived')
  assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback|误接|纠正关联',corpus,re.I)
  for section in sections:
   assert pid in section['people'] and len(section['events'])==1 and section['events'][0] in events,(pid,section['id'],'broken relation')
   assert len(section['sources'])>=6 and set(section['sources'])<=sources.keys(),(pid,section['id'],'broken source')
   for sentence in re.split(r'(?<=[。！？；])',section['text']):
    sentence=sentence.strip()
    if len(sentence)<30: continue
    assert sentence not in seen_sentences or seen_sentences[sentence]==pid,(pid,'cross-ruler template sentence',seen_sentences.get(sentence),sentence)
    seen_sentences[sentence]=pid
 endings={event_id:events[event_id]['body'] for event_id in [f'v55_reign_{pid}_b' for pid in early_xia_ids]}
 assert all('去世、被废、被俘或政权覆亡' not in body and len(re.findall(r'[\u4e00-\u9fff]',body))>=35 for body in endings.values())
 assert '宁令哥' in endings['v55_reign_s_xia_jingzong_b'] and '两位梁太后不可混为一人' in endings['v55_reign_s_xia_huizong_b']
 print('V101 PASS: the first five Western Xia rulers have specific succession, war, institutions, social costs and evidence boundaries')

if d['version']>=102:
 late_xia_ids=['s_xia_huanzong','s_xia_xiangzong','s_xia_shenzong','s_xia_xianzong','s_xia_mozhu']
 late_xia_terms={
  's_xia_huanzong':['1193年','德行集','1205年','宋夏互市','1206年'],
  's_xia_xiangzong':['1206年','1209年','中兴府','1210年','1211年'],
  's_xia_shenzong':['1211年','十三年','蒙古','1223年','1226年'],
  's_xia_xianzong':['1223年','夏金','1226年','最后三位皇帝','金史'],
  's_xia_mozhu':['1226年','中兴府','1227年','投降','元代'],
 }
 forbidden=['处于宋、辽、西夏、金及蒙古势力先后并立的时代','同一事件在宋、辽、夏、金材料中的称谓','这一时期不是宋朝单方面面对“边患”','本节只陈述可以落到年代','去世、被废、被俘或政权覆亡']
 required_sources={'v128_cssn_xixia_historiography','v128_nxkg_chunyou','v128_xixia_protection_plan'}
 required_events={'v128_xixia_dexingji','v128_xixia_1205_conflict','v128_xixia_1209_siege','v128_xixia_jin_war','v128_xixia_mongol_coercion','v128_xixia_wartime_economy','v128_xixia_war_displacement','v128_xixia_jin_reconciliation','v128_xixia_final_campaign','v128_xixia_last_tombs','v128_xixia_final_siege'}
 assert required_sources<=sources.keys() and all(sources[source_id]['url'].startswith('https://') for source_id in required_sources)
 assert required_events<=events.keys()
 seen_titles=set()
 seen_sentences={}
 for pid in late_xia_ids:
  sections=articles[pid]['sections']
  assert len(sections)==5 and all(section['id']==f'{pid}-v128-{index}' for index,section in enumerate(sections,1)),(pid,'wrong section structure')
  assert all(section['title'] not in seen_titles for section in sections),(pid,'cross-person repeated title')
  seen_titles.update(section['title'] for section in sections)
  assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=170 for section in sections),(pid,'thin section')
  corpus=''.join(section['text'] for section in sections)
  assert len(re.findall(r'[\u4e00-\u9fff]',corpus))>=900,(pid,'reading below 900 Chinese characters')
  assert all(term in corpus for term in late_xia_terms[pid]),(pid,'missing ruler-specific chronology, institution or evidence boundary')
  assert not any(phrase in corpus for phrase in forbidden),(pid,'legacy template survived')
  assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback|误接|纠正关联',corpus,re.I)
  for section in sections:
   assert pid in section['people'] and len(section['events'])==1 and section['events'][0] in events,(pid,section['id'],'broken relation')
   assert len(section['sources'])>=6 and set(section['sources'])<=sources.keys(),(pid,section['id'],'broken source')
   for sentence in re.split(r'(?<=[。！？；])',section['text']):
    sentence=sentence.strip()
    if len(sentence)<30: continue
    assert sentence not in seen_sentences or seen_sentences[sentence]==pid,(pid,'cross-ruler template sentence',seen_sentences.get(sentence),sentence)
    seen_sentences[sentence]=pid
 endings={event_id:events[event_id]['body'] for event_id in [f'v55_reign_{pid}_b' for pid in late_xia_ids]}
 assert all('去世、被废、被俘或政权覆亡' not in body and len(re.findall(r'[\u4e00-\u9fff]',body))>=35 for body in endings.values())
 assert '太上皇' in endings['v55_reign_s_xia_shenzong_b'] and '各材料仍有分歧' in endings['v55_reign_s_xia_mozhu_b']
 assert all(not re.search(r'人物页|本轮|开发进度|占位|AI生成|fallback',events[event_id]['body'],re.I) for event_id in required_events)
 late_pairs={frozenset((association['from'],association['to'])) for association in d['associations']}
 assert not any((pair & set(late_xia_ids)) and any(person_id.startswith('s_liao_') for person_id in pair) for pair in late_pairs)
 assert frozenset(('s_xia_mozhu','y_genghis')) in late_pairs
 expected_context_people={
  's_xia_huanzong':{'s_xia_renzong','s_xia_xiangzong','y_genghis'},
  's_xia_xiangzong':{'s_xia_huanzong','s_xia_shenzong','y_genghis'},
  's_xia_shenzong':{'s_xia_xiangzong','s_xia_xianzong','s_jin_xuanzong'},
  's_xia_xianzong':{'s_xia_shenzong','s_xia_mozhu','y_genghis'},
  's_xia_mozhu':{'s_xia_xianzong','y_genghis','s_jin_aizong'},
 }
 contexts={context['person']:context for context in d['reignContexts']}
 assert all(set(contexts[pid]['people'])==expected_context_people[pid] for pid in late_xia_ids)
 assert 's_xia_xiangzong' not in contexts['s_liao_taizu']['people'] and 's_liao_shulu' in contexts['s_liao_taizu']['people']
 print('V102 PASS: the last five Western Xia rulers distinguish coups, coercive diplomacy, social costs, final conquest and source disagreement')

if d['version']>=103:
 early_jin_ids=['s_jin_taizu','s_jin_taizong','s_jin_xizong','s_jin_hailing','s_jin_shizong']
 early_jin_terms={
  's_jin_taizu':['1114年','1115年','猛安谋克','1119年','1123年'],
  's_jin_taizong':['1123年','1125年','海上之盟','1127年','1135年'],
  's_jin_xizong':['1135年','天眷','1141年','完颜希尹','1150年'],
  's_jin_hailing':['1150年','1153年','中都','四十猛安','1161年'],
  's_jin_shizong':['1161年','隆兴和议','1171年','1185年','1189年'],
 }
 forbidden=['处于宋、辽、西夏、金及蒙古势力先后并立的时代','同一事件在宋、辽、夏、金材料中的称谓','这一时期不是宋朝单方面面对“边患”','本节只陈述可以落到年代','去世、被废、被俘或政权覆亡']
 required_sources={'v129_cssn_jin_victory_stele','v129_cssn_jin_six_ministries','v129_cssn_jin_elites','v129_cssn_jin_migration','v129_cssn_shangjing_archaeology','v129_beijing_zhongdu_archaeology'}
 required_events={'v129_jin_taizu_war','v129_jin_1119_script','v129_jin_bojilie_transition','v129_jin_taizong_revenue','v129_jin_tianjuan_reform','v129_jin_xizong_song_war','v129_jin_hailing_centralization','v129_jin_zhenglong_reform','v129_jin_mengan_migration','v129_jin_1161_mutiny','v129_jin_1161_tokyo_accession','v129_jin_shizong_song_war','v129_jin_dading_governance','v129_jin_dading_education','v129_jin_mengan_livelihood'}
 assert required_sources<=sources.keys() and all(sources[source_id]['url'].startswith('https://') for source_id in required_sources)
 assert required_events<=events.keys()
 seen_titles=set()
 seen_sentences={}
 for pid in early_jin_ids:
  sections=articles[pid]['sections']
  assert len(sections)==5 and all(section['id']==f'{pid}-v129-{index}' for index,section in enumerate(sections,1)),(pid,'wrong section structure')
  assert all(section['title'] not in seen_titles for section in sections),(pid,'cross-person repeated title')
  seen_titles.update(section['title'] for section in sections)
  assert all(len(re.findall(r'[\u4e00-\u9fff]',section['text']))>=170 for section in sections),(pid,'thin section')
  corpus=''.join(section['text'] for section in sections)
  assert len(re.findall(r'[\u4e00-\u9fff]',corpus))>=900,(pid,'reading below 900 Chinese characters')
  assert all(term in corpus for term in early_jin_terms[pid]),(pid,'missing ruler-specific chronology, institution or evidence boundary')
  assert not any(phrase in corpus for phrase in forbidden),(pid,'legacy template survived')
  assert not re.search(r'本轮|补充内容|数据缺口|高标准|验收线|开发进度|AI生成|fallback|误接|纠正关联',corpus,re.I)
  for section in sections:
   assert pid in section['people'] and len(section['events'])==1 and section['events'][0] in events,(pid,section['id'],'broken relation')
   assert len(section['sources'])>=6 and set(section['sources'])<=sources.keys(),(pid,section['id'],'broken source')
   for sentence in re.split(r'(?<=[。！？；])',section['text']):
    sentence=sentence.strip()
    if len(sentence)<30: continue
    assert sentence not in seen_sentences or seen_sentences[sentence]==pid,(pid,'cross-ruler template sentence',seen_sentences.get(sentence),sentence)
    seen_sentences[sentence]=pid
 endings={event_id:events[event_id]['body'] for event_id in [f'v55_reign_{pid}_b' for pid in early_jin_ids]}
 assert all('去世、被废、被俘或政权覆亡' not in body and len(re.findall(r'[\u4e00-\u9fff]',body))>=35 for body in endings.values())
 assert '兄终弟及' in endings['v55_reign_s_jin_taizu_b'] and '扬州附近' in endings['v55_reign_s_jin_hailing_b']
 early_pairs={frozenset((association['from'],association['to'])) for association in d['associations']}
 assert frozenset(('s_jin_hailing','s_xia_zhangyuan')) not in early_pairs
 assert not any((pair&set(early_jin_ids)) and ({'s_liao_taizu','s_liao_taizong'}&pair) for pair in early_pairs)
 expected_context_people={
  's_jin_taizu':{'s_jin_taizong','s_jin_wanyanxiyin','s_liao_tianzuo'},
  's_jin_taizong':{'s_jin_taizu','s_liao_tianzuo','s_qinzong','s_jin_xizong'},
  's_jin_xizong':{'s_jin_taizong','s_jin_hailing','s_jin_wanyanxiyin','s_jin_zonghan'},
  's_jin_hailing':{'s_jin_xizong','s_jin_shizong','s_jin_zhanghao','s_yuyunwen'},
  's_jin_shizong':{'s_jin_hailing','s_jin_zhangzong','s_xiaozong','s_jin_zhanghao'},
 }
 assert all(set(contexts[pid]['people'])==expected_context_people[pid] for pid in early_jin_ids)
 assert all({events[event_id]['category'] for event_id in contexts[pid]['events']}=={'政治','军事','文化','经济','社会'} for pid in early_jin_ids)
 print('V103 PASS: the first five Jin rulers distinguish state formation, conquest, reform, migration, diplomacy and source-shaped memory')

if d['version']>=104:
 late_jin=['s_jin_zhangzong','s_jin_weishao','s_jin_xuanzong','s_jin_aizong','s_jin_modi']
 terms={'s_jin_zhangzong':['1189年','泰和','1194年','开禧北伐','1208年'],'s_jin_weishao':['1208年','1211年','野狐岭','1213年','卫绍王'],'s_jin_xuanzong':['1213年','1214年','开封','1215年','1224年'],'s_jin_aizong':['1224年','西夏','三峰山','蔡州','1234年'],'s_jin_modi':['1234年','不足一日','受位','战死','元好问']}
 req_sources={'v130_cssn_taihe_law','v130_cssn_taihe_palace','v130_cssn_taihe_legacy','v130_cssn_jin_migration','v130_cssn_kaifeng','v130_jingyuan_late_jin'}
 req_events={'v130_jin_taihe_law','v130_jin_zhangzong_fiscal','v130_jin_weishao_defense','v130_jin_weishao_court','v130_jin_south_migration','v130_jin_song_war','v130_jin_xuanzong_culture','v130_jin_aizong_diplomacy','v130_jin_kaifeng_siege','v130_jin_cai_food','v130_jin_chenglin_memory'}
 assert req_sources<=sources.keys() and req_events<=events.keys()
 seen=set()
 for pid in late_jin:
  ss=articles[pid]['sections']; assert len(ss)==5 and all(x['id']==f'{pid}-v130-{i}' for i,x in enumerate(ss,1))
  assert all(len(re.findall(r'[\u4e00-\u9fff]',x['text']))>=170 for x in ss)
  corpus=''.join(x['text'] for x in ss); assert len(re.findall(r'[\u4e00-\u9fff]',corpus))>=900 and all(t in corpus for t in terms[pid])
  assert not re.search(r'本轮|补充内容|数据缺口|开发进度|AI生成|fallback|人物页|不能写成',corpus,re.I)
  for x in ss:
   assert pid in x['people'] and len(x['events'])==1 and len(x['sources'])>=6
   assert x['title'] not in seen; seen.add(x['title'])
 endings=[events[f'v55_reign_{p}_b']['body'] for p in late_jin]
 assert all('去世、被废、被俘或政权覆亡' not in x and len(re.findall(r'[\u4e00-\u9fff]',x))>=35 for x in endings)
 pairs={frozenset((a['from'],a['to'])) for a in d['associations']}
 assert not any((pair&set(late_jin)) and ({'s_liao_taizu','s_liao_taizong'}&pair) for pair in pairs)
 assert frozenset(('s_jin_weishao','y_genghis')) in pairs
 print('V104 PASS: the last five Jin rulers separate legal florescence, Mongol invasion, southern migration, multi-front collapse and source-bounded succession')
