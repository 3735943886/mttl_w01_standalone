const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHANNEL ? {channel:process.env.PLAYWRIGHT_CHANNEL} : {}) });
  const page = await browser.newPage({ viewport: { width: 1000, height: 900 }, deviceScaleFactor: 1 });
  await page.setContent(`<style>body{margin:0;padding:20px;background:#f2f4f7;font:14px Arial,sans-serif;--primary-text-color:#212121;--secondary-text-color:#666;--primary-color:#0288d1;--card-background-color:#fff;--secondary-background-color:#f2f4f7;--divider-color:#ddd}ha-card{display:block;border-radius:12px;box-shadow:0 2px 8px #0001}mttl-w01-2-0-card{max-width:700px;margin:auto}</style>`);
  await page.evaluate(() => {
    customElements.define('ha-card', class extends HTMLElement { constructor(){super();this.attachShadow({mode:'open'}).innerHTML='<style>:host{display:block;background:var(--card-background-color);border-radius:12px;box-shadow:0 2px 8px #0001}</style><slot></slot>';}});
    customElements.define('ha-icon', class extends HTMLElement { constructor(){super();this.attachShadow({mode:'open'}).innerHTML='<svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="18" rx="4"/><circle cx="8" cy="12" r="1"/><circle cx="16" cy="12" r="1"/></svg>';}});
  });
  await page.addScriptTag({ path: path.join(__dirname, 'mttl-w01-2.0-card.js') });
  await page.evaluate(() => {
    window.services = []; window.moreInfos = [];
    document.addEventListener('hass-more-info', e => window.moreInfos.push(e.detail.entityId));
    const card = document.createElement('mttl-w01-2-0-card');
    card.setConfig({ mac: '97c0123', name: 'MTTL-W01 · Timers', mobile_two_rows: true, channel_names: ['Desk & Monitor','Lamp','Charger','Spare'] });
    const states = {};
    const add = (id, state, unit) => states[id] = { state, attributes: { unit_of_measurement: unit } };
    const base = 'mttl_97c0123';
    add(`switch.${base}_all`, 'off');
    for(let n=1;n<=4;n++){
      add(`switch.${base}_sw${n}`, n===1||n===3?'on':'off');
      for(const [suffix,value,unit] of [['power',15.2,'W'],['meter',0.123,'kWh'],['current',0.07,'A'],['temperature',27.1,'°C']])add(`sensor.${base}_${suffix}${n}`,String(value),unit);
      add(`number.${base}_timer${n}`, ['90','0','1440','unavailable'][n-1], 'min');
      add(`sensor.${base}_timer_remaining${n}`, ['5340','0','86395','unavailable'][n-1], 's');
    }
    for(const [suffix,value,unit] of [['powerall',60.8,'W'],['meter',0.492,'kWh'],['voltage',220.1,'V'],['current',0.28,'A']])add(`sensor.${base}_${suffix}`,String(value),unit);
    window.hassMock = { states, callService: (...args) => window.services.push(args) };
    card.hass = window.hassMock;document.body.append(card);window.card = card;
  });
  let checks = 0;
  const expect = async (selector, text) => { assert.equal(await page.locator(selector).first().locator('strong').innerText(),text);checks++; };
  await expect('.timer-remaining','01:29:00');
  assert.equal(await page.locator('.timer-setting').count(),0);checks++;
  assert.equal(await page.locator('.timer-remaining').count(),4);checks++;
  assert.equal(await page.locator('.timer-remaining').nth(1).locator('strong').innerText(),'00:00:00');checks++;
  assert.equal(await page.locator('.timer-remaining').nth(2).locator('strong').innerText(),'23:59:55');checks++;
  assert(await page.locator('.timer-remaining').nth(3).isDisabled());checks++;
  assert.equal(await page.locator('.timer-remaining').nth(3).locator('strong').innerText(),'—');checks++;
  for(let i=0;i<3;i++)await page.locator('.timer-remaining').nth(i).click();
  assert.deepEqual(await page.evaluate(()=>window.moreInfos),[1,2,3].map(n=>`number.mttl_97c0123_timer${n}`));checks++;
  assert.equal(await page.evaluate(()=>window.services.length),0);checks++;
  await page.locator('.channel-toggle').first().click();
  assert.deepEqual(await page.evaluate(()=>window.services[0]),['switch','toggle',{entity_id:'switch.mttl_97c0123_sw1'}]);checks++;
  const artifactDir = path.resolve(process.env.MTTL_CARD_TEST_OUTPUT || require('node:os').tmpdir(), 'mttl-ha-card-timer-preview');fs.mkdirSync(artifactDir,{recursive:true});
  await page.locator('mttl-w01-2-0-card').screenshot({ path: path.join(artifactDir,'desktop.png') });
  await page.setViewportSize({width:390,height:1100});
  await page.evaluate(()=>document.fonts.ready);
  await page.waitForTimeout(150);
  await page.locator('mttl-w01-2-0-card').screenshot({ path: path.join(artifactDir,'mobile.png') });
  const overflow = await page.locator('.timer-remaining').evaluateAll(nodes=>nodes.filter(n=>n.scrollWidth>n.clientWidth+1).map(n=>n.textContent));
  assert.deepEqual(overflow,[]);checks++;
  await page.setViewportSize({width:320,height:1100});
  assert.deepEqual(await page.locator('.timer-remaining').evaluateAll(nodes=>nodes.filter(n=>n.scrollWidth>n.clientWidth+1).map(n=>n.textContent)),[]);checks++;
  for(const [unit,expected] of [['s','00:01:30'],['min','01:30:00']]){
    await page.evaluate(unit=>{window.hassMock.states['sensor.mttl_97c0123_timer_remaining1']={state:'90',attributes:{unit_of_measurement:unit}};window.card.hass=window.hassMock;},unit);
    await expect('.timer-remaining',expected);
  }
  const cases = [['0','min','00:00:00'],['90','min','01:30:00'],['5400','s','01:30:00'],['1.5','h','01:30:00'],['unavailable','s','—'],['unknown','s','—'],['','s','—'],['-1','s','—'],['NaN','s','—'],['Infinity','s','—'],['90','bogus','—']];
  for(const [value,unit,expected] of cases){
    const actual=await page.evaluate(({value,unit})=>{window.hassMock.states['sensor.mttl_97c0123_timer_remaining1']={state:value,attributes:{unit_of_measurement:unit}};window.card.hass=window.hassMock;return window.card.shadowRoot.querySelector('.timer-remaining strong').textContent;},{value,unit});
    assert.equal(actual,expected);checks++;
  }
  assert(await page.locator('.timer-remaining').first().isEnabled());checks++;
  await page.evaluate(()=>{delete window.hassMock.states['number.mttl_97c0123_timer2'];window.card.hass=window.hassMock;});
  assert(await page.locator('.timer-remaining').nth(1).isDisabled());checks++;
  assert.equal(await page.locator('.timer-remaining').nth(1).locator('strong').innerText(),'00:00:00');checks++;
  await browser.close();console.log(JSON.stringify({checks,failed:0,scope:'Chromium with mock HA states/services; native more-info event verified, no live HA changes',screenshots:artifactDir}));
})().catch(error=>{console.error(error);process.exit(1);});

