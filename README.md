# 业余无线电 A 类题库练习系统

基于业余无线电 A 类操作证书题库的在线练习系统，支持随机练习、新题练习和错题练习。

## 功能特性

- ✅ **683 道真题**：涵盖法规、操作、设备等知识点
- 🎲 **随机练习**：从题库随机抽取题目
- 🆕 **新题练习**：优先练习未做过的题目
- 📕 **错题本**：自动收集错误率 >60% 的题目
- 📊 **进度统计**：实时追踪学习进度和正确率
- 🎯 **单选/多选**：智能识别题目类型

## 快速开始

### 安装依赖

```bash
# 使用 uv 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

### 启动服务

```bash
# 启动 Web 服务
uv run python run.py

# 访问 http://localhost:8000
```

### 重新解析 PDF

如果题库更新，可以重新解析：

```bash
uv run python parse_pdf.py
```

## 项目结构

```
radio/
├── data/                   # 数据文件
│   ├── class_a.pdf        # 题库 PDF
│   └── questions.json     # 解析后的题目
├── parser/                 # PDF 解析模块
├── practice/               # 练习业务逻辑
├── storage/                # SQLite 数据存储
├── api/                    # FastAPI 后端
├── static/                 # 前端界面
├── tests/                  # 测试文件
└── run.py                  # 启动脚本
```

## 开发

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行单个测试文件
uv run pytest tests/test_parser.py

# 查看覆盖率
uv run pytest --cov=.
```

### 代码检查

```bash
# Linting
uv run ruff check .

# 类型检查
uv run mypy .

# 格式化代码
uv run ruff format .
```

## 技术栈

- **后端**: FastAPI + uvicorn
- **数据库**: SQLite
- **前端**: 原生 HTML/CSS/JavaScript
- **PDF 解析**: pdfplumber
- **数据验证**: Pydantic
- **测试**: pytest
- **包管理**: uv

## 题目数据格式

```json
{
  "question_id": "MC1-0003",
  "content": "题目内容",
  "options": {
    "A": "选项A",
    "B": "选项B",
    "C": "选项C",
    "D": "选项D"
  },
  "correct_answer": "AC",
  "section": "1.1.1",
  "legacy_id": "LY0004"
}
```

## API 接口

- `GET /` - 练习页面
- `GET /api/questions?mode=random&limit=20` - 获取题目
- `POST /api/submit` - 提交答案
- `GET /api/stats` - 获取统计信息

## 许可证

MIT
