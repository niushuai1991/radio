"""PDF 解析器。"""

import logging
import re
from pathlib import Path

import pdfplumber

from parser.question import Question


logger = logging.getLogger(__name__)


class PDFParser:
    """PDF 题目解析器。"""

    def __init__(self, pdf_path: str | Path):
        """初始化解析器。"""
        self.pdf_path = Path(pdf_path)
        self.pattern = re.compile(r"\[([QABCDTPIJ])\]([^\[]*?)(?=\[[A-Z]\]|$)")

    def parse(self) -> list[Question]:
        """解析 PDF 文件，返回题目列表。"""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {self.pdf_path}")

        questions: list[Question] = []
        current_data: dict[str, str | dict[str, str]] = {}

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    self._process_page(text, current_data, questions)

                    if page_num % 10 == 0:
                        logger.debug(f"已处理 {page_num}/{len(pdf.pages)} 页")

        except Exception as e:
            logger.error(f"PDF 解析失败: {e}")
            raise

        # 保存最后一题
        if current_data.get("[Q]"):
            questions.append(self._create_question(current_data))

        # 处理重复ID
        questions = self._deduplicate_questions(questions)

        logger.info(f"解析完成，共 {len(questions)} 题")
        return questions

    def _deduplicate_questions(self, questions: list[Question]) -> list[Question]:
        """处理重复ID的题目。"""
        id_count: dict[str, int] = {}
        id_mapping: dict[str, int] = {}

        # 统计每个ID出现的次数
        for q in questions:
            qid = q.question_id
            id_count[qid] = id_count.get(qid, 0) + 1

        # 为重复的ID生成唯一ID
        for q in questions:
            qid = q.question_id
            if id_count[qid] > 1:
                # 该ID重复，生成唯一ID
                if qid not in id_mapping:
                    id_mapping[qid] = 1
                else:
                    id_mapping[qid] += 1
                # 修改question_id
                object.__setattr__(q, "question_id", f"{qid}-{id_mapping[qid]}")

        return questions

    def _process_page(
        self,
        text: str,
        current_data: dict[str, str | dict[str, str]],
        questions: list[Question],
    ) -> None:
        """处理单页文本。"""
        matches = self.pattern.findall(text)

        for tag, content in matches:
            content = content.strip()
            if not content:
                continue

            if tag == "I":
                # 新题目ID，保存前一题（如果有）
                if current_data.get("[Q]"):
                    questions.append(self._create_question(current_data))
                current_data = {}
                current_data["[I]"] = content
            elif tag == "Q":
                current_data["[Q]"] = content
            elif tag in ["A", "B", "C", "D"]:
                if "[Q]" not in current_data:
                    continue
                if "options" not in current_data:
                    current_data["options"] = {}
                options = current_data["options"]
                if isinstance(options, dict):
                    options[tag] = content
            else:
                current_data[f"[{tag}]"] = content

    def _create_question(self, data: dict[str, str | dict[str, str]]) -> Question:
        """创建题目对象。"""
        options_value = data.get("options")
        options: dict[str, str] = (
            options_value if isinstance(options_value, dict) else {}
        )

        # 如果没有[I]，使用[J]作为ID
        question_id = data.get("[I]", "")
        if not question_id or not isinstance(question_id, str):
            question_id = data.get("[J]", "")
            if not isinstance(question_id, str):
                question_id = ""

        question_data: dict[str, str | dict[str, str]] = {
            "question_id": question_id,
            "content": data.get("[Q]", "") if isinstance(data.get("[Q]"), str) else "",
            "options": options,
            "correct_answer": data.get("[T]", "")
            if isinstance(data.get("[T]"), str)
            else "",
            "section": data.get("[P]", "") if isinstance(data.get("[P]"), str) else "",
            "legacy_id": data.get("[J]", "")
            if isinstance(data.get("[J]"), str)
            else "",
        }
        return Question(**question_data)  # type: ignore[arg-type]

    def save_json(self, output_path: str | Path, questions: list[Question]) -> None:
        """保存题目为 JSON 文件。"""
        import json

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = [q.model_dump(mode="json", exclude_none=True) for q in questions]
        output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info(f"已保存 {len(questions)} 题到 {output_path}")
