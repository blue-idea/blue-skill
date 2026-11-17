#!/usr/bin/env python3
"""顺序执行已审批 TASK 的本地队列；失败即停止，不自动恢复不确定状态。"""
import argparse
import datetime
import json
import pathlib
import subprocess
import sys


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def atomic_write(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def validate_tasks(data, repo):
    tasks = data.get('tasks')
    if not isinstance(tasks, list) or not tasks:
        raise ValueError('tasks 必须是非空数组')
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or not all(isinstance(task.get(k), str) and task[k].strip() for k in ('id', 'file', 'branch')):
            raise ValueError('每个任务必须包含 id、file、branch')
        if task['id'] in seen:
            raise ValueError('任务 ID 重复')
        seen.add(task['id'])
        path = (repo / task['file']).resolve()
        if not path.is_relative_to(repo) or not path.is_file():
            raise ValueError('任务文件不存在或超出仓库: ' + task['file'])
        if not path.read_text(encoding='utf-8').strip():
            raise ValueError('任务文件为空: ' + task['file'])
    return tasks


def main():
    p = argparse.ArgumentParser(description='Hermes 已审批任务队列')
    p.add_argument('action', choices=['plan', 'run', 'status'])
    p.add_argument('--repo', required=True)
    p.add_argument('--config')
    p.add_argument('--queue')
    a = p.parse_args()
    repo = pathlib.Path(a.repo).resolve()
    state_file = repo / '.hermes-loop' / 'queue-state.json'
    if a.action == 'status':
        if not state_file.exists():
            print('尚无队列状态')
            return 0
        print(state_file.read_text(encoding='utf-8'))
        return 0
    if not a.config or not a.queue:
        p.error('plan/run 需要 --config 和 --queue')
    tasks = validate_tasks(json.loads(pathlib.Path(a.queue).read_text(encoding='utf-8')), repo)
    if a.action == 'plan':
        print(json.dumps({'模式': '仅预览', '任务数': len(tasks), '任务': tasks}, ensure_ascii=False, indent=2))
        return 0
    if state_file.exists():
        print('已有队列状态。为避免重复提交，禁止自动覆盖或恢复；请人工核对。', file=sys.stderr)
        return 2
    state_file.parent.mkdir(exist_ok=True)
    state = {'status': 'RUNNING', 'started': now(), 'tasks': [{'id': t['id'], 'status': 'PENDING'} for t in tasks]}
    atomic_write(state_file, state)
    runner = pathlib.Path(__file__).with_name('hermes_runner.py')
    for i, task in enumerate(tasks):
        state['tasks'][i]['status'] = 'RUNNING'
        atomic_write(state_file, state)
        command = [sys.executable, str(runner), 'run', '--repo', str(repo), '--config', str(pathlib.Path(a.config).resolve()), '--task-file', str((repo / task['file']).resolve()), '--branch', task['branch']]
        with (state_file.parent / ('queue-' + str(i + 1) + '.log')).open('w', encoding='utf-8') as log:
            result = subprocess.run(command, cwd=repo, stdout=log, stderr=subprocess.STDOUT, check=False)
        state['tasks'][i]['status'] = 'DONE' if result.returncode == 0 else 'BLOCKED'
        state['tasks'][i]['exit_code'] = result.returncode
        atomic_write(state_file, state)
        if result.returncode:
            state['status'] = 'BLOCKED'
            state['updated'] = now()
            atomic_write(state_file, state)
            print('任务失败，已停止队列:', task['id'], file=sys.stderr)
            return result.returncode
    state['status'] = 'DONE_LOCAL'
    state['updated'] = now()
    atomic_write(state_file, state)
    print('本地队列完成；远程 CI 未验证。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
