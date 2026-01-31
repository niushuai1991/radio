"""API 测试。"""

import pytest
from fastapi.testclient import TestClient

from api.app import app


@pytest.fixture
def client():
    """测试客户端。"""
    return TestClient(app)


def test_root(client):
    """测试首页。"""
    response = client.get("/")
    assert response.status_code == 200


def test_get_questions(client):
    """测试获取题目。"""
    response = client.get("/api/questions?mode=random&limit=5")
    assert response.status_code == 200

    data = response.json()
    assert "mode" in data
    assert "count" in data
    assert "questions" in data
    assert data["mode"] == "random"
    assert data["count"] <= 5


def test_submit_answer(client):
    """测试提交答案。"""
    response = client.post(
        "/api/submit",
        json={"question_id": "MC1-0003", "answer": "AC"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "is_correct" in data
    assert "question_id" in data


def test_stats(client):
    """测试统计接口。"""
    response = client.get("/api/stats")
    assert response.status_code == 200

    data = response.json()
    assert "total_questions" in data
    assert "total_practiced" in data
    assert "accuracy" in data
