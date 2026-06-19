"""
Detects gaps in retrieval, such as when the model has to hallucinate because the retrieval system failed to provide sufficient information.
"""
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from config.settings import settings

GAP_PROMPT = PromptTemplate.from_template(
    """Analyze the QUERY and the RETRIEVED_CONTEXT.
    Identify if there are critical pieces of information required to answer the QUERY that are MISSING from the RETRIEVED_CONTEXT.
    
    QUERY: {query}
    RETRIEVED_CONTEXT: {context}
    
    Return a JSON array of strings describing the missing information. If nothing is missing, return [].
    """
)

class RetrievalGapDetector:
    def __init__(self):
        self.llm = ChatGroq(model_name=settings.PRIMARY_MODEL, temperature=0.0)
        
    async def detect_gaps(self, query: str, context: list[str]) -> list[str]:
        if not context:
            return ["Complete retrieval failure. No context provided."]
            
        import json
        prompt_val = GAP_PROMPT.format(query=query, context="\n".join(context))
        try:
            response = await self.llm.ainvoke(prompt_val)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception:
            return ["Failed to analyze gaps."]
