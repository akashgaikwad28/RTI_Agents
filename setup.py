# setup.py
from setuptools import setup, find_packages

setup(
    name="rti_agent",
    version="0.1.0",
    packages=find_packages(include=["agents", "agents.*", "mcp_clients", "mcp_clients.*", "memory", "memory.*", "utils", "utils.*", "schemas", "schemas.*", "prompts", "prompts.*", "config", "config.*", "database", "database.*"]),
    include_package_data=True,
)
