#!/usr/bin/env python3
"""Initialize, inspect, and transition a durable Hermes task state (stdlib only)."""
import argparse
import datetime
import json
import os
import pathlib
import tempfile

STATES = ('PLANNED','DISPATCHED','CODING','IMPLEMENTED','TESTING','REVIEWING','FIX_REQUIRED','COMMITTING','CI_VERIFYING','DONE','BLOCKED')
NEXT = {
 'PLANNED': {'DISPATCHED','BLOCKED'}, 'DISPATCHED': {'CODING','BLOCKED'},
 'CODING': {'IMPLEMENTED','BLOCKED'}, 'IMPLEMENTED': {'TESTING','BLOCKED'},
 'TESTING': {'REVIEWING','FIX_REQUIRED','BLOCKED'},
 'REVIEWING': {'COMMITTING','FIX_REQUIRED','BLOCKED'},
 'COMMITTING': {'CI_VERIFYING','FIX_REQUIRED','BLOCKED'},
 'CI_VERIFYING': {'DONE','BLOCKED'}, 'FIX_REQUIRED': {'CODING','BLOCKED'},
 'DONE': set(), 'BLOCKED': set()
}
def save(path, data):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(dir=str(path.parent),prefix='.state-')
 try:
  with os.fdopen(fd,'w') as f:
   json.dump(data,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp): os.unlink(tmp)
def main():
 p=argparse.ArgumentParser(); p.add_argument('--dir',default='.agent-loop'); s=p.add_subparsers(dest='action',required=True)
 init=s.add_parser('init'); init.add_argument('task_id'); init.add_argument('--version',default='v1'); init.add_argument('--branch',required=True); init.add_argument('--max-retries',type=int,default=3)
 move=s.add_parser('transition'); move.add_argument('state',choices=STATES); move.add_argument('--message',default='')
 s.add_parser('show'); a=p.parse_args(); root=pathlib.Path(a.dir); path=root/'state.json'
 if a.action=='init':
  if path.exists(): p.error('Existing task state found; archive or resume it first')
  if a.max_retries<0: p.error('Invalid retry count')
  data=dict(schema_version=1,task_id=a.task_id,spec_version=a.version,branch=a.branch,state='PLANNED',correction_cycles=0,max_correction_cycles=a.max_retries,agent_sessions={},evidence={},last_error=None,commit=None,ci=None)
 else:
  if not path.exists(): p.error('Initialize state first')
  data=json.loads(path.read_text())
  if a.action=='show': print(json.dumps(data,indent=2)); return
  old=data['state']; new=a.state
  if new not in NEXT[old]: p.error(f'Illegal transition: {old} -> {new}')
  if new=='FIX_REQUIRED':
   data['correction_cycles']+=1
   if data['correction_cycles']>data['max_correction_cycles']: new='BLOCKED'
  data['state']=new
  if a.message: data['last_error']=a.message if new in ('FIX_REQUIRED','BLOCKED') else None
 save(path,data)
 if a.action!='show':
  event=dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),task_id=data['task_id'],role='hermes',event=a.action,state=data['state'],attempt=data['correction_cycles'],message=getattr(a,'message',''))
  with (root/'events.jsonl').open('a') as f: f.write(json.dumps(event,ensure_ascii=False)+'\n')
 print(json.dumps(data,indent=2))
if __name__=='__main__': main()
