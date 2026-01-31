"""FastAPI 应用。"""

import logging
from typing import Literal

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from practice.manager import PracticeManager

logger = logging.getLogger(__name__)

practice_manager = PracticeManager()

app = FastAPI(title="业余无线电 A 类题库练习系统")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

PracticeMode = Literal["random", "new", "wrong"]


@app.get("/")
async def index():
    """首页。"""
    from fastapi.responses import FileResponse

    return FileResponse("static/index.html")


@app.get("/api/questions")
async def get_questions(mode: PracticeMode = "random", limit: int = 20):
    """获取题目列表。"""
    if mode == "random":
        questions = practice_manager.get_random_questions(limit)
    elif mode == "new":
        questions = practice_manager.get_new_questions(limit)
    elif mode == "wrong":
        questions = practice_manager.get_wrong_questions(limit)
    else:
        questions = []

    return {
        "mode": mode,
        "count": len(questions),
        "questions": [q.model_dump(mode="json") for q in questions],
    }


@app.get("/api/questions/{question_id}")
async def get_question(question_id: str):
    """获取单个题目。"""
    question = practice_manager.get_question_by_id(question_id)
    if not question:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="题目不存在")

    return question.model_dump(mode="json")


@app.post("/api/submit")
async def submit_answer(data: dict):
    """提交答案。"""
    question_id = data.get("question_id")
    user_answer = data.get("answer", "")

    if not question_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="缺少题目ID")

    result = practice_manager.submit_answer(question_id, user_answer)
    return result


@app.get("/api/stats")
async def get_stats():
    """获取统计信息。"""
    return practice_manager.get_stats()
