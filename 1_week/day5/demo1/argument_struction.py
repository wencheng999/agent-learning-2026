from typing import Literal

from pydantic import BaseModel


class ToolDecision(BaseModel):
    tool: Literal[
        "search",
        "calculator"
    ]

    arguments: dict

schema = ToolDecision.model_json_schema()
print(schema)

import json


schema_text = json.dumps(
    schema,
    ensure_ascii=False,
    indent=2
)
print(schema_text)
print(type(schema_text))