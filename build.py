"""Produce a zero-dependency standalone HTML and optional static-host/PWA files."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'src'
html=(SRC/'shell.html').read_text()
for key,name in [('STYLES','styles.css'),('DATA','data.js'),('ENGINE','engine.js'),('APP','app.js')]:
    html=html.replace('/*'+key+'*/',(SRC/name).read_text())
standalone=html.replace('<!--PWA-->','').replace('<!--WORKER-->','')
(ROOT/'Mow_Polish.html').write_text(standalone)
pwa=html.replace('<!--PWA-->','<link rel="manifest" href="./manifest.webmanifest"><link rel="icon" href="./icon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="./icon-192.png">').replace('<!--WORKER-->','''<script>
if ('serviceWorker' in navigator && window.isSecureContext && /^https?:$/.test(location.protocol)) {
  window.addEventListener('load', () => navigator.serviceWorker.register('./sw.js').catch(() => {}));
}
</script>''')
(ROOT/'index.html').write_text(pwa)
manifest={'id':'./','name':'Mów — Polish Conversation Trainer','short_name':'Mów','description':'Everyday Polish, one conversation at a time.','start_url':'./index.html','scope':'./','display':'standalone','display_override':['standalone','minimal-ui'],'orientation':'any','background_color':'#101114','theme_color':'#101114','lang':'en','icons':[{'src':'./icon-192.png','sizes':'192x192','type':'image/png','purpose':'any maskable'},{'src':'./icon-512.png','sizes':'512x512','type':'image/png','purpose':'any maskable'}]}
(ROOT/'manifest.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(ROOT/'sw.js').write_text('''const CACHE='mow-polish-v1.1.0-ios';
const ASSETS=['./','./index.html','./manifest.webmanifest','./icon.svg','./icon-192.png','./icon-512.png'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('mow-polish-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',event=>{
 if(event.request.method!=='GET'||new URL(event.request.url).origin!==self.location.origin)return;
 if(event.request.mode==='navigate'){
  event.respondWith(fetch(event.request).then(response=>{
    if(response.ok){const copy=response.clone();event.waitUntil(caches.open(CACHE).then(cache=>cache.put('./index.html',copy)));}
    return response;
  }).catch(()=>caches.match('./index.html')));
 }else event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request)));
});
''')
# A geometric app mark, with no bundled font files or external assets.
svg='''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512"><rect width="512" height="512" rx="112" fill="#16171c"/><rect x="78" y="78" width="356" height="356" rx="80" fill="#262219" stroke="#665036" stroke-width="3"/><g fill="#e8b974" transform="translate(0 0) skewY(-10)"><rect x="157" y="213" width="48" height="152" rx="22"/><rect x="232" y="183" width="48" height="211" rx="22"/><rect x="307" y="239" width="48" height="152" rx="22"/></g></svg>'''
(ROOT/'icon.svg').write_text(svg)
try:
    import cairosvg
    for size in (192,512):cairosvg.svg2png(bytestring=svg.encode(),write_to=str(ROOT/f'icon-{size}.png'),output_width=size,output_height=size)
except ImportError:
    from PIL import Image,ImageDraw
    for size in (192,512):
        im=Image.new('RGB',(size,size),'#16171c');d=ImageDraw.Draw(im);s=size/512
        for x,y,h in ((157,170,152),(232,125,211),(307,160,152)):
            d.rounded_rectangle((int(x*s),int(y*s),int((x+48)*s),int((y+h)*s)),radius=int(22*s),fill='#e8b974')
        im.save(ROOT/f'icon-{size}.png')
print('Built',ROOT/'Mow_Polish.html',f'({len(standalone.encode()):,} bytes)')
print('Built',ROOT/'index.html')
