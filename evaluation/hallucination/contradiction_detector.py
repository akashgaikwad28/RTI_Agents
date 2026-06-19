"""
Detects contradictory statements within the LLM's own output or between output and context.
"""
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from config.settings import settings

CONTRADICTION_PROMPT = PromptTemplate.from_template(
    """Analyze the following text for internal contradictions.
    A contradiction occurs when the text makes two statements that cannot both be true simultaneously.
    
    TEXT: {text}
    
    Return ONLY 'True' if a contradiction exists, or 'False' if it is consistent.
    """
)

class ContradictionDetector:
    def __init__(self):
        self.llm = ChatGroq(model_name=settings.PRIMARY_MODEL, temperature=0.0, api_key=settings.GROQ_API_KEY)
        
    async def has_contradiction(self, text: str) -> bool:
        prompt_val = CONTRADICTION_PROMPT.format(text=text)
        response = await self.llm.ainvoke(prompt_val)
        return response.content.strip().lower() == "true"
