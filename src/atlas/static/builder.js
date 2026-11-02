"use strict";
// Draft state is separate from the active simulation until the server validates it.
const DRAFT_KEY = "atlas.manual-draft.v1";
let draft = null, connectionStart = null, previousFixture = "chain", builderSaving = false;

function newDraft() {
  return {units:"synthetic teaching units", banks:[
    {id:"A", name:"Bank A", external_assets:200, equity:40, pd:0.02},
    {id:"B", name:"Bank B", external_assets:200, equity:40, pd:0.02}
  ], exposures:[]};
}
function copyDataset(source) {
  return {units:source.units, banks:source.banks.map(b=>({id:b.id,name:b.name,external_assets:b.external_assets,equity:b.equity,pd:b.pd})), exposures:source.exposures.map(e=>({...e}))};
}
function readDraft() {
  try {
    const saved=JSON.parse(localStorage.getItem(DRAFT_KEY));
    if(!saved||!Array.isArray(saved.banks)||!Array.isArray(saved.exposures)||saved.banks.length>50||saved.exposures.length>2450)return null;
    if(!saved.banks.every(b=>b&&typeof b.id==="string"&&/^[A-Za-z0-9_-]{1,32}$/.test(b.id)&&typeof b.name==="string"))return null;
    if(!saved.exposures.every(e=>e&&typeof e.lender==="string"&&typeof e.borrower==="string"))return null;
    return saved;
  } catch {return null;}
}
function openBuilder(mode) {
  if(taskRun)return;
  stop(); previousFixture = data?.topology==="manual"?"manual":data?.topology==="teaching_branch"?"branch":data?.topology==="teaching_chain"?"chain":"generated";
  draft = mode==="resume"?readDraft():mode==="edit"&&data?copyDataset(data):newDraft();
  if(!draft)draft=newDraft();
  connectionStart=null;$("connect-hint").textContent="Select the bank that lends first.";$("builder-title").textContent=mode==="edit"?"Edit your network":"Create your network";
  $("draft-status").textContent="Your live scenario stays unchanged until you apply.";
  $("loan-error").hidden=true;renderBuilder();$("network-builder").showModal();
}
function closeBuilder() {
  if(builderSaving)return;
  $("network-builder").close();
  // Choosing the manual menu should not switch the live dataset on cancel.
  if($("fixture").value==="manual"&&data?.topology!=="manual")$("fixture").value=previousFixture;
  $("generation").hidden=$("fixture").value!=="generated";
  $("edit-manual").hidden=$("fixture").value!=="manual";
}
function numeric(value){return value===""||value===null||value===undefined?NaN:Number(value);}
function checkDraft() {
  const issues=[],accounts=[],ids=new Set(draft.banks.map(b=>b.id)),pairs=new Set();
  if(draft.banks.length<2)issues.push("Add at least two banks to run a simulation.");
  if(draft.banks.length>50)issues.push("Use at most 50 banks.");
  if(ids.size!==draft.banks.length)issues.push("Bank IDs must be unique.");
  draft.exposures.forEach(e=>{
    if(!ids.has(e.lender)||!ids.has(e.borrower))issues.push("Remove loans with missing banks.");
    if(e.lender===e.borrower)issues.push("A bank cannot lend to itself.");
    const key=`${e.lender}|${e.borrower}`;
    if(pairs.has(key))issues.push(`Duplicate loan ${e.lender} → ${e.borrower}; edit the existing amount.`);pairs.add(key);
    if(!Number.isFinite(numeric(e.amount))||numeric(e.amount)<=0)issues.push("Loan amounts must be positive numbers.");
  });
  draft.banks.forEach(b=>{
    const assets=numeric(b.external_assets),equity=numeric(b.equity);
    if(!b.name.trim()||b.name.length>80)issues.push(`${b.id}: enter a bank name (1–80 characters).`);
    if(!Number.isFinite(assets)||assets<0)issues.push(`${b.id}: external assets must be zero or more.`);
    if(!Number.isFinite(equity)||equity<=0)issues.push(`${b.id}: equity must be greater than zero.`);
    const lending=draft.exposures.filter(e=>e.lender===b.id).reduce((s,e)=>s+numeric(e.amount),0);
    const borrowing=draft.exposures.filter(e=>e.borrower===b.id).reduce((s,e)=>s+numeric(e.amount),0);
    const deposits=assets+lending-borrowing-equity;
    if(Number.isFinite(deposits)&&deposits<0)issues.push(`${b.id}: deposits would be ${fmt(deposits)}. Increase assets or lending, or reduce borrowing or equity.`);
    if(!Number.isFinite(deposits)&&Number.isFinite(assets)&&Number.isFinite(equity))issues.push(`${b.id}: account totals must be finite.`);
    accounts.push({id:b.id,deposits});
  });
  return {issues:[...new Set(issues)],accounts};
}
function saveDraft() {
  try {localStorage.setItem(DRAFT_KEY,JSON.stringify(draft));$("draft-status").textContent="Draft saved in this browser · live network unchanged";$("restore-draft").hidden=false;}
  catch {$("draft-status").textContent="Draft is in memory only; browser storage is unavailable.";}
}
function inputCell(value,label,type,onInput) {
  const td=document.createElement("td"),input=document.createElement("input");input.type=type;input.value=value??"";input.setAttribute("aria-label",label);
  if(type==="number"){input.min="0";input.step="any";}else input.maxLength=80;
  input.addEventListener("input",()=>{onInput(input.value);updateDraft(true);});td.append(input);return td;
}
function removeCell(label,onClick) {
  const td=document.createElement("td"),button=document.createElement("button");button.className="icon-button danger";button.type="button";button.textContent="×";button.setAttribute("aria-label",label);button.title=label;button.addEventListener("click",onClick);td.append(button);return td;
}
function bankOptions(select,current) {
  select.replaceChildren(...draft.banks.map(b=>new Option(`${b.id} · ${b.name||"Unnamed"}`,b.id)));
  if(draft.banks.some(b=>b.id===current))select.value=current;
}
function renderLoanSelectors() {
  const lender=$("loan-lender").value,borrower=$("loan-borrower").value;
  bankOptions($("loan-lender"),lender);bankOptions($("loan-borrower"),borrower);
  if(!borrower&&draft.banks.length>1)$("loan-borrower").value=draft.banks[1].id;
}
function renderBuilder() {
  $("builder-banks").replaceChildren(...draft.banks.map(b=>{
    const row=document.createElement("tr"),id=document.createElement("td");id.className="bank-id";id.textContent=b.id;row.append(id);
    row.append(inputCell(b.name,`Bank ${b.id} name`,"text",v=>{b.name=v;renderLoanSelectors();draft.exposures.forEach((loan,i)=>{for(const field of ["lender","borrower"]){const select=$("builder-loans").querySelector(`[aria-label="Loan ${i+1} ${field}"]`);if(select)bankOptions(select,loan[field]);}});}));
    row.append(inputCell(b.external_assets,`Bank ${b.id} external assets`,"number",v=>b.external_assets=v));
    row.append(inputCell(b.equity,`Bank ${b.id} equity`,"number",v=>b.equity=v));
    row.append(removeCell(`Remove bank ${b.id} and connected loans`,()=>{
      draft.banks=draft.banks.filter(n=>n.id!==b.id);draft.exposures=draft.exposures.filter(e=>e.lender!==b.id&&e.borrower!==b.id);connectionStart=null;renderBuilder();saveDraft();
    }));return row;
  }));
  renderLoanSelectors();
  $("builder-loans").replaceChildren(...draft.exposures.map((loan,index)=>{
    const row=document.createElement("tr");
    for(const field of ["lender","borrower"]){const td=document.createElement("td"),select=document.createElement("select");bankOptions(select,loan[field]);select.setAttribute("aria-label",`Loan ${index+1} ${field}`);select.addEventListener("change",()=>{loan[field]=select.value;updateDraft(true);});td.append(select);row.append(td);}
    row.append(inputCell(loan.amount,`Loan ${index+1} amount`,"number",v=>loan.amount=v));
    row.append(removeCell(`Remove loan ${index+1}`,()=>{draft.exposures.splice(index,1);renderBuilder();saveDraft();}));return row;
  }));
  $("loan-table").hidden=draft.exposures.length===0;$("no-loans").hidden=draft.exposures.length>0;
  $("add-bank").disabled=draft.banks.length>=50;$("add-loan").disabled=draft.banks.length<2;
  updateDraft(false);
}
function updateDraft(persist) {
  const {issues,accounts}=checkDraft();$("apply-network").disabled=issues.length>0;
  const status=$("builder-validation");status.className=issues.length?"validation invalid":"validation valid";
  status.textContent=issues.length?issues.slice(0,3).join(" "):"✓ Balanced and ready to simulate";
  $("accounting-rows").replaceChildren(...accounts.map(a=>{const row=document.createElement("div");row.className="account-row";const name=document.createElement("span"),value=document.createElement("strong");name.textContent=`${a.id} · deposits`;value.textContent=Number.isFinite(a.deposits)?fmt(a.deposits):"—";if(a.deposits<0)value.className="negative";row.append(name,value);return row;}));
  $("draft-count").textContent=`${draft.banks.length} banks · ${draft.exposures.length} loans`;
  $("builder-units").textContent=`All amounts: ${draft.units}. No real institutions are implied.`;
  drawDraft();if(persist)saveDraft();
}
function drawDraft() {
  const svg=$("draft-graph");svg.replaceChildren();const defs=svgNode("defs"),marker=svgNode("marker",{id:"draft-arrow",viewBox:"0 0 10 10",refX:9,refY:5,markerWidth:6,markerHeight:6,orient:"auto"});marker.append(svgNode("path",{d:"M0 0 L10 5 L0 10z",fill:"#6d8da7"}));defs.append(marker);svg.append(defs);
  const pos=new Map(draft.banks.map((b,i)=>{const angle=Math.PI+i*2*Math.PI/Math.max(1,draft.banks.length);return [b.id,{x:250+175*Math.cos(angle),y:145+90*Math.sin(angle)}];}));
  for(const e of draft.exposures){const a=pos.get(e.lender),b=pos.get(e.borrower);if(!a||!b||e.lender===e.borrower)continue;const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy)||1;const reciprocal=draft.exposures.some(other=>other.lender===e.borrower&&other.borrower===e.lender);const bend=reciprocal?23:0;const cx=(a.x+b.x)/2-dy/len*bend,cy=(a.y+b.y)/2+dx/len*bend;
    const path=svgNode("path",{d:`M${a.x+dx/len*24} ${a.y+dy/len*24} Q${cx} ${cy} ${b.x-dx/len*29} ${b.y-dy/len*29}`,fill:"none",stroke:"#6d8da7","stroke-width":2,"marker-end":"url(#draft-arrow)"});path.append(svgNode("title",{},`${e.lender} → ${e.borrower}: ${e.amount}`));svg.append(path);
    if(draft.banks.length<=12)svg.append(svgNode("text",{x:cx,y:cy-8,fill:"#c6d8e9","text-anchor":"middle","font-size":12,stroke:"#111d30","stroke-width":4,"paint-order":"stroke"},Number.isFinite(numeric(e.amount))?fmt(e.amount):"?"));
  }
  draft.banks.forEach(b=>{const p=pos.get(b.id),g=svgNode("g",{role:"button",tabindex:0,class:"draft-node","aria-label":`Connect bank ${b.id}`,transform:`translate(${p.x},${p.y})`});g.append(svgNode("circle",{r:22,fill:connectionStart===b.id?"#48dbb9":"#1c5969",stroke:connectionStart===b.id?"#b0ffe4":"#3a8e9d","stroke-width":2}));g.append(svgNode("text",{y:4,fill:connectionStart===b.id?"#092623":"#edf8fc","text-anchor":"middle","font-size":b.id.length>4?9:12,"font-weight":700},b.id));
    if(draft.banks.length<=12){const name=b.name.length>19?b.name.slice(0,17)+"…":b.name;g.append(svgNode("text",{y:42,fill:"#a6bcd2","text-anchor":"middle","font-size":11},name));}
    const connect=()=>{if(connectionStart===null){connectionStart=b.id;$("loan-lender").value=b.id;$("connect-hint").textContent=`${b.id} is the lender. Select a different bank to borrow.`;}else if(connectionStart!==b.id){$("loan-borrower").value=b.id;$("connect-hint").textContent=`${connectionStart} → ${b.id}. Enter the amount, then add the loan.`;connectionStart=null;$("loan-amount").focus();}drawDraft();};
    g.addEventListener("click",connect);g.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();connect();}});svg.append(g);
  });
}
$("new-network").addEventListener("click",()=>openBuilder("new"));
$("edit-network").addEventListener("click",()=>openBuilder("edit"));
$("edit-manual").addEventListener("click",()=>openBuilder("edit"));
$("restore-draft").addEventListener("click",()=>openBuilder("resume"));
$("close-builder").addEventListener("click",closeBuilder);$("cancel-builder").addEventListener("click",closeBuilder);
$("network-builder").addEventListener("cancel",event=>{event.preventDefault();closeBuilder();});
$("add-bank").addEventListener("click",()=>{
  if(draft.banks.length>=50)return;
  let i=0,id;do{id=i<26?String.fromCharCode(65+i):`B${i+1}`;i++;}while(draft.banks.some(b=>b.id===id));
  draft.banks.push({id,name:`Bank ${id}`,external_assets:200,equity:40,pd:0.02});renderBuilder();saveDraft();
  $("builder-banks").querySelector(`input[aria-label="Bank ${id} name"]`).focus();
});
$("add-loan-form").addEventListener("submit",event=>{
  event.preventDefault();const lender=$("loan-lender").value,borrower=$("loan-borrower").value,amount=numeric($("loan-amount").value);let problem="";
  if(!lender||!borrower)problem="Add two banks first.";else if(lender===borrower)problem="Choose different banks for lender and borrower.";else if(!Number.isFinite(amount)||amount<=0)problem="Enter a positive loan amount.";else if(draft.exposures.some(e=>e.lender===lender&&e.borrower===borrower))problem="That loan already exists. Edit its amount in the list below.";
  $("loan-error").textContent=problem;$("loan-error").hidden=!problem;if(problem)return;
  draft.exposures.push({lender,borrower,amount});connectionStart=null;renderBuilder();saveDraft();$("connect-hint").textContent=`Added ${lender} → ${borrower}. Select another lender to continue.`;
});
$("apply-network").addEventListener("click",async()=>{
  const {issues}=checkDraft();if(issues.length)return;
  builderSaving=true;$("apply-network").disabled=true;$("apply-network").textContent="Validating…";
  // Lock edits until validation returns so the accepted data cannot lag behind the preview.
  const controls=[...$("network-builder").querySelectorAll("input,select,button")];const disabled=controls.map(c=>c.disabled);controls.forEach(c=>c.disabled=true);
  try {
    const payload={units:draft.units,banks:draft.banks.map(b=>({...b,name:b.name.trim(),external_assets:numeric(b.external_assets),equity:numeric(b.equity)})),exposures:draft.exposures.map(e=>({...e,amount:numeric(e.amount)}))};
    const accepted=await request("/networks/manual",payload);
    manualData=accepted;datasetConfig="";$("fixture").value="manual";$("manual-option").textContent="My custom network";$("generation").hidden=true;$("edit-manual").hidden=false;
    saveDraft();$("network-builder").close();view="graph";await run(true);
  } catch(err){$("builder-validation").className="validation invalid";$("builder-validation").textContent=`Could not apply network: ${err.message}`;}
  finally {builderSaving=false;controls.forEach((c,i)=>c.disabled=disabled[i]);$("apply-network").textContent="Use this network →";$("apply-network").disabled=checkDraft().issues.length>0;}
});
$("restore-draft").hidden=!readDraft();
