class PolicyMemory:
    async def learn_department_mapping(self, db, query: str, department: str, confidence: str) -> None:
        if db is not None:
            await db["learned_department_mappings"].update_one(
                {"query_signature": query.lower()[:160]},
                {"$set": {"department": department, "confidence": confidence}, "$inc": {"observations": 1}},
                upsert=True,
            )

