"""题目数据模型。"""

from pydantic import BaseModel, ConfigDict, Field


class Question(BaseModel):
    """题目模型。"""

    model_config = ConfigDict(populate_by_name=True)

    question_id: str = Field(default="", alias="[I]")
    content: str = Field(default="", alias="[Q]")
    options: dict[str, str] = Field(default_factory=dict)
    correct_answer: str = Field(default="", alias="[T]")
    section: str = Field(default="", alias="[P]")
    legacy_id: str = Field(default="", alias="[J]")

    @property
    def is_multiple_choice(self) -> bool:
        """是否为多选题。"""
        return len(self.correct_answer) > 1

    def has_option(self, option: str) -> bool:
        """检查是否有指定选项。"""
        return option in self.options

    def check_answer(self, user_answer: str) -> bool:
        """检查答案是否正确。"""
        return set(user_answer) == set(self.correct_answer)
