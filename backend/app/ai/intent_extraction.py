"""LangGraph-based guest-intent extraction node (Phase 9C / F07C, Agent 10).

A minimal LangGraph StateGraph wraps the classification step so the pipeline
genuinely uses LangGraph for orchestration, with a deterministic keyword
classifier as the node body (no LLM call needed just to pick a category —
keeping intent extraction fast, transparent, and independent of the mocked
LLM used only for the final natural-language explanation).
"""

from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

CATEGORY_KEYWORDS = {
    "SPA": ["spa", "massage", "relax", "therapy"],
    "POOL": ["pool", "swim", "swimming"],
    "GYM": ["gym", "fitness", "workout", "weights"],
    "YOGA": ["yoga", "meditation", "stretch"],
    "SAUNA": ["sauna", "steam"],
    "DINING": ["dinner", "restaurant", "dining", "food", "eat"],
}


class IntentState(TypedDict):
    query: str
    intent_category: Optional[str]


def _classify_node(state: IntentState) -> IntentState:
    text = state["query"].lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return {"query": state["query"], "intent_category": category}
    return {"query": state["query"], "intent_category": None}


def _build_graph():
    graph = StateGraph(IntentState)
    graph.add_node("classify_intent", _classify_node)
    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", END)
    return graph.compile()


_compiled_graph = _build_graph()


def extract_intent(
    query: str, fallback_category: Optional[str] = None
) -> Optional[str]:
    result = _compiled_graph.invoke({"query": query, "intent_category": None})
    return result["intent_category"] or fallback_category
