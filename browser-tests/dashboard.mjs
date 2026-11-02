// Run from any directory with Atlas API running. These are automated UI checks, not human-study trials.
import {chromium} from 'playwright';
import {expect} from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const base=process.env.ATLAS_BASE_URL||'http://127.0.0.1:8030';
const out=path.join(root,'reports','visualization');
fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[],remote=[],results=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('request',r=>{if(!r.url().startsWith(base)&&/^https?:/.test(r.url()))remote.push(r.url());});
async function check(name,fn){try{const detail=await fn();results.push({name,status:'PASS',detail});}catch(e){results.push({name,status:'FAIL',detail:e.message});}console.log(name,results.at(-1).status);}
async function ready(){await expect(page.locator('#results')).toHaveAttribute('aria-busy','false');await expect(page.locator('#error')).toBeHidden();}
async function reset(){await page.goto(base);await ready();}
async function slider(id,value){await page.locator('#'+id).evaluate((el,v)=>{el.value=String(v);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));},value);}
await check('Chain loads with exact graph/matrix evidence',async()=>{
 await reset();await expect(page.locator('#loss')).toHaveText('108');await expect(page.locator('#extra-loss')).toHaveText('+48');
 expect(await page.locator('#graph g.node').count()).toBe(3);expect(await page.locator('#graph > path').count()).toBe(2);
 await expect(page.locator('#matrix button[aria-label^="A lends 100 to B"]')).toHaveText('100');
 await expect(page.locator('#matrix button[aria-label^="C lends 80 to A"]')).toHaveText('80');
 return '3 nodes, 2 directed exposures; 60 direct vs 108 cascade';
});
await check('Round trace and bank inspection',async()=>{
 await slider('round',1);await expect(page.locator('#events')).toContainText('60');
 await page.locator('#focus').selectOption('A');await expect(page.locator('#bank-detail')).toContainText('current equity -10');
 await slider('round',2);await expect(page.locator('#events')).toContainText('48');
 await page.locator('#focus').selectOption('C');await expect(page.locator('#bank-detail')).toContainText('current equity -8');
 return 'Independent chain arithmetic visible by round';
});
await check('Graph/matrix isolation and identical final results',async()=>{
 await page.getByRole('button',{name:'Matrix',exact:true}).click();await expect(page.locator('#graph-panel')).toBeHidden();await expect(page.locator('#matrix-panel')).toBeVisible();
 await expect(page.locator('#loss')).toHaveText('108');
 await page.getByRole('button',{name:'Graph',exact:true}).click();await expect(page.locator('#matrix-panel')).toBeHidden();await expect(page.locator('#graph-panel')).toBeVisible();
 await page.getByRole('button',{name:'Compare',exact:true}).click();return 'Representation toggles preserve scenario outcomes';
});
await check('Recovery boundary and live rerun',async()=>{
 await slider('recovery',100);await ready();await expect(page.locator('#loss')).toHaveText('0');await expect(page.locator('#failures')).toHaveText('1 / 3');
 await slider('recovery',50);await ready();await expect(page.locator('#failures')).toHaveText('3 / 3');
 await slider('recovery',51);await ready();await expect(page.locator('#failures')).toHaveText('1 / 3');
 await page.getByRole('button',{name:'Reset guided example'}).click();await ready();return '100%, exact-zero 50%, and 51% boundaries verified';
});
await check('Branch, generated network and external shock',async()=>{
 await page.locator('#fixture').selectOption('branch');await ready();await expect(page.locator('#loss')).toHaveText('180');
 await expect(page.locator('#failures')).toHaveText('4 / 6');
 await page.locator('#fixture').selectOption('generated');await ready();expect(await page.locator('#graph g.node').count()).toBe(12);
 await page.locator('#initial').selectOption('');await ready();await expect(page.locator('#failures')).toHaveText('0 / 12');
 await slider('shock',30);await ready();await expect(page.locator('#failures')).toHaveText('12 / 12');
 await reset();return 'Branch truth, generator, zero shock and common shock exercised';
});
await check('Evidence download is a complete reproducible response',async()=>{
 const download=page.waitForEvent('download');await page.locator('#export').click();const d=await download;
 const payload=JSON.parse(fs.readFileSync(await d.path(),'utf8'));
 expect(payload.cascade.interbank_loss).toBe(108);expect(payload.dataset_hash).toHaveLength(64);expect(payload.matrix.values[0][1]).toBe(100);
 return 'Export contains scenario, dataset, hash, both model outcomes and matrix';
});
await check('Invalid generator input cannot silently reuse an older network',async()=>{
 await page.locator('#fixture').selectOption('generated');await ready();
 await page.locator('#banks').fill('51');await page.locator('#banks').dispatchEvent('change');
 await expect(page.locator('#error')).toContainText('valid bank count');
 await page.locator('#run').click();await expect(page.locator('#error')).toContainText('valid bank count');
 await page.locator('#banks').fill('24');await page.locator('#banks').dispatchEvent('change');await ready();
 expect(await page.locator('#graph g.node').count()).toBe(24);await reset();return 'Invalid changes are rejected; valid retry rebuilds requested network';
});
await check('Practice task locks conditions and exports rehearsal only',async()=>{
 await page.locator('.practice-drawer > summary').click();
 await page.getByRole('button',{name:'Graph',exact:true}).click();await page.locator('#start-task').click();
 await expect(page.locator('#recovery')).toBeDisabled();await expect(page.getByRole('button',{name:'Matrix',exact:true})).toBeDisabled();
 await expect(page.locator('#model-comparison')).toBeHidden();await expect(page.locator('#explanation')).toBeHidden();
 await page.locator('#answer').fill('100');await page.getByRole('button',{name:'Submit answer',exact:true}).click();
 await expect(page.locator('#task-feedback')).toContainText('Correct. Expected: 100');
 const download=page.waitForEvent('download');await page.locator('#export-trials').click();const d=await download;
 const csv=fs.readFileSync(await d.path(),'utf8');expect(csv).toContain('"rehearsal"');expect(csv).not.toContain('"study"');
 await page.locator('#task').selectOption('secondary');await page.locator('#start-task').click();await page.locator('#answer').fill('A,C');await page.getByRole('button',{name:'Submit answer',exact:true}).click();
 await expect(page.locator('#task-feedback')).toContainText('Correct. Expected: A,C');
 await reset();return 'Automated practice records remained browser-local and were not saved as study observations';
});
await check('API failure is visible and retry recovers',async()=>{
 await page.route('**/visualization',route=>route.fulfill({status:500,contentType:'application/json',body:JSON.stringify({detail:'QA injected error'})}));
 await page.locator('#run').click();await expect(page.locator('#error')).toContainText('QA injected error');await expect(page.locator('#start-task')).toBeDisabled();
 await page.unroute('**/visualization');await page.locator('#run').click();await ready();await expect(page.locator('#loss')).toHaveText('108');return 'No silent failure; previous evidence flagged and retry works';
});
await check('Desktop and mobile layouts',async()=>{
 await reset();await slider('round',2);
 for(const [name,size] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]]){
  await page.setViewportSize(size);await expect(page.locator('#graph')).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  await page.screenshot({path:path.join(out,`dashboard-${name}.png`),fullPage:true});
 }
 await page.setViewportSize({width:1440,height:1000});return '1440px and 390px widths have no page-level horizontal overflow';
});
await check('No browser errors or remote dashboard dependencies',async()=>{expect(errors).toEqual([]);expect(remote).toEqual([]);return {errors,remoteRequests:remote};});
await check('Swagger and OpenAPI expose visual endpoints',async()=>{
 const response=await page.request.get(base+'/openapi.json');const schema=await response.json();expect(schema.paths['/visualization']).toBeTruthy();expect(schema.paths['/fixtures/{name}']).toBeTruthy();
 await page.goto(base+'/docs');await expect(page.locator('.swagger-ui')).toContainText('/visualization',{timeout:30000});return 'OpenAPI routes and rendered Swagger available';
});
await check('Executed notebook exports work offline',async()=>{
 await page.context().setOffline(true);
 for(const stem of ['04_visualization_comparison','05_visualization_study_analysis']){
  await page.goto('file://'+path.join(out,stem+'.html'));
  expect(await page.locator('script[src]').count()).toBe(0);
  expect(await page.locator('img').evaluateAll(imgs=>imgs.every(i=>i.complete&&i.naturalWidth>0))).toBe(true);
  await expect(page.locator('body')).toContainText(stem.startsWith('04')?'108':'NOT EVALUATED');
 }
 return 'Code-hidden HTML opens offline with embedded figures and honest empty-study status';
});
await browser.close();
fs.writeFileSync(path.join(out,'browser-qa.json'),JSON.stringify({kind:'automated software verification; not participant evidence',base,browser:'Chromium',results},null,2));
process.exit(results.some(r=>r.status==='FAIL')?1:0);
