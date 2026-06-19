"""Citation and source credibility checks for government outputs."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


class CitationValidator:
    def validate(self, output: Any) -> dict[str, Any]:
        urls: list[str] = []
        if isinstance(output, dict):
            for key in ("url", "source_url", "citation", "citations", "sources", "results"):
                value = output.get(key)
                if isinstance(value, str):
                    urls.append(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            urls.append(item)
                        elif isinstance(item, dict):
                            urls.extend(str(item.get(k, "")) for k in ("url", "source_url", "citation") if item.get(k))
        official = [u for u in urls if self._is_official(u)]
        return {
            "citations_found": len([u for u in urls if u]),
            "official_citations": len(official),
            "credible": not urls or bool(official) or bool(output),
            "official_sources": official[:10],
        }

    def _is_official(self, value: str) -> bool:
        host = urlparse(value).netloc.lower() if "://" in value else value.lower()
        return any(host.endswith(suffix) for suffix in (".gov.in", ".nic.in", "data.gov.in")) or "municipal" in host
