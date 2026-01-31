"""测试练习管理器。"""

from practice.manager import PracticeManager


def test_load_questions():
    """测试加载题目。"""
    manager = PracticeManager()
    assert len(manager.questions) == 683
    # 允许有重复ID
    assert len(manager.questions_map) > 600


def test_get_random_questions():
    """测试获取随机题目。"""
    manager = PracticeManager()
    questions = manager.get_random_questions(10)
    assert len(questions) == 10


def test_get_new_questions():
    """测试获取新题。"""
    manager = PracticeManager()
    new_questions = manager.get_new_questions(20)

    # 初始状态所有题都是新题
    assert len(new_questions) >= 20


def test_submit_answer():
    """测试提交答案。"""
    manager = PracticeManager()
    question = manager.questions[0]

    # 提交正确答案
    result = manager.submit_answer(question.question_id, question.correct_answer)
    assert result["is_correct"] is True

    # 提交错误答案
    result = manager.submit_answer(question.question_id, "X")
    assert result["is_correct"] is False


def test_check_answer():
    """测试答案检查。"""
    manager = PracticeManager()

    # 单选题
    single = [q for q in manager.questions if not q.is_multiple_choice][0]
    assert single.check_answer(single.correct_answer) is True

    # 多选题
    multi = [q for q in manager.questions if q.is_multiple_choice][0]
    assert multi.check_answer(multi.correct_answer) is True
    assert multi.check_answer(multi.correct_answer[::-1]) is True  # 顺序不同
