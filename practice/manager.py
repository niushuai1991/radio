"""练习管理器。"""

import json
import logging
import random
from pathlib import Path
from typing import Literal

from parser.question import Question
from storage.database import get_db

logger = logging.getLogger(__name__)

PracticeMode = Literal["random", "new", "wrong"]


class PracticeManager:
    """练习管理器。"""

    def __init__(self, questions_path: str | Path = "data/questions.json"):
        """初始化练习管理器。"""
        self.questions_path = Path(questions_path)
        self._questions: list[Question] | None = None
        self._questions_map: dict[str, Question] | None = None
        self.db = get_db()

    @property
    def questions(self) -> list[Question]:
        """获取所有题目（懒加载）。"""
        if self._questions is None:
            self._load_questions()
        return self._questions or []

    @property
    def questions_map(self) -> dict[str, Question]:
        """获取题目字典（懒加载）。"""
        if self._questions_map is None:
            self._load_questions()
        return self._questions_map or {}

    def _load_questions(self) -> None:
        """从 JSON 文件加载题目。"""
        if not self.questions_path.exists():
            raise FileNotFoundError(f"题库文件不存在: {self.questions_path}")

        data = json.loads(self.questions_path.read_text(encoding="utf-8"))
        self._questions = [Question(**q) for q in data]

        # 处理重复ID，保留第一次出现的题目
        self._questions_map = {}
        for q in self._questions:
            if q.question_id not in self._questions_map:
                self._questions_map[q.question_id] = q

        logger.info(
            f"已加载 {len(self._questions)} 题 ({len(self._questions_map)} 个唯一ID)"
        )

    def get_random_questions(self, limit: int = 20) -> list[Question]:
        """获取随机题目。"""
        return random.sample(self.questions, min(limit, len(self.questions)))

    def get_new_questions(self, limit: int = 20) -> list[Question]:
        """获取未练习的题目。"""
        practiced_ids = set(row["question_id"] for row in self.db.get_all_progress())

        new_questions = [
            q for q in self.questions if q.question_id not in practiced_ids
        ]

        if len(new_questions) <= limit:
            return new_questions

        return random.sample(new_questions, limit)

    def get_wrong_questions(self, limit: int = 20) -> list[Question]:
        """获取错题（正确率 < 60%）。"""
        progress_list = self.db.get_all_progress()
        wrong_ids: list[str] = []

        for p in progress_list:
            practice_count = p["practice_count"]
            correct_count = p["correct_count"]

            if practice_count > 0 and correct_count / practice_count < 0.6:
                question_id = p["question_id"]
                if isinstance(question_id, str):
                    wrong_ids.append(question_id)

        wrong_questions = [
            self.questions_map[qid] for qid in wrong_ids if qid in self.questions_map
        ]

        # 按错误率排序
        wrong_questions.sort(
            key=lambda q: self._calculate_error_rate(q.question_id), reverse=True
        )

        return wrong_questions[:limit]

    def _calculate_error_rate(self, question_id: str) -> float:
        """计算题目错误率。"""
        progress = self.db.get_progress(question_id)
        if not progress or progress["practice_count"] == 0:
            return 0.0

        return 1.0 - (progress["correct_count"] / progress["practice_count"])

    def submit_answer(
        self, question_id: str, user_answer: str
    ) -> dict[str, str | bool]:
        """提交答案并记录。"""
        question = self.questions_map.get(question_id)
        if not question:
            raise ValueError(f"题目不存在: {question_id}")

        is_correct = question.check_answer(user_answer)
        self.db.record_practice(question_id, is_correct)

        return {
            "question_id": question_id,
            "user_answer": user_answer,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct,
            "is_multiple": question.is_multiple_choice,
        }

    def get_question_by_id(self, question_id: str) -> Question | None:
        """根据 ID 获取题目。"""
        return self.questions_map.get(question_id)

    def get_stats(self) -> dict[str, int | float | str]:
        """获取统计信息。"""
        db_stats = self.db.get_stats()

        return {
            **db_stats,
            "total_questions": len(self.questions),
            "new_questions": len(self.get_new_questions(limit=9999)),
            "wrong_questions": len(self.get_wrong_questions(limit=9999)),
        }
