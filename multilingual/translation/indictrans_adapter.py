"""IndicTrans adapter placeholder for local deployment."""

from __future__ import annotations


class IndicTransAdapter:
    async def translate(self, text: str, source_language: str, target_language: str) -> str:
        try:
            # Hook for ai4bharat/IndicTrans2 local service when deployed.
            import httpx

            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    "http://localhost:8008/translate",
                    json={"text": text, "source_language": source_language, "target_language": target_language},
                )
                if response.status_code == 200:
                    return response.json().get("translated_text") or text
        except Exception:
            pass
        return text
