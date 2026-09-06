from pydantic import BaseModel, Field


class SearchInput(BaseModel):

    query: str = Field(
        min_length=1,
        description="需要搜索的关键词"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="返回结果数量"
    )

    language: str | None = Field(
        default=None,
        description="搜索语言，可选"
    )


