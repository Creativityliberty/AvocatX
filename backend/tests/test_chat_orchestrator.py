"""
Tests d'intégration pour le ChatOrchestrator.

Ces tests vérifient l'intégration du ChatOrchestrator avec le pipeline existant.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path
import sys

# Ajout du répertoire racine au PYTHONPATH pour les imports
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Import du module à tester
from src.defenseur_ia.services.chat_orchestrator import ChatOrchestrator, CommandType

@pytest.fixture
def mock_pipeline():
    """Crée un mock du pipeline pour les tests."""
    pipeline = MagicMock()
    pipeline.create_flow.return_value = "test_flow_123"
    pipeline.execute_flow = AsyncMock()
    # Ensure get_flow_status is an async mock
    pipeline.get_flow_status = AsyncMock(return_value={"status": "running", "progress": 50})
    return pipeline

@pytest.fixture
def chat_orchestrator(mock_pipeline):
    """Crée une instance de ChatOrchestrator avec un mock de pipeline."""
    return ChatOrchestrator(mock_pipeline)

@pytest.mark.asyncio
async def test_handle_start_command(chat_orchestrator, mock_pipeline):
    """Teste la commande /start."""
    # Exécution
    response = await chat_orchestrator.handle_message("/start", "test_user_123")
    
    # Vérifications
    assert response["status"] == "success"
    assert "test_flow_123" in response["response"]
    mock_pipeline.create_flow.assert_called_once()
    mock_pipeline.execute_flow.assert_called_once_with("test_flow_123")
    
    # Vérification que le flux est bien enregistré
    assert "test_flow_123" in chat_orchestrator.active_flows
    assert chat_orchestrator.active_flows["test_flow_123"]["user_id"] == "test_user_123"

@pytest.mark.asyncio
async def test_handle_status_command_global(chat_orchestrator, mock_pipeline):
    """Teste la commande /status sans argument."""
    # Préparation
    await chat_orchestrator.handle_message("/start", "test_user_123")
    
    # Exécution
    response = await chat_orchestrator.handle_message("/status", "test_user_123")
    
    # Vérifications
    assert response["status"] == "success"
    assert "1 flux actifs" in response["response"]

@pytest.mark.asyncio
async def test_handle_status_command_specific_flow(chat_orchestrator, mock_pipeline):
    """Teste la commande /status avec un ID de flux spécifique."""
    # Préparation
    await chat_orchestrator.handle_message("/start", "test_user_123")
    flow_id = "test_flow_123"
    
    # Exécution
    response = await chat_orchestrator.handle_message(f"/status {flow_id}", "test_user_123")
    
    # Vérifications
    assert response["status"] == "success"
    assert flow_id in response["response"]
    assert "running" in response["response"]  # Vérifie le statut renvoyé par le mock

@pytest.mark.asyncio
async def test_handle_pause_command(chat_orchestrator, mock_pipeline):
    """Teste la commande /pause."""
    # Préparation
    await chat_orchestrator.handle_message("/start", "test_user_123")
    flow_id = "test_flow_123"
    
    # Exécution
    response = await chat_orchestrator.handle_message(f"/pause {flow_id}", "test_user_123")
    
    # Vérifications
    assert response["status"] == "success"
    assert "mis en pause" in response["response"]
    assert chat_orchestrator.active_flows[flow_id]["status"] == "paused"

@pytest.mark.asyncio
async def test_handle_help_command(chat_orchestrator):
    """Teste la commande /help."""
    # Exécution
    response = await chat_orchestrator.handle_message("/help", "test_user_123")
    
    # Vérifications
    assert response["status"] == "success"
    assert "Commandes disponibles" in response["response"]
    assert "/status" in response["response"]
    assert "/start" in response["response"]
    assert "/pause" in response["response"]
    assert "/help" in response["response"]

@pytest.mark.asyncio
async def test_handle_unknown_command(chat_orchestrator):
    """Teste une commande inconnue."""
    # Exécution
    response = await chat_orchestrator.handle_message("/commande_inconnue", "test_user_123")
    
    # Vérifications
    assert response["status"] == "error"
    assert "non reconnue" in response["response"]

@pytest.mark.asyncio
async def test_handle_empty_message(chat_orchestrator):
    """Teste un message vide."""
    # Exécution
    response = await chat_orchestrator.handle_message("", "test_user_123")
    
    # Vérifications
    assert response["status"] == "error"
    assert "non reconnue" in response["response"]

# Exécution des tests si le fichier est exécuté directement
if __name__ == "__main__":
    pytest.main(["-v", "tests/test_chat_orchestrator.py"])
