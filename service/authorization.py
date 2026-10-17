"""Locally issued, expiring scope approvals; no MCP endpoint can issue them."""
import json
import os
from pathlib import Path
import tempfile
import time


MODES = {'client', 'local'}


def require(files, root, path):
    mode = files.config.get('approval_mode', 'client')
    if mode not in MODES:
        raise PermissionError('Invalid approval_mode; review local configuration')
    if mode == 'client':
        return
    record = files.runtime / 'local-approval.json'
    files._no_links(record)
    try:
        grants = json.loads(record.read_text('utf-8'))
    except (OSError, ValueError):
        grants = []
    for grant in grants if isinstance(grants, list) else []:
        try:
            folder = Path(grant['scope'])
            if (grant['root'] == root and grant['root_path'] == str(files.roots[root]['path'].resolve())
                    and isinstance(grant['expires'], (int, float)) and time.time() < grant['expires']
                    and path.resolve().is_relative_to(folder.resolve())):
                files._no_links(folder)
                return
        except (KeyError, TypeError, ValueError, OSError):
            continue
    raise PermissionError('Local scope approval required. The owner must use diagnostics.py approve locally; no change was applied.')


def grant(files, root, relative, minutes):
    if not 1 <= minutes <= 60:
        raise ValueError('Approval duration must be 1–60 minutes')
    scope = files.path(root, relative, write=True)
    if not files.config.get('direct_operations', False):
        raise PermissionError('Direct operations are disabled')
    if scope.exists() and not scope.is_dir():
        raise ValueError('Approve a directory scope, not an individual file')
    # Bind approvals to the actual root; changing configuration invalidates them.
    issued = dict(root=root, root_path=str(files.roots[root]['path'].resolve()),
                  scope=str(scope.resolve()), expires=time.time() + minutes * 60)
    record = files.runtime / 'local-approval.json'
    files._no_links(record)
    try:
        previous = json.loads(record.read_text('utf-8'))
    except (OSError, ValueError):
        previous = []
    value = [g for g in previous if isinstance(g, dict) and isinstance(g.get('expires'), (int, float))
             and time.time() < g['expires'] and (g.get('root'), g.get('scope')) != (root, issued['scope'])] if isinstance(previous, list) else []
    if len(value) >= 64:
        raise ValueError('Too many active scopes; revoke before issuing more')
    value.append(issued)
    fd, name = tempfile.mkstemp(dir=files.runtime)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as output:
            json.dump(value, output)
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, record)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return dict(status='approved', root=root, minutes=minutes,
                scope='selected directory and descendants; all permitted direct mutations')


def revoke(files):
    record = files.runtime / 'local-approval.json'
    files._no_links(record)
    # Atomic invalidation; an already executing operation may finish.
    fd, name = tempfile.mkstemp(dir=files.runtime)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as output:
            output.write('[]')
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, record)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return dict(status='revoked')
