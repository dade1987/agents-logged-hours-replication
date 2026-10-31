"""Failure audit analysis (exploratory). Final codes = agreed codes; 3 disagreements adjudicated by the main session using the codebook decision rule."""
import json,glob,random,math,collections
import numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from scipy.stats import fisher_exact
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'failure_audit'; S=ROOT/'moodle'
ADJ={'C11':('W','unrequested change of Content-Type behaviour breaks existing behaviour: defect regardless of tests'),
     'C32':('W','validate_redirect_uri never matches registered URIs: required behaviour missing'),
     'C33':('A','agent did what the issue asked; tests check an extra guard the issue does not mention')}
def load(r):
    d={}
    for f in sorted(glob.glob(f'{F}/ratings/rater{r}_b*.jsonl')):
        for l in open(f):
            if l.strip(): x=json.loads(l); d[x['case']]=x['code']
    return d
A,B=load('A'),load('B'); keys=json.load(open(f'{F}/moodle_sample_keys.json'))
for s in keys:
    c=s['case']; s['A']=A[c]; s['B']=B[c]; s['final']=A[c] if A[c]==B[c] else ADJ[c][0]
json.dump(keys,open(f'{F}/moodle_final_codes.json','w'),indent=1)
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return [round(c-h,3),round(c+h,3)]
out={'n':len(keys),'by_stratum':{}}
for st in 'SL':
    xs=[s for s in keys if s['stratum']==st]; cnt=collections.Counter(s['final'] for s in xs); n=len(xs)
    out['by_stratum'][st]={'n':n,'counts':dict(cnt),'M_share':round(cnt['M']/n,3),'M_CI95':wilson(cnt['M'],n),
                           'MA_share':round((cnt['M']+cnt['A'])/n,3),'MA_CI95':wilson(cnt['M']+cnt['A'],n)}
for lab,cs in [('M',{'M'}),('MA',{'M','A'})]:
    t=[[sum(s['final'] in cs for s in keys if s['stratum']==st), sum(s['final'] not in cs for s in keys if s['stratum']==st)] for st in 'SL']
    out[f'fisher_{lab}']={'table_S_L':t,'p':round(fisher_exact(t)[1],4)}
# sensitivity GEE: reclassify M (and M+A) failures as solved
hours={json.loads(l)['key']:json.loads(l)['hours'] for l in open(f'{S}/issues.jsonl')}
valid=open(f'{S}/issues.txt').read().split()
e=pd.read_csv(f'{S}/results.csv'); e=e[(e.cond=='strict')&(e.run==1)&(e.key.isin(valid))]
aud=pd.read_csv(ROOT/'analysis'/'moodle'/'audit_runs.csv').fillna(''); aud=aud[(aud.cond=='strict')&(aud.run==1)]
leak={(r.key,r.model) for r in aud.itertuples() if 'seen' in r.flags}
e=e[[ (k,m) not in leak for k,m in zip(e.key,e.model)]].copy()
e['log2h']=np.log2(e.key.map(hours)); e['stratum']=np.where(e.key.map(hours)<=4,'S','L')
e['model']=pd.Categorical(e.model,categories=['haiku','sonnet','opus','fable'])
code={(s['key'],s['model']):s['final'] for s in keys}
def gee(d):
    m=smf.gee('solved ~ log2h + model',groups='key',data=d,family=sm.families.Binomial(),cov_struct=sm.cov_struct.Exchangeable()).fit()
    return m.params['log2h'], m.bse['log2h']
b,se=gee(e); out['gee_original']={'OR':round(math.exp(b),3),'CI95':[round(math.exp(b-1.96*se),3),round(math.exp(b+1.96*se),3)]}
for lab,cs in [('M',{'M'}),('MA',{'M','A'})]:
    p={st:(sum(s['final'] in cs for s in keys if s['stratum']==st)/sum(1 for s in keys if s['stratum']==st)) for st in 'SL'}
    rng=np.random.default_rng(20261028); est=[];var=[]
    for it in range(200):
        d=e.copy(); y=d.solved.values.copy()
        for i,(k,mo,st,sv) in enumerate(zip(d.key,d.model,d.stratum,d.solved)):
            if sv==1: continue
            c=code.get((k,mo))
            y[i]=int(c in cs) if c is not None else int(rng.random()<p[st])
        d['solved']=y; b,se=gee(d); est.append(b); var.append(se*se)
    est=np.array(est); W=np.mean(var); Bv=np.var(est,ddof=1); T=W+(1+1/len(est))*Bv; bm=est.mean(); st_=math.sqrt(T)
    from scipy.stats import norm
    out[f'gee_reclassify_{lab}']={'impute_share':{k:round(v,3) for k,v in p.items()},'OR':round(math.exp(bm),3),
        'CI95':[round(math.exp(bm-1.96*st_),3),round(math.exp(bm+1.96*st_),3)],'p_one_sided':round(norm.cdf(bm/st_),4),'imputations':len(est)}
json.dump(out,open(f'{F}/moodle_results.json','w'),indent=1); print(json.dumps(out,indent=1))
