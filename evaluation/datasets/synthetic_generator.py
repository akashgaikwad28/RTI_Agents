"""
Synthetic generator to dynamically produce datasets using LLMs.
"""
import uuid
import random
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from config.settings import settings
from evaluation.datasets.versioning.dataset_manifest import DatasetManifest, BenchmarkQuery

SYNTHETIC_PROMPT = PromptTemplate.from_template(
    """You are an expert RTI analyst. Generate {count} realistic, complex Right to Information (RTI) queries.
    Focus on the domain: {domain}.
    
    Output exactly {count} queries, one per line. No numbering, no extra text.
    """
)

class SyntheticGenerator:
    def __init__(self):
        self.llm = ChatGroq(model_name=settings.PRIMARY_MODEL, temperature=0.7)
        
    async def generate_dataset(self, domain: str, count: int, dataset_name: str) -> DatasetManifest:
        prompt_val = SYNTHETIC_PROMPT.format(count=count, domain=domain)
        response = await self.llm.ainvoke(prompt_val)
        
        lines = [line.strip() for line in response.content.split('\n') if line.strip()]
        queries = []
        for line in lines:
            queries.append(
                BenchmarkQuery(
                    id=f"synth_{uuid.uuid4().hex[:6]}",
                    query=line,
                    metadata={"generated_by": "synthetic_generator", "domain": domain}
                )
            )
            
        return DatasetManifest(
            dataset_name=dataset_name,
            version="1.0.0",
            description=f"Synthetic queries generated for {domain}",
            language="en",
            queries=queries
        )
