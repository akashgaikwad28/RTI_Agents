class ReasoningMemory:
    async def store_trace(self, db, request_id: str, reasoning_trace: list[dict]) -> None:
        if db is not None:
            await db["reasoning_memory"].insert_one({"request_id": request_id, "reasoning_trace": reasoning_trace})

