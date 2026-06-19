"""
LLM-as-judge Grounding Checker.
Evaluates if a generated output is strictly grounded in the provided contexts.
"""
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from config.settings import settings

GROUNDING_PROMPT = PromptTemplate.from_template(
    """You are a strict fact-checker. Determine if the STATEMENT is entirely supported by the CONTEXT.
    If the STATEMENT contains ANY fact not present in the CONTEXT, return 0.0.
    If the STATEMENT is fully supported, return 1.0.
    If partially supported, return a float between 0.0 and 1.0.

    CONTEXT: {context}
    STATEMENT: {statement}

    Respond ONLY with a float number between 0.0 and 1.0. Do not provide explanations.
    """
)

class GroundingChecker:
    def __init__(self):
        self.llm = ChatGroq(model_name=settings.PRIMARY_MODEL, temperature=0.0, api_key=settings.GROQ_API_KEY)
        
    async def check_grounding(self, statement: str, contexts: list[str]) -> float:
        if not contexts:
            return 0.0
            
        context_str = "\n".join(contexts)
        prompt_val = GROUNDING_PROMPT.format(context=context_str, statement=statement)
        try:
            response = await self.llm.ainvoke(prompt_val)
            score = float(response.content.strip())
            return max(0.0, min(1.0, score))
        except ValueError:
            return 0.0  # Fallback on failure
