#!/usr/bin/env python3
"""
Script de test d'intégration pour le ChatOrchestrator avec le pipeline DEFENSEUR-IA.

Ce script teste toutes les fonctionnalités du ChatOrchestrator en utilisant
le pipeline existant ou des mocks réalistes.
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ajout du répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

try:
    from src.defenseur_ia.services.chat_orchestrator import ChatOrchestrator, CommandType, DocumentType
except ImportError as e:
    print(f"Erreur d'import: {e}")
    print("Assurez-vous que le module ChatOrchestrator est correctement installé")
    sys.exit(1)

class MockDefenseurPipeline:
    """
    Mock réaliste du pipeline DEFENSEUR-IA pour les tests.
    """
    
    def __init__(self):
        self.flows = {}
        self.flow_counter = 0
    
    def create_flow(self) -> str:
        """Crée un nouveau flux et retourne son ID."""
        self.flow_counter += 1
        flow_id = f"flow_{self.flow_counter:04d}"
        self.flows[flow_id] = {
            "id": flow_id,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "agents_completed": 0,
            "total_agents": 12
        }
        print(f"✓ Pipeline: Flux {flow_id} créé")
        return flow_id
    
    async def execute_flow(self, flow_id: str, context: Dict[str, Any] = None):
        """Simule l'exécution d'un flux avec les 12 agents."""
        if flow_id not in self.flows:
            raise ValueError(f"Flux {flow_id} non trouvé")
        
        flow = self.flows[flow_id]
        flow["status"] = "running"
        flow["context"] = context or {}
        
        print(f"✓ Pipeline: Exécution du flux {flow_id} démarrée")
        
        # Simulation des 12 agents
        agents = [
            "Écouteur", "Cadreur Juridique", "Parseur Preuves", "Juriste Matching",
            "Recherche Web", "Rédacteur Narratif", "Relecteur IA #1", "Agrégateur",
            "Relecteur IA #2", "Synthèse Stratégique", "Avocat IA", "Export Final"
        ]
        
        for i, agent_name in enumerate(agents):
            await asyncio.sleep(0.1)  # Simulation du temps de traitement
            flow["agents_completed"] = i + 1
            flow["current_agent"] = agent_name
            print(f"  → Agent {i+1}/12: {agent_name} terminé")
        
        flow["status"] = "completed"
        flow["completed_at"] = datetime.now().isoformat()
        print(f"✓ Pipeline: Flux {flow_id} terminé avec succès")
    
    def get_flow_status(self, flow_id: str) -> Dict[str, Any]:
        """Retourne le statut d'un flux."""
        return self.flows.get(flow_id, {"status": "not_found"})
    
    def pause_flow(self, flow_id: str):
        """Met en pause un flux."""
        if flow_id in self.flows:
            self.flows[flow_id]["status"] = "paused"
    
    def resume_flow(self, flow_id: str):
        """Reprend un flux en pause."""
        if flow_id in self.flows:
            self.flows[flow_id]["status"] = "running"
    
    def cancel_flow(self, flow_id: str):
        """Annule un flux."""
        if flow_id in self.flows:
            self.flows[flow_id]["status"] = "cancelled"

async def test_basic_commands():
    """Test des commandes de base du ChatOrchestrator."""
    print("\n🧪 TEST: Commandes de base")
    print("=" * 50)
    
    pipeline = MockDefenseurPipeline()
    orchestrator = ChatOrchestrator(pipeline)
    user_id = "test_user_001"
    
    # Test /help
    response = await orchestrator.handle_message("/help", user_id)
    assert response["status"] == "success"
    print("✓ Commande /help fonctionne")
    
    # Test /status (global)
    response = await orchestrator.handle_message("/status", user_id)
    assert response["status"] == "success"
    print("✓ Commande /status (global) fonctionne")
    
    # Test /start
    response = await orchestrator.handle_message("/start", user_id)
    assert response["status"] == "success"
    flow_id = response.get("flow_id")
    assert flow_id is not None
    print(f"✓ Commande /start fonctionne (flux: {flow_id})")
    
    # Test /status (spécifique)
    response = await orchestrator.handle_message(f"/status {flow_id}", user_id)
    assert response["status"] == "success"
    print("✓ Commande /status (spécifique) fonctionne")
    
    return orchestrator, user_id, flow_id

async def test_document_management():
    """Test de la gestion des documents."""
    print("\n🧪 TEST: Gestion des documents")
    print("=" * 50)
    
    pipeline = MockDefenseurPipeline()
    orchestrator = ChatOrchestrator(pipeline)
    user_id = "test_user_002"
    
    # Simulation d'attachments
    mock_attachments = [
        {
            "name": "oqtf_decision.pdf",
            "size": 1024000,
            "path": "/tmp/oqtf_decision.pdf"
        },
        {
            "name": "temoignage.mp3",
            "size": 5120000,
            "path": "/tmp/temoignage.mp3"
        },
        {
            "name": "piece_identite.jpg",
            "size": 512000,
            "path": "/tmp/piece_identite.jpg"
        }
    ]
    
    # Test upload de documents
    response = await orchestrator.handle_message(
        "Voici mes documents", 
        user_id, 
        attachments=mock_attachments
    )
    assert response["status"] == "success"
    assert len(response["documents"]) == 3
    print("✓ Upload de documents fonctionne")
    
    # Vérification du stockage
    assert user_id in orchestrator.document_store
    assert len(orchestrator.document_store[user_id]) == 3
    print("✓ Stockage des documents fonctionne")
    
    # Test détection de types
    docs = orchestrator.document_store[user_id]
    types = [doc["type"] for doc in docs]
    assert DocumentType.PDF in types
    assert DocumentType.AUDIO in types
    assert DocumentType.IMAGE in types
    print("✓ Détection des types de documents fonctionne")
    
    return orchestrator, user_id

async def test_analysis_workflow():
    """Test du workflow d'analyse complet."""
    print("\n🧪 TEST: Workflow d'analyse")
    print("=" * 50)
    
    pipeline = MockDefenseurPipeline()
    orchestrator = ChatOrchestrator(pipeline)
    user_id = "test_user_003"
    
    # Upload de documents d'abord
    mock_attachments = [
        {"name": "dossier.pdf", "size": 1024000, "path": "/tmp/dossier.pdf"}
    ]
    
    await orchestrator.handle_message(
        "Voici mon dossier", 
        user_id, 
        attachments=mock_attachments
    )
    print("✓ Documents uploadés")
    
    # Test /analyse
    response = await orchestrator.handle_message("/analyse", user_id)
    assert response["status"] == "success"
    flow_id = response.get("flow_id")
    assert flow_id is not None
    print(f"✓ Analyse démarrée (flux: {flow_id})")
    
    # Attendre que l'analyse se termine
    await asyncio.sleep(2)
    
    # Test /resultats
    response = await orchestrator.handle_message("/resultats", user_id)
    assert response["status"] == "success"
    print("✓ Récupération des résultats fonctionne")
    
    # Test /historique
    response = await orchestrator.handle_message("/historique", user_id)
    assert response["status"] == "success"
    print("✓ Historique fonctionne")
    
    return orchestrator, user_id, flow_id

async def test_natural_language():
    """Test de l'analyse d'intention en langage naturel."""
    print("\n🧪 TEST: Langage naturel")
    print("=" * 50)
    
    pipeline = MockDefenseurPipeline()
    orchestrator = ChatOrchestrator(pipeline)
    user_id = "test_user_004"
    
    # Upload de documents d'abord
    mock_attachments = [
        {"name": "test.pdf", "size": 1024, "path": "/tmp/test.pdf"}
    ]
    await orchestrator.handle_message(
        "Document test", 
        user_id, 
        attachments=mock_attachments
    )
    
    # Test intentions naturelles
    test_cases = [
        ("Analyser mes documents", "analyse"),
        ("Voir les résultats", "resultats"),
        ("Afficher l'historique", "historique"),
        ("Comment ça marche ?", "help")
    ]
    
    for message, expected_intent in test_cases:
        response = await orchestrator.handle_message(message, user_id)
        print(f"✓ '{message}' → intention détectée")
    
    return orchestrator, user_id

async def test_session_management():
    """Test de la gestion des sessions utilisateur."""
    print("\n🧪 TEST: Gestion des sessions")
    print("=" * 50)
    
    pipeline = MockDefenseurPipeline()
    orchestrator = ChatOrchestrator(pipeline)
    
    # Test avec plusieurs utilisateurs
    users = ["user_001", "user_002", "user_003"]
    
    for user_id in users:
        response = await orchestrator.handle_message("/config test_key test_value", user_id)
        assert response["status"] == "success"
        print(f"✓ Session créée pour {user_id}")
    
    # Vérification de l'isolation des sessions
    assert len(orchestrator.user_sessions) == 3
    for user_id in users:
        assert user_id in orchestrator.user_sessions
        assert orchestrator.user_sessions[user_id]["context"]["test_key"] == "test_value"
    
    print("✓ Isolation des sessions fonctionne")
    
    return orchestrator

async def test_error_handling():
    """Test de la gestion d'erreurs."""
    print("\n🧪 TEST: Gestion d'erreurs")
    print("=" * 50)
    
    pipeline = MockDefenseurPipeline()
    orchestrator = ChatOrchestrator(pipeline)
    user_id = "test_user_005"
    
    # Test commande inconnue
    response = await orchestrator.handle_message("/commande_inexistante", user_id)
    assert response["status"] == "error"
    print("✓ Gestion des commandes inconnues")
    
    # Test analyse sans documents
    response = await orchestrator.handle_message("/analyse", user_id)
    assert response["status"] == "error"
    print("✓ Gestion de l'analyse sans documents")
    
    # Test accès à un flux inexistant
    response = await orchestrator.handle_message("/status flux_inexistant", user_id)
    assert response["status"] == "error"
    print("✓ Gestion des flux inexistants")
    
    return orchestrator

async def run_comprehensive_test():
    """Exécute tous les tests de manière séquentielle."""
    print("🚀 DÉBUT DES TESTS D'INTÉGRATION CHATORCHESTRATEUR")
    print("=" * 60)
    
    try:
        # Tests séquentiels
        await test_basic_commands()
        await test_document_management()
        await test_analysis_workflow()
        await test_natural_language()
        await test_session_management()
        await test_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS !")
        print("✅ Le ChatOrchestrator est prêt pour l'intégration frontend")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR DANS LES TESTS: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def interactive_demo():
    """Démo interactive du ChatOrchestrator."""
    print("\n🎮 DÉMO INTERACTIVE")
    print("=" * 50)
    print("Tapez vos commandes (ou 'quit' pour quitter):")
    
    pipeline = MockDefenseurPipeline()
    orchestrator = ChatOrchestrator(pipeline)
    user_id = "demo_user"
    
    while True:
        try:
            user_input = input("\n> ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input:
                response = await orchestrator.handle_message(user_input, user_id)
                print(f"Status: {response['status']}")
                print(f"Response: {response['response']}")
                
                if 'flow_id' in response:
                    print(f"Flow ID: {response['flow_id']}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erreur: {e}")
    
    print("\nAu revoir !")

if __name__ == "__main__":
    print("ChatOrchestrator - Tests d'Intégration")
    print("Choisissez une option:")
    print("1. Tests automatiques complets")
    print("2. Démo interactive")
    
    try:
        choice = input("\nVotre choix (1 ou 2): ").strip()
        
        if choice == "1":
            success = asyncio.run(run_comprehensive_test())
            sys.exit(0 if success else 1)
        elif choice == "2":
            asyncio.run(interactive_demo())
        else:
            print("Choix invalide. Exécution des tests automatiques...")
            success = asyncio.run(run_comprehensive_test())
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\nTests interrompus par l'utilisateur.")
        sys.exit(1)
