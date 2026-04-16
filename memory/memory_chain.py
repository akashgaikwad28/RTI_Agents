# memory/memory_chain.py

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from memory.memory_manager import MemoryManager

class MemoryChain:
    """
    MemoryChain interfaces with LLM to determine
    what to remember, forget, or retrieve.
    """

    def __init__(self):
        self.manager = MemoryManager()
        self.llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0.3)
        self.prompt = PromptTemplate(
            input_variables=["context", "query"],
            template=(
                "You are a memory reasoning assistant.\n"
                "Given the previous context:\n{context}\n\n"
                "And the new user query:\n{query}\n\n"
                "Determine what information should be remembered or forgotten."
            ),
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def update_memory(self, session_id: str, query: str):
        """Update context based on LLM decision."""
        old_context = self.manager.load_context(session_id)
        context_text = str(old_context)
        decision = self.chain.run(context=context_text, query=query)
        self.manager.save_context(session_id, {"last_query": query, "decision": decision})
        self.manager.add_to_vector_memory(decision)
        return decision

    def recall(self, session_id: str):
        """Recall stored memory."""
        return self.manager.load_context(session_id)
