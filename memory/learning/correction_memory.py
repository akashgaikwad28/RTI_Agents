class CorrectionMemory:
    async def store_correction(self, db, request_id: str, correction: dict) -> None:
        if db is not None:
            await db["correction_memory"].insert_one({"request_id": request_id, **correction})

