"""Pluggable open-weight LLM client.

BLOCKER (see AGENT_CONTEXT.md): no open-weight LLM weights/inference endpoint
are reachable from this sandboxed environment. MockLLMClient implements the
same `explain(...)` interface a real client (e.g. a local vLLM/Ollama
open-weight model) would — it is a template renderer over already-verified
structured data, which also satisfies the hard "never invent availability"
requirement by construction: it cannot say anything not present in the input.
"""

from typing import List, Dict


class LLMClient:
    def explain(
        self,
        requested_amenity: str | None,
        requested_available: bool,
        verified_candidates: List[Dict],
    ) -> str:
        raise NotImplementedError


class MockLLMClient(LLMClient):
    def explain(
        self, requested_amenity, requested_available, verified_candidates
    ) -> str:
        parts = []
        if requested_amenity:
            if requested_available:
                parts.append(f"{requested_amenity} is currently available.")
            else:
                parts.append(f"{requested_amenity} is not available right now.")
        if verified_candidates:
            names = ", ".join(c["name"] for c in verified_candidates)
            parts.append(
                f"Based on verified live availability, you could instead try: {names}."
            )
        else:
            parts.append("No verified alternatives are available at this moment.")
        return " ".join(parts)


def get_llm_client() -> LLMClient:
    # Only 'mock' is wired in this environment; a real open-weight provider can
    # be added here behind the same LLMClient interface.
    return MockLLMClient()
