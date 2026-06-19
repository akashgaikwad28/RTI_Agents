"""
Evaluates the quality of the reasoning chain (Agent Scratchpad / Traces).
"""
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from config.settings import settings

CHAIN_PROMPT = PromptTemplate.from_template(
    """Analyze the following agent reasoning trace.
    Score the logical coherence from 0.0 to 1.0.
    1.0 means perfectly logical and step-by-step.
    0.0 means completely illogical jumps or loops.
    
    TRACE:
    {trace}
    
    Return ONLY a float between 0.0 and 1.0.
    """
)

class ChainQualityEvaluator:
    def __init__(self):
        self.llm = ChatGroq(model_name=settings.PRIMARY_MODEL, temperature=0.0)
        
    async def evaluate(self, trace_steps: list[str]) -> float:
        if not trace_steps:
            return 0.0
        prompt_val = CHAIN_PROMPT.format(trace="\n".join(trace_steps))
        try:
            response = await self.llm.ainvoke(prompt_val)
            return float(response.content.strip())
        except ValueError:
            return 0.0
