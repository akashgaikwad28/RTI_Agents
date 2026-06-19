"""Semantic diff detection for document versioning."""

from __future__ import annotations

import difflib
import hashlib
from typing import TypedDict

class DiffResult(TypedDict):
    has_changes: bool
    change_summary: str
    content_delta_hash: str

class DiffDetector:
    @staticmethod
    def compute_diff(old_text: str, new_text: str) -> DiffResult:
        """Computes semantic difference and generates change summary."""
        if old_text == new_text:
            return {
                "has_changes": False,
                "change_summary": "No semantic changes detected.",
                "content_delta_hash": ""
            }
            
        matcher = difflib.SequenceMatcher(None, old_text.splitlines(), new_text.splitlines())
        additions = 0
        deletions = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                additions += (j2 - j1)
            elif tag == 'delete':
                deletions += (i2 - i1)
            elif tag == 'replace':
                additions += (j2 - j1)
                deletions += (i2 - i1)
                
        summary = f"Detected {additions} added lines and {deletions} removed lines."
        delta_hash = hashlib.sha256(f"{additions}_{deletions}_{len(new_text)}".encode()).hexdigest()
        
        return {
            "has_changes": True,
            "change_summary": summary,
            "content_delta_hash": delta_hash
        }
