"""PDF 解析脚本。"""

import logging
from parser.pdf_parser import PDFParser

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> None:
    """解析 PDF 并保存为 JSON。"""
    parser = PDFParser("data/class_a.pdf")
    questions = parser.parse()
    parser.save_json("data/questions.json", questions)


if __name__ == "__main__":
    main()
