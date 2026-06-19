"""Deterministic mock for the LLM router and agents."""

from pydantic import BaseModel
from unittest.mock import MagicMock

class MockLLMResponse:
    def __init__(self, content: str):
        self.content = content

class MockStructuredLLM:
    def __init__(self, schema):
        self.schema = schema

    async def ainvoke(self, messages, *args, **kwargs):
        # Return a deterministic mock output based on the schema class
        schema_name = self.schema.__name__ if hasattr(self.schema, "__name__") else str(self.schema)
        
        if "RouterOutput" in schema_name:
            return self.schema(
                intent="new_request",
                reason="Mocked router decision for formal RTI query"
            )
        elif "ClassificationOutput" in schema_name:
            return self.schema(
                department="Public Works Department",
                sub_department="Roads and Infrastructure",
                confidence="high",
                notes="Mocked classification decision"
            )
        elif "ReviewOutput" in schema_name:
            return self.schema(
                review_passed=True,
                review_score=0.95,
                grounding_score=0.98,
                hallucination_flags=[],
                review_feedback="Mocked review passed successfully",
                suggested_improvements=[]
            )
        else:
            return MagicMock(spec=self.schema)

class MockLLM:
    def __init__(self, *args, **kwargs):
        pass

    def with_structured_output(self, schema, *args, **kwargs):
        return MockStructuredLLM(schema)

    async def ainvoke(self, messages, *args, **kwargs):
        # Convert messages list to content string for routing
        prompt_content = ""
        if isinstance(messages, list):
            for m in messages:
                if isinstance(m, dict):
                    prompt_content += " " + m.get("content", "")
                elif hasattr(m, "content"):
                    prompt_content += " " + getattr(m, "content", "")
        else:
            prompt_content = str(messages)

        if "formatter" in prompt_content or "Applicant" in prompt_content or "format" in prompt_content:
            return MockLLMResponse(
                content='{"formal_query": "This is a structured, legally sound formal RTI request draft regarding PWD road construction projects in 2024.", "rti_template": {"applicant_name": "Applicant", "subject": "PWD Road Budget"}}'
            )
        elif "reflection" in prompt_content or "reflection_needed" in prompt_content:
            return MockLLMResponse(
                content='{"reflection_needed": false, "reflection_reason": "Mocked reflection path verified", "retry_count": 0}'
            )
        else:
            return MockLLMResponse(
                content="Mocked LLM generic response"
            )
