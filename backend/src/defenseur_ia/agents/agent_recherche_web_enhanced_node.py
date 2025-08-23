"""
Wrapper Node to integrate AgentRechercheWebEnhanced into the pipeline orchestrator.
Provides BaseNode-compatible id/name and delegates exec to the enhanced agent.
"""

import logging
from typing import Any

from ..core.base import BaseNode, NodeContext
from .agent_recherche_web_enhanced import AgentRechercheWebEnhanced

logger = logging.getLogger(__name__)


class RechercheWebEnhancedNode(BaseNode):
    def __init__(self):
        super().__init__(node_id="recherche_web_enhanced", name="Recherche Web Enhanced")
        self.agent = AgentRechercheWebEnhanced()

    async def exec(self, ctx: NodeContext) -> None:
        # Delegate to the enhanced agent's exec (already implements all store writes & metadata)
        logger.info("🚀 Running Recherche Web Enhanced agent")
        await self.agent.exec(ctx)
        logger.info("✅ Recherche Web Enhanced agent completed")
