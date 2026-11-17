#!/usr/bin/env python3
"""Hermes local orchestration MVP: configured CLI adapters, tmux, gates, bounded retries."""
import argparse, datetime, json, os, pathlib, re, shlex, shutil, subprocess, sys, time

def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def call(argv, cwd, timeout=30):
    return subprocess.run(argv,cwd=cwd,text=True,capture_output=True,timeout=timeout)
def main():
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['doctor','run']); p.add_argument('--repo',required=True); p.add_argument('--config',required=True); p.add_argument('--task-file'); p.add_argument('--branch'); p.add_argument('--dry-run',action='store_true'); a=p.parse_args()
    repo=pathlib.Path(a.repo).resolve(); config=json.loads(pathlib.Path(a.config).read_text()); agents=config['agents']; gates=config['gates']; allowed=config['allowed_paths']; retries=int(config.get('max_retries',3))
    def git(*args): return call(['git',*args],repo)
    problems=[]
    for executable in ['git','tmux']:
        if not shutil.which(executable): problems.append('Missing executable: '+executable)
    if not (repo/'AGENTS.md').is_file(): problems.append('Missing AGENTS.md')
    if git('rev-parse','--is-inside-work-tree').returncode: problems.append('Not a git repository')
    if not allowed or any(x in ('.','..','/') or pathlib.PurePath(x).is_absolute() or '..' in pathlib.PurePath(x).parts for x in allowed): problems.append('allowed_paths must be explicit safe relative paths')
    for role in ('coder','tester','reviewer'):
        if not agents.get(role): problems.append('Missing agent command: '+role)
    for gate in ('lint','typecheck','unit','build'):
        if not gates.get(gate): problems.append('Missing required gate: '+gate)
    if retries<0: problems.append('Invalid retries')
    if a.action=='doctor':
        print(json.dumps({'ok':not problems,'problems':problems,'agents':list(agents),'gates':list(gates)},indent=2)); return 1 if problems else 0
    if not a.task_file or not a.branch: p.error('run requires --task-file and --branch')
    if not re.fullmatch(r'(feature|fix|chore)/[a-zA-Z0-9._/-]+',a.branch): problems.append('Invalid branch')
    task=pathlib.Path(a.task_file).resolve().read_text()
    if not task.strip(): problems.append('Empty task')
    if git('status','--porcelain').stdout.strip(): problems.append('Dirty worktree: stop before branch creation')
    for role in ('coder','tester','reviewer'):
        if shutil.which('tmux') and call(['tmux','has-session','-t','='+f'session-{role}'],repo).returncode==0: problems.append('tmux session already exists: session-'+role)
    if problems: print('\n'.join(problems),file=sys.stderr); return 2
    if a.dry_run:
        print(json.dumps({'branch':a.branch,'task':task[:400],'allowed_paths':allowed,'gates':gates,'agents':list(agents),'max_retries':retries,'commit':config.get('commit_message'),'note':'No processes started'},indent=2)); return 0
    runtime=repo/'.hermes-loop'; runtime.mkdir(exist_ok=True)
    exclude=repo/'.git/info/exclude'
    if exclude.is_file() and '.hermes-loop/' not in exclude.read_text():
        with exclude.open('a') as f: f.write('\n.hermes-loop/\n')
    state={'state':'STARTING','branch':a.branch,'attempt':0,'ci':'not_triggered','commit':None,'started':stamp()}
    def event(stage,message):
        state.update(state=stage,updated=stamp()); (runtime/'state.json').write_text(json.dumps(state,indent=2))
        with (runtime/'events.jsonl').open('a') as f: f.write(json.dumps({'time':stamp(),'stage':stage,'message':message})+'\n')
    def run_logged(stage,cmd,timeout):
        event(stage,'starting')
        result=subprocess.run(cmd,shell=True,cwd=repo,text=True,capture_output=True,timeout=timeout,executable='/bin/sh')
        (runtime/f'{state["attempt"]}-{stage}.log').write_text(result.stdout+'\n--- STDERR ---\n'+result.stderr+'\nEXIT='+str(result.returncode))
        if result.returncode: raise RuntimeError(f'{stage} exit={result.returncode}')
        return result.stdout
    def agent(role,prompt):
        prompt_path=runtime/f'{state["attempt"]}-{role}.prompt'; prompt_path.write_text(prompt)
        output=runtime/f'{state["attempt"]}-{role}.out'
        template=agents[role]
        command=template.replace('{prompt_file}',shlex.quote(str(prompt_path))).replace('{output_file}',shlex.quote(str(output)))
        script=runtime/f'{state["attempt"]}-{role}.sh'; status=runtime/f'{state["attempt"]}-{role}.exit'
        script.write_text('#!/bin/sh\ncd '+shlex.quote(str(repo))+'\n'+command+' > '+shlex.quote(str(output))+' 2>&1\nrc=$?\nprintf "%s\\n" "$rc" > '+shlex.quote(str(status))+'\n')
        script.chmod(0o700)
        session='session-'+role
        r=call(['tmux','new-session','-d','-s',session,'/bin/sh '+shlex.quote(str(script))],repo)
        if r.returncode: raise RuntimeError('tmux start '+role+': '+r.stderr)
        deadline=time.monotonic()+int(config.get('agent_timeout_seconds',1800))
        while not status.exists() and time.monotonic()<deadline: time.sleep(.5)
        if not status.exists(): raise RuntimeError(role+' timeout; inspect tmux and logs')
        code=int(status.read_text().strip()); text=output.read_text() if output.exists() else ''
        event(role.upper(),'exit='+str(code))
        if code: raise RuntimeError(role+' exit='+str(code))
        return text
    try:
        r=git('switch','-c',a.branch)
        if r.returncode: raise RuntimeError('branch creation failed: '+r.stderr)
        for attempt in range(retries+1):
            state['attempt']=attempt+1
            try:
                previous=(runtime/'failure.txt').read_text() if (runtime/'failure.txt').exists() else ''
                agent('coder','TASK:\n'+task+'\nOnly edit allowed paths: '+', '.join(allowed)+'\nPrevious failure:\n'+previous+'\nImplement and exit. Do not commit.')
                agent('tester','Independently inspect changes and test acceptance criteria. Do not edit or commit. TASK:\n'+task)
                for name,cmd in gates.items(): run_logged('gate-'+name,cmd,int(config.get('gate_timeout_seconds',600)))
                review=agent('reviewer','Review diff against task and security risks. Do not edit. Finish with standalone APPROVED or BLOCKED. TASK:\n'+task+'\nDIFF:\n'+git('diff','--',*allowed).stdout[:120000])
                if not re.search(r'(?m)^APPROVED\s*$',review) or re.search(r'(?i)\bP[012]\b|(?m)^BLOCKED\s*$',review): raise RuntimeError('review blocked or uncertain')
                run_logged('diff-check','git diff --check',30)
                changed=git('status','--porcelain','--untracked-files=all').stdout.splitlines()
                if not changed: raise RuntimeError('no changed files')
                def allowed_file(path):
                    return any(path==root or path.startswith(root.rstrip('/')+'/') for root in allowed)
                out_of_scope=[line[3:] for line in changed if not allowed_file(line[3:])]
                if out_of_scope: raise RuntimeError('out-of-scope changes: '+', '.join(out_of_scope))
                r=git('add','--',*allowed)
                if r.returncode: raise RuntimeError('staging failed: '+r.stderr)
                staged=git('diff','--cached','--name-only').stdout.splitlines()
                if not staged: raise RuntimeError('no staged files')
                event('COMMITTING','staged: '+', '.join(staged))
                r=git('commit','-m',config.get('commit_message','feat: complete approved task'))
                (runtime/f'{state["attempt"]}-commit.log').write_text(r.stdout+r.stderr)
                if r.returncode: raise RuntimeError('commit/hooks failed: '+r.stderr)
                state['commit']=git('rev-parse','HEAD').stdout.strip(); event('DONE','local commit completed; remote CI not triggered')
                print(json.dumps(state,indent=2)); return 0
            except Exception as exc:
                (runtime/'failure.txt').write_text(str(exc)); event('FIX_REQUIRED',str(exc))
                if attempt>=retries: raise
        return 1
    except Exception as exc:
        event('BLOCKED',str(exc)); print('BLOCKED:',exc,file=sys.stderr); return 1
    finally:
        for role in ('coder','tester','reviewer'):
            call(['tmux','kill-session','-t','='+f'session-{role}'],repo) if shutil.which('tmux') else None
if __name__=='__main__': sys.exit(main())
