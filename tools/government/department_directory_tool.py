from __future__ import annotations

from pydantic import BaseModel

from tools.base.base_tool import BaseTool
from tools.department_lookup import get_valid_departments


class DepartmentInput(BaseModel):
    query: str = ""


class DepartmentDirectoryTool(BaseTool):
    name = "department_directory"
    description = "Read-only directory of RTI-relevant departments."
    category = "government"
    permissions = ["read:public"]
    capabilities = ["department_lookup", "routing"]
    input_schema = DepartmentInput
    cache_ttl_seconds = 3600

    async def execute(self, query: str = ""):
        departments = get_valid_departments()
        if query:
            lowered = query.lower()
            departments = [dept for dept in departments if any(part in dept.lower() for part in lowered.split())] or departments
        return {"departments": departments}

