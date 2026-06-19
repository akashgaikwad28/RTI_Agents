"""
Harness to run the same query across multiple LLMs and measure cost, latency, and quality.
"""
import time
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

class LLMComparator:
    def __init__(self):
        self.models = {
            "groq-llama3": ChatGroq(model_name="llama3-70b-8192", temperature=0.0),
            "gemini-pro": ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.0)
        }
        
    async def compare(self, query: str, context: str) -> Dict[str, Any]:
        results = {}
        prompt = PromptTemplate.from_template("Answer {query} based on {context}")
        prompt_val = prompt.format(query=query, context=context)
        
        for name, llm in self.models.items():
            start = time.time()
            try:
                response = await llm.ainvoke(prompt_val)
                latency = time.time() - start
                
                # Extract token usage if available
                tokens_used = 0
                if hasattr(response, "response_metadata") and "token_usage" in response.response_metadata:
                    tokens_used = response.response_metadata["token_usage"].get("total_tokens", 0)
                    
                results[name] = {
                    "response": response.content,
                    "latency_sec": latency,
                    "tokens_used": tokens_used,
                    "status": "success"
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "latency_sec": time.time() - start
                }
                
        return results
