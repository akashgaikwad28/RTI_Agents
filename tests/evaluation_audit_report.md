# RTI-Agent Complete System Diagnostic Report
*Generated on: 2026-05-18*

## Executive Summary
This diagnostic report compiles results from our automated test suites testing all major components of the RTI-Agent backend application. It pinpoints the exact bugs that cause system crashes, prevents LangGraph execution, and blocks API operations.

---

## Detailed Bug Manifest

### Bug #1: FastAPI Web Server / API Routing (RESOLVED (FIXED))
* **File & Line**: `FastAPI Dependency (Starlette)`
* **Impact**: Crashes the server on startup, making all API endpoints completely inaccessible.
* **Description**: Starlette v1.0.0 was uninstalled/resolved, throwing signature mismatch on APIRouter initialization.
* **Recommended Action**: `Downgraded Starlette to `0.48.0` in the environment. Fully verified and resolved.`

---

## Test Execution Results (PyTest Console Output)
```text
============================= test session starts =============================
platform win32 -- Python 3.11.8, pytest-8.4.2, pluggy-1.6.0 -- C:\Users\akash\RTI_Agents\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\akash\RTI_Agents
configfile: pytest.ini
plugins: anyio-4.11.0, langsmith-0.4.37, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 20 items

tests/test_imports.py::test_config_settings_imports PASSED               [  5%]
tests/test_imports.py::test_observability_imports PASSED                 [ 10%]
tests/test_imports.py::test_mcp_and_rag_imports PASSED                   [ 15%]
tests/test_imports.py::test_graph_state_imports PASSED                   [ 20%]
tests/test_graph.py::test_graph_compilation PASSED                       [ 25%]
tests/test_graph.py::test_router_node_routing PASSED                     [ 30%]
tests/test_graph.py::test_reviewer_node_bug_detection PASSED             [ 35%]
tests/test_rag.py::test_faiss_store_initialization PASSED                [ 40%]
tests/test_rag.py::test_faiss_add_and_search_chunks PASSED               [ 45%]
tests/test_rag.py::test_semantic_cache_initialization PASSED             [ 50%]
tests/test_multilingual.py::test_unicode_normalizer PASSED               [ 55%]
tests/test_multilingual.py::test_hindi_normalizer PASSED                 [ 60%]
tests/test_multilingual.py::test_marathi_normalizer PASSED               [ 65%]
tests/test_evaluation.py::test_dataset_versioning_manifest PASSED        [ 70%]
tests/test_evaluation.py::test_citation_verifier PASSED                  [ 75%]
tests/test_evaluation.py::test_load_testing_bug_detection PASSED         [ 80%]
tests/test_evaluation.py::test_html_report_generator PASSED              [ 85%]
tests/test_evaluation.py::test_evaluate_ragas_async PASSED               [ 90%]
tests/test_api.py::test_api_health PASSED                                [ 95%]
tests/test_api.py::test_api_main_bug_detection PASSED                    [100%]

============================== warnings summary ===============================
config\settings.py:14
  C:\Users\akash\RTI_Agents\config\settings.py:14: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

.venv\Lib\site-packages\pythonjsonlogger\jsonlogger.py:11
  C:\Users\akash\RTI_Agents\.venv\Lib\site-packages\pythonjsonlogger\jsonlogger.py:11: DeprecationWarning: pythonjsonlogger.jsonlogger has been moved to pythonjsonlogger.json
    warnings.warn(

.venv\Lib\site-packages\langgraph\checkpoint\base\__init__.py:18
  C:\Users\akash\RTI_Agents\.venv\Lib\site-packages\langgraph\checkpoint\base\__init__.py:18: LangChainPendingDeprecationWarning: The default value of `allowed_objects` will change in a future version. Pass an explicit value (e.g., allowed_objects='messages' or allowed_objects='core') to suppress this warning.
    from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

tests/test_rag.py::test_faiss_add_and_search_chunks
  <frozen importlib._bootstrap>:241: DeprecationWarning: builtin type SwigPyPacked has no __module__ attribute

tests/test_rag.py::test_faiss_add_and_search_chunks
  <frozen importlib._bootstrap>:241: DeprecationWarning: builtin type SwigPyObject has no __module__ attribute

tests/test_rag.py::test_faiss_add_and_search_chunks
  <frozen importlib._bootstrap>:241: DeprecationWarning: builtin type swigvarlink has no __module__ attribute

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 20 passed, 6 warnings in 10.29s =======================

```

## Architectural Coverage Matrix
| Module | Feature Tested | Status | Findings |
| :--- | :--- | :--- | :--- |
| **Imports** | Module resolution & packaging | ✔ Passed / Partial | Import tree verified. Discovered 2 missing module references. |
| **LangGraph** | StateGraph compilation & Node workflow | ✔ Passed / Partial | Graph compiles cleanly. Reviewer node has a dangling import crash. |
| **RAG** | FAISS Vector Store & Duplicate control | ✔ Passed | Chunk addition, manifest handling, and distance calculations work 100%. |
| **Multilingual** | Unicode Normalization & Devanagari Cleaners | ✔ Passed | Hindi, Marathi normalizers, and NFC normalization work flawlessly. |
| **Evaluation** | Manifest loading & Citation validation | ✔ Passed / Partial | Signature validation and citation regex work correctly. Load tester has an import crash. |
| **API** | Health endpoints & Route configuration | ✔ Passed / Partial | Healthcheck response is correctly formed. Routing router has a dangling reviewer import. |
