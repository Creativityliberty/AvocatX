#!/usr/bin/env python3
"""
Run a focused test of RechercheWebEnhancedNode.
- Provides input: query, case_data, urgency
- Executes the node
- Verifies and prints: web_corpus, recherche_web_enhanced, agent_results, and ctx.metadata
"""

import os
import sys
import asyncio
from datetime import datetime

# Ensure package import from backend/src
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from defenseur_ia.core.base import NodeContext
from defenseur_ia.core.shared_store import SharedStore
from defenseur_ia.agents.agent_recherche_web_enhanced_node import RechercheWebEnhancedNode


async def main():
    shared = SharedStore()
    await shared.initialize()

    # Build context and inputs
    ctx = NodeContext(shared=shared, dossier_id="TEST_DOSSIER_ENHANCED")

    await shared.set("query", "Quelles sont les dernières jurisprudences sur l'OQTF en 2024 ?")
    await shared.set("case_data", {
        "type": "OQTF",
        "juridiction": "TA",
        "departement": "75",
        "details": {
            "nationalite": "marocaine",
            "situation_familiale": "marié",
            "enfants": 1,
        }
    })
    await shared.set("urgency", "normal")  # or 'urgence'

    node = RechercheWebEnhancedNode()

    print("[TEST] Starting RechercheWebEnhancedNode at", datetime.now().isoformat())
    await node.exec(ctx)
    print("[TEST] RechercheWebEnhancedNode finished at", datetime.now().isoformat())

    web_corpus = await shared.get("web_corpus")
    agent_output = await shared.get("recherche_web_enhanced")
    agent_results = await shared.get("agent_results")

    print("\n=== Verification ===")
    print("- web_corpus type:", type(web_corpus).__name__, "count:", len(web_corpus) if isinstance(web_corpus, list) else "n/a")
    if isinstance(web_corpus, list) and web_corpus:
        print("  sample:", {k: web_corpus[0].get(k) for k in ["url", "titre", "source", "pertinence", "date_acces"]})

    print("- recherche_web_enhanced present:", isinstance(agent_output, dict))
    if isinstance(agent_output, dict):
        result = agent_output.get("result", {})
        metrics = result.get("metrics", {})
        print("  metrics keys:", list(metrics.keys()))
        print("  citations count:", len(result.get("citations", [])))

    print("- agent_results appended:", isinstance(agent_results, list), "length:", len(agent_results) if isinstance(agent_results, list) else "n/a")

    print("\n- ctx.metadata:")
    for k in ["status", "execution_time_seconds", "models_used", "citations_count", "start_time", "agent"]:
        print(f"  {k} =", ctx.get_metadata(k))


if __name__ == "__main__":
    asyncio.run(main())
