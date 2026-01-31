"""SQLite 数据库操作。"""

import logging
from datetime import datetime
from pathlib import Path
from sqlite3 import Connection, Row, connect

logger = logging.getLogger(__name__)


class Database:
    """数据库管理类。"""

    def __init__(self, db_path: str | Path = "data/practice.db"):
        """初始化数据库。"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Connection | None = None

    def connect(self) -> Connection:
        """获取数据库连接。"""
        if self._conn is None:
            self._conn = connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = Row
        return self._conn

    def close(self) -> None:
        """关闭数据库连接。"""
        if self._conn:
            self._conn.close()
            self._conn = None

    def init_db(self) -> None:
        """初始化数据库表。"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                question_id TEXT PRIMARY KEY,
                practice_count INTEGER NOT NULL DEFAULT 0,
                correct_count INTEGER NOT NULL DEFAULT 0,
                last_practice TEXT,
                is_correct INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """
        )

        conn.commit()
        logger.info(f"数据库初始化完成: {self.db_path}")

    def record_practice(
        self, question_id: str, is_correct: bool
    ) -> dict[str, int | bool]:
        """记录练习结果。"""
        conn = self.connect()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO progress (question_id, practice_count, correct_count, last_practice, is_correct)
            VALUES (?, 1, ?, ?, ?)
            ON CONFLICT(question_id) DO UPDATE SET
                practice_count = practice_count + 1,
                correct_count = correct_count + ?,
                last_practice = ?,
                is_correct = ?,
                updated_at = ?
            """,
            (
                question_id,
                1 if is_correct else 0,
                now,
                1 if is_correct else 0,
                1 if is_correct else 0,
                now,
                1 if is_correct else 0,
                now,
            ),
        )

        conn.commit()

        cursor.execute("SELECT * FROM progress WHERE question_id = ?", (question_id,))
        row = cursor.fetchone()
        return dict(row) if row else {}

    def get_progress(self, question_id: str) -> dict[str, int | bool] | None:
        """获取题目练习进度。"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM progress WHERE question_id = ?", (question_id,))
        row = cursor.fetchone()

        if row:
            data = dict(row)
            data["is_correct"] = bool(data["is_correct"])
            return data
        return None

    def get_all_progress(self) -> list[dict[str, int | bool]]:
        """获取所有练习进度。"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM progress ORDER BY updated_at DESC")
        rows = cursor.fetchall()

        result = []
        for row in rows:
            data = dict(row)
            data["is_correct"] = bool(data["is_correct"])
            result.append(data)

        return result

    def get_stats(self) -> dict[str, int | float]:
        """获取统计信息。"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM progress")
        total_practiced = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM progress WHERE correct_count > 0")
        correct_questions = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(practice_count) FROM progress")
        total_attempts = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(correct_count) FROM progress")
        total_correct = cursor.fetchone()[0] or 0

        accuracy = total_correct / total_attempts if total_attempts > 0 else 0.0

        return {
            "total_practiced": total_practiced,
            "correct_questions": correct_questions,
            "total_attempts": total_attempts,
            "total_correct": total_correct,
            "accuracy": round(accuracy * 100, 2),
        }


# 全局数据库实例
_db: Database | None = None


def get_db() -> Database:
    """获取数据库实例。"""
    global _db
    if _db is None:
        _db = Database()
        _db.init_db()
    return _db
