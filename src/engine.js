/* Pure study logic; works in the browser and in Node tests. */
(function(root,factory){const engine=factory();if(typeof module==='object'&&module.exports)module.exports=engine;else root.MowEngine=engine;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const DAY=86400000;
const intervals=[0,1,3,7,14,30];
const stages=['New','Learning','Familiar','Remembering','Confident','Mastered'];
const defaults={name:'Shane',form:'m',goal:20,roundSize:20,direction:'en-pl',quizType:'choice',strict:false,autoplay:false,bridges:true,rate:0.9,voice:''};
function normalize(text,strict=true){let s=String(text).normalize('NFC').toLocaleLowerCase('pl').replace(/’/g,"'");
 const contractions={"don't":'do not',"doesn't":'does not',"didn't":'did not',"isn't":'is not',"aren't":'are not',"wasn't":'was not',"weren't":'were not',"can't":'cannot',"won't":'will not',"couldn't":'could not',"wouldn't":'would not',"shouldn't":'should not',"haven't":'have not',"hasn't":'has not',"hadn't":'had not',"i'm":'i am',"you're":'you are',"we're":'we are',"they're":'they are',"it's":'it is',"he's":'he is',"she's":'she is',"that's":'that is',"what's":'what is',"i've":'i have',"you've":'you have',"we've":'we have',"they've":'they have',"i'll":'i will',"you'll":'you will',"we'll":'we will',"they'll":'they will'};
 s=s.replace(/\b[a-z]+'[a-z]+\b/g,w=>contractions[w]||w).replace(/\bcan not\b/g,'cannot').replace(/[.,!?;:…"“”„'’()\[\]{}\/–—-]/g,' ').replace(/\s+/g,' ').trim();if(!strict)s=s.replace(/ł/g,'l').normalize('NFD').replace(/[\u0300-\u036f]/g,'');return s;}
function matchAnswer(input,answers,strict=true){const list=Array.isArray(answers)?answers:[answers];const exact=list.some(a=>normalize(input,true)===normalize(a,true));const folded=list.some(a=>normalize(input,false)===normalize(a,false));return {correct:exact||(!strict&&folded),accentWarning:!exact&&!strict&&folded};}
function polish(card,settings={}){return ((settings.form==='f'&&card.f)?card.f:card.pl).replaceAll('{name}',settings.name||'Shane');}
function english(card,settings={}){return card.en.replaceAll('{name}',settings.name||'Shane');}
function acceptedAnswers(card,side='pl',settings={}){
 if(side==='pl')return [polish(card,settings),...(card.alts||[]).map(a=>a.replaceAll('{name}',settings.name||'Shane'))];
 const original=english(card,settings),plain=original.replace(/\s*\([^)]*\)/g,'').trim(),out=new Set([original,plain]);
 for(const item of plain.split('/')){const value=item.trim();if(value){out.add(value);if(/^(a|an|the)\s+/i.test(value))out.add(value.replace(/^(a|an|the)\s+/i,''));}}
 return [...out];
}
function shuffle(items,rng=Math.random){let out=[...items];for(let i=out.length-1;i>0;i--){let j=Math.floor(rng()*(i+1));[out[i],out[j]]=[out[j],out[i]];}return out;}
function review(old,grade,now=Date.now()){
 if(!['again','hard','good','easy'].includes(grade))throw new Error('Unknown review grade.');
 let p=old?{...old}:{stage:0,due:0,reviews:0,lapses:0,last:0};
 const eligible=!old||p.due<=now;
 if(grade==='again'){p.stage=Math.max(1,p.stage-1);p.due=now+600000;p.lapses=(p.lapses||0)+1;}
 else if(eligible){
  if(grade==='hard'){p.stage=Math.max(1,p.stage);p.due=now+6*3600000;}
  else{p.stage=Math.min(5,p.stage+1);p.due=now+intervals[p.stage]*DAY*(grade==='easy'?1.5:1);}
 }
 p.reviews=(p.reviews||0)+1;p.last=now;return p;
}
function queue(cards,progress,limit=20,srs=true,now=Date.now()){
 let due=cards.filter(c=>progress[c.id]&&progress[c.id].due<=now).sort((a,b)=>progress[a.id].due-progress[b.id].due);
 let unseen=cards.filter(c=>!progress[c.id]);
 if(srs)return [...due,...unseen].slice(0,limit);
 return shuffle(cards).slice(0,limit);
}
function choices(card,pool,side='pl',settings={},count=4){
 const textOf=c=>side==='pl'?polish(c,settings):english(c,settings);
 const answer=textOf(card),used=new Set([normalize(answer)]);
 if(side==='pl')for(const a of card.alts||[])used.add(normalize(a));
 const options=[{id:card.id,text:answer,correct:true}];
 const local=shuffle(pool.filter(c=>c.cat===card.cat&&c.id!==card.id));
 const other=shuffle(pool.filter(c=>c.cat!==card.cat&&c.id!==card.id));
 for(const c of [...local,...other]){const text=textOf(c),key=normalize(text);if(used.has(key))continue;
  if(side==='pl'&&(c.alts||[]).some(a=>normalize(a)===normalize(answer)))continue;
  used.add(key);options.push({id:c.id,text,correct:false});if(options.length>=count)break;
 }
 return shuffle(options);
}
function dayKey(date=new Date()){return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;}
function streak(activity,date=new Date()){
 let d=new Date(date.getFullYear(),date.getMonth(),date.getDate(),12),count=0;
 if(!(activity[dayKey(d)]?.reviews>0))d.setDate(d.getDate()-1);
 for(let i=0;i<36500;i++){if(!(activity[dayKey(d)]?.reviews>0))break;count++;d.setDate(d.getDate()-1);}return count;
}
function freshState(){return {settings:{...defaults},progress:{},activity:{},xp:0,stars:[],custom:[]};}
function backup(state){return {app:'mow-polish',version:1,exportedAt:new Date().toISOString(),state:JSON.parse(JSON.stringify(state))};}
function validateBackup(input,builtInIds=[]){
 const fail=()=>{throw new Error('This is not a valid Mów Polish backup. No data was changed.');};
 const obj=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
 const int=(v,min,max)=>Number.isSafeInteger(v)&&v>=min&&v<=max;
 const text=(v,max)=>typeof v==='string'&&v.length<=max;
 if(!obj(input)||input.app!=='mow-polish'||input.version!==1||!obj(input.state))fail();
 const s=input.state,base=freshState(),ids=new Set(builtInIds);
 if(!obj(s.settings)||!obj(s.progress)||!obj(s.activity)||!Array.isArray(s.stars)||!Array.isArray(s.custom)||!int(s.xp,0,1e9))fail();
 const st=s.settings;
 if(!text(st.name,40)||!st.name.trim()||!['m','f'].includes(st.form)||![10,20,30,40,50].includes(st.goal)||![10,20,30,40].includes(st.roundSize)||!['en-pl','pl-en'].includes(st.direction)||!['choice','type'].includes(st.quizType)||!Number.isFinite(st.rate)||st.rate<0.5||st.rate>1.2||!text(st.voice,200))fail();
 for(const key of ['strict','autoplay','bridges'])if(typeof st[key]!=='boolean')fail();
 base.settings=Object.fromEntries(Object.keys(defaults).map(k=>[k,st[k]]));
 if(s.custom.length>1000)fail();
 for(const c of s.custom){if(!obj(c)||!text(c.id,80)||!/^custom-[a-zA-Z0-9-]+$/.test(c.id)||ids.has(c.id)||c.cat!=='custom'||!text(c.en,300)||!text(c.pl,300)||!c.en.trim()||!c.pl.trim()||!text(c.note,1000))fail();ids.add(c.id);base.custom.push({id:c.id,cat:'custom',en:c.en,pl:c.pl,note:c.note});}
 if(Object.keys(s.progress).length>ids.size)fail();
 for(const [id,p] of Object.entries(s.progress)){
  if(!ids.has(id)||['__proto__','constructor','prototype'].includes(id)||!obj(p)||!int(p.stage,1,5)||!int(p.due,0,8640000000000000)||!int(p.reviews,1,1e8)||!int(p.lapses,0,p.reviews)||(p.last!==undefined&&!int(p.last,0,8640000000000000)))fail();
  base.progress[id]={stage:p.stage,due:p.due,reviews:p.reviews,lapses:p.lapses,last:p.last||0};
 }
 if(s.stars.length>ids.size||new Set(s.stars).size!==s.stars.length||s.stars.some(id=>!ids.has(id)))fail();base.stars=[...s.stars];
 if(Object.keys(s.activity).length>36500)fail();
 for(const [key,a] of Object.entries(s.activity)){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(key)||!obj(a)||!int(a.reviews,0,1e7)||!int(a.correct,0,a.reviews)||!int(a.xp,0,1e9))fail();
  const date=new Date(key+'T12:00:00');if(Number.isNaN(date.getTime())||dayKey(date)!==key)fail();
  base.activity[key]={reviews:a.reviews,correct:a.correct,xp:a.xp};
 }
 base.xp=s.xp;return base;
}
return {DAY,intervals,stages,defaults,normalize,matchAnswer,polish,english,acceptedAnswers,shuffle,review,queue,choices,dayKey,streak,freshState,backup,validateBackup};
});
