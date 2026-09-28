from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'Mow_Polish.html').read_text()
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    page.on('pageerror',lambda e:print('ERROR:',e))
    page.evaluate("""window.testStore={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>window.testStore[k]??null,setItem:(k,v)=>window.testStore[k]=String(v),removeItem:k=>delete window.testStore[k]},configurable:true});""")
    page.set_content(html,wait_until='domcontentloaded')
    print('TITLE',page.title(),'DECKS',page.locator('.deck-card').count())
    page.screenshot(path=str(ROOT/'docs'/'preview-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(ROOT/'docs'/'preview-mobile.png'),full_page=True)
    print('mobile width',page.evaluate('document.documentElement.scrollWidth'), 'viewport',390)
    browser.close()
