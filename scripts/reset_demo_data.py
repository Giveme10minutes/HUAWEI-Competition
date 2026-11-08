#!/usr/bin/env python3
"""Clear local demo records without changing schema, credentials or source files."""
from __future__ import annotations

import argparse
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backend.config import load_settings

TABLES = ('messages', 'profile_items', 'plan_versions', 'plans', 'conversations')
LABELS = dict(messages='消息', profile_items='个人线索', plan_versions='规划版本及行动',
              plans='规划', conversations='对话（含已删除）')


def reset_data(path: Path, *, dry_run: bool = False) -> dict[str, int]:
    if not path.is_file():
        raise ValueError('数据库尚不存在，无需清空。')
    # mode=rw prevents accidental creation if the database disappears.
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=rw', uri=True, timeout=5)) as conn, conn:
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('BEGIN IMMEDIATE')
        actual = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        if actual != set(TABLES):
            raise ValueError('数据库业务表与脚本版本不一致，未清空；请先更新脚本。')
        counts = {t: conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in TABLES}
        if dry_run:
            conn.rollback()
            return counts
        pending = conn.execute("SELECT COUNT(*) FROM messages WHERE status='pending'").fetchone()[0]
        if pending:
            raise ValueError('有待完成的消息，请先等待回复完成或重试失败消息，再清空。')
        for table in TABLES:
            conn.execute(f'DELETE FROM {table}')
        if any(conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in TABLES):
            raise ValueError('空状态检查未通过，已撤销本次清空。')
        conn.commit()
        return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='清空本地Demo业务数据，保留.env、代码、表结构和历史备份。')
    parser.add_argument('--yes', action='store_true', help='直接清空，不再输入CLEAR确认')
    parser.add_argument('--dry-run', action='store_true', help='只显示数据量，不清空')
    parser.add_argument('--db', type=Path, help='指定其他本地SQLite（默认按项目.env的APP_DB_PATH读取）')
    args = parser.parse_args(argv)
    path = args.db.expanduser().resolve() if args.db else load_settings().db_path
    print(f'本地数据库：{path}')
    if not args.dry_run and not args.yes:
        if not sys.stdin.isatty():
            print('请使用 --yes 执行，或 --dry-run 只查看。', file=sys.stderr)
            return 1
        if input('将清空全部对话、线索、规划和行动。输入 CLEAR 执行：').strip() != 'CLEAR':
            print('已取消。')
            return 1
    try:
        counts = reset_data(path, dry_run=args.dry_run)
    except (ValueError, sqlite3.Error, OSError) as exc:
        print(f'未清空：{exc}', file=sys.stderr)
        return 1
    for table, count in counts.items():
        print(f'  {LABELS[table]}：{count}' + ('' if args.dry_run else ' → 0'))
    print('仅查看，数据未改变。' if args.dry_run else '清空完成。无需重启后端；刷新网页后开始新Demo。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
