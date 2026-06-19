from __future__ import annotations

from tools.government.department_directory_tool import DepartmentDirectoryTool, DepartmentInput


class DepartmentLookupTool(DepartmentDirectoryTool):
    name = "department_lookup"
    description = "Validates department mapping, hierarchy, and likely RTI jurisdiction."
    input_schema = DepartmentInput
