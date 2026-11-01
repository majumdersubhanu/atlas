import {chromium} from 'playwright';
import {expect} from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve('..');
const browser=await chromium.launch({headless:true,executablePath:chromium.executablePath()});
const results=[];
async function check(name,fn){try{const detail=await fn();results.push({name,status:'PASS',detail});}catch(e){results.push({name,status:'FAIL',detail:e.message});}console.log(name,results.at(-1).status);}
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await check('Jupyter authenticated notebook loads',async()=>{
 await page.goto(fs.readFileSync(root+'/.runtime/jupyter_url.txt','utf8'),{waitUntil:'domcontentloaded'});
 await page.locator('.jp-Notebook').waitFor({timeout:60000});
 await expect(page.locator('.jp-Notebook')).toContainText('ATLAS',{timeout:60000});
 await expect(page.getByRole('heading',{name:'ATLAS',exact:true})).toBeVisible();
 await expect(page.locator('body')).toContainText('Idle',{timeout:60000});
 await page.screenshot({path:root+'/reports/jupyter-loaded.png'});
 return 'Authenticated notebook and rendered ATLAS content visible';
});
await check('Jupyter Run All interaction',async()=>{
 const started=Date.now();
 await page.getByRole('menuitem',{name:'Run',exact:true}).click();
 await page.getByRole('menuitem',{name:'Run All Cells',exact:true}).click();
 await expect.poll(()=>fs.statSync(root+'/reports/real_data_summary.json').mtimeMs,{timeout:90000}).toBeGreaterThan(started);
 await expect(page.locator('body')).toContainText('Idle',{timeout:60000});
 await expect(page.locator('.jp-Notebook')).not.toContainText('Traceback (most recent call last)');
 await page.keyboard.press('Control+s');
 await page.screenshot({path:root+'/reports/jupyter-run-all.png'});
 return 'Run All triggered the final summary export; kernel returned Idle, no rendered traceback';
});
await check('Jupyter browser JavaScript errors',async()=>{expect(errors).toEqual([]);return errors;});
await check('Swagger documentation and live health execution',async()=>{
 await page.goto('http://127.0.0.1:8000/docs');
 const health=page.locator('#operations-default-health_health_get');await health.waitFor({timeout:30000});
 await health.locator('.opblock-summary').click();
 await health.getByRole('button',{name:'Try it out'}).click();
 await health.getByRole('button',{name:'Execute',exact:true}).click();
 await expect(health.locator('.responses-wrapper')).toContainText('"status": "ok"');
 await page.screenshot({path:root+'/reports/swagger-health.png'});
 return 'Health endpoint executed through Swagger UI and returned ok';
});
for(const [name,viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]]){
 await check('Presentation '+name,async()=>{
  await page.setViewportSize(viewport);await page.goto('file://'+root+'/reports/03_real_data_defense.html');
  await expect(page.getByRole('heading',{name:'ATLAS',exact:true})).toBeVisible();
  const images=page.locator('img');expect(await images.count()).toBe(3);
  await expect.poll(()=>images.evaluateAll(imgs=>imgs.every(i=>i.complete&&i.naturalWidth>0))).toBe(true);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
  await page.screenshot({path:root+'/reports/presentation-'+name+'.png'});
  expect(overflow,'Page-level horizontal overflow').toBe(false);
  return 'Heading and 3 figures load; no page-level horizontal overflow';
 });
}
await check('Presentation offline with equations and figures',async()=>{
 await page.context().setOffline(true);
 await page.goto('file://'+root+'/reports/03_real_data_defense.html');
 await expect(page.locator('.atlas-equation')).toContainText('E′ᵢ');
 expect(await page.locator('script[src]').count()).toBe(0);
 expect(await page.locator('img').evaluateAll(imgs=>imgs.every(i=>i.complete&&i.naturalWidth>0))).toBe(true);
 return 'All three images embedded; equations visible without JavaScript or network';
});
await browser.close();
fs.writeFileSync(root+'/reports/browser-qa.json',JSON.stringify({browser:'Chromium',results},null,2));
console.log(JSON.stringify(results,null,2));
process.exit(results.some(r=>r.status==='FAIL')?1:0);
