# 业余无线电 A 类题库练习系统 - Agent 指南

## 项目概述

这是一个业余无线电 A 类操作证书在线练习系统。题目来源于 `data/class_a.pdf`，使用 Python 脚本解析 PDF 中的结构化题目数据。

**核心功能：**
- 随机练习
- 新题练习（未练习过的题）
- 错题练习（错题本）

## PDF 题目标识符格式

PDF 中的题目使用结构化标识符，解析时必须遵循：

```
[Q] - Question（题干）
[A]、[B]、[C]、[D] - 选项（单选/多选）
[T] - Topic/Tag（知识点分类，如 AC 表示 A类法规）
[P] - Position/Section（章节编号，如 1.1.1）
[I] - Item ID（唯一题号，如 MC2-0002，MC2=Multiple Choice Class 2）
[J] - Legacy ID（旧版题号兼容，如 LY0002）
```

**解析规则：**
- 每个题目必须包含 [Q] 和至少一个选项
- [T] 用于知识点分类和筛选
- [P] 对应教材章节，用于进度跟踪
- [I] 是题目主要索引，必须唯一
- 缺失的标识符使用默认值或跳过

## 开发命令

### 包管理器
项目使用 **uv** 作为包管理器：

```bash
# 安装依赖
uv sync

# 添加依赖
uv add <package>
uv add --dev <package>  # 开发依赖

# 运行 Python
uv run python <script>

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

### 测试命令

```bash
# 运行所有测试
uv run pytest

# 运行单个测试文件
uv run pytest tests/test_parser.py

# 运行单个测试函数
uv run pytest tests/test_parser.py::test_parse_question

# 运行带标记的测试
uv run pytest -m "not slow"

# 显示详细输出
uv run pytest -v

# 显示代码覆盖率
uv run pytest --cov=.
```

### 代码质量检查

```bash
# 类型检查
uv run mypy .

# Linting
uv run ruff check .

# 自动修复
uv run ruff check --fix .

# 格式化代码
uv run ruff format .
```

## 代码风格指南

### Python 代码规范

**遵循 PEP 8 标准，使用 ruff 进行格式化和检查。**

#### 导入顺序

```python
# 1. 标准库导入
import re
from pathlib import Path
from typing import Optional

# 2. 第三方库导入
import pdfplumber
from pydantic import BaseModel

# 3. 本地应用导入
from parser.question import Question
from utils.helpers import clean_text
```

#### 类型注解

```python
# 函数必须包含类型注解
def parse_question(text: str) -> Optional[Question]:
    """解析题目文本为 Question 对象。"""
    if not text:
        return None
    return Question.from_text(text)

# 使用 typing 模块
from typing import List, Dict, Optional, Union

data: Dict[str, List[str]] = {"questions": []}
items: Optional[List[Question]] = None
```

#### 命名约定

```python
# 模块名：小写，下划线分隔
question_parser.py  # ✓
QuestionParser.py   # ✗

# 类名：大驼峰
class QuestionBank:  # ✓
class question_bank: # ✗

# 函数/变量：小写，下划线分隔
def parse_pdf():     # ✓
def parsePDF():      # ✗

user_id = "001"      # ✓
userId = "001"       # ✗

# 常量：全大写
MAX_QUESTIONS = 100  # ✓
max_questions = 100  # ✗

# 私有成员：单下划线前缀
class Parser:
    def _clean_text(self):  # 内部方法
        self._cache = {}     # 内部属性
```

#### 错误处理

```python
# 使用具体异常
try:
    questions = parse_pdf(file_path)
except FileNotFoundError as e:
    logger.error(f"PDF 文件不存在: {file_path}")
    raise
except ValueError as e:
    logger.warning(f"题目解析失败: {e}")
    return []

# 自定义异常
class ParseError(Exception):
    """题目解析错误。"""
    pass

# 使用上下文管理器
with pdfplumber.open(pdf_path) as pdf:
    process_pdf(pdf)
```

#### 数据模型

```python
# 使用 Pydantic 定义数据模型
from pydantic import BaseModel, Field

class Question(BaseModel):
    """题目模型。"""
    question_id: str = Field(..., alias="[I]")
    content: str = Field(..., alias="[Q]")
    options: Dict[str, str] = Field(default_factory=dict)
    topic: str = Field(default="", alias="[T]")
    section: str = Field(default="", alias="[P]")
    correct_answer: Optional[str] = None

    class Config:
        populate_by_name = True  # 允许使用别名
```

#### 文档字符串

```python
def get_wrong_questions(user_id: str, limit: int = 20) -> List[Question]:
    """
    获取用户的错题列表。

    Args:
        user_id: 用户 ID
        limit: 返回题目数量上限

    Returns:
        错题列表，按错误次数降序排列
    """
    pass
```

#### 代码组织

```
radio/
├── data/                   # 数据文件（PDF、解析后的 JSON）
│   └── class_a.pdf
├── parser/                 # PDF 解析模块
│   ├── __init__.py
│   ├── pdf_parser.py       # PDF 提取逻辑
│   └── question.py         # 题目数据模型
├── practice/               # 练习模块
│   ├── __init__.py
│   ├── random.py           # 随机练习
│   ├── new_questions.py    # 新题练习
│   └── wrong_questions.py  # 错题练习
├── storage/                # 数据存储
│   ├── __init__.py
│   └── user_progress.py    # 用户进度跟踪
├── tests/                  # 测试目录
│   ├── test_parser.py
│   └── test_practice.py
├── pyproject.toml          # 项目配置（uv）
└── AGENTS.md               # 本文件
```

## 最佳实践

### 1. PDF 解析
- 使用 `pdfplumber` 或 `PyPDF2` 提取文本
- 使用正则表达式匹配标识符：`r'\[([QABCDTPIJ])\]([^\[]*?)(?=\[[A-Z]\]|$)'`
- 处理多行题目和跨页内容
- 解析后验证数据完整性

### 2. 用户进度跟踪
- 记录每题的练习次数、正确次数、最后练习时间
- 使用 JSON 或 SQLite 存储进度数据
- 新题判断：`练习次数 == 0`
- 错题判断：`正确次数 / 练习次数 < 0.6`

### 3. 测试优先
- 为解析逻辑编写单元测试
- 使用 fixtures 创建测试数据
- 边界情况：空 PDF、损坏的题目、缺失字段

### 4. 日志记录
```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"解析完成，共 {len(questions)} 题")
logger.debug(f"题目详情: {question.model_dump()}")
```

## 开发工作流

1. **新建功能分支**：`git checkout -b feature/pdf-parser`
2. **编写测试**：先写失败的测试
3. **实现功能**：让测试通过
4. **运行检查**：`ruff check . && mypy . && pytest`
5. **提交代码**：使用清晰的消息（如："feat: 添加 PDF 题目解析"）

## 常见任务

```bash
# 添加新的 PDF 解析依赖
uv add pdfplumber

# 创建新的题目数据模型
uv run touch parser/question.py

# 运行单个测试（开发时频繁使用）
uv run pytest tests/test_parser.py::test_parse_single_question -v
```

## 注意事项

- **不提交 PDF 文件到 Git**：已在 .gitignore 中排除
- **用户数据隐私**：进度数据不包含敏感信息
- **向后兼容**：解析器支持旧版题号 [J]
- **性能优化**：大型 PDF 使用流式处理
