"""测试 PDF 解析器。"""

from parser.pdf_parser import PDFParser
from parser.question import Question


def test_parse_pdf():
    """测试 PDF 解析。"""
    parser = PDFParser("data/class_a.pdf")
    questions = parser.parse()

    assert len(questions) > 600, "题目数量应该超过600"

    # 验证第一题
    first = questions[0]
    assert first.question_id == "MC2-0001"
    assert "无线电管理" in first.content
    assert first.has_option("A")
    assert first.correct_answer == "AC"
    assert first.is_multiple_choice is True
    assert first.section == "1.1.1"
    assert first.legacy_id == "LY0002"


def test_question_model():
    """测试题目模型。"""
    q = Question(
        question_id="TEST-001",
        content="测试题干",
        options={"A": "选项A", "B": "选项B"},
        correct_answer="A",
        section="1.1",
    )

    assert q.question_id == "TEST-001"
    assert q.content == "测试题干"
    assert q.correct_answer == "A"
    assert q.is_multiple_choice is False
    assert q.has_option("A")
    assert q.has_option("B")
    assert not q.has_option("C")
    assert q.check_answer("A") is True
    assert q.check_answer("B") is False
