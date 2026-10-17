"""Native Windows tray icon with a small Celious control panel."""
import argparse
import json
import os
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
import webbrowser
import win32api
import win32con
import win32event
import win32gui
import winerror
from connect import BASE, normalize_key, LOCAL_CONFIG
from tray_core import Connection, RUNTIME
from diagnostics import status as diagnostic_status

ASSETS = BASE.parent / 'assets'
PLUGIN = LOCAL_CONFIG.get('plugin_url', 'https://chatgpt.com/plugins')


class TrayIcon:
    CALLBACK = win32con.WM_USER + 20
    def __init__(self, events):
        self.events = events
        self.hwnd = None
        self.state = 'off'
        self.ready = threading.Event()
        threading.Thread(target=self.run, daemon=True).start()
        if not self.ready.wait(5):
            raise RuntimeError('Windows tray icon could not start')

    def run(self):
        wc = win32gui.WNDCLASS()
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = 'CeliousTrayIconWindow'
        restart = win32gui.RegisterWindowMessage('TaskbarCreated')
        wc.lpfnWndProc = {self.CALLBACK: self.click, win32con.WM_COMMAND: self.command,
                         win32con.WM_DESTROY: self.destroy, win32con.WM_USER + 21: self.modify,
                         restart: lambda *args: self.modify(*args, add=True)}
        win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(wc.lpszClassName, 'Celious Tray', 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
        self.icons = {state: win32gui.LoadImage(0, str(ASSETS / ('celious-' + state + '.ico')), win32con.IMAGE_ICON, 32, 32, win32con.LR_LOADFROMFILE)
                      for state in ['off', 'on', 'starting', 'error']}
        self.modify(add=True)
        self.ready.set()
        win32gui.PumpMessages()

    def modify(self, *args, add=False):
        state = 'on' if self.state == 'external' else self.state
        data = (self.hwnd, 1, win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                self.CALLBACK, self.icons[state], 'Celious • ' + self.state.title())
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD if add else win32gui.NIM_MODIFY, data)
        return 0

    def update(self, state):
        self.state = state
        win32gui.PostMessage(self.hwnd, win32con.WM_USER + 21, 0, 0)

    def click(self, hwnd, msg, wp, lp):
        if lp in (win32con.WM_LBUTTONUP, win32con.WM_LBUTTONDBLCLK):
            self.events.put('show')
        elif lp == win32con.WM_RBUTTONUP:
            menu = win32gui.CreatePopupMenu()
            for ident, label in [(1, 'Open Celious switch'), (2, 'Turn off' if self.state in ('on', 'external') else 'Turn on'),
                                  (3, 'Open ChatGPT'), (4, 'Exit Celious')]:
                win32gui.AppendMenu(menu, win32con.MF_STRING, ident, label)
            win32gui.SetForegroundWindow(hwnd)
            win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, *win32gui.GetCursorPos(), 0, hwnd, None)
            win32gui.PostMessage(hwnd, win32con.WM_NULL, 0, 0)
            win32gui.DestroyMenu(menu)
        return 0

    def command(self, hwnd, msg, wp, lp):
        event = {1: 'show', 2: 'toggle', 3: 'chat', 4: 'exit'}.get(win32api.LOWORD(wp))
        if event:
            self.events.put(event)
        return 0

    def destroy(self, *args):
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self.hwnd, 1))
        for icon in self.icons.values():
            win32gui.DestroyIcon(icon)
        win32gui.PostQuitMessage(0)
        return 0

    def close(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)


class App:
    def __init__(self, show=False):
        self.root = tk.Tk()
        def report_error(kind, value, trace):
            import traceback
            (RUNTIME / 'tray-error.log').write_text(''.join(traceback.format_exception(kind, value, trace)), 'utf-8')
        self.root.report_callback_exception = report_error
        self.root.withdraw()
        self.root.title('Celious')
        self.root.geometry('470x340')
        self.root.resizable(False, False)
        self.root.configure(bg='#111827')
        self.root.iconbitmap(str(ASSETS / 'celious-on.ico'))
        self.root.protocol('WM_DELETE_WINDOW', self.root.withdraw)
        self.events = queue.Queue()
        self.connection = Connection()
        self.busy = False
        self.tray = TrayIcon(self.events)
        tk.Label(self.root, text='CELIOUS', bg='#111827', fg='#f9fafb', font=('Segoe UI', 24, 'bold')).pack(pady=(22, 0))
        tk.Label(self.root, text='Your files. Connected when you choose.', bg='#111827', fg='#9ca3af', font=('Segoe UI', 10)).pack(pady=(2, 18))
        self.status = tk.Label(self.root, bg='#111827', fg='#9ca3af', font=('Segoe UI', 12, 'bold'))
        self.status.pack()
        self.switch = tk.Canvas(self.root, width=90, height=44, bg='#111827', highlightthickness=0, cursor='hand2')
        self.switch.pack(pady=12)
        self.switch.bind('<Button-1>', lambda e: self.toggle())
        self.message = tk.Label(self.root, bg='#111827', fg='#9ca3af', font=('Segoe UI', 9), wraplength=380)
        self.message.pack()
        self.migrate = tk.Button(self.root, text='Move to tray', command=lambda: self.toggle(migrate=True), bg='#2563eb', fg='white', relief='flat', font=('Segoe UI', 10), padx=18)
        self.migrate.pack(pady=8)
        row = tk.Frame(self.root, bg='#111827')
        row.pack(pady=10)
        for label, callback in [('Open ChatGPT', lambda: webbrowser.open(PLUGIN)), ('Diagnostics', self.diagnose), ('Connection log', self.open_log), ('Hide', self.root.withdraw)]:
            tk.Button(row, text=label, command=callback, bg='#1f2937', fg='#e5e7eb', relief='flat', padx=10, pady=6).pack(side='left', padx=4)
        self.detect_async()
        self.root.after(100, self.tick)
        self.root.after(2500, self.monitor)
        if show:
            self.show()

    def show(self):
        self.root.deiconify()
        self.root.lift()

    def diagnose(self):
        report = diagnostic_status(BASE)
        summary = dict(version=report.get('version'), build=report['build'],
                       configuration=report['configuration'], dependency_lock_matches=report['dependencies']['matches'],
                       tools=report.get('tools', {}).get('count'), connection=report['connection'],
                       errors=report['errors'])
        messagebox.showinfo('Celious diagnostics', json.dumps(summary, indent=2), parent=self.root)

    def open_log(self):
        log = RUNTIME / 'tray-connection.log'
        if log.exists():
            os.startfile(log)
        else:
            messagebox.showinfo('Celious', 'No connection log yet.', parent=self.root)

    def render(self):
        state = self.connection.state
        on = state in ('on', 'external')
        color = '#22c55e' if on else '#f59e0b' if state == 'starting' else '#ef4444' if state == 'error' else '#6b7280'
        self.status.config(text={'on': 'Connected', 'external': 'Connected · terminal', 'off': 'Off', 'starting': 'Connecting…', 'error': 'Connection needs attention'}[state], fg=color)
        self.message.config(text=self.connection.message)
        self.switch.delete('all')
        self.switch.create_oval(2, 2, 42, 42, fill=color, outline=color)
        self.switch.create_oval(48, 2, 88, 42, fill=color, outline=color)
        self.switch.create_rectangle(22, 2, 68, 42, fill=color, outline=color)
        x = 50 if on else 4
        self.switch.create_oval(x, 4, x+36, 40, fill='#ffffff', outline='')
        if state == 'external':
            self.migrate.pack(pady=8, before=self.migrate.master.winfo_children()[-1])
        else:
            self.migrate.pack_forget()
        self.tray.update(state)
        (RUNTIME / 'tray-status.json').write_text(json.dumps({'pid': os.getpid(), 'state': state,
                                                            'message': self.connection.message, 'busy': self.busy}), 'utf-8')

    def work(self, operation):
        if self.busy:
            return
        self.busy = True
        def worker():
            try:
                operation()
                self.events.put('done')
            except Exception as error:
                self.events.put(('error', str(error)))
        threading.Thread(target=worker, daemon=True).start()

    def detect_async(self):
        self.work(self.connection.detect)

    def toggle(self, migrate=False):
        if self.busy:
            return
        if self.connection.state in ('on', 'external') and not migrate:
            self.work(self.connection.stop)
            return
        key = self.connection.key
        if key is None:
            self.busy = True  # Keep periodic detection out of the dialog's nested event loop.
            self.show()
            try:
                value = simpledialog.askstring('Celious API key', 'Paste your secret key beginning with sk-.\nIt stays in memory until you exit Celious.', show='*', parent=self.root)
            finally:
                self.busy = False
            if value is None:
                return
            key = normalize_key(value)
            value = None
            if key is None:
                messagebox.showerror('Celious', 'Paste the secret value beginning with sk-, not the key name.', parent=self.root)
                return
        self.connection.state, self.connection.message = 'starting', 'Checking the connection…'
        self.render()
        self.work(lambda: self.connection.start(key))

    def monitor(self):
        if not self.busy:
            self.detect_async()
        self.root.after(2500, self.monitor)

    def tick(self):
        try:
            while True:
                event = self.events.get_nowait()
                if isinstance(event, tuple):
                    self.busy = False
                    self.connection.state, self.connection.message = 'error', event[1]
                    self.render()
                    self.show()
                elif event == 'done':
                    self.busy = False
                    self.render()
                elif event == 'show':
                    self.show()
                elif event == 'toggle':
                    self.toggle()
                elif event == 'chat':
                    webbrowser.open(PLUGIN)
                elif event == 'exit':
                    self.exit()
                    return
        except queue.Empty:
            pass
        self.root.after(100, self.tick)

    def exit(self):
        if self.busy:
            messagebox.showinfo('Celious', 'Wait for the current connection operation to finish, then exit.', parent=self.root)
            return
        self.connection.stop(clear_key=True)
        self.tray.close()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        from tray_core import ManagedProcess
        import sys, time
        marker = RUNTIME / 'tray-test-child.json'
        marker.unlink(missing_ok=True)
        script = ('import subprocess,sys,time,json; from pathlib import Path; '
                  'child=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); '
                  'Path(sys.argv[1]).write_text(json.dumps({"pid":child.pid})); time.sleep(30)')
        proc = ManagedProcess([sys.executable, '-c', script, str(marker)], os.environ.copy(), RUNTIME / 'tray-test.log')
        deadline = time.monotonic() + 5
        try:
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.05)
            assert marker.exists(), 'Managed child did not start'
            child_pid = json.loads(marker.read_text())['pid']
            child_handle = win32api.OpenProcess(win32con.SYNCHRONIZE, False, child_pid)
            try:
                assert proc.running()
                proc.close()
                assert win32event.WaitForSingleObject(child_handle, 5000) == win32event.WAIT_OBJECT_0, 'Child survived turn-off'
            finally:
                child_handle.Close()
        finally:
            proc.close()
            marker.unlink(missing_ok=True)
        print('Hidden parent/child startup and complete Job Object shutdown passed.')
        return
    mutex = win32event.CreateMutex(None, False, 'Local\\CeliousFilesTray')
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        # A second shortcut launch opens the existing panel.
        hwnd = win32gui.FindWindow('CeliousTrayIconWindow', 'Celious Tray')
        if hwnd:
            win32gui.PostMessage(hwnd, TrayIcon.CALLBACK, 1, win32con.WM_LBUTTONUP)
        return
    try:
        App(show=args.show).root.mainloop()
    finally:
        mutex.Close()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import sys
        if '--self-test' in sys.argv:
            raise
        import traceback
        (RUNTIME / 'tray-error.log').write_text(traceback.format_exc(), 'utf-8')
        win32gui.MessageBox(0, 'Celious tray could not start. See service/.runtime/tray-error.log.', 'Celious', win32con.MB_ICONERROR)
