"""Chromium DOM acceptance tests of the built standalone app.

This environment prohibits URL navigation. The unchanged HTML is loaded with
set_content. Tests that need persistence use a clearly identified in-memory
localStorage boundary; this does NOT verify native file/host storage or Safari.
No browser security/administrator policy is changed.
"""
import json, sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'Mow_Polish.html').read_text()
KEY='mow-polish-v1'
results=[]
errors=[]


def nav(page, view):
    desktop=page.locator(f'#desktop-nav [data-view="{view}"]')
    (desktop if desktop.is_visible() else page.locator(f'#mobile-nav [data-view="{view}"]')).click()


def begin(page,mode='flash',cat='greetings',size='10',direction='en-pl',kind='choice'):
    page.locator(f'[data-action="setup"][data-mode="{mode}"]').first.click()
    page.locator('#setup-category').select_option(cat)
    page.locator('#setup-size').select_option(size)
    page.locator('#setup-direction').select_option(direction)
    if mode=='quiz': page.locator('#setup-type').select_option(kind)
    page.locator('#begin-session').click()


def saved(page):
    return page.evaluate("JSON.parse(localStorage.getItem('mow-polish-v1')).state")


def current(page, selector='.quiz-prompt h2', side='en'):
    prompt=page.locator(selector).inner_text()
    return page.evaluate("""([text,side])=>{const s=JSON.parse(localStorage.getItem('mow-polish-v1')).state;
    return [...MowData.cards,...s.custom].find(c=>(side==='en'?MowEngine.english(c,s.settings):MowEngine.polish(c,s.settings))===text);}""",[prompt,side])


def newpage(browser,store=None,width=1440,storage=True):
    page=browser.new_page(viewport={'width':width,'height':1000 if width>720 else 844})
    page.set_default_timeout(4000)
    page.on('pageerror',lambda e:errors.append(str(e)))
    if storage:
        page.evaluate("""store=>{window.testStore=store;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>window.testStore[k]??null,setItem:(k,v)=>window.testStore[k]=String(v),removeItem:k=>delete window.testStore[k]}});} """,store or {})
    page.set_content(HTML,wait_until='domcontentloaded')
    return page


def check(name,fn):
    try:
        fn();results.append({'test':name,'passed':True});print('PASS',name,flush=True)
    except Exception as e:
        results.append({'test':name,'passed':False,'error':str(e)});print('FAIL',name,str(e)[:800],flush=True)


def seeded(browser,mutate):
    p=newpage(browser)
    envelope=p.evaluate("MowEngine.backup(MowEngine.freshState())")
    mutate(envelope['state'],p)
    p.close()
    return newpage(browser,{KEY:json.dumps(envelope,ensure_ascii=False)})


def dashboard(browser):
    p=newpage(browser)
    expect(p.locator('h1')).to_contain_text('Polski')
    expect(p.locator('.deck-card')).to_have_count(16)
    expect(p.locator('.mini-stats strong')).to_have_text(['0','0','0'])
    assert '320' in p.locator('#page').inner_text()
    assert p.evaluate('localStorage.getItem("mow-polish-v1")') is None
    for group,n in [('Start talking',4),('Everyday life',6),('Keep it going',4),('A little further',2),('All topics',16)]:
        p.locator(f'[data-action="topic-filter"][data-filter="{group}"]').click()
        expect(p.locator('.deck-card')).to_have_count(n)
    p.screenshot(path=str(ROOT/'docs'/'preview-desktop.png'),full_page=True)
    p.screenshot(path=str(ROOT/'docs'/'preview-desktop-viewport.png'))
    p.close()


def setup_boundaries(browser):
    p=newpage(browser)
    p.locator('[data-action="setup"][data-mode="flash"]').first.click()
    expect(p.locator('#modal')).to_be_visible()
    p.locator('#setup-category').select_option('saved')
    expect(p.locator('#begin-session')).to_be_disabled()
    p.locator('#setup-category').select_option('greetings')
    p.locator('#setup-size').select_option('40')
    expect(p.locator('#setup-info')).to_contain_text('20')
    expect(p.locator('#begin-session')).to_be_enabled()
    p.keyboard.press('Escape')
    expect(p.locator('#modal')).not_to_be_visible()
    p.locator('.deck-card[data-id="home"]').click()
    p.locator('[data-action="browse-deck"]').click()
    expect(p.locator('#library-category')).to_have_value('home')
    expect(p.locator('.phrase-row')).to_have_count(20)
    p.close()


def flash_round(browser):
    p=newpage(browser)
    begin(p)
    seen=set()
    for i in range(10):
        expect(p.locator('[data-action="rate"]')).to_have_count(0)
        c=current(p,'.prompt');assert c['id'] not in seen;seen.add(c['id'])
        p.locator('[data-action="reveal"]').click()
        expect(p.locator('.flash-answer')).to_have_text(c['pl'].replace('{name}','Shane'))
        expect(p.locator('[data-action="rate"]')).to_have_count(4)
        expect(p.locator('[data-grade="good"] small')).to_have_text('1 day')
        expect(p.locator('[data-slow="true"]')).to_have_text('Slow')
        if i==0:p.screenshot(path=str(ROOT/'docs'/'preview-flashcards.png'))
        p.locator('[data-action="rate"][data-grade="good"]').click()
    expect(p.locator('.recap h1')).to_contain_text('Dobra robota')
    expect(p.locator('.recap-stats strong')).to_have_text(['100%','+100','10'])
    s=saved(p);assert len(s['progress'])==10 and s['xp']==100
    assert all(v['stage']==1 and v['reviews']==1 for v in s['progress'].values())
    p.close()


def exit_round_and_keyboard(browser):
    p=newpage(browser)
    begin(p,'srs')
    p.locator('.prompt').click()
    p.keyboard.press('Space')
    expect(p.locator('.flash-answer')).to_be_visible()
    p.keyboard.press('3')
    assert len(saved(p)['progress'])==1
    p.locator('[data-action="exit-session"]').click()
    expect(p.locator('#modal')).to_contain_text('Leave this round?')
    p.locator('[data-action="close-modal"]').first.click()
    expect(p.locator('.prompt')).to_be_visible()
    p.locator('[data-action="exit-session"]').click()
    p.locator('[data-action="leave-session"]').click()
    expect(p.locator('h1')).to_contain_text('Polski')
    assert len(saved(p)['progress'])==1
    p.close()


def srs_due_and_early(browser):
    def seed(s,p):
        now=p.evaluate('Date.now()')
        ids=p.evaluate("MowData.cards.filter(c=>c.cat==='greetings').map(c=>c.id)")
        for i,cid in enumerate(ids):s['progress'][cid]={'stage':2,'reviews':2,'lapses':0,'due':now+(3600000 if i else -1000),'last':now-86400000}
    p=seeded(browser,seed)
    begin(p,'srs')
    c=current(p,'.prompt');first_id=c['id']
    p.locator('[data-action="reveal"]').click();p.locator('[data-grade="good"]').click()
    expect(p.locator('.recap')).to_be_visible()
    assert saved(p)['progress'][first_id]['stage']==3
    nav(p,'learn')
    begin(p,'flash')
    c=current(p,'.prompt');old=saved(p)['progress'][c['id']]
    p.locator('[data-action="reveal"]').click();p.locator('[data-grade="good"]').click()
    after=saved(p)['progress'][c['id']]
    assert after['stage']==old['stage'] and after['due']==old['due']
    p.close()


def choice_quiz(browser):
    p=newpage(browser);begin(p,'quiz')
    seen=set()
    for i in range(10):
        c=current(p);assert c['id'] not in seen;seen.add(c['id'])
        labels=p.locator('.option-label').all_inner_texts()
        assert len(labels)==4 and len(set(labels))==4
        idx=labels.index(c['pl'])
        if i==1:idx=(idx+1)%4
        p.locator('[data-action="quiz-choice"]').nth(idx).click()
        expect(p.locator('[data-action="quiz-choice"]:enabled')).to_have_count(0)
        expect(p.locator('.feedback')).to_be_visible()
        if i==1:
            expect(p.locator('.feedback.wrong')).to_be_visible()
            assert saved(p)['progress'][c['id']]['lapses']==1
        if i==0:p.screenshot(path=str(ROOT/'docs'/'preview-quiz.png'))
        p.locator('[data-action="next-card"]').click()
    expect(p.locator('.recap-stats strong').first).to_have_text('90%')
    assert saved(p)['xp']==92
    expect(p.locator('.recap-review .phrase-row')).to_have_count(1)
    p.close()


def typed_quiz(browser):
    p=newpage(browser);begin(p,'quiz',kind='type')
    expect(p.locator('.diacritics button')).to_have_count(9)
    p.locator('#typed-form [type="submit"]').click()
    assert saved(p)['progress']=={}
    p.locator('[data-letter="ą"]').click()
    expect(p.locator('#typed-answer')).to_have_value('ą')
    c=current(p)
    value=p.evaluate('(text)=>MowEngine.normalize(text,false)',c['pl'])
    p.locator('#typed-answer').fill(value)
    p.locator('#typed-answer').press('Enter')
    expect(p.locator('.feedback:not(.wrong)')).to_be_visible()
    p.locator('[data-action="next-card"]').click()
    p.locator('[data-action="quiz-reveal"]').click()
    expect(p.locator('.feedback.wrong')).to_be_visible()
    assert len(saved(p)['progress'])==2
    p.close()


def english_typing(browser):
    p=newpage(browser);begin(p,'quiz',direction='pl-en',kind='type')
    expect(p.locator('.diacritics button')).to_have_count(0)
    for i in range(10):
        c=current(p,side='pl')
        a=p.evaluate('(c)=>MowEngine.acceptedAnswers(c,"en",{})',c)
        # Use the most stripped alternative rather than the full teaching label.
        p.locator('#typed-answer').fill(a[-1])
        p.locator('#typed-form [type="submit"]').click()
        expect(p.locator('.feedback:not(.wrong)')).to_be_visible()
        p.locator('[data-action="next-card"]').click()
    expect(p.locator('.recap-stats strong').first).to_have_text('100%')
    p.close()


def strict_typed(browser):
    def seed(s,p):
        s['settings']['strict']=True
        s['custom']=[{'id':'custom-strict-test','cat':'custom','en':'Thank you.','pl':'Dziękuję.','note':''}]
    p=seeded(browser,seed);begin(p,'quiz',cat='custom',kind='type')
    p.locator('#typed-answer').fill('Dziekuje');p.locator('#typed-form [type="submit"]').click()
    expect(p.locator('.feedback.wrong')).to_be_visible()
    p.close()


def search_and_bookmark(browser):
    p=newpage(browser);nav(p,'cards')
    expect(p.locator('.phrase-row')).to_have_count(40)
    p.locator('[data-action="load-more"]').click()
    expect(p.locator('.phrase-row')).to_have_count(80)
    p.locator('#phrase-search').fill('samochodu')
    expect(p.locator('.phrase-row')).to_have_count(1)
    expect(p.locator('.phrase-row')).to_contain_text('Nie mam samochodu')
    p.locator('#library-results [data-action="star"]').click()
    expect(p.locator('[data-filter="saved"]')).to_have_text('Saved · 1')
    p.locator('[data-action="card-detail"]').click()
    expect(p.locator('#modal')).to_contain_text('genitive')
    p.keyboard.press('Escape')
    p.locator('#phrase-search').fill('')
    p.locator('[data-filter="saved"]').click()
    expect(p.locator('.phrase-row')).to_have_count(1)
    p.locator('#library-results [data-action="star"]').click()
    expect(p.locator('[data-filter="saved"]')).to_have_text('Saved · 0')
    expect(p.locator('.phrase-row')).to_have_count(0)
    p.locator('[data-filter="all"]').click()
    p.locator('#phrase-search').fill('ucze sie polskiego')
    expect(p.locator('.phrase-row')).to_have_count(1)
    p.close()


def settings_and_reload(browser):
    p=newpage(browser);nav(p,'settings')
    p.locator('#setting-name').fill('Marta');p.locator('#setting-name').press('Tab')
    p.locator('#setting-form').select_option('f')
    p.locator('#setting-goal').select_option('40')
    p.locator('#setting-roundSize').select_option('30')
    p.locator('#setting-strict').check()
    p.locator('#setting-bridges').uncheck()
    p.locator('#setting-quizType').select_option('type')
    p.locator('#setting-direction').select_option('pl-en')
    s=saved(p)['settings']
    assert s['name']=='Marta' and s['form']=='f' and s['goal']==40 and s['strict'] and not s['bridges']
    nav(p,'cards');p.locator('#phrase-search').fill('Mam na imię')
    expect(p.locator('.phrase-row')).to_contain_text('Marta')
    p.locator('#phrase-search').fill('początkująca')
    expect(p.locator('.phrase-row')).to_have_count(1)
    store=p.evaluate('window.testStore');p.close()
    p=newpage(browser,store);nav(p,'settings')
    expect(p.locator('#setting-name')).to_have_value('Marta')
    expect(p.locator('#setting-form')).to_have_value('f')
    expect(p.locator('#setting-strict')).to_be_checked()
    expect(p.locator('#setting-direction')).to_have_value('pl-en')
    p.close()


def custom_card_lifecycle(browser):
    p=newpage(browser);nav(p,'cards')
    p.locator('[data-action="add-card"]').click()
    malicious='<img src=x onerror="window.injected=true">'
    p.locator('#custom-en').fill('A test phrase.')
    p.locator('#custom-pl').fill('Moje zdanie.')
    p.locator('#custom-note').fill(malicious)
    p.locator('#custom-form [type="submit"]').click()
    expect(p.locator('.phrase-row')).to_have_count(1)
    s=saved(p);assert len(s['custom'])==1
    cid=s['custom'][0]['id']
    p.locator('[data-action="card-detail"]').click()
    expect(p.locator('#modal')).to_contain_text(malicious)
    assert p.evaluate('window.injected') is None
    assert p.locator('#modal img').count()==0
    p.locator('[data-action="edit-card"]').click()
    p.locator('#custom-pl').fill('To moje zdanie.')
    p.locator('#custom-form [type="submit"]').click()
    assert saved(p)['custom'][0]['pl']=='To moje zdanie.'
    nav(p,'learn');expect(p.locator('.deck-card')).to_have_count(17)
    begin(p,'flash',cat='custom')
    p.locator('[data-action="reveal"]').click();p.locator('[data-grade="good"]').click()
    expect(p.locator('.recap')).to_be_visible()
    assert saved(p)['progress'][cid]['stage']==1
    nav(p,'cards');p.locator('[data-filter="custom"]').click()
    p.locator('[data-action="card-detail"]').click();p.locator('[data-action="edit-card"]').click()
    p.locator('#custom-en').fill('My revised sentence.')
    p.locator('#custom-form [type="submit"]').click()
    assert cid not in saved(p)['progress']
    p.locator('[data-action="card-detail"]').click();p.locator('[data-action="edit-card"]').click()
    p.locator('[data-action="delete-card-confirm"]').click();p.locator('[data-action="delete-card"]').click()
    assert saved(p)['custom']==[]
    p.close()


def backup_import_export(browser):
    p=newpage(browser);nav(p,'settings')
    p.locator('#setting-name').fill('Backup Name');p.locator('#setting-name').press('Tab')
    # Capture the exact download Blob, not an external download/navigation.
    p.evaluate("""window.capture=null;const create=URL.createObjectURL.bind(URL);URL.createObjectURL=b=>{window.capture=b;return create(b);};document.addEventListener('click',e=>{if(e.target.closest('a[download]'))e.preventDefault();},true);""")
    p.locator('[data-action="export"]').click()
    blob=p.evaluate('async()=>JSON.parse(await window.capture.text())')
    assert blob['app']=='mow-polish' and blob['state']['settings']['name']=='Backup Name'
    blob['state']['settings']['name']='Restored Name'
    p.locator('#import-file').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':json.dumps(blob).encode()})
    expect(p.locator('#modal')).to_contain_text('Restore this backup?')
    assert saved(p)['settings']['name']=='Backup Name'
    p.keyboard.press('Escape')
    assert saved(p)['settings']['name']=='Backup Name'
    p.locator('#import-file').set_input_files({'name':'backup2.json','mimeType':'application/json','buffer':json.dumps(blob).encode()})
    p.locator('[data-action="confirm-import"]').click()
    assert saved(p)['settings']['name']=='Restored Name'
    before=saved(p)
    p.locator('#import-file').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{"state":{}}'})
    expect(p.locator('#toast')).to_contain_text('not a valid')
    assert saved(p)==before
    p.close()


def reset_progress(browser):
    def seed(s,p):
        cid=p.evaluate('MowData.cards[0].id');now=p.evaluate('Date.now()')
        s['stars']=[cid];s['settings']['name']='Still here';s['xp']=100
        s['custom']=[{'id':'custom-keep','cat':'custom','en':'Hello','pl':'Hej','note':''}]
        s['progress'][cid]={'stage':2,'reviews':2,'lapses':0,'due':now+1000,'last':now}
    p=seeded(browser,seed);nav(p,'settings')
    p.locator('[data-action="reset-confirm"]').click()
    expect(p.locator('#reset-button')).to_be_disabled()
    p.locator('#reset-word').fill('reset')
    expect(p.locator('#reset-button')).to_be_disabled()
    p.locator('#reset-word').fill('RESET');p.locator('#reset-button').click()
    s=saved(p);assert not s['progress'] and not s['activity'] and s['xp']==0
    assert len(s['stars'])==1 and len(s['custom'])==1 and s['settings']['name']=='Still here'
    p.close()


def storage_failure(browser):
    p=newpage(browser,storage=False)
    expect(p.locator('#storage-warning')).to_be_visible()
    expect(p.locator('.deck-card')).to_have_count(16)
    begin(p)
    p.locator('[data-action="reveal"]').click();p.locator('[data-grade="good"]').click()
    expect(p.locator('#storage-warning')).to_contain_text('could not save')
    p.close()


def corrupt_storage(browser):
    raw='{malformed'
    p=newpage(browser,{KEY:raw})
    expect(p.locator('#storage-warning')).to_contain_text('not been overwritten')
    nav(p,'settings');expect(p.locator('[data-action="export-corrupt"]')).to_be_visible()
    p.locator('#setting-name').fill('Ignored until reset');p.locator('#setting-name').press('Tab')
    assert p.evaluate('localStorage.getItem("mow-polish-v1")')==raw
    p.close()


def pronunciation_audio(browser):
    p=newpage(browser);nav(p,'sounds')
    expect(p.locator('.sound-card')).to_have_count(6)
    assert p.evaluate('speechSynthesis.getVoices().filter(v=>/^pl/i.test(v.lang)).length')==0
    p.locator('[data-action="speak-text"]').first.click()
    expect(p.locator('#modal')).to_be_visible()
    expect(p.locator('#modal')).to_contain_text('Polish voice')
    p.keyboard.press('Escape')
    # Explicitly simulated platform voice boundary: verify language and rates.
    p.evaluate("""window.spoken=[];window.SpeechSynthesisUtterance=class {constructor(text){this.text=text;}};speechSynthesis.getVoices=()=>[{name:'Test Polish',lang:'pl-PL',localService:true}];speechSynthesis.speak=u=>window.spoken.push({text:u.text,lang:u.lang,rate:u.rate});speechSynthesis.cancel=()=>{};""")
    p.locator('[data-action="speak-text"]').first.click()
    spoken=p.evaluate('window.spoken')
    assert len(spoken)==1 and spoken[0]['lang']=='pl-PL' and spoken[0]['rate']==.9
    nav(p,'learn');begin(p)
    p.locator('[data-action="speak"][data-slow="true"]').click()
    assert p.evaluate('window.spoken.at(-1).rate')==.65
    p.close()


def progress_page(browser):
    def seed(s,p):
        cid=p.evaluate('MowData.cards[0].id');now=p.evaluate('Date.now()');key=p.evaluate('MowEngine.dayKey()')
        s['progress'][cid]={'stage':5,'reviews':5,'lapses':0,'due':now+86400000,'last':now}
        s['activity'][key]={'reviews':20,'correct':18,'xp':180};s['xp']=180
    p=seeded(browser,seed);nav(p,'progress')
    text=p.locator('#page').inner_text()
    assert '180' in text and '20' in text and 'Mastered' in text
    p.screenshot(path=str(ROOT/'docs'/'preview-progress.png'))
    p.close()


def mobile_layouts(browser):
    p=newpage(browser,width=390)
    for width in [320,360,390,430,768,1024,1440]:
        p.set_viewport_size({'width':width,'height':844})
        for view in ['learn','cards','sounds','progress','settings']:
            nav(p,view)
            size=p.evaluate('({scroll:document.documentElement.scrollWidth,width:innerWidth})')
            assert size['scroll']<=size['width'],(width,view,size)
            if width==390 and view=='learn':
                p.screenshot(path=str(ROOT/'docs'/'preview-mobile.png'),full_page=True)
                p.screenshot(path=str(ROOT/'docs'/'preview-mobile-viewport.png'))
        nav(p,'learn');begin(p,'quiz',kind='type')
        size=p.evaluate('({scroll:document.documentElement.scrollWidth,width:innerWidth})')
        assert size['scroll']<=size['width'],(width,'study',size)
        if width==390:p.screenshot(path=str(ROOT/'docs'/'preview-mobile-quiz.png'))
        p.locator('[data-action="exit-session"]').click();p.locator('[data-action="leave-session"]').click()
    p.close()


if __name__=='__main__':
 with sync_playwright() as play:
    browser=play.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    checks=[
      ('fresh dashboard, true zero progress and topic groups',dashboard),
      ('setup limits, empty saved deck and deck browsing',setup_boundaries),
      ('10-card flashcard round, unique cards and grading',flash_round),
      ('keyboard flashcards and safe early exit',exit_round_and_keyboard),
      ('SRS due ordering, short round and no early stage inflation',srs_due_and_early),
      ('10-question multiple-choice quiz and missed-card recap',choice_quiz),
      ('typed Polish, empty input, letter toolbar and reveal',typed_quiz),
      ('10-question English recognition with natural short answers',english_typing),
      ('strict Polish spelling rejects missing diacritics',strict_typed),
      ('phrase search, pagination and live saved counts',search_and_bookmark),
      ('settings, feminine forms, name and simulated reload',settings_and_reload),
      ('custom phrase create, escaping, study, edit and delete',custom_card_lifecycle),
      ('backup Blob, cancel restore, restore and invalid rejection',backup_import_export),
      ('destructive reset guard preserves personal phrases',reset_progress),
      ('unavailable native storage remains usable and warns',storage_failure),
      ('corrupt save is preserved until explicit recovery',corrupt_storage),
      ('pronunciation guide, missing voice and simulated speech parameters',pronunciation_audio),
      ('progress dashboard from stored history',progress_page),
      ('responsive pages and study at seven viewport widths',mobile_layouts)
    ]
    for name,fn in checks:check(name,lambda fn=fn:fn(browser))
    check('no uncaught JavaScript errors',lambda:(_ for _ in ()).throw(AssertionError(errors)) if errors else None)
    report={'environment':'System Chromium, set_content; explicit in-memory storage for persistence tests. Not Safari/native-origin/PWA validation.','results':results,'javascript_errors':errors}
    (ROOT/'docs'/'BROWSER_TESTS.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    browser.close()
 print(f"{sum(r['passed'] for r in results)}/{len(results)} browser acceptance checks passed")
 if any(not r['passed'] for r in results):sys.exit(1)
