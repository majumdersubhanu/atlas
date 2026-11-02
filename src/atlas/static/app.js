"use strict";
const $ = id => document.getElementById(id);
const NS = "http://www.w3.org/2000/svg";
const fmt = n => Number(n).toLocaleString("en-US", {maximumFractionDigits: 2});
let data, evidence, view = "graph", round = 0, selected = "", timer, pending = 0, taskRun = null;
const practiceRows = [];
let datasetConfig = "";
let manualData = null;
const colors = {alive: "#167b79", fresh: "#de6672", failed: "#8d4d68"};

function error(message = "") { $("error").hidden = !message; $("error").textContent = message; }
async function request(path, body) {
  const response = await fetch(path, body ? {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)} : {});
  if (!response.ok) {
    let detail; try { detail = (await response.json()).detail; } catch { detail = response.statusText; }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return response.json();
}
function stop() { clearInterval(timer); timer = null; $("play").textContent = "▶ Play"; }
function options(select, values, first) {
  select.replaceChildren(new Option(first[1], first[0]), ...values.map(b => new Option(b.name, b.id)));
}
async function run(rebuild = false) {
  if (taskRun) return;
  stop(); error();
  const generation = ++pending;
  const requestedConfig = JSON.stringify([$("fixture").value,$("topology").value,$("banks").value,$("seed").value]);
  rebuild = rebuild || requestedConfig !== datasetConfig;
  $("results").setAttribute("aria-busy", "true");
  $("run").disabled = true; $("start-task").disabled = true; $("edit-network").disabled = true; $("new-network").disabled = true;
  try {
    let candidate = data;
    if (rebuild || !candidate) {
      if ($("fixture").value === "generated") {
        if (!$("banks").reportValidity() || !$("seed").reportValidity()) throw new Error("Enter a valid bank count and seed.");
        candidate = await request("/generate", {banks:Number($("banks").value), seed:Number($("seed").value), topology:$("topology").value});
      } else if ($("fixture").value === "manual") {
        if (!manualData) throw new Error("Create a manual network first.");
        candidate = manualData;
      } else candidate = await request(`/fixtures/${$("fixture").value}`);
      if (generation !== pending) return;
      options($("initial"), candidate.banks, ["", "None · external shock only"]);
      $("initial").value = candidate.banks.some(b => b.id === "B") ? "B" : candidate.banks[0].id;
      options($("focus"), candidate.banks, ["", "All banks"]); selected = "";
    }
    const scenario = {name:"Interactive demonstration", recovery:Number($("recovery").value)/100, external_impairment:Number($("shock").value)/100, initial_defaults:$("initial").value ? [$("initial").value] : []};
    const result = await request("/visualization", {dataset:candidate, scenario});
    if (generation !== pending) return;
    data = candidate; datasetConfig = requestedConfig; evidence = result; round = 0;
    $("round").max = result.cascade.rounds.length - 1; $("round").value = 0;
    $("failures").textContent = `${result.cascade.default_count} / ${data.banks.length}`;
    $("failure-breakdown").textContent = `${result.cascade.initial_defaults.length} initial · ${result.cascade.secondary_defaults.length} secondary`;
    $("loss").textContent = fmt(result.cascade.interbank_loss);
    $("extra-loss").textContent = `+${fmt(result.comparison.additional_interbank_loss)}`;
    $("extra-defaults").textContent = `${result.comparison.additional_defaults} additional failures vs direct loss`;
    $("units").textContent = `Amounts: ${data.units}.`;
    $("network-meta").textContent = `${data.banks.length} banks · ${data.exposures.length} loans · density ${fmt(result.metrics.directed_density*100)}%`;
    const rows = [["Initial failures", result.baseline.initial_defaults.length, result.cascade.initial_defaults.length], ["Secondary failures",result.baseline.secondary_defaults.length,result.cascade.secondary_defaults.length], ["Total failures",result.baseline.default_count,result.cascade.default_count], ["Posted interbank loss",result.baseline.interbank_loss,result.cascade.interbank_loss], ["External asset loss",result.baseline.external_loss,result.cascade.external_loss]];
    tableRows($("comparison"), rows.map(r => [r[0],fmt(r[1]),fmt(r[2])]));
    render();
  } catch (e) { if (generation === pending) { error(`Could not run scenario: ${e.message}. Previous evidence, if visible, is unchanged.`); evidence = null; } }
  finally { if (generation === pending) { $("run").disabled = false; $("start-task").disabled = !evidence; $("results").setAttribute("aria-busy", "false"); $("edit-network").disabled = !data; $("new-network").disabled = false; } }
}
function tableRows(body, rows) {
  body.replaceChildren(...rows.map(row => { const tr = document.createElement("tr"); row.forEach(value => {const td=document.createElement("td");td.textContent=value;tr.append(td);}); return tr; }));
}
function svgNode(name, attrs, text) { const node=document.createElementNS(NS,name); Object.entries(attrs || {}).forEach(([k,v]) => node.setAttribute(k,v)); if (text !== undefined) node.textContent=text; return node; }
function state(bank) { return bank.default_round === round ? "fresh" : bank.default_round !== null && bank.default_round < round ? "failed" : "alive"; }
function stateLabel(bank) { return state(bank) === "alive" ? "surviving" : state(bank) === "fresh" ? "failed this round" : "failed earlier"; }
function choose(id) { selected = selected === id ? "" : id; $("focus").value = selected; render(); }
function renderGraph() {
  const svg=$("graph"); svg.replaceChildren();
  const desc=svgNode("desc",{},`Loan arrows point from lender to borrower; losses move in reverse. Round ${round}. ${evidence.nodes.map(n=>`${n.id}: ${stateLabel(n)}`).join("; ")}`);svg.append(desc);
  const defs=svgNode("defs");
  for (const [id,fill] of [["loan-arrow","#7089a3"],["loss-arrow","#f2bf68"]]) {const marker=svgNode("marker",{id,viewBox:"0 0 10 10",refX:9,refY:5,markerWidth:6,markerHeight:6,orient:"auto-start-reverse"});marker.append(svgNode("path",{d:"M 0 0 L 10 5 L 0 10 z",fill}));defs.append(marker);}svg.append(defs);
  const width=Math.max(360,Math.min(900,svg.clientWidth||600));
  svg.setAttribute("viewBox",`0 0 ${width} 330`);
  const positions=new Map(evidence.nodes.map(n=>[n.id,{x:width/2+n.x*(width/2-65),y:155+n.y*100}]));
  const events=evidence.cascade.events.filter(e=>e.round===round);
  const max=Math.max(1,...evidence.edges.map(e=>e.amount));
  const edges=new Set(evidence.edges.map(e=>`${e.lender}|${e.borrower}`));
  evidence.edges.forEach(e=>{
    const a=positions.get(e.lender),b=positions.get(e.borrower),dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy)||1;
    const x1=a.x+dx/d*27,y1=a.y+dy/d*27,x2=b.x-dx/d*31,y2=b.y-dy/d*31;
    const bend=edges.has(`${e.borrower}|${e.lender}`)?24:0;
    const cx=(x1+x2)/2-dy/d*bend,cy=(y1+y2)/2+dx/d*bend;
    const event=events.find(v=>v.lender===e.lender&&v.borrower===e.borrower);
    const active=Boolean(event);const involved=!selected||selected===e.lender||selected===e.borrower;
    const path=svgNode("path",{d:`M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`,fill:"none",stroke:active?"#f2bf68":"#7089a3","stroke-width":1+e.amount/max*3,"marker-end":`url(#${active?"loss":"loan"}-arrow)`,opacity:involved?1:.15});
    path.append(svgNode("title",{},`${e.lender} lends ${fmt(e.amount)} to ${e.borrower}${event?`; loss to ${e.lender} this round: ${fmt(event.loss)}`:""}`));svg.append(path);
    if(evidence.nodes.length<=12||selected===e.lender||selected===e.borrower){const label=svgNode("text",{x:cx,y:cy-7,"text-anchor":"middle","font-size":11,fill:active?"#f2bf68":"#b8c8dd",stroke:"#111a29","stroke-width":4,"paint-order":"stroke",opacity:involved?1:.2},fmt(e.amount));svg.append(label);}
  });
  evidence.nodes.forEach(n=>{
    const p=positions.get(n.id),s=state(n),g=svgNode("g",{class:"node",tabindex:0,role:"button","aria-label":`Inspect ${n.name}, ${stateLabel(n)}`,transform:`translate(${p.x},${p.y})`});
    g.append(svgNode("circle",{r:selected===n.id?28:24,fill:colors[s],stroke:selected===n.id?"#bd771e":"#fffefa","stroke-width":selected===n.id?4:3}));
    g.append(svgNode("text",{"text-anchor":"middle",y:4,fill:"white","font-size":n.id.length>3?10:14,"font-weight":700},n.id));
    if(evidence.nodes.length<=12||selected===n.id){g.append(svgNode("text",{"text-anchor":"middle",y:43,fill:"#bdcadd","font-size":11},`E ${fmt(evidence.cascade.rounds[round].equity[n.id])}${s!=="alive"?" · failed":""}`));}
    g.append(svgNode("title",{},`${n.name}: ${stateLabel(n)}. Equity ${fmt(evidence.cascade.rounds[round].equity[n.id])}.`));
    g.addEventListener("click",()=>choose(n.id));g.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();choose(n.id);}});svg.append(g);
  });
}
function renderMatrix() {
  const table=$("matrix"); table.replaceChildren(); table.classList.toggle("small-matrix",evidence.nodes.length<=6);
  const head=document.createElement("thead"),hr=document.createElement("tr");const corner=document.createElement("th");corner.textContent="L ↓ / B →";hr.append(corner);
  evidence.nodes.forEach(n=>{const th=document.createElement("th");th.scope="col";th.textContent=n.id+(state(n)!=="alive"?" ×":"");th.style.color=state(n)==="alive"?"#8bdace":state(n)==="fresh"?"#ff9eac":"#c18ba6";th.title=stateLabel(n);hr.append(th);});head.append(hr);table.append(head);
  const body=document.createElement("tbody"),max=Math.max(1,...evidence.edges.map(e=>e.amount));
  const events=new Set(evidence.cascade.events.filter(e=>e.round===round).map(e=>`${e.lender}|${e.borrower}`));
  evidence.nodes.forEach((n,i)=>{const tr=document.createElement("tr"),th=document.createElement("th");th.scope="row";th.className="row-label";th.textContent=n.id+(state(n)!=="alive"?" ×":"");th.style.color=state(n)==="alive"?"#8bdace":state(n)==="fresh"?"#ff9eac":"#c18ba6";th.title=stateLabel(n);tr.append(th);
    evidence.nodes.forEach((b,j)=>{const value=evidence.matrix.values[i][j],td=document.createElement("td"),button=document.createElement("button");button.textContent=value?fmt(value):"—";
      button.title=`${n.id} lends ${fmt(value)} to ${b.id}. ${n.id}: ${stateLabel(n)}; ${b.id}: ${stateLabel(b)}`;button.setAttribute("aria-label",button.title);
      const ratio=value/max;td.style.background=value?`rgba(45,180,167,${.18+.65*ratio})`:"#172337";td.style.color=ratio>.5?"#fff":"#b8dfde";
      if(events.has(`${n.id}|${b.id}`))td.classList.add("active-cell");if(selected&&(n.id===selected||b.id===selected))td.classList.add("focus-cell");
      button.addEventListener("click",()=>choose(n.id));td.append(button);tr.append(td);
    });body.append(tr);
  });table.append(body);const caption=document.createElement("caption");caption.textContent="Darker cells = larger original loans. × = failed by this round. Zero / no loan = —. Click a cell to inspect its lender.";table.append(caption);
}
function render() {
  if(!evidence)return;
  $("graph-panel").hidden=view==="matrix";$("matrix-panel").hidden=view==="graph";$("view-grid").classList.toggle("single",view!=="both");
  document.querySelectorAll("[data-view]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.view===view));
  renderGraph();renderMatrix();
  const current=evidence.cascade.rounds[round],events=evidence.cascade.events.filter(e=>e.round===round);
  $("round-value").textContent=round;$("round").value=round;$("round-note").textContent=`${current.cumulative_defaults} failed · ${fmt(current.interbank_loss)} new loan loss`;
  $("explanation-title").textContent=`Round ${round} · ${round===0?"the initial event":current.new_defaults.length?"new failures":"no further failures"}`;
  $("round-explanation").textContent=round===0?`External losses total ${fmt(evidence.cascade.external_loss)}. Initial failures: ${current.new_defaults.join(", ")||"none"}. A forced failure is an imposed credit event and can retain positive book equity.`:`${events.length} loan loss entries total ${fmt(current.interbank_loss)}. New failures: ${current.new_defaults.join(", ")||"none"}. ${current.new_defaults.length?"These banks can transmit losses in the next round.":"The cascade has no new failures to propagate."}`;
  tableRows($("events"),events.length?events.map(e=>[e.borrower,e.lender,fmt(e.ead),fmt(e.loss)]):[["No loan losses posted in this round","—","—","—"]]);
  const node=evidence.nodes.find(n=>n.id===selected);
  $("bank-detail").textContent=node?`${node.name} · ${stateLabel(node)} · Starting equity ${fmt(node.equity)} → current equity ${fmt(current.equity[node.id])}. External assets ${fmt(node.external_assets)}; loans made ${fmt(node.interbank_assets)}; interbank borrowing ${fmt(node.interbank_liabilities)}.`:"";
}
function download(name,content,type) {const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement("a");a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function taskLocks(locked) {
  document.body.classList.toggle("practicing",locked);
  document.querySelectorAll(".controls input,.controls select,.controls button,[data-view],#task,#start-task,#export,#new-network,#edit-network,#restore-draft").forEach(el=>el.disabled=locked);
}
function finishTask(){taskRun=null;taskLocks(false);$("task-active").hidden=true;stop();}
$("start-task").addEventListener("click",()=>{
  if(!evidence||view==="both"){error("Choose Graph or Matrix before starting a practice task.");return;}
  if($("task").value==="exposure"&&!evidence.edges.length){error("This network has no loans. Choose a different network or task.");return;}
  error();stop();round=0;selected="";$("focus").value="";render();
  const edge=evidence.edges[0],type=$("task").value;
  taskRun={type,view,expected:type==="exposure"?edge.amount:evidence.cascade.secondary_defaults.slice().sort().join(","),start:performance.now(),hash:evidence.dataset_hash,startedAt:new Date().toISOString(),scenario:JSON.stringify(evidence.scenario)};
  $("task-prompt").textContent=type==="exposure"?`How much did ${edge.lender} lend to ${edge.borrower}? Enter the loan amount (a number).`:`Which banks fail after the initial failures? Inspect the rounds, then enter all secondary bank IDs separated by commas, or “none”.`;
  $("answer").value="";$("task-feedback").textContent="";$("task-active").hidden=false;taskLocks(true);$("answer").focus();
});
$("answer-form").addEventListener("submit",event=>{
  event.preventDefault();if(!taskRun)return;
  const raw=$("answer").value.trim();let correct;
  if(taskRun.type==="exposure")correct=raw!==""&&Number.isFinite(Number(raw))&&Math.abs(Number(raw)-taskRun.expected)<=.011;
  else {const answer=raw.toLowerCase()==="none"?"":Array.from(new Set(raw.toUpperCase().split(/[\s,]+/).filter(Boolean))).sort().join(",");correct=answer===taskRun.expected;}
  const elapsed=(performance.now()-taskRun.start)/1000;
  practiceRows.push({record_type:"rehearsal",participant_id:"local-practice",representation:taskRun.view,task:taskRun.type,correct:Number(correct),duration_seconds:elapsed.toFixed(3),confidence:$("confidence").value,dataset_hash:taskRun.hash,scenario_json:taskRun.scenario,started_utc:taskRun.startedAt,response:raw,expected:String(taskRun.expected),viewport:`${innerWidth}x${innerHeight}`});
  $("task-feedback").textContent=`${correct?"Correct":"Not correct"}. Expected: ${String(taskRun.expected)||"none"}. Time: ${elapsed.toFixed(1)} s. Practice row ${practiceRows.length} saved in this tab only; download before closing. This is not study evidence.`;
  $("export-trials").disabled=false;finishTask();
});
$("cancel-task").addEventListener("click",()=>{finishTask();$("task-feedback").textContent="Practice canceled; no row recorded.";});
$("export-trials").addEventListener("click",()=>{if(!practiceRows.length)return;const keys=Object.keys(practiceRows[0]);const quote=v=>'"'+String(v).replaceAll('"','""')+'"';download("atlas-practice-only.csv",[keys.join(","),...practiceRows.map(r=>keys.map(k=>quote(r[k])).join(","))].join("\n"),"text/csv");});
$("export").addEventListener("click",()=>{if(evidence)download("atlas-visual-evidence.json",JSON.stringify({...evidence,displayed_round:round,representation:view},null,2),"application/json");});
$("run").addEventListener("click",()=>run(false));
$("reset").addEventListener("click",()=>{$("fixture").value="chain";$("generation").hidden=true;$("edit-manual").hidden=true;$("recovery").value=40;$("shock").value=0;updateOutputs();run(true);});
$("fixture").addEventListener("change",()=>{$("generation").hidden=$("fixture").value!=="generated"; $("edit-manual").hidden=$("fixture").value!=="manual"; if($("fixture").value==="manual"&&!manualData){openBuilder("new");return;}run(true);});
for(const id of ["topology","banks","seed"])$(id).addEventListener("change",()=>run(true));
$("initial").addEventListener("change",()=>run());
function updateOutputs(){$("recovery-value").textContent=`${$("recovery").value}%`;$("shock-value").textContent=`${$("shock").value}%`;}
for(const id of ["recovery","shock"]){$(id).addEventListener("input",updateOutputs);$(id).addEventListener("change",()=>run());}
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>{view=b.dataset.view;render();}));
$("focus").addEventListener("change",()=>{selected=$("focus").value;render();});
$("round").addEventListener("input",()=>{stop();round=Number($("round").value);render();});
$("last").addEventListener("click",()=>{if(evidence){stop();round=evidence.cascade.rounds.length-1;render();}});
$("play").addEventListener("click",()=>{if(!evidence)return;if(timer){stop();return;}if(round>=evidence.cascade.rounds.length-1)round=0;render();$("play").textContent="Ⅱ Pause";timer=setInterval(()=>{if(round<evidence.cascade.rounds.length-1){round++;render();}else stop();},1200);});
run(true);

window.addEventListener("resize",()=>{if(evidence)render();});
