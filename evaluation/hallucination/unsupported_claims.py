"""
Detects claims made in the text that are entirely unsupported by context or common sense governance.
"""
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from config.settings import settings

UNSUPPORTED_CLAIMS_PROMPT = PromptTemplate.from_template(
    """Analyze the STATEMENT against the provided FACTS.
    Identify any claims in the STATEMENT that are not supported by the FACTS.
    
    FACTS: {facts}
    STATEMENT: {statement}
    
    Return a JSON array of strings, where each string is an unsupported claim. If all claims are supported, return an empty array [].
    Ensure your response is valid JSON.
    """
)

class UnsupportedClaimsDetector:
    def __init__(self):
        self.llm = ChatGroq(model_name=settings.PRIMARY_MODEL, temperature=0.0, api_key=settings.GROQ_API_KEY)
        
    async def detect(self, statement: str, facts: list[str]) -> list[str]:
        if not facts:
            return ["No facts provided to support the statement."]
            
        import json
        prompt_val = UNSUPPORTED_CLAIMS_PROMPT.format(facts="\n".join(facts), statement=statement)
        try:
            response = await self.llm.ainvoke(prompt_val)
            content = response.content.strip()
            # Clean up markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            return json.loads(content)
        except Exception:
            return ["Failed to analyze claims."]
