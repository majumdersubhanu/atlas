import {chromium} from 'playwright';
import {expect} from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const base=process.env.ATLAS_BASE_URL||'http://127.0.0.1:8030';
const out=path.join(root,'reports','visualization');
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const results=[],errors=[];page.on('pageerror',e=>errors.push(e.message));
async function check(name,fn){try{await fn();results.push({name,status:'PASS'});}catch(e){results.push({name,status:'FAIL',error:e.message});}console.log(name,results.at(-1).status);}
async function ready(){await expect(page.locator('#results')).toHaveAttribute('aria-busy','false');await expect(page.locator('#error')).toBeHidden();}
async function setBank(id,field,value){await page.getByRole('spinbutton',{name:`Bank ${id} ${field}`,exact:true}).fill(String(value));}
async function loan(lender,borrower,amount){await page.locator('#loan-lender').selectOption(lender);await page.locator('#loan-borrower').selectOption(borrower);await page.locator('#loan-amount').fill(String(amount));await page.getByRole('button',{name:'Add loan',exact:true}).click();}
await page.goto(base);await ready();
await check('Compact dark graph-first workspace',async()=>{
 await expect(page.getByRole('heading',{name:'Contagion workspace'})).toBeVisible();
 await expect(page.locator('#matrix-panel')).toBeHidden();
 expect(await page.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--paper').trim())).toBe('#0a111e');
 await page.screenshot({path:path.join(out,'dashboard-dark.png'),fullPage:true});
});
await check('Build the hand-computed chain from scratch',async()=>{
 await page.locator('#new-network').click();await expect(page.locator('#network-builder')).toBeVisible();
 await page.locator('#add-bank').click();
 await setBank('A','external assets',100);await setBank('A','equity',50);
 await setBank('B','external assets',200);await setBank('B','equity',50);
 await setBank('C','external assets',100);await setBank('C','equity',40);
 await page.getByRole('textbox',{name:'Bank A name',exact:true}).fill('Alpha');
 await loan('A','B',100);await loan('C','A',80);
 await expect(page.locator('#builder-validation')).toHaveText('✓ Balanced and ready to simulate');
 const accounts=await page.locator('#accounting-rows strong').allTextContents();expect(accounts).toEqual(['70','50','140']);
 await page.screenshot({path:path.join(out,'manual-builder-desktop.png'),fullPage:true});
 await page.locator('#apply-network').click();await expect(page.locator('#network-builder')).toBeHidden();await ready();
 await expect(page.locator('#fixture')).toHaveValue('manual');await expect(page.locator('#loss')).toHaveText('108');
 await expect(page.locator('#failures')).toHaveText('3 / 3');
 const d=page.waitForEvent('download');await page.locator('#export').click();const downloaded=await d;
 const record=JSON.parse(fs.readFileSync(await downloaded.path(),'utf8'));expect(record.dataset.topology).toBe('manual');expect(record.dataset.banks[0].name).toBe('Alpha');expect(record.dataset.banks.map(b=>b.deposits)).toEqual([70,50,140]);
});
await check('Reject invalid loans and negative residual accounts',async()=>{
 await page.locator('#edit-network').click();await loan('A','A',20);await expect(page.locator('#loan-error')).toContainText('different banks');
 await loan('A','B',20);await expect(page.locator('#loan-error')).toContainText('already exists');expect(await page.locator('#builder-loans tr').count()).toBe(2);
 await setBank('B','external assets',100);await expect(page.locator('#builder-validation')).toContainText('deposits would be -50');await expect(page.locator('#apply-network')).toBeDisabled();
 await setBank('B','external assets',200);await expect(page.locator('#apply-network')).toBeEnabled();
 await page.getByRole('spinbutton',{name:'Loan 1 amount',exact:true}).fill('0');await expect(page.locator('#apply-network')).toBeDisabled();
 await page.getByRole('spinbutton',{name:'Loan 1 amount',exact:true}).fill('100');await expect(page.locator('#apply-network')).toBeEnabled();
 await page.locator('#cancel-builder').click();await expect(page.locator('#loss')).toHaveText('108');
});
await check('Removing banks deletes their loans, but cancel preserves the active network',async()=>{
 await page.locator('#edit-network').click();await page.getByRole('button',{name:'Remove bank A and connected loans',exact:true}).click();
 expect(await page.locator('#builder-loans tr').count()).toBe(0);expect(await page.locator('#builder-banks tr').count()).toBe(2);
 await page.getByRole('button',{name:'Remove bank B and connected loans',exact:true}).click();await expect(page.locator('#apply-network')).toBeDisabled();
 await page.keyboard.press('Escape');await expect(page.locator('#network-builder')).toBeHidden();await expect(page.locator('#loss')).toHaveText('108');
});
await check('Canvas connection and saved draft recovery',async()=>{
 await page.locator('#new-network').click();await page.getByRole('button',{name:'Connect bank B',exact:true}).click();await page.getByRole('button',{name:'Connect bank A',exact:true}).click();
 await expect(page.locator('#loan-lender')).toHaveValue('B');await expect(page.locator('#loan-borrower')).toHaveValue('A');
 await page.locator('#loan-amount').fill('75');await page.getByRole('button',{name:'Add loan',exact:true}).click();
 await page.locator('#cancel-builder').click();await page.reload();await ready();
 await page.locator('#restore-draft').click();expect(await page.locator('#builder-loans tr').count()).toBe(1);
 await expect(page.getByRole('spinbutton',{name:'Loan 1 amount',exact:true})).toHaveValue('75');await page.locator('#cancel-builder').click();
});
await check('Manual menu cancel and failed server validation do not apply a draft',async()=>{
 await page.locator('#fixture').selectOption('manual');await expect(page.locator('#network-builder')).toBeVisible();await page.locator('#cancel-builder').click();await expect(page.locator('#fixture')).toHaveValue('chain');
 await page.locator('#new-network').click();await page.route('**/networks/manual',route=>route.fulfill({status:422,contentType:'application/json',body:JSON.stringify({detail:'QA rejected draft'})}));
 await page.locator('#apply-network').click();await expect(page.locator('#builder-validation')).toContainText('QA rejected draft');await expect(page.locator('#network-builder')).toBeVisible();await expect(page.locator('#apply-network')).toBeEnabled();
 await page.unroute('**/networks/manual');await page.locator('#cancel-builder').click();await expect(page.locator('#loss')).toHaveText('108');
});
await check('Mobile builder fits the screen and remains usable',async()=>{
 await page.setViewportSize({width:390,height:844});await page.locator('#new-network').click();
 await expect(page.locator('#apply-network')).toBeVisible();
 const fit=await page.locator('#network-builder').evaluate(el=>{const r=el.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight;});expect(fit).toBe(true);
 await page.screenshot({path:path.join(out,'manual-builder-mobile.png'),fullPage:true});
 await page.locator('#apply-network').click();await ready();await expect(page.locator('#fixture')).toHaveValue('manual');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});
await check('No browser script errors',async()=>{expect(errors).toEqual([]);});
await browser.close();fs.writeFileSync(path.join(out,'manual-builder-qa.json'),JSON.stringify({kind:'automated manual network software verification',results},null,2));
process.exit(results.some(r=>r.status==='FAIL')?1:0);
