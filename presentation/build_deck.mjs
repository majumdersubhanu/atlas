import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const output = new URL('./.build/', import.meta.url);
await fs.mkdir(output, {recursive:true});
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
const session={};
const nodeRepl={write:console.log};
var evidence = JSON.parse(await fs.readFile(new URL('./evidence.json', import.meta.url),'utf8'));
await (async () => {
  presentation.theme.defaultFont='Liberation Sans';
  const C={ink:'#142B3B',blue:'#176B92',red:'#B34535',green:'#276957',gray:'#526471',paper:'#FCFCF8'};
  function text(s,t,x,y,w,h,size=28,color=C.ink,bold=false){const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});a.text=t;a.text.style={fontSize:size,color,bold};return a;}
  function slide(title,notes){const s=presentation.slides.add();s.background.fill=C.paper;text(s,title,64,44,1150,100,42,C.ink,true);s.speakerNotes.text=notes;return s;}
  function note(s,t){text(s,t,64,627,1150,64,21,C.gray);}
  function body(s,t,x=64,y=170,w=1110,h=390,size=31){text(s,t,x,y,w,h,size);}
  function table(s,values,x=64,y=180,w=1150,h=330){const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values});for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){const z=t.getCell(r,c);z.fill=r===0?C.ink:(r%2?'#F1F5F5':'#FFFFFF');z.text.style={fontSize:25,color:r===0?'#FFFFFF':C.ink,bold:r===0};} t.borders.assign({fill:'#D7E0E3',width:1,style:'solid'});return t;}
  function chart(s,type,categories,series,extra={}){return s.charts.add(type,{position:{left:64,top:175,width:1140,height:410},categories,series,hasLegend:series.length>1,legend:{position:'bottom',overlay:false,textStyle:{fontSize:22,fill:C.ink}},xAxis:{textStyle:{fontSize:20,fill:C.gray}},yAxis:{min:0,textStyle:{fontSize:20,fill:C.gray},majorGridlines:{fill:'#D7E0E3',width:1}},...extra});}
  let s=slide('ATLAS','Opening: Atlas is a B.Tech research prototype for direct counterparty credit contagion. The deck reports reproducible synthetic experiments, not predictions of historical bank failure. No claim of inventing Furfine or DebtRank.');
  text(s,'A graph-based framework for\nsystemic financial risk experiments',64,195,1110,170,52,C.ink,true);
  text(s,'Scientific MVP and academic defense',64,440,1100,60,30,C.blue);
  note(s,'Notebook and API implementation, 30 October 2026');

  s=slide('The research problem','A bank can appear solvent on its own but hold claims on other banks. The research question concerns how contractual links alter scenario outcomes. Scope is solvency losses through interbank loans. Liquidity runs, asset fire sales, legal resolution and forecasting remain outside this MVP.');
  body(s,'A bank’s losses can become another bank’s losses.\n\nHow much does repeated transmission change a stress scenario?\n\nWhich institutions impose the largest losses on their creditors?');
  note(s,'Research object: a directed network of contractual loan exposures');

  s=slide('A bank balance sheet','Bank A from the manually verified fixture. Assets are 100 external + 100 interbank = 200. Funding is deposits 70 + interbank borrowing 80 + equity 50 = 200. Equity absorbs losses. Deposits represent all outside liabilities in this simplified model. Units are synthetic INR crore. Source: tests/test_engine.py, chain fixture.');
  table(s,[['Assets','Amount','Funding','Amount'],['External assets','100','Deposits','70'],['Loans to banks','100','Borrowing from banks','80'],['','', 'Equity','50'],['Total','200','Total','200']],64,180,1150,330);
  note(s,'Equity is the loss-absorbing buffer. All amounts are synthetic INR crore.');

  s=slide('Lending direction and loss direction','A lends 100 to B. C lends 80 to A. A loan creates an asset for the lender and liability for the borrower. When B defaults, A suffers a credit loss. When A subsequently defaults, C suffers a loss. The exposure matrix uses lender rows and borrower columns. This is the reverse of loss transmission.');
  table(s,[['Loan contract','Lender’s asset','Borrower’s obligation'],['A lends to B','A holds 100','B owes 100'],['C lends to A','C holds 80','A owes 80']],64,175,1150,225);
  text(s,'B’s failure first harms A.\nA’s subsequent failure then harms C.',64,445,1100,130,38,C.red,true);
  note(s,'Loan arrows denote claims. A loss moves from a borrower to its creditor.');

  s=slide('A cascade that can be checked by hand','Force B to default with recovery 0.40. LGD is 1 minus recovery = 0.60. A loses 100*0.6=60, exhausting equity 50. C then loses 80*0.6=48, exhausting equity 40. Total posted interbank loss is 108. B can retain positive book equity because its forced default is an imposed credit event. Rounds are computational, not calendar periods. Source: test_furfine_chain_and_no_mutation.');
  table(s,[['Round','Credit loss','Equity after loss','New failure'],['0','Imposed credit event','B remains a forced default','B'],['1','A: 100 × 60% = 60','A: 50 − 60 = −10','A'],['2','C: 80 × 60% = 48','C: 40 − 48 = −8','C']],64,175,1150,300);
  text(s,'60 + 48 = 108',64,520,1100,70,48,C.red,true);
  note(s,'Recovery 40%. Equity at or below zero triggers modeled default. Synthetic INR crore.');

  s=slide('The experimental control isolates propagation','The baseline is deliberately truncated after one generation of counterparty losses. Both methods use identical network, equity, initial defaults and recovery. In the chain baseline B and A fail, C does not receive a loss. The cascade adds C and 48 posted loss. This is an algorithmic ablation, not a claim about the methods used by actual supervisors. Sources: src/atlas/baseline.py, src/atlas/engine.py.');
  table(s,[['Same three-bank scenario','Direct-loss-only control','Repeated cascade'],['Total defaults','2','3'],['Posted interbank loss','60','108'],['C’s remaining equity','40','−8']],64,180,1150,300);
  note(s,'Only the propagation rule changes. The comparison tests a mechanism under stated assumptions.');

  s=slide('Established methods and current practice','ECB, November 2025: Integrating contagion risk into the 2025 EU-wide stress test. https://www.ecb.europa.eu/press/financial-stability-publications/macroprudential-bulletin/html/ecb.mpbu202511_03.en.html . The integrated model includes banks, funds and insurers, counterparty losses, liquidity and forced sales with granular data. Atlas does not reproduce its empirical results. Source: docs/BASELINE_METHODS.md.');
  table(s,[['Method','Purpose','Atlas scope'],['Static expected credit loss','Expected direct loan loss','Elementary PD × LGD × EAD'],['Furfine-style cascade','Repeated default transmission','Implemented with stated conventions'],['DebtRank-style distress','Distress before binary default','Exploratory active-step variant'],['ECB integrated stress, 2025','Counterparty, liquidity and fire sales','Broader supervisory framework']],64,175,1150,355);
  note(s,'Atlas’s direct-loss-only control is an ablation, not a description of industry practice.');

  s=slide('The implemented scientific workflow','Python 3.12 src-layout package, Pydantic validation, NumPy/Pandas, NetworkX, FastAPI, pytest and uv. The notebook uses the same package functions as the API. Inputs and outputs are persisted with dataset hashes. All equations and conventions reside in docs/MODELS.md.');
  table(s,[['Stage','Executable result'],['Data and validation','Bank balance sheets and directed exposure matrix'],['Financial model','Expected credit loss and loss propagation'],['Experiments','Shock sensitivity, rankings and generator ensembles'],['Reproducibility','Executed notebooks, API requests and saved results']],64,175,1150,360);
  note(s,'The UI is removed. Notebooks explain the calculations and the API exposes them.');

  s=slide('Expected loss and scenario loss answer different questions','At an assumed one-period borrower PD of 2%, recovery 40% and exposure 100, expected loss is 0.02*0.60*100=1.2. Conditional on that borrower defaulting, the credit loss is 60. This elementary expected-loss model does not implement IFRS 9 staging, maturity, discounting, calibrated PD or correlated credit migration. The 50-bank seed-42 baseline has 222 loans and ECL 61.805849 synthetic crore.');
  table(s,[['For a loan of 100','Calculation','Result'],['Expected loss','2% × 60% × 100','1.2'],['Loss if borrower defaults','60% × 100','60']],64,190,1150,250);
  text(s,'PD is an assumed probability.\nRecovery is an assumed fraction repaid after default.',64,485,1110,110,30);
  note(s,'Synthetic INR crore. ECL covers direct loan loss, not a forecast of cascade losses.');

  s=slide('The COVID-period market decline is observed','Source: S&P Dow Jones Indices via FRED series SP500, https://fred.stlouisfed.org/series/SP500 . Packaged CSV covers February–April 2020 with 62 numeric daily closes. February 19 close 3386.15, March 23 close 2237.40. Maximum drawdown magnitude 1−2237.40/3386.15 = 33.924959%. Missing observations are dropped without interpolation. Chart uses ordered observed closes, equal spacing per trading observation. Provenance and SHA-256: docs/DATA_PROVENANCE.md.');
  chart(s,'line',evidence.market.map(r=>r.date),[{name:'S&P 500 close',smooth:false,values:evidence.market.map(r=>r.close),line:{fill:C.blue,width:3}}],{yAxis:{min:2000,max:3500,title:'Index points',textStyle:{fontSize:20},majorGridlines:{fill:'#D7E0E3',width:1}}});
  note(s,'Peak 3,386.15 on 19 February. Trough 2,237.40 on 23 March. Drawdown 33.925%.');

  s=slide('The market-to-bank mapping is an assumption','External impairment equals min(1, maximum drawdown magnitude times multiplier). At multiplier 0.30 the impairment is 10.177488%. Apply it to each synthetic bank external assets. The S&P index does not reveal banks’ asset composition, bilateral exposures or default history. This link is a scenario design, not an estimated causal relationship. Every scenario resets the original balance sheet. Source: src/atlas/market.py.');
  text(s,'33.925% × 0.30 = 10.177%',64,190,1150,100,52,C.blue,true);
  body(s,'Observed index drawdown × chosen multiplier\n\nThe result becomes an external-asset write-down in a synthetic banking system.',64,330,1110,230,32);
  note(s,'Observed market prices support the drawdown. They do not establish the bank-loss multiplier.');

  s=slide('Repeated propagation changes the modeled outcome','50 banks, core_periphery, seed 42, 222 directed loans, recovery 0.40. Multiplier 0.30 gives 14 initial defaults. Direct-loss-only gives 21 total. Furfine gives 45 total, hence 24 additional failures relative to the truncated control. These counts describe only the current synthetic dataset and assumptions. Source: presentation/evidence.json generated directly from atlas.baseline and atlas.engine.');
  chart(s,'bar',['Initial shock','Direct-loss-only','Repeated cascade'],[{name:'Synthetic defaults',values:[14,21,45],fill:C.red}],{barOptions:{direction:'column',gapWidth:80},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:27,bold:true}},yAxis:{min:0,max:50,title:'Banks out of 50',textStyle:{fontSize:20},majorGridlines:{fill:'#D7E0E3',width:1}}});
  note(s,'Seed 42, 50 banks, recovery 40%, external impairment 10.177%.');

  s=slide('Results depend strongly on the assumed shock','These exact values come from the generated evidence file. Display impairment rounded to three decimals. A small parameter change can move capital across default thresholds. This is sensitivity, not robustness to real-world uncertainty. At multipliers .2,.3,.4 the total counts are 2,45,50.');
  table(s,[['Multiplier','Impairment','Initial defaults','Final defaults'],...evidence.scenarios.map(r=>[r.multiplier.toFixed(2),(r.impairment*100).toFixed(3)+'%',String(r.initial),String(r.total)])],64,175,1150,350);
  note(s,'Every row starts from the same original balance sheets. Defaults are synthetic.');

  s=slide('Institution rankings are conditional on the scenario','Each bank is forced to default separately with no external shock, recovery .40, unchanged seed-42 network. All 50 single-bank runs have zero secondary defaults. The displayed rank is therefore determined by posted direct loss, not cascade count. B010 218.8414, B009 214.4029, B007 195.1258. Structural degree alone cannot establish loss impact. Source: impact_ranking and presentation/evidence.json.');
  table(s,[['Forced default','Secondary defaults','Posted loss'],...evidence.ranking.slice(0,3).map(r=>[r.bank_id,String(r.secondary_defaults),r.posted_interbank_loss.toFixed(2)])],64,180,1150,290);
  text(s,'No single-bank default triggers a cascade in this baseline.',64,505,1120,90,31,C.green,true);
  note(s,'Synthetic INR crore. A conditional impact ranking is not a probability of bank failure.');

  s=slide('Exploratory extensions and their limits','DebtRank uses a one-active-step variant with capped distress, LGD-scaled weights and total-assets valuation. It is not an empirically calibrated default probability. Under a common positive shock all positive-external-asset nodes begin active, so this one-active-step variant transmits only one wave in that setting. Monte Carlo assumes independent Bernoulli PDs conditional on the fixed shock. MCSE measures numerical uncertainty in the sample mean only. Generator families differ in density, exposure totals and capital as well as structure, so descriptive comparisons cannot identify a causal topology effect.');
  table(s,[['Extension','Implemented analysis','Interpretation limit'],['DebtRank variant','Continuous distress propagation','Different quantity from defaults'],['Monte Carlo','Repeated assumed default draws','Independence and PD assumptions'],['Topology ensemble','Repeated generator-family runs','Density and balance-sheet confounding']],64,180,1150,330);
  note(s,'These analyses extend scenario exploration. They do not establish empirical predictive accuracy.');

  s=slide('Verification supports computational correctness','Tests check arithmetic on manually calculated fixtures, accounting reconciliation, invalid input rejection, edge direction, boundary recovery, deterministic seeds and API agreement. These are implementation verification. Empirical validation requires observed exposures, bank states, calibration targets, out-of-sample design and comparison with observed outcomes. Do not claim a passing test count proves model realism. Conceptual sources: Furfine BIS WP70 (1999, journal 2003), Battiston et al. Scientific Reports 2, 541 (2012).');
  table(s,[['Evidence available now','Evidence still required'],['Hand-calculated cascade and control','Observed bilateral exposures'],['Accounting and invariant tests','Parameter calibration'],['Reproducible seeds and archived inputs','Out-of-sample outcome validation'],['Notebook and API agreement','External review of model adequacy']],64,175,1150,350);
  note(s,'The defensible contribution is a transparent, reproducible experimental framework.');

  s=slide('Contribution, roadmap and discussion','Close: Atlas integrates transparent balance-sheet inputs, directed counterparty risk, benchmark controls, scenario sensitivity and reproducible evidence. It does not introduce a new contagion theory. Next steps: measured bank-level data with provenance, uncertainty-aware reconstruction, empirically motivated shock calibration, alternative clearing/liquidity models, and later a visual-analysis user study. References: Furfine, https://www.bis.org/publ/work70.htm ; Battiston et al., https://doi.org/10.1038/srep00541 ; FRED SP500, https://fred.stlouisfed.org/series/SP500 . Viva: why no ML? No supervised prediction task or labeled dataset. Why synthetic? Bilateral data is unavailable in this prototype. Why one-active-step DebtRank? Explicit exploratory convention. Can you predict a crisis? No empirical forecasting claim.');
  body(s,'Current contribution\nAn auditable framework for conditional credit-contagion experiments.\n\nNext research gate\nCalibrate and validate against suitable observed bank data.',64,170,1110,300,34);
  text(s,'References: Furfine (1999/2003), Battiston et al. (2012), FRED SP500',64,525,1110,95,25,C.gray);
  note(s,'Discussion: model assumptions, baseline choice, scientific limits and validation plan');
  nodeRepl.write({slides:presentation.slides.items.length,sessionId:session.sessionId});
})();

const pptx=await PresentationFile.exportPptx(presentation);await pptx.save(new URL('candidate.pptx', output).pathname);
for(let i=0;i<presentation.slides.items.length;i++){const png=await presentation.export({slide:presentation.slides.items[i],format:'png',scale:1});await fs.writeFile(new URL(`slide-${i+1}.png`, output),new Uint8Array(await png.arrayBuffer()));}
