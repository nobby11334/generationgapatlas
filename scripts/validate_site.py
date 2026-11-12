#!/usr/bin/env python3
"""Fail builds on missing, inconsistent, or syntactically invalid dashboard evidence."""
import json,re,subprocess,sys, tempfile
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(p):return json.loads((ROOT/'data'/p).read_text(encoding='utf-8'))
def ok(cond,msg):
 if not cond:raise AssertionError(msg)
def main():
 grant=load('local-grants-2026.json')
 partners=load('wide-area-partners-2026.json')
 kpi=load('kpis.json')
 first=load('first-job-cohorts.json')
 income=load('income-distribution-2022.json')
 pension=load('pension-cohort-projections.json')
 original_pages=load('official-kpi-pages-2026-10.json')
 funding=load('funding.json')
 measures=load('measures-2026.json')
 report=load('october-2026-official-documents.json')
 market=load('graduate-market.json')
 cohorts=load('wages.json')
 ages=load('age-band-regular-employment.json')
 latest=load('kpi-updates-2026-10.json')
 cases=load('policy-case-studies.json')
 assets=load('household-assets.json')
 wages=load('wages-2024-cross-section.json')
 ok(len(grant['projects'])==152,'grant records != 152')
 ok(sum(x['budget_thousand_yen'] for x in grant['projects'])==grant['total_expense_thousand_yen'],'grant amount mismatch')
 ok(len(set((x['municipality'],x['project'],x['budget_thousand_yen']) for x in grant['projects']))==152,'duplicate grant')
 ok(len(partners['municipalities'])==207,'partners != 207')
 ok(len(set(x['municipality'] for x in partners['municipalities']))==207,'partner duplicates')
 ok(all(x['participating_project'] for x in partners['municipalities']),'partner missing project')
 ok(len(kpi['kpis'])==29,'KPI count')
 ok(len(income['brackets'])==16 and len(income['records'])==90,'income distribution 90 series of 16 brackets missing')
 for item in income['records']:
  ok(len(item['people_by_bracket'])==16,'income brackets inconsistent')
  ok(sum(item['people_by_bracket'])==item['known_income_people'],'income group mismatch')
  ok(item['known_income_people']+item['unknown_income_people']==item['total_people'],'income unknown denominator mismatch')
 ok(len(first['eras'])==5 and all(len(x['regular'])==5 and len(x['nonregular'])==5 for x in first['eras']),'first job cohorts invalid')
 ok(len(pension['rows'])==3,'pension cohorts invalid')
 ok(len(original_pages['pages'])==8,'latest report missing page')
 ok(len(funding['entries'])==29,'budget count')
 ok(len(measures['measures'])==28,'measure count')
 ok(len(report['documents'])==15,'October meeting 15 documents')
 ok(len(market['records'])==26,'graduate hiring 26 years')
 ok([r['year'] for r in market['records']]==list(range(1987,2013)),'graduate hiring gap')
 ok(len(cohorts['cohorts'])==5 and all(len(c['values'])==len(cohorts['age_groups']) for c in cohorts['cohorts']),'wages cohort shape')
 ok(len(ages['historical_years'])==11 and all(len(v)==11 for v in ages['regular_by_age'].values()),'employment age time series incomplete')
 ok(len(latest['updates'])>=6,'2026 follow-up updates missing')
 ok(len(assets['data'])>=5,'household asset age bands missing')
 ok(len(wages['rows'])>=10,'2024 salary ages missing')
 ok(len(cases['cases'])>=2,'policy-case count')
 paths=['age-band-regular-employment','wages','household-assets','graduate-market','wages-2024-cross-section','policy-case-studies','kpi-updates-2026-10','october-2026-official-documents','local-grants-2026','wide-area-partners-2026','kpis','funding','measures-2026','employment-history','source-register','official-kpi-pages-2026-10','first-job-cohorts','pension-cohort-projections','income-distribution-2022']
 html=(ROOT/'index.html').read_text(encoding='utf-8')
 for p in paths:
  ok((ROOT/'data'/f'{p}.json').exists(),f'file missing {p}')
  ok(p in html or p in ('employment-history','source-register'),f'no frontend reference {p}')
 js=re.findall(r'<script>(.*?)</script>',html,re.DOTALL)
 ok(len(js)>=9,'script blocks missing')
 if subprocess.run(['node','--version'],capture_output=True).returncode==0:
  with tempfile.TemporaryDirectory() as temp:
   for i,source in enumerate(js):
    path=Path(temp)/f'inline-{i}.js';path.write_text(source,encoding='utf-8')
    check=subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
    ok(check.returncode==0,f'Inline JavaScript {i} syntax invalid: {check.stderr}')
 print(f'PASS: {len(paths)} datasets, 152 projects, 207 partners, 29 KPIs, 15 official PDFs, 26 graduating classes; JS parsed')
if __name__=='__main__':main()
