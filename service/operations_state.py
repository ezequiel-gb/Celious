"""Private, process-serialized, durable operational state; never a knowledge store."""
from contextlib import contextmanager
import hashlib
import json
import os
import re
import tempfile
import threading


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


class State:
    def __init__(self, files):
        self.files = files
        self.path = files.runtime / 'operations'
        files._no_links(self.path)
        self.path.mkdir(exist_ok=True)
        self.local = threading.RLock()

    @contextmanager
    def locked(self):
        self.files._no_links(self.path / 'lock')
        with self.local, (self.path / 'lock').open('a+b') as lock:
            self.files._no_links(self.path / 'lock')
            lock.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                lock.seek(0)
                if os.name == 'nt':
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def file(self, ident):
        if not re.fullmatch(r'(workflow|ingest)-[a-f0-9]{32}', ident):
            raise ValueError('Invalid operation identity')
        path = self.path / (ident + '.json')
        self.files._no_links(path)
        return path

    def load(self, ident):
        return json.loads(self.file(ident).read_text('utf-8'))

    def save(self, value):
        self.replace(self.file(value['id']), value)

    def replace(self, destination, value):
        self.files._no_links(destination)
        fd, temporary = tempfile.mkstemp(dir=destination.parent)
        try:
            with os.fdopen(fd, 'wb') as out:
                out.write(canonical(value))
                out.flush()
                os.fsync(out.fileno())
            os.replace(temporary, destination)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
