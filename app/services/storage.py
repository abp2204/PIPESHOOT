import sqlite3
import json
import os

DB_PATH = os.environ.get('DATABASE_URL', 'sqlite:///./data/runs.db')


class DB:
    def __init__(self, path: str | None = None):
        # simple sqlite JSON store
        self.path = path or os.path.join(os.getcwd(), 'data', 'runs.db')
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._create()

    def _create(self):
        cur = self._conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, input_summary TEXT, result_json TEXT)''')
        self._conn.commit()

    def save_run(self, record: dict) -> int:
        cur = self._conn.cursor()
        cur.execute('INSERT INTO runs (timestamp, input_summary, result_json) VALUES (?, ?, ?)', (record.get('timestamp'), json.dumps(record.get('input_summary')), json.dumps(record.get('result'))))
        self._conn.commit()
        return cur.lastrowid

    def list_runs(self):
        cur = self._conn.cursor()
        cur.execute('SELECT id, timestamp, input_summary FROM runs ORDER BY id DESC LIMIT 50')
        rows = cur.fetchall()
        out = []
        for r in rows:
            out.append({'id': r[0], 'timestamp': r[1], 'input_summary': json.loads(r[2])})
        return out

    def get_run(self, run_id: int):
        cur = self._conn.cursor()
        cur.execute('SELECT id, timestamp, input_summary, result_json FROM runs WHERE id=?', (run_id,))
        r = cur.fetchone()
        if not r:
            return None
        return {'id': r[0], 'timestamp': r[1], 'input_summary': json.loads(r[2]), 'result': json.loads(r[3])}
