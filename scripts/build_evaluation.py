"""Build the presentation notebook and immutable input manifest (no network)."""

import argparse
import hashlib
import json
import platform
from pathlib import Path
from urllib.parse import urlencode

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Overwrite notebook 03 and rebuild the frozen-input manifest."
    )
    parser.parse_args()
    raw = ROOT / "data/raw"
    fields = "CERT,CERTCONS,BKCLASS,NAME,REPDTE,ASSET,EQ,EQTOT,DEP,LIAB"
    items = []
    for date in ["20191231", "20200630"]:
        p = raw / f"fdic_{date}.json"
        items.append(
            {
                "file": str(p.relative_to(ROOT)),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "source": "https://api.fdic.gov/banks/financials?"
                + urlencode(
                    {
                        "filters": f"REPDTE:{date}",
                        "fields": fields,
                        "sort_by": "ASSET",
                        "sort_order": "DESC",
                        "limit": 100,
                        "format": "json",
                    }
                ),
                "reference_date": date,
                "retrieved": "2026-11-01",
                "units": "USD thousands",
                "vintage": "Latest revised historical observations downloaded on retrieval date; not a real-time vintage",
            }
        )
    for file, url in [
        ("data/raw/fdic_field_definitions.yaml", "https://api.fdic.gov/banks/docs/risview_properties.yaml"),
        (
            "src/atlas/data/sp500_2020.csv",
            "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd=2020-02-01&coed=2020-04-30",
        ),
    ]:
        p = ROOT / file
        items.append({"file": file, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "source": url})
    (ROOT / "data/manifest.json").write_text(json.dumps(items, indent=2))
    cells = []

    def md(s):
        c = nbf.v4.new_markdown_cell(s)
        c.metadata.slideshow = {"slide_type": "slide"}
        cells.append(c)

    def code(s):
        c = nbf.v4.new_code_cell(s)
        c.metadata.slideshow = {"slide_type": "subslide"}
        cells.append(c)

    md(
        """# ATLAS\n## Observed bank capital under historical market stress\n### Research demonstration · 2 November 2026\n**Question → literature → data → methods → results → verification → limitations**\n\n30 large US banks · December 2019 baseline · June 2020 observed comparison\n\n**Claim:** reproducible conditional stress analysis using official financial observations. The bank-to-bank contagion engine is demonstrated separately on a controlled network."""
    )
    md(
        """# 1 · Research question and scope\n**RQ:** How does a uniform hypothetical asset impairment affect the capital buffers of a fixed cohort of large US banks, and how sensitive is capital exhaustion to the assumed market-to-asset loss mapping?\n\n**Secondary descriptive question:** How did reported equity/assets ratios change between December 2019 and June 2020?\n\nA bank's equity absorbs losses. For assets A and equity E, an assumed loss qA leaves E − qA. The break-even impairment is E/A. These are static accounting scenarios, not predictions of legal default.\n\n**Scope:** no inferred bilateral network, estimated PDs, liquidity runs, fiscal/monetary responses, or forecast validation in the empirical experiment."""
    )
    md(
        """# 2 · Literature and the data decision\n| Prior work | Relevant lesson | Atlas decision |\n|---|---|---|\n| Battiston et al., *Leveraging the network* (2015), DOI 10.1515/strm-2015-0005 | Uses commercial Bankscope and estimated networks | Public financials require a separate field audit |\n| Macchiati et al., *Interbank network reconstruction enforcing density and reciprocity* (2024), DOI 10.1016/j.chaos.2024.115279 | Totals alone do not identify topology; method addresses binary links | Do not manufacture observed loan amounts |\n| Niu et al., *iConViz* (2020), DOI 10.1109/VAST50239.2020.00013 | Private company-guarantee data; case-study evaluation | Useful design precedent; different network mechanism |\n| Eisenberg & Noe (2001), DOI 10.1287/mnsc.47.2.236.9835 | Simultaneous clearing | Future model comparison; current engine is fixed-recovery |\n\nUndermind review: 292 search results; focused full-text reading of four papers. This is a focused synthesis, not an exhaustive systematic review. No algorithmic novelty is claimed."""
    )
    code("""from pathlib import Path
    import json, sys, platform
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from IPython.display import display
    from atlas.observed import load_snapshot, cohort, stress, checksum
    from atlas.market import market_data, calibration
    ROOT = Path.cwd()
    if not (ROOT / 'data/manifest.json').exists(): ROOT = ROOT.parent
    assert (ROOT / 'data/manifest.json').exists()
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({'figure.figsize': (11, 5), 'font.size': 12, 'axes.spines.top': False, 'axes.spines.right': False})
    manifest = json.loads((ROOT / 'data/manifest.json').read_text())
    for item in manifest: assert checksum(ROOT / item['file']) == item['sha256']
    print('Input checksums verified | Python', platform.python_version())""")
    md(
        """# 3 · Sources, aggregation and normalization\n- FDIC official API: largest 100 reporting institutions by assets at each date; raw responses retained.\n- Baseline cohort: largest 30 eligible December 2019 banks, positive assets/equity, supported bank classes, no reported parent-bank consolidation (`CERTCONS=0`).\n- Fixed cohort joined by FDIC certificate, not bank name. Follow-up missingness remains visible; no replacement with surviving banks.\n- Monetary amounts: source USD thousands → USD millions. Ratios remain dimensionless. No z-score normalization of accounting amounts.\n- `EQTOT` reconciles total assets and liabilities; `EQ` is retained in raw data but not substituted. Rounding tolerance: $2,000.\n- FRED daily S&P 500 prices remain a separate time series. No daily interpolation of balance sheets.\n\nHistorical reports are retrieved in their current revised vintage; the exercise is retrospective, not a no-look-ahead backtest. Cohort sums describe these bank reports, not the entire US banking system."""
    )
    code("""before = load_snapshot(ROOT/'data/raw/fdic_20191231.json')
    after = load_snapshot(ROOT/'data/raw/fdic_20200630.json')
    banks = cohort(before, after, 30)
    audit = pd.DataFrame({'date':['2019-12-31','2020-06-30'], 'raw_rows':[len(before),len(after)], 'eligible_rows':[int(before.eligible.sum()),int(after.eligible.sum())], 'max_abs_accounting_residual_USD_thousand':[before.accounting_residual_usd_thousand.abs().max(),after.accounting_residual_usd_thousand.abs().max()]})
    display(audit)
    print('Fixed cohort:',len(banks),' | Matched follow-up:',banks.equity_later.notna().sum())
    assert len(banks)==30 and banks.bank_id.is_unique
    assert banks.eligible_later.fillna(False).all(), 'Follow-up needs review'
    (ROOT/'data/processed').mkdir(exist_ok=True)
    banks.to_csv(ROOT/'data/processed/bank_cohort.csv',index=False)
    display(banks[['bank_id','NAME','assets','equity','equity_ratio']].head(10).round(4))""")
    md(
        """# 4 · What the observed data show\nThe following ratios are calculated from reported financial statements. A change across dates can reflect earnings, distributions, capital issuance, balance-sheet growth, acquisitions and other factors. It does not isolate COVID's causal effect."""
    )
    code("""ordered=banks.sort_values('equity_ratio')
    fig, ax=plt.subplots(figsize=(12,8))
    y=np.arange(len(ordered))
    ax.hlines(y,ordered.equity_ratio*100,ordered.equity_ratio_later*100,color='#b6c4d0')
    ax.scatter(ordered.equity_ratio*100,y,label='December 2019',color='#245a81')
    ax.scatter(ordered.equity_ratio_later*100,y,label='June 2020',color='#bf6636',marker='D')
    ax.set_yticks(y,ordered.NAME,fontsize=8);ax.set_xlabel('Reported total equity / assets (%)');ax.legend()
    ax.set_title('Fixed baseline cohort: observed capital ratios');plt.tight_layout();plt.show()""")
    md(
        """# 5 · Historical stress driver\nThe S&P 500 drawdown is observed. It is an equity price-index movement, not the loss rate on bank assets. Define q = m × D, where D is the selected-window drawdown and m is an assumed transmission multiplier. We sweep m rather than estimate it from these data.\n\nThe main sensitivity experiment uses q directly, so it remains interpretable independently of the market mapping."""
    )
    code("""market=market_data(); mapping=calibration(multiplier=.3)
    fig, axes=plt.subplots(1,2,figsize=(12,4))
    axes[0].plot(market.date,market.close,color='#245a81');axes[0].set_title('Observed S&P 500 close');axes[0].set_ylabel('Index points')
    axes[1].plot(market.date,100*market.drawdown,color='#bf6636');axes[1].set_title('Within-window drawdown');axes[1].set_ylabel('%')
    for ax in axes: ax.tick_params(axis='x',rotation=30)
    plt.tight_layout();plt.show()
    display(pd.Series(mapping))""")
    md(
        """# 6 · Model specification and evaluation plan\n$$L_i=q A_i,\\quad E_i'=E_i-L_i,\\quad q_i^*=E_i/A_i$$\n\nReport (a) bank-level remaining equity; (b) number with nonpositive modeled equity; (c) summed capital shortfall. Assets receive a uniform hypothetical haircut, including categories with different real risk. Liabilities are held fixed. No earnings, recapitalization, hedging, tax or policy response is modeled.\n\n**Verification:** hand calculations; zero-shock control; threshold identity; monotonic exhaustion counts; source checksums; accounting reconciliation.\n\n**Empirical limitation:** the observed June financials are descriptive context, not ground-truth losses from this hypothetical model. No accuracy score is justified."""
    )
    code("""grid=np.linspace(0,.20,81)
    rows=[]
    for q in grid:
     r=stress(banks,float(q))
     rows.append({'impairment':q,'capital_exhausted':int(r.capital_exhausted.sum()),'capital_shortfall_usd_million':float(r.capital_shortfall.sum())})
    sensitivity=pd.DataFrame(rows)
    assert sensitivity.capital_exhausted.is_monotonic_increasing
    assert stress(banks,0).capital_exhausted.sum()==0
    assert np.allclose(stress(banks,0).remaining_equity,banks.equity)
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    axes[0].step(sensitivity.impairment*100,sensitivity.capital_exhausted,where='post',color='#245a81')
    axes[0].set_ylabel('Banks with exhausted modeled capital');axes[0].set_ylim(0,31)
    axes[1].plot(sensitivity.impairment*100,sensitivity.capital_shortfall_usd_million/1000,color='#bf6636')
    axes[1].set_ylabel('Modeled capital shortfall (USD billions)')
    for ax in axes: ax.set_xlabel('Assumed uniform asset impairment (%)')
    plt.tight_layout();plt.show()
    sensitivity.to_csv(ROOT/'data/processed/stress_sensitivity.csv',index=False)""")
    md(
        """# 7 · Scenario results and sensitivity\nThe 0.3 multiplier is illustrative. All results below are conditional on the same static haircut model. Capital exhaustion does not indicate an observed bank failure."""
    )
    code("""scenarios=[]
    for m in [0,.1,.2,.3,.4,.5]:
     q=min(1,m*mapping['drawdown_magnitude']);r=stress(banks,q)
     scenarios.append({'assumed_multiplier':m,'asset_impairment_pct':100*q,'capital_exhausted':int(r.capital_exhausted.sum()),'shortfall_USD_billion':r.capital_shortfall.sum()/1000})
    scenario_table=pd.DataFrame(scenarios);display(scenario_table.round(3))
    result=stress(banks,mapping['external_impairment'])
    display(result.sort_values('remaining_equity')[['NAME','equity_ratio','loss','remaining_equity','capital_exhausted']].head(10).round(3))
    result.to_csv(ROOT/'data/processed/scenario_results.csv',index=False)
    scenario_table.to_csv(ROOT/'data/processed/market_mapping_scenarios.csv',index=False)""")
    md(
        """# 8 · Contagion mechanism: independent controlled demonstration\nThe empirical experiment above has **no measured bilateral lending edges**. To explain the implemented network mechanism, use a separate synthetic three-bank chain:\n\nA lends B 100; C lends A 80; recovery is 40%. B is forced to default. A loses 60 against equity 50, then C loses 48 against equity 40. Gross posted losses total 108. A direct-loss-only control stops at 60.\n\nThis verifies propagation arithmetic; it does not describe the named FDIC banks. Losses move from debtor to creditor, opposite the lending arrow."""
    )
    code("""from atlas.models import Bank, Dataset, Exposure, Scenario
    from atlas.engine import furfine
    chain=Dataset(units='Synthetic monetary units',topology='hand_chain',banks=[
     Bank(id='A',name='A',external_assets=100,interbank_assets=100,interbank_liabilities=80,deposits=70,equity=50),
     Bank(id='B',name='B',external_assets=150,interbank_assets=0,interbank_liabilities=100,deposits=30,equity=20),
     Bank(id='C',name='C',external_assets=20,interbank_assets=80,interbank_liabilities=0,deposits=60,equity=40)],
     exposures=[Exposure(lender='A',borrower='B',amount=100),Exposure(lender='C',borrower='A',amount=80)])
    cascade=furfine(chain,Scenario(initial_defaults=['B'],recovery=.4))
    assert cascade['default_count']==3 and np.isclose(cascade['interbank_loss'],108)
    display(pd.DataFrame(cascade['events']))
    display(pd.DataFrame([{'round':r['round'],'new_defaults':', '.join(r['new_defaults']),'cumulative_defaults':r['cumulative_defaults']} for r in cascade['rounds']]))""")
    md(
        """# 9 · Findings, contribution and limits\n- Observed capital buffers differ across the fixed cohort; the threshold q*=E/A explains the order of modeled exhaustion under a uniform shock.\n- Scenario outcomes depend strongly on the chosen asset impairment. A historical market drawdown alone cannot identify that impairment.\n- Reported financial changes and conditional stress outcomes answer different questions.\n- The reproducible pipeline, audit trail and documented tests are the demonstrated engineering contribution.\n- Network reconstruction and empirical contagion validation remain open work. Complete compatible lending/borrowing margins and uncertainty analysis are needed before extending the named-bank experiment.\n\n**Next research milestone:** hold observed margins fixed and compare contagion outcomes across multiple plausible exposure reconstructions. No novelty or superiority is established at this stage."""
    )
    code("""summary={'cohort_size':len(banks),'baseline':'2019-12-31','followup':'2020-06-30','observed_drawdown':mapping['drawdown_magnitude'],'assumed_multiplier':.3,'assumed_impairment':mapping['external_impairment'],'capital_exhausted':int(result.capital_exhausted.sum()),'shortfall_usd_million':float(result.capital_shortfall.sum()),'chain_loss':cascade['interbank_loss'],'python':platform.python_version(),'inputs_verified':True}
    (ROOT/'reports/real_data_summary.json').write_text(json.dumps(summary,indent=2))
    display(pd.Series(summary))
    print('All notebook assertions passed. Outputs saved under data/processed and reports/.')""")
    md(
        """# 10 · References and reproducibility\n- [FDIC API documentation](https://api.fdic.gov/banks/docs) and packaged official field definitions.\n- [FRED SP500 series and usage notes](https://fred.stlouisfed.org/series/SP500). The packaged market fixture retains its separate provenance and provider rights.\n- [Literature decision review](https://app.undermind.ai/projects/0fc02641-fd90-41a3-bd60-b5043202955b?path=/Atlas%20data%20and%20literature%20decision%20review).\n- Literature DOIs on slide 2; methodology and acquisition URLs in `docs/research/PROTOCOL.md` and `data/manifest.json`.\n\nRun all cells from a fresh kernel. Offline replay uses raw snapshots; `scripts/fetch_observed.py` is an explicit online refresh. A refresh changes data vintage and requires re-execution.\n\n**Discussion:** what additional evidence would justify turning this scenario study into a validated contagion model?"""
    )
    nb = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3 (Atlas)", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": platform.python_version()},
        },
    )
    nbf.write(nb, ROOT / "notebooks/03_real_data_defense.ipynb")
    print("Built notebook and manifest")


if __name__ == "__main__":
    main()
