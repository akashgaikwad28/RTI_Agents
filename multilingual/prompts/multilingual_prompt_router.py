"""Routes agent prompts by response language."""

from __future__ import annotations

from multilingual.prompts import english_prompts, hindi_prompts, marathi_prompts


PROMPT_MODULES = {"en": english_prompts, "hi": hindi_prompts, "mr": marathi_prompts}


class MultilingualPromptRouter:
    def get(self, agent: str, language: str = "en") -> str:
        module = PROMPT_MODULES.get(language, english_prompts)
        key = f"{agent.upper()}_SYSTEM"
        return getattr(module, key, getattr(english_prompts, key, ""))
