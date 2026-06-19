"""Dynamic MCP-style tool registry."""

from __future__ import annotations

from collections import defaultdict
import re
from typing import Any

from tools.base.base_tool import BaseTool
from tools.base.tool_executor import ToolExecutor
from tools.base.tool_schemas import ToolExecutionResult, ToolInvocation, ToolMetadata


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._capabilities: dict[str, set[str]] = defaultdict(set)
        self.executor = ToolExecutor()

    def register_tool(self, tool: BaseTool) -> None:
        if not tool.name:
            raise ValueError("Tool name is required")
        self._tools[tool.name] = tool
        for capability in tool.capabilities:
            self._capabilities[capability].add(tool.name)

    def unregister_tool(self, name: str) -> None:
        self._tools.pop(name, None)
        for names in self._capabilities.values():
            names.discard(name)

    def get_tool(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"Tool not registered: {name}")
        return self._tools[name]

    def list_tools(self, *, permissions: list[str] | None = None, category: str | None = None) -> list[ToolMetadata]:
        allowed = set(permissions or [])
        tools = []
        for tool in self._tools.values():
            if category and tool.category != category:
                continue
            if tool.permissions and not set(tool.permissions).issubset(allowed):
                continue
            tools.append(tool.metadata)
        return tools

    def get_tools_by_capability(self, capability: str, *, permissions: list[str] | None = None) -> list[ToolMetadata]:
        return [tool for tool in self.discover_tools(capability) if self._allowed(tool.permissions, permissions)]

    def get_tools_by_department(self, department: str, *, permissions: list[str] | None = None) -> list[ToolMetadata]:
        normalized = department.lower()
        matches = []
        for tool in self._tools.values():
            departments = [d.lower() for d in (tool.supported_departments or tool.departments)]
            if not departments or any(normalized in dept or dept in normalized for dept in departments):
                if self._allowed(tool.permissions, permissions):
                    matches.append(tool.metadata)
        return matches

    def search_tools(self, query: str, *, permissions: list[str] | None = None, limit: int = 10) -> list[ToolMetadata]:
        tokens = set(re.findall(r"[a-z0-9_]+", query.lower()))
        scored = []
        for tool in self._tools.values():
            if not self._allowed(tool.permissions, permissions):
                continue
            haystack = " ".join([tool.name, tool.description, tool.category, *tool.capabilities, *tool.departments]).lower()
            score = sum(1 for token in tokens if token in haystack)
            if score:
                scored.append((score, tool.metadata))
        return [metadata for _, metadata in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]

    def auto_select_tools(self, query: str, department: str = "", *, permissions: list[str] | None = None, limit: int = 6) -> list[ToolMetadata]:
        candidates = self.search_tools(query, permissions=permissions, limit=limit * 2)
        if department:
            dept_matches = self.get_tools_by_department(department, permissions=permissions)
            by_name = {tool.name: tool for tool in [*dept_matches, *candidates]}
            candidates = list(by_name.values())
        if not candidates:
            candidates = self.list_tools(permissions=permissions)[:limit]
        return candidates[:limit]

    def discover_tools(self, capability: str, *, department: str | None = None) -> list[ToolMetadata]:
        names = self._capabilities.get(capability, set())
        tools = [self._tools[name] for name in names]
        if department:
            tools = [tool for tool in tools if not tool.departments or department in tool.departments]
        return [tool.metadata for tool in tools]

    def _allowed(self, required: list[str], permissions: list[str] | None) -> bool:
        allowed = set(permissions or [])
        return not required or set(required).issubset(allowed)

    async def execute_tool(
        self,
        name: str,
        payload: dict[str, Any],
        *,
        permissions: list[str] | None = None,
        request_id: str | None = None,
        department: str | None = None,
    ) -> ToolExecutionResult:
        invocation = ToolInvocation(
            tool_name=name,
            payload=payload,
            permissions=permissions or [],
            request_id=request_id,
            department=department,
        )
        return await self.executor.execute(self.get_tool(name), invocation)


_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
        auto_register_tools(_registry)
    return _registry


def auto_register_tools(registry: ToolRegistry) -> None:
    from tools.analytics.confidence_tool import ConfidenceTool
    from tools.analytics.grounding_score_tool import GroundingScoreTool
    from tools.analytics.hallucination_detector import HallucinationDetectorTool
    from tools.analytics.risk_analyzer_tool import RiskAnalyzerTool
    from tools.database.mongo_query_tool import MongoQueryTool
    from tools.government.circular_lookup_tool import CircularLookupTool
    from tools.government.department_directory_tool import DepartmentDirectoryTool
    from tools.government.department_lookup_tool import DepartmentLookupTool
    from tools.government.gov_search_tool import GovernmentSearchTool
    from tools.government.govt_search_tool import GovernmentWebsiteSearchTool
    from tools.government.gazette_search_tool import GazetteSearchTool
    from tools.government.budget_search_tool import BudgetSearchTool
    from tools.government.municipal_data_tool import MunicipalDataTool
    from tools.government.rti_history_tool import RTIHistoryTool
    from tools.government.website_scraper_tool import WebsiteScraperTool
    from tools.government.policy_search_tool import PolicySearchTool
    from tools.government.rti_guideline_tool import RTIGuidelineTool
    from tools.government.scheme_lookup_tool import SchemeLookupTool
    from tools.retrieval.citation_tool import CitationTool
    from tools.retrieval.hybrid_search_tool import HybridSearchTool
    from tools.retrieval.semantic_search_tool import SemanticSearchTool
    from tools.retrieval.summarizer_tool import SummarizerTool
    from tools.utility.formatter_tool import FormatterUtilityTool
    from tools.utility.language_detector_tool import LanguageDetectorTool
    from tools.utility.pii_redaction_tool import PIIRedactionTool
    from tools.utility.translator_tool import TranslatorUtilityTool
    from tools.utility.validator_tool import ValidatorTool

    for tool in [
        GovernmentSearchTool(), GovernmentWebsiteSearchTool(), PolicySearchTool(), DepartmentDirectoryTool(), DepartmentLookupTool(), CircularLookupTool(),
        GazetteSearchTool(), BudgetSearchTool(), MunicipalDataTool(), RTIHistoryTool(), WebsiteScraperTool(),
        SchemeLookupTool(), RTIGuidelineTool(), SemanticSearchTool(), HybridSearchTool(),
        CitationTool(), SummarizerTool(), TranslatorUtilityTool(), LanguageDetectorTool(),
        PIIRedactionTool(), ValidatorTool(), FormatterUtilityTool(), ConfidenceTool(), MongoQueryTool(),
        HallucinationDetectorTool(), GroundingScoreTool(), RiskAnalyzerTool(),
    ]:
        registry.register_tool(tool)
