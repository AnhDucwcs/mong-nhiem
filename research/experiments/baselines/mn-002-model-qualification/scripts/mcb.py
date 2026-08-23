#!/usr/bin/env python3
"""Local, experiment-specific MCB v0.1.0 generator, validator, and runner."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'benchmark'; C=B/'cases'; S=ROOT/'schemas'; F=ROOT/'configs'; RUNS=ROOT/'runs'; REPORTS=ROOT/'reports'
MODELS=Path(r'D:\Code\mong-nhiem\artifacts\models\mn-002'); BIN=Path(r'D:\Materials\llama.cpp\build\bin\Release')
SUITES=('instruction_following','structured_output','context_retrieval','state_tracking','causal_reasoning'); LIMITS=dict(zip(SUITES,(.8,.9,.8,.7,.7),strict=True))
MODELS_REQUIRED=('Qwen3-1.7B-Q4_K_M.gguf','Llama-3.2-3B-Instruct-Q4_K_M.gguf','SmolLM3-Q4_K_M.gguf','microsoft_Phi-4-mini-instruct-Q4_K_M.gguf','gemma-3-4b-it-Q4_K_M.gguf','Qwen3-4B-Q4_K_M.gguf')
def dump(p:Path,x:Any): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def load(p:Path): return json.loads(p.read_text(encoding='utf8'))
def cmd(a:list[str]):
 p=subprocess.run(a,capture_output=True,text=True,encoding='utf8',errors='replace',check=False);return(p.stdout or '')+(p.stderr or '')
def digest(p:Path):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def q(i:int,s:str,context:str,prompt:str,expected:dict[str,Any],method='normalized_exact_match',tokens=32):
 return {'id':f'{s.replace("_","-")}-{i:03d}','suite':s,'version':1,'tags':['synthetic',s],'input':{'system':None,'context':context,'prompt':prompt},'expected':expected,'evaluation':{'method':method},'generation':{'max_tokens':tokens}}
def ins():
 vals=['amber','cedar','orbit','lantern','17','204','+','@','north','SABLE','river','ember','BETA','lucid','prism','violet','731','a','quartz','calm harbor']
 ps=[f'Return only this exact text, no explanation or punctuation: {x}' for x in vals]
 ps[10]='Choose the second item and return only it: moss, river, cloud';ps[11]='Choose the last item and return only it: pine, slate, ember';ps[15]='Return only the text inside brackets: [violet]';ps[16]='Return only the value after equals: code=731';ps[17]='Return only the third letter of piano';ps[18]='Return only the first item: quartz | willow | tide'
 return[q(i,'instruction_following','',p,{'value':v},tokens=16)for i,(p,v)in enumerate(zip(ps,vals,strict=True),1)]
def obj(v):
 def t(x):return'boolean'if isinstance(x,bool)else'integer'if isinstance(x,int)else'string'
 return{'type':'object','properties':{k:{'type':t(x),'const':x}for k,x in v.items()},'required':list(v),'additionalProperties':False}
def struct():
 vals=[{'name':'Ivy','active':True},{'count':3},{'enabled':False,'label':'north'},{'code':'A7','rank':2},{'ready':True,'retries':0},{'city':'Luma','zone':'east'},{'id':19,'valid':True},{'color':'teal','size':4},{'open':False,'reason':'sealed'},{'owner':'Nia','score':8},{'kind':'signal','urgent':False},{'step':5,'done':True},{'token':'r4','weight':1},{'level':'low','visible':True},{'letter':'Q','index':17},{'mode':'quiet','limit':12},{'path':'west','blocked':False},{'title':'Map','pages':6},{'group':'oak','member':'Rin'},{'key':'delta','value':42}]
 return[q(i,'structured_output','',f'Return only valid JSON, no Markdown. Return exactly: {json.dumps(v)}',{'schema':obj(v)},'json_schema',48)for i,v in enumerate(vals,1)]
def retrieve():
 items=[('Nela','badge color','cobalt'),('Miro','pass type','silver'),('Rook','route','west gate'),('Sera','compass direction','118 degrees'),('Nori','cache location','under marker P'),('Mela','archive label','Q-17'),('Kivo','vial fluid','amber'),('Aster','channel','41'),('Lina','parcel mark','fragile'),('Harbor','meeting room','Cedar'),('Umber','serial','506'),('Cinder','target temperature','63 C'),('Jae','notebook owner','Jae'),('Hush','signal priority','three'),('Delta','map shelf','nine'),('Orin','key location','drawer blue'),('Vale','bridge team','Vale'),('Sunrise','project code','marigold'),('North beacon','flash interval','12 seconds'),('Rin','locker number','27')];out=[]
 for i,(who,field,a)in enumerate(items,1):
  target=f'The {field} for {who} is {a}.';fill=[f'Record {n}: unrelated marker {i}-{n}.'for n in range(9)];wrong=f'The {field} for {who}x is wrong-{i}.';lines=[target,*fill,wrong]if i%3==1 else[*fill[:4],target,wrong,*fill[4:]]if i%3==2 else[wrong,*fill,target]
  out.append(q(i,'context_retrieval','\n'.join(lines),f'According to the context, what is the {field} for {who}? Return only the answer.',{'value':a},tokens=24))
 return out
def state():
 specs=[('A has the key.\nA gives the key to B.\nB gives the key to C.','Who has the key now?','C'),('The coin is in box Red.\nMove the coin to box Blue.','Where is the coin now?','box Blue'),('Ira owns the lamp.\nIra gives the lamp to Nia.\nNia gives the lamp to Oren.','Who owns the lamp now?','Oren'),('The board shows status open.\nSet status to closed.\nSet status to pending.','What is the current status?','pending'),('Milo is at the dock.\nMilo walks to the gate.\nMilo walks to the archive.','Where is Milo now?','the archive'),('The tray contains a bead and a pin.\nRemove the pin.','Which item remains?','bead'),('Vera has file K.\nVera gives file K to Sol.\nSol gives file K to Vera.','Who has file K now?','Vera'),('The switch is off.\nTurn the switch on.\nTurn the switch off.','What is the switch state?','off'),('A map is on desk One.\nMove it to desk Two.\nMove it to desk Three.','Where is the map now?','desk Three'),('Kian holds the torch.\nKian gives it to Lea.','Who holds the torch now?','Lea'),('The roster has Aya and Bo.\nRemove Bo.\nAdd Cy.','Return names in alphabetical order, comma only.','Aya,Cy'),('The vault code is 11.\nOverwrite it with 28.','What is the code now?','28'),('Nox is in room A.\nNox moves to room B.\nNox moves to room A.','Where is Nox now?','room A'),('Pia owns a card.\nPia gives it to Quin.\nQuin gives it to Rae.\nRae gives it to Sol.','Who owns the card now?','Sol'),('The cart holds crate X.\nAdd crate Y.\nRemove crate X.','Which crate remains?','crate Y'),('The signal is weak.\nUpdate it to strong.','What is the latest signal state?','strong'),('Uma is at the tower.\nUma travels to the lake.\nUma travels to the mill.','Where is Uma now?','the mill'),('The folder contains note A.\nAdd note B.\nDelete note A.','Which note remains?','note B'),('Ren has the seal.\nRen gives the seal to Tia.\nTia gives the seal to Uma.','Who has the seal now?','Uma'),('The display reads 4.\nChange it to 9.\nChange it to 2.','What does the display read now?','2')]
 return[q(i,'state_tracking',c,p,{'value':a},tokens=24)for i,(c,p,a)in enumerate(specs,1)]
def cause():
 specs=[('If a valve opens, water flows.\nThe valve opens.','What follows?','water flows'),('If a fuse burns, the alarm sounds.\nIf the alarm sounds, the guard wakes.\nThe fuse burns.','Who wakes?','the guard'),('If rain falls, the path is wet.\nIf the path is wet, boots get muddy.\nRain falls.','What happens to the boots?','boots get muddy'),('If the gate is locked, entry is blocked.\nThe gate is locked.','What is the consequence?','entry is blocked'),('If a seed gets water, it sprouts.\nThe seed gets no water.','Does the seed sprout? Return only yes or no.','no'),('If lamp A is on, the room is lit.\nLamp B is on.\nLamp A is off.','Is the room lit? Return only yes or no.','no'),('If a message is signed, it is accepted.\nThe message is unsigned.','Is it accepted? Return only yes or no.','no'),('If the pump runs, the tank fills.\nIf the tank fills, the gauge rises.\nThe pump runs.','What happens to the gauge?','the gauge rises'),('If a battery is charged, the sensor starts.\nThe battery is charged.','What starts?','the sensor'),('If a bridge is closed, traffic stops.\nThe bridge is open.','Does traffic stop? Return only yes or no.','no'),('If the switch is pressed, a bell rings.\nThe bell rings.\nNo rule says bells imply switches were pressed.','Can you conclude it was pressed? Return only yes or no.','no'),('If a file is encrypted, it needs a key.\nThe file is encrypted.','What does the file need?','a key'),('If a beacon is active, it sends a signal.\nIf it sends a signal, the monitor records it.\nThe beacon is active.','What does the monitor do?','the monitor records it'),('If the lens is clean, the image is sharp.\nThe lens is dirty.','Is the image guaranteed sharp? Return only yes or no.','no'),('If the lock receives code 7, it opens.\nThe lock receives code 7.','What happens to the lock?','it opens'),('If a route is clear, the drone departs.\nThe route is blocked.','Does the drone depart? Return only yes or no.','no'),('If the server restarts, the cache clears.\nIf the cache clears, stale data disappears.\nThe server restarts.','What disappears?','stale data'),('If a marker is blue, it is selected.\nThe marker is red.\nA different marker is blue.','Is the red marker selected? Return only yes or no.','no'),('If the key turns, the door unlocks.\nThe key turns.','What happens to the door?','the door unlocks'),('If a report is complete, it is sent.\nThe report is incomplete.','Is the report sent? Return only yes or no.','no')]
 return[q(i,'causal_reasoning',c,p,{'value':a},tokens=24)for i,(c,p,a)in enumerate(specs,1)]
def schemas():
 common={'type':'object','additionalProperties':False};case={'$schema':'https://json-schema.org/draft/2020-12/schema',**common,'required':['id','suite','version','tags','input','expected','evaluation','generation'],'properties':{'id':{'type':'string','pattern':'^[a-z]+(?:-[a-z]+)*-[0-9]{3}$'},'suite':{'enum':list(SUITES)},'version':{'const':1},'tags':{'type':'array'},'input':{'type':'object','additionalProperties':False,'required':['system','context','prompt'],'properties':{'system':{'type':['string','null']},'context':{'type':'string'},'prompt':{'type':'string'}}},'expected':{'type':'object','additionalProperties':False,'properties':{'value':{},'schema':{'type':'object'}}},'evaluation':{'type':'object','additionalProperties':False,'required':['method'],'properties':{'method':{'enum':['exact_match','normalized_exact_match','choice_match','json_schema','contains_all','unordered_set_match','numeric_match']}}},'generation':{'type':'object','additionalProperties':False,'required':['max_tokens'],'properties':{'max_tokens':{'type':'integer','minimum':1,'maximum':256}}}}}
 result={'$schema':'https://json-schema.org/draft/2020-12/schema',**common,'required':['case_id','output','evaluation','usage','timing','error'],'properties':{'case_id':{'type':'string'},'output':{'type':'object','additionalProperties':False,'required':['text','parsed'],'properties':{'text':{'type':'string'},'parsed':{}}},'evaluation':{'type':'object','additionalProperties':False,'required':['passed','score'],'properties':{'passed':{'type':'boolean'},'score':{'type':'number','minimum':0,'maximum':1}}},'usage':{'type':'object'},'timing':{'type':'object'},'error':{'type':['object','null']}}}
 meta={'$schema':'https://json-schema.org/draft/2020-12/schema',**common,'required':['run_id','created_at','benchmark','repository','model','runtime','inference','hardware','command'],'properties':{'run_id':{'type':'string'},'created_at':{'type':'string'},'benchmark':{'type':'object'},'repository':{'type':'object'},'model':{'type':'object','required':['name','file','size_bytes','sha256'],'properties':{'name':{'type':'string'},'file':{'type':'string'},'size_bytes':{'type':'integer'},'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}}},'runtime':{'type':'object'},'inference':{'type':'object'},'hardware':{'type':'object'},'command':{'type':'object'}}}
 summary={'$schema':'https://json-schema.org/draft/2020-12/schema',**common,'required':['run_id','run_status','qualification','overall','suites','performance'],'properties':{'run_id':{'type':'string'},'run_status':{'enum':['valid','invalid','error']},'qualification':{'type':'object'},'overall':{'type':['object','null']},'suites':{'type':'object'},'performance':{'type':'object'}}}
 return{'benchmark-case.schema.json':case,'run-metadata.schema.json':meta,'case-result.schema.json':result,'run-summary.schema.json':summary}
def write():
 for s,x in zip(SUITES,(ins(),struct(),retrieve(),state(),cause()),strict=True):C.mkdir(parents=True,exist_ok=True);(C/f'{s}.jsonl').write_text(''.join(json.dumps(i,ensure_ascii=False)+'\n'for i in x),encoding='utf8')
 dump(B/'manifest.yaml',{'id':'mcb','version':'0.1.0','minimum_overall_score':.8,'total_cases':100,'suites':[{'id':s,'cases':20,'critical':True,'minimum_score':LIMITS[s]}for s in SUITES]})
 for n,x in schemas().items():dump(S/n,x)
 dump(F/'qualification-config.json',{'temperature':0.0,'seed':42,'context_size':4096,'threads':12,'gpu_layers':'all','batch_size':2048,'host':'127.0.0.1','port':18080,'chat_template':'GGUF metadata via --jinja','performance':{'prompt_tokens':512,'generation_tokens':64,'repetitions':3}})
def allcases():return[json.loads(l)for s in SUITES for l in(C/f'{s}.jsonl').read_text(encoding='utf8').splitlines()if l]
def valid():
 v=Draft202012Validator(load(S/'benchmark-case.schema.json'));x=allcases();counts={s:0 for s in SUITES};errors=[]
 for i in x:counts[i.get('suite','')]=counts.get(i.get('suite',''),0)+1;errors += [f"{i.get('id')}: {e.message}"for e in v.iter_errors(i)]
 if len(x)!=100 or len({i['id']for i in x})!=100 or any(counts[s]!=20 for s in SUITES):errors.append(f'case counts: {counts}, total={len(x)}')
 if errors:raise RuntimeError('\n'.join(errors))
 print('Validated MCB v0.1.0: 100 cases, 20 per suite.')
def api(url,data):
 r=urllib.request.Request(url,json.dumps(data).encode(),{'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(r,timeout=180)as z:return json.loads(z.read().decode())
def norm(x):return' '.join(x.strip().split())
def evalcase(c,text):
 if c['evaluation']['method']=='json_schema':
  try:p=json.loads(text)
  except json.JSONDecodeError:return False,None
  return not list(Draft202012Validator(c['expected']['schema']).iter_errors(p)),p
 return norm(text)==norm(str(c['expected']['value'])),norm(text)
def hw():
 x={'gpu':None,'driver':None,'cuda':None,'vram_bytes':None}
 if shutil.which('nvidia-smi'):
  r=cmd(['nvidia-smi','--query-gpu=name,driver_version,memory.total','--format=csv,noheader,nounits']).splitlines()
  if r and len(r[0].split(','))==3:n,d,m=(z.strip()for z in r[0].split(','));x.update(gpu=n,driver=d,vram_bytes=int(m)*1048576)
  z=re.search(r'CUDA Version:\s*([^\s|]+)',cmd(['nvidia-smi']));x['cuda']=z.group(1)if z else None
 try:ram=os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')
 except (AttributeError,ValueError,OSError):ram=None
 return{'os':platform.platform()or None,'cpu':platform.processor()or None,'ram_bytes':ram,**x}
def run(model:Path,server:Path,bench:Path,port:int):
 valid();cfg=load(F/'qualification-config.json');rid=f"{dt.datetime.now(dt.UTC):%Y%m%dT%H%M%SZ}-{re.sub('[^a-z0-9]+','-',model.stem.lower()).strip('-')}-{uuid.uuid4().hex[:8]}";r=RUNS/rid;raw=r/'raw';raw.mkdir(parents=True)
 version=cmd([str(server),'--version'])
 match=re.search(r'version:\s*([^\n]+?)\s*\(build\s+(\d+),\s*commit\s+([0-9a-f]+)\)',version,re.IGNORECASE)
 command=[str(server),'-m',str(model),'--host',cfg['host'],'--port',str(port),'-c',str(cfg['context_size']),'-t',str(cfg['threads']),'-b',str(cfg['batch_size']),'-ngl',str(cfg['gpu_layers']),'-fa','on','--temp','0','--seed','42','--jinja','--no-webui','--metrics']
 meta={'run_id':rid,'created_at':dt.datetime.now(dt.UTC).isoformat(),'benchmark':{'id':'mcb','version':'0.1.0'},'repository':{'commit':cmd(['git','rev-parse','HEAD']).strip()or None},'model':{'name':model.stem,'file':model.name,'size_bytes':model.stat().st_size,'sha256':digest(model)},'runtime':{'backend':'llama.cpp','version':match.group(1).strip()if match else None,'build':match.group(2)if match else None,'commit':match.group(3)if match else None,'raw_version_output':version},'inference':{'temperature':0.0,'seed':42,'context_size':4096,'threads':cfg['threads'],'gpu_layers':cfg['gpu_layers'],'batch_size':cfg['batch_size'],'chat_template':cfg['chat_template']},'hardware':hw(),'command':{'server':command,'benchmark':None}};dump(r/'metadata.json',meta);so,se=(raw/'llama-server.stdout.txt').open('w',encoding='utf8'),(raw/'llama-server.stderr.txt').open('w',encoding='utf8');p=None;records=[];problem=None
 try:
  p=subprocess.Popen(command,stdout=so,stderr=se);base=f"http://{cfg['host']}:{port}";deadline=time.monotonic()+180
  while time.monotonic()<deadline:
   if p.poll()is not None:raise RuntimeError(f'llama-server exited: {p.returncode}')
   try:
    with urllib.request.urlopen(base+'/health',timeout=2)as h:
     if h.status==200:break
   except(urllib.error.URLError,TimeoutError):time.sleep(1)
  else:raise RuntimeError('llama-server did not become ready in 180 seconds')
  for c in allcases():
   started=time.perf_counter();content='\n\n'.join(x for x in(c['input']['context'],c['input']['prompt'])if x)
   try:z=api(base+'/v1/chat/completions',{'messages':[{'role':'user','content':content}],'temperature':0,'seed':42,'max_tokens':c['generation']['max_tokens']});text=z['choices'][0]['message']['content']or'';passed,parsed=evalcase(c,text);use=z.get('usage',{});err=None
   except (KeyError, OSError, TimeoutError, urllib.error.URLError, ValueError) as e:text,parsed,passed,use,err='',None,False,{}, {'type':'model_request_error','message':f'{type(e).__name__}: {e}'}
   records.append({'case_id':c['id'],'output':{'text':text,'parsed':parsed},'evaluation':{'passed':passed,'score':float(passed)},'usage':{'prompt_tokens':use.get('prompt_tokens'),'generated_tokens':use.get('completion_tokens')},'timing':{'prompt_eval_ms':None,'generation_ms':None,'total_ms':round((time.perf_counter()-started)*1000,3),'generation_tokens_per_second':None},'error':err})
 except (OSError, RuntimeError, TimeoutError, urllib.error.URLError, ValueError) as e:problem=f'{type(e).__name__}: {e}'
 finally:
  if p and p.poll()is None:
   p.terminate()
   try:p.wait(20)
   except subprocess.TimeoutExpired:p.kill()
  so.close();se.close()
 (r/'results.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n'for x in records),encoding='utf8');pp=tg=None
 if problem or len(records)!=100:summary={'run_id':rid,'run_status':'invalid','qualification':{'passed':None,'failure_reasons':[problem or f'only {len(records)} cases']},'overall':None,'suites':{},'performance':{'median_generation_tokens_per_second':None,'median_total_ms':None,'llama_bench_generation_tokens_per_second':None,'llama_bench_prompt_tokens_per_second':None}}
 else:
  bc=[str(bench),'-m',str(model),'-p',str(cfg['performance']['prompt_tokens']),'-n',str(cfg['performance']['generation_tokens']),'-r',str(cfg['performance']['repetitions']),'-t',str(cfg['threads']),'-ngl',str(cfg['gpu_layers']),'-fa','on','-o','json'];z=subprocess.run(bc,capture_output=True,text=True,encoding='utf8',errors='replace',check=False);(raw/'llama-bench.stdout.txt').write_text(z.stdout or'',encoding='utf8');(raw/'llama-bench.stderr.txt').write_text(z.stderr or'',encoding='utf8');meta['command']['benchmark']=bc;dump(r/'metadata.json',meta)
  try:
   for x in json.loads(z.stdout).get('tests',[]):
    if x.get('t/s')is not None and 'pp'in str(x.get('test','')).lower():pp=float(x['t/s'])
    if x.get('t/s')is not None and 'tg'in str(x.get('test','')).lower():tg=float(x['t/s'])
  except(json.JSONDecodeError,TypeError,ValueError):pass
  lookup={x['id']:x for x in allcases()};groups={s:[]for s in SUITES}
  for x in records:groups[lookup[x['case_id']]['suite']].append(x)
  suites={s:{'cases':20,'passed':sum(x['evaluation']['passed']for x in g),'score':sum(x['evaluation']['score']for x in g)/20}for s,g in groups.items()};passed=sum(x['evaluation']['passed']for x in records);overall={'cases':100,'passed':passed,'score':passed/100};reasons=([]if overall['score']>=.8 else[f"overall {overall['score']:.2f} < 0.80"])+[f"{s} {v['score']:.2f} < {LIMITS[s]:.2f}"for s,v in suites.items()if v['score']<LIMITS[s]];summary={'run_id':rid,'run_status':'valid','qualification':{'passed':not reasons,'failure_reasons':reasons},'overall':overall,'suites':suites,'performance':{'median_generation_tokens_per_second':None,'median_total_ms':statistics.median(x['timing']['total_ms']for x in records),'llama_bench_generation_tokens_per_second':tg,'llama_bench_prompt_tokens_per_second':pp}}
 dump(r/'summary.json',summary);validate_run(r);print(f'{model.name}: {r.name} ({summary["run_status"]})')
def validate_run(r):
 errors=[]
 for s,f in(('run-metadata.schema.json','metadata.json'),('run-summary.schema.json','summary.json')):errors+=list(Draft202012Validator(load(S/s)).iter_errors(load(r/f)))
 v=Draft202012Validator(load(S/'case-result.schema.json'));records=[json.loads(x)for x in(r/'results.jsonl').read_text(encoding='utf8').splitlines()if x];errors += [e for x in records for e in v.iter_errors(x)];summary=load(r/'summary.json')
 if summary['run_status']=='valid'and(len(records)!=100 or sum(x['evaluation']['score']for x in records)/len(records)!=summary['overall']['score']):errors.append('summary does not derive from result records')
 if errors:raise RuntimeError('; '.join(e.message if hasattr(e,'message')else str(e)for e in errors))
def report():
 latest={}
 for r in RUNS.glob('*'):
  if(r/'metadata.json').is_file()and(r/'summary.json').is_file():m,s=load(r/'metadata.json'),load(r/'summary.json');latest[m['model']['file']]=(m,s)
 rows=sorted(latest.values(),key=lambda x:(not bool(x[1]['qualification']['passed']),-(x[1]['overall']or{'score':-1})['score'],x[0]['model']['file']));lines=['# MN-002 Model Qualification — MCB v0.1.0','','Generated from measured run artifacts. Capability and performance remain separate.','','| Model | Instruction Following | Structured Output | Context Retrieval | State Tracking | Causal Reasoning | Overall | Qualification | Generation tok/s |','| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |']
 for m,s in rows:
  scores=[f"{s['suites'][k]['score']:.2f}"for k in SUITES]+[f"{s['overall']['score']:.2f}"]if s['overall']else['invalid']*6;q='PASS'if s['qualification']['passed']else'FAIL'if s['qualification']['passed']is False else'INVALID';t=s['performance']['llama_bench_generation_tokens_per_second'];lines.append('| '+' | '.join([m['model']['file'],*scores,q,f'{t:.2f}'if t is not None else'unknown'])+' |')
 lines+=['','## Limitations','','Each run retains raw server output, commands, model SHA-256, runtime output, hardware snapshot, records, and summary. MCB v0.1.0 is a small synthetic qualification gate, not a broad knowledge, safety, multilingual, or long-context benchmark. llama-bench throughput is auxiliary only.'];REPORTS.mkdir(parents=True,exist_ok=True);(REPORTS/'model-qualification.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
def main():
 a=argparse.ArgumentParser();a.add_argument('--write-definition',action='store_true');a.add_argument('--validate',action='store_true');a.add_argument('--run-all',action='store_true');a.add_argument('--model',action='append');a.add_argument('--report',action='store_true');a.add_argument('--models-dir',type=Path,default=MODELS);a.add_argument('--llama-server',type=Path,default=BIN/'llama-server.exe');a.add_argument('--llama-bench',type=Path,default=BIN/'llama-bench.exe');x=a.parse_args()
 if x.write_definition:write()
 if x.validate:valid()
 names=x.model or(list(MODELS_REQUIRED)if x.run_all else[])
 for i,n in enumerate(names):
  if not(x.models_dir/n).is_file():print(f'MISSING MODEL: {n}',file=sys.stderr);continue
  try:run(x.models_dir/n,x.llama_server,x.llama_bench,18080+i)
  except (OSError, RuntimeError, TimeoutError, urllib.error.URLError, ValueError) as e:print(f'MODEL RUN ERROR {n}: {type(e).__name__}: {e}',file=sys.stderr)
 if x.report:report()
 if not any((x.write_definition,x.validate,names,x.report)):a.error('choose an action')
if __name__=='__main__':main()
