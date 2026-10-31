"""Failure audit analysis, MariaDB (exploratory). Same method as analyze_moodle.py; strata <=2 h / >2 h (codebook)."""
import json,glob,math,collections
import numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from scipy.stats import fisher_exact, norm
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'failure_audit'; M=ROOT/'mariadb'
ADJ={'D09':('W','a closely related crash (SP variable in INTERVAL) is left unfixed: defect regardless of tests'),
     'D15':('A','agent rejects definers with a newline, developers escape them; both are reasonable readings of the issue'),
     'D19':('W','agent lets a session with an expired password switch to another user: security defect regardless of tests')}
def load(r):
    d={}
    for f in sorted(glob.glob(f'{F}/ratings/mdb_rater{r}_b*.jsonl')):
        for l in open(f):
            if l.strip(): x=json.loads(l); d[x['case']]=x['code']
    return d
A,B=load('A'),load('B'); keys=json.load(open(f'{F}/mariadb_sample_keys.json'))
n=len(keys); po=sum(A[s['case']]==B[s['case']] for s in keys)/n
pa=collections.Counter(A[s['case']] for s in keys); pb=collections.Counter(B[s['case']] for s in keys); cats='WMAU'
pe=sum(pa[k]*pb[k] for k in cats)/n/n; pi={k:(pa[k]+pb[k])/(2*n) for k in cats}; q=sum(1 for k in cats if pa[k]+pb[k])
out={'n':n,'agreement':{'observed':round(po,3),'kappa':round((po-pe)/(1-pe),3),'AC1':round((po-sum(p*(1-p) for p in pi.values())/(q-1))/(1-sum(p*(1-p) for p in pi.values())/(q-1)),3),
     'disagreements':{s['case']:[A[s['case']],B[s['case']],ADJ[s['case']][0]] for s in keys if A[s['case']]!=B[s['case']]}},'by_stratum':{}}
for s in keys: c=s['case']; s['A']=A[c]; s['B']=B[c]; s['final']=A[c] if A[c]==B[c] else ADJ[c][0]
json.dump(keys,open(f'{F}/mariadb_final_codes.json','w'),indent=1)
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return [round(c-h,3),round(c+h,3)]
for st in 'SL':
    xs=[s for s in keys if s['stratum']==st]; cnt=collections.Counter(s['final'] for s in xs); m=len(xs)
    out['by_stratum'][st]={'n':m,'counts':dict(cnt),'M_share':round(cnt['M']/m,3),'M_CI95':wilson(cnt['M'],m),'MA_share':round((cnt['M']+cnt['A'])/m,3),'MA_CI95':wilson(cnt['M']+cnt['A'],m)}
for lab,cs in [('M',{'M'}),('MA',{'M','A'})]:
    t=[[sum(s['final'] in cs for s in keys if s['stratum']==st), sum(s['final'] not in cs for s in keys if s['stratum']==st)] for st in 'SL']
    out[f'fisher_{lab}']={'table_S_L':t,'p':round(fisher_exact(t)[1],4)}
fz={x['key']:x['hours'] for x in json.load(open(f'{M}/frozen_sample.json'))}
rows=[]
for l in open(f'{M}/results.jsonl'):
    r=json.loads(l); k,mo,c,run=r['run'].split('_')
    if run=='1': rows.append(dict(key=k,model=mo,solved=int(r['result']=='PASS')))
e=pd.DataFrame(rows); e['log2h']=np.log2(e.key.map(fz)); e['stratum']=np.where(e.key.map(fz)<=2,'S','L')
e['model']=pd.Categorical(e.model,categories=['haiku','sonnet','opus','fable'])
code={(s['key'],s['model']):s['final'] for s in keys}
def gee(d):
    m=smf.gee('solved ~ log2h + model',groups='key',data=d,family=sm.families.Binomial(),cov_struct=sm.cov_struct.Exchangeable()).fit(); return m.params['log2h'],m.bse['log2h']
b,se=gee(e); out['gee_original']={'OR':round(math.exp(b),3),'CI95':[round(math.exp(b-1.96*se),3),round(math.exp(b+1.96*se),3)]}
for lab,cs in [('M',{'M'}),('MA',{'M','A'})]:
    p={st:sum(s['final'] in cs for s in keys if s['stratum']==st)/sum(1 for s in keys if s['stratum']==st) for st in 'SL'}
    rng=np.random.default_rng(20261029); est=[];var=[]
    for it in range(200):
        y=e.solved.values.copy()
        for i,(k,mo,st,sv) in enumerate(zip(e.key,e.model,e.stratum,e.solved)):
            if sv: continue
            c=code.get((k,mo)); y[i]=int(c in cs) if c is not None else int(rng.random()<p[st])
        d=e.copy(); d['solved']=y; bb,ss=gee(d); est.append(bb); var.append(ss*ss)
    est=np.array(est); T=np.mean(var)+(1+1/len(est))*np.var(est,ddof=1); bm=est.mean(); st_=math.sqrt(T)
    out[f'gee_reclassify_{lab}']={'impute_share':{k:round(v,3) for k,v in p.items()},'OR':round(math.exp(bm),3),'CI95':[round(math.exp(bm-1.96*st_),3),round(math.exp(bm+1.96*st_),3)],'p_one_sided':round(norm.cdf(bm/st_),4)}
json.dump(out,open(f'{F}/mariadb_results.json','w'),indent=1); print(json.dumps(out,indent=1))
