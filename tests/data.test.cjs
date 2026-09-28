const {test} = require('node:test'); const assert = require('node:assert/strict');
let D; try {D = require('../src/data.js');}catch{}
test('authored learning content exists',()=>assert.ok(D,'Author the deck content'));
test('320 distinct cards across 16 decks',()=>{assert.equal(D.cards.length,320);assert.equal(D.decks.length,16);assert.equal(new Set(D.cards.map(c=>c.id)).size,320);});
test('20 complete cards per topic',()=>{for(const d of D.decks){let cs=D.cards.filter(c=>c.cat===d.id);assert.equal(cs.length,20,d.id);for(const c of cs){assert.ok(c.pl.trim()&&c.en.trim(),c.id);assert.ok(!c.pl.includes('undefined'));}}});
test('no identical English/Polish pairs',()=>{assert.equal(new Set(D.cards.map(c=>c.en.toLowerCase()+'|'+c.pl.toLowerCase())).size,320);});
test('masculine/feminine fields are complete and different',()=>{for(const c of D.cards.filter(c=>c.f)){assert.ok(c.f.trim());assert.notEqual(c.f,c.pl);}});
test('negated car phrase uses genitive',()=>{assert.ok(D.cards.some(c=>c.pl==='Nie mam samochodu.'));assert.ok(!D.cards.some(c=>c.pl==='Nie mam samochód.'));});
test('all cards belong to declared decks',()=>{const ids=new Set(D.decks.map(d=>d.id));assert.ok(D.cards.every(c=>ids.has(c.cat)));});
