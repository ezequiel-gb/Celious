"""Interactive tunnel launcher. Never stores or prints the runtime credential."""
import argparse
import getpass
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from connection_settings import tunnel_id

BASE = Path(__file__).resolve().parent
CLIENT = BASE.parent / 'tools' / 'tunnel-client' / 'tunnel-client.exe'
PROFILES = BASE / '.runtime' / 'profiles'
LOCAL_CONFIG = json.loads((BASE / 'config.json').read_text('utf-8-sig'))


TUNNEL_ID = tunnel_id(LOCAL_CONFIG, PROFILES / 'celious.yaml')


def check():
    for required in [CLIENT, PROFILES / 'celious.yaml', BASE / 'server.py', BASE / 'config.json']:
        if not required.is_file():
            raise FileNotFoundError(f'Missing local setup file: {required.name}')
    config = json.loads((BASE / 'config.json').read_text('utf-8-sig'))
    for root in config['roots'].values():
        if not Path(root['path']).is_dir():
            raise FileNotFoundError('An authorized directory is missing')
    from mcp.server import MCPServer  # Confirm SDK works in this Python environment.
    return True


def normalize_key(value):
    if value is None:
        return None
    key = value.strip().strip('\"\'').strip()
    if not key.startswith('sk-') or len(key) < 12 or any(ord(c) < 33 or c in '\"\'' for c in key):
        return None
    return key


def prompt_key(terminal=False):
    if terminal:
        for _ in range(3):
            key = normalize_key(getpass.getpass('Runtime API secret key (hidden): '))
            if key:
                return key
            print('Paste the secret value beginning with sk-, not the name Celious API. Try again.')
        return None
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    root = tk.Tk()
    root.withdraw()
    try:
        for _ in range(3):
            value = simpledialog.askstring(
                'Celious API key',
                'Paste your NEW secret key beginning with sk- using Ctrl+V.\n'
                'Use the secret value, not the name Celious API.\n'
                'The field is masked and the key is not saved.',
                show='*', parent=root,
            )
            if value is None:
                return None
            key = normalize_key(value)
            value = None
            if key:
                return key
            messagebox.showerror('Celious key input',
                                 'No secret key was received in the expected format.\n'
                                 'Copy the actual secret value beginning with sk-, then try again.\n'
                                 'Nothing has been sent to OpenAI.', parent=root)
        return None
    finally:
        root.destroy()


def main():
    parser = argparse.ArgumentParser(description='Start Celious Files for ChatGPT')
    parser.add_argument('--check', action='store_true', help='Validate local setup without credentials or network calls')
    parser.add_argument('--terminal', action='store_true', help='Use hidden terminal input instead of the Windows paste dialog')
    args = parser.parse_args()
    check()
    if args.check:
        print('Celious launcher local check passed. No key or network request was used.')
        return 0
    print('Celious Files connection')
    print('A Celious API key dialog will open. Paste the secret there with Ctrl+V and click OK.')
    key = prompt_key(terminal=args.terminal)
    if key is None:
        print('Key entry cancelled or no valid secret received. Nothing was connected.')
        return 1
    env = os.environ.copy()
    env['CONTROL_PLANE_API_KEY'] = key
    key = None
    common = ['--profile', 'celious', '--profile-dir', str(PROFILES), '--control-plane.tunnel-id', TUNNEL_ID]
    try:
        diagnostics = subprocess.run([str(CLIENT), 'doctor', *common, '--explain'], env=env, shell=False)
        if diagnostics.returncode:
            print('Celious diagnostics failed. Check the message above, key permissions and workspace association.')
            return diagnostics.returncode
        print('Diagnostics passed. Keep this window open while using Celious.')
        print('Next: connect Celious Files in ChatGPT Plugins using Connection > Tunnel.')
        print('Press Ctrl+C here to stop the connection.')
        return subprocess.run([
            str(CLIENT), 'run', *common,
            '--health.url-file', str(BASE / '.runtime' / 'health-url.txt'),
            '--mcp.stdio-send-initialized-notification',
        ], env=env, shell=False).returncode
    finally:
        env.pop('CONTROL_PLANE_API_KEY', None)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\nCelious connection stopped.')
        sys.exit(0)
    except (OSError, ValueError) as error:
        print(f'Celious could not start: {error}', file=sys.stderr)
        sys.exit(1)
