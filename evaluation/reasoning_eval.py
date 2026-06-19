def reasoning_completeness(trace: list[dict]) -> float:
    required = {"planner_node", "tool_selection_node", "retrieval_node", "debate_node", "critic_node", "verifier_node"}
    seen = {item.get("node") for item in trace}
    return len(required & seen) / len(required)

