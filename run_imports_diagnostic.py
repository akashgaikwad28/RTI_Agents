import sys
import os

PROJECT_ROOT = "C:\\Users\\akash\\RTI_Agents"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
env_path = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env.example"))

if not os.environ.get("GROQ_API_KEY") or "your_" in os.environ.get("GROQ_API_KEY", ""):
    os.environ["GROQ_API_KEY"] = "gsk_dummykey123456789012345678901234"
if not os.environ.get("GEMINI_API_KEY") or "your_" in os.environ.get("GEMINI_API_KEY", ""):
    os.environ["GEMINI_API_KEY"] = "AIzaSyDummyKey_12345678901234567890"

import traceback

modules_to_test = [
    "config.settings",
    "observability.structured_logger",
    "observability.metrics",
    "observability.tracing",
    "database.schema",
    "mcp_clients.mongo_client",
    "rag.vectorstore.faiss_store",
    "rag.vectorstore.semantic_cache",
    "tools.base.tool_registry",
    "graph.state",
    "graph.graph_builder",
    "graph.nodes.router_node",
    "graph.nodes.planner_node",
    "graph.nodes.formatter_node",
    "graph.nodes.classifier_node",
    "graph.nodes.tool_selection_node",
    "graph.nodes.retrieval_node",
    "graph.nodes.debate_node",
    "graph.nodes.critic_node",
    "graph.nodes.verifier_node",
    "graph.nodes.reviewer_node",
    "graph.nodes.approval_node",
    "graph.nodes.reflection_node",
    "graph.nodes.consensus_node",
    "graph.nodes.memory_learning_node",
    "graph.nodes.tracker_node",
    "api.main",
    "evaluation.datasets.versioning.dataset_manifest",
    "evaluation.datasets.versioning.dataset_hashing",
    "evaluation.datasets.versioning.dataset_registry",
    "evaluation.datasets.versioning.reproducibility_tracker",
    "evaluation.datasets.synthetic_generator",
    "evaluation.datasets.golden_dataset",
    "evaluation.datasets.multilingual_dataset",
    "evaluation.datasets.governance_cases",
    "evaluation.hallucination.grounding_checker",
    "evaluation.hallucination.contradiction_detector",
    "evaluation.hallucination.unsupported_claims",
    "evaluation.hallucination.citation_verifier",
    "evaluation.hallucination.hallucination_detector",
    "evaluation.latency.load_testing",
    "evaluation.reports.html_report_generator",
    "evaluation.replay.graph_replay",
    "api.routers.eval",
]

print("Starting Import Diagnostics with updated list...")
failed = []
for mod in modules_to_test:
    try:
        __import__(mod)
        print(f"[OK] {mod}")
    except Exception as e:
        print(f"[FAIL] {mod} - Error: {e}")
        # Only print traceback if it is NOT a simple ModuleNotFoundError on prompts.reviewer or api.schemas.request
        if "prompts.reviewer" not in str(e) and "api.schemas.request" not in str(e):
            traceback.print_exc()
        failed.append((mod, str(type(e).__name__) + ": " + str(e)))

print("\n--- Diagnostics Summary ---")
if not failed:
    print("All core modules imported successfully!")
else:
    print(f"{len(failed)} modules failed to import:")
    for mod, err in failed:
        print(f" - {mod}: {err}")
    sys.exit(1)
