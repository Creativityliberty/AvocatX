#!/usr/bin/env python3
"""
Script de démonstration du système de raisonnement RRLA
pour les agents DEFENSEUR-IA

Montre la visualisation DAG et les capacités de métacognition
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Ajouter le chemin du module
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.defenseur_ia.agents.enhanced_ecouteur import create_enhanced_ecouteur
from src.defenseur_ia.core.shared_store import SharedStore
from src.defenseur_ia.core.reasoning_schema import ReasoningDAGVisualizer


async def demo_rrla_reasoning():
    """
    Démonstration complète du système de raisonnement RRLA
    """
    
    print("🧠 DÉMONSTRATION SYSTÈME RRLA - DEFENSEUR-IA")
    print("=" * 60)
    
    # 1. Créer un agent Écouteur amélioré
    print("\n1️⃣ Création de l'agent Écouteur avec raisonnement RRLA...")
    agent = create_enhanced_ecouteur()
    
    # Afficher le DAG initial
    print("\n📊 DAG de raisonnement initial:")
    print(agent.get_dag_visualization())
    
    # 2. Préparer le contexte de test
    print("\n2️⃣ Préparation du contexte de test...")
    shared_store = SharedStore()
    await shared_store.initialize()
    
    # Simuler des données d'entrée
    test_data = {
        "meta_info": {
            "dossier_id": "DEMO_001",
            "type_contentieux": "OQTF",
            "date_creation": datetime.now().isoformat()
        },
        "audio_input": {
            "file_path": "/tmp/demo_marie_dubois.wav",
            "duration": 120,
            "format": "wav"
        }
    }
    
    for key, value in test_data.items():
        shared_store.set(key, value)
    
    print(f"✅ Contexte préparé: dossier {test_data['meta_info']['dossier_id']}")
    
    # 3. Exécuter le raisonnement complet
    print("\n3️⃣ Exécution du pipeline de raisonnement RRLA...")
    print("-" * 50)
    
    try:
        result = await agent.process(shared_store, immediate_goal="Analyser témoignage Marie Dubois")
        
        print("\n✅ Pipeline terminé avec succès!")
        
        # 4. Afficher les résultats détaillés
        print("\n4️⃣ Résultats du raisonnement:")
        print("-" * 40)
        
        status = agent.get_reasoning_status()
        print(f"🎯 Objectif: {status['goal']}")
        print(f"📋 Sous-objectif: {status['subgoal']}")
        print(f"✅ Étapes complétées: {status['completed_steps']}/{status['total_steps']}")
        print(f"💡 Explication: {status['explainability']}")
        
        if status['errors']:
            print(f"❌ Erreurs: {', '.join(status['errors'])}")
        
        if status['warnings']:
            print(f"⚠️ Avertissements: {', '.join(status['warnings'])}")
        
        # 5. Visualisation DAG finale
        print("\n5️⃣ Visualisation DAG finale:")
        print("=" * 50)
        print(agent.get_dag_visualization())
        
        # 6. Diagramme Mermaid
        print("\n6️⃣ Diagramme Mermaid (pour documentation):")
        print("-" * 50)
        print(agent.get_mermaid_diagram())
        
        # 7. Analyse des connaissances acquises
        print("\n7️⃣ Connaissances et apprentissages:")
        print("-" * 40)
        
        reasoning_export = agent.export_reasoning()
        reasoning_data = reasoning_export['reasoning']
        
        # Triplets de connaissance
        kg_triplets = reasoning_data.get('kg', {}).get('tri', [])
        print(f"🧠 Triplets de connaissance: {len(kg_triplets)}")
        for i, triplet in enumerate(kg_triplets[:3]):  # Afficher les 3 premiers
            print(f"   {i+1}. {triplet['sub']} → {triplet['pred']} → {triplet['obj']}")
        
        # Expériences mémorisées
        experiences = reasoning_data.get('rrla_ext', {}).get('memory_experiential', [])
        print(f"💭 Expériences mémorisées: {len(experiences)}")
        for exp in experiences:
            print(f"   - Contexte: {exp['context'][:50]}...")
            print(f"     Solution: {exp['solution'][:50]}...")
        
        # Propositions logiques
        logic_props = reasoning_data.get('logic', {}).get('propos', [])
        print(f"🔬 Propositions logiques: {len(logic_props)}")
        for prop in logic_props[:2]:  # Afficher les 2 premières
            print(f"   - {prop['nl']}")
        
        # 8. Résultats métier
        print("\n8️⃣ Résultats métier (données extraites):")
        print("-" * 40)
        
        # Qualité audio
        audio_quality = shared_store.get("audio_quality_analysis", {})
        print(f"🔊 Qualité audio: {audio_quality.get('quality_grade', 'N/A')} (score: {audio_quality.get('clarity_score', 0):.2f})")
        
        # Transcription
        transcription = shared_store.get("transcription_result", {})
        print(f"🎤 Transcription: {transcription.get('word_count', 0)} mots, confiance: {transcription.get('confidence', 0):.2f}")
        
        # Émotions
        emotions = shared_store.get("emotion_analysis", {})
        print(f"😟 Émotion dominante: {emotions.get('primary_emotion', 'N/A')} (urgence: {emotions.get('urgency_level', 'N/A')})")
        
        # Segmentation
        narration = shared_store.get("narration", {})
        print(f"📝 Segments narratifs: {narration.get('total_segments', 0)}, cohérence: {narration.get('coherence_score', 0):.2f}")
        
        # 9. Export complet
        print("\n9️⃣ Export du raisonnement complet:")
        print("-" * 40)
        
        export_filename = f"./reasoning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_filename, 'w', encoding='utf-8') as f:
            json.dump(reasoning_export, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Export sauvegardé: {export_filename}")
        
        # 10. Comparaison avant/après
        print("\n🔟 Comparaison des capacités:")
        print("-" * 40)
        print("📊 AVANT (Agent classique):")
        print("   - Exécution linéaire des étapes")
        print("   - Pas de mémoire des erreurs")
        print("   - Pas d'explication du raisonnement")
        print("   - Pas d'adaptation contextuelle")
        
        print("\n🧠 APRÈS (Agent RRLA):")
        print("   - Raisonnement structuré avec DAG")
        print("   - Mémoire expérientielle et apprentissage")
        print("   - Métacognition et auto-explication")
        print("   - Adaptation basée sur le contexte")
        print("   - Anticipation des erreurs")
        print("   - Documentation automatique")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {e}")
        
        # Afficher l'état de l'agent même en cas d'erreur
        status = agent.get_reasoning_status()
        print(f"\n📊 État de l'agent au moment de l'erreur:")
        print(f"   - Étape courante: {status['current_step']}")
        print(f"   - Étapes complétées: {status['completed_steps']}")
        print(f"   - Erreurs: {status['errors']}")
        
        return False


def demo_dag_visualization():
    """
    Démonstration de la visualisation DAG seule
    """
    
    print("\n" + "="*60)
    print("🎨 DÉMONSTRATION VISUALISATION DAG")
    print("="*60)
    
    # Créer un agent simple pour la démo
    agent = create_enhanced_ecouteur()
    
    print("\n📊 Diagramme ASCII du raisonnement:")
    print(agent.get_dag_visualization())
    
    print("\n🌐 Diagramme Mermaid:")
    print(agent.get_mermaid_diagram())
    
    print("\n💡 Explication:")
    print("Le DAG montre les dépendances entre les étapes de raisonnement.")
    print("Chaque nœud représente une étape, chaque flèche une dépendance.")
    print("L'agent ne peut exécuter une étape que si ses dépendances sont satisfaites.")


async def demo_memory_learning():
    """
    Démonstration des capacités d'apprentissage et de mémoire
    """
    
    print("\n" + "="*60)
    print("🧠 DÉMONSTRATION APPRENTISSAGE ET MÉMOIRE")
    print("="*60)
    
    agent = create_enhanced_ecouteur()
    
    # Ajouter des expériences simulées
    print("\n1️⃣ Ajout d'expériences d'apprentissage...")
    
    agent.reasoning.add_experience(
        context="Transcription audio de mauvaise qualité",
        error="Confiance < 0.6 sur transcription Whisper",
        solution="Utiliser Gemini Live pour audio dégradé",
        validated=True
    )
    
    agent.reasoning.add_experience(
        context="Détection émotionnelle sur témoignage OQTF",
        error="Sous-estimation du niveau d'urgence",
        solution="Prioriser les marqueurs familiaux (enfants scolarisés)",
        validated=True
    )
    
    print("✅ Expériences ajoutées à la mémoire")
    
    # Tester la récupération d'expériences pertinentes
    print("\n2️⃣ Test de récupération d'expériences pertinentes...")
    
    relevant_exp = agent.reasoning.get_relevant_experiences(["transcription", "qualité", "audio"])
    print(f"🔍 Expériences trouvées pour 'transcription audio': {len(relevant_exp)}")
    
    for exp in relevant_exp:
        print(f"   - Erreur: {exp.error}")
        print(f"   - Solution: {exp.solution}")
        print(f"   - Validée: {exp.validated}")
    
    # Démonstration anti-récurrence
    print("\n3️⃣ Démonstration anti-récurrence...")
    print(f"Anti-récurrence activée: {agent.reasoning.rrla_ext.anti_recurrence}")
    print("→ L'agent évitera automatiquement les erreurs déjà rencontrées")
    
    # Mémoire temporelle
    print("\n4️⃣ Mémoire temporelle des actions...")
    for action in agent.reasoning.rrla_ext.temporal_memory[-3:]:  # 3 dernières actions
        print(f"   {action.timestamp}: {action.action}")


def main():
    """Point d'entrée principal de la démonstration"""
    
    print("🚀 DÉMONSTRATION SYSTÈME RRLA - DEFENSEUR-IA")
    print("Raisonnement, Réflexion, Apprentissage, Adaptation")
    print("="*70)
    
    print("\nChoisissez une démonstration:")
    print("1. 🧠 Démonstration complète RRLA")
    print("2. 🎨 Visualisation DAG uniquement") 
    print("3. 💭 Apprentissage et mémoire")
    print("4. 🚀 Toutes les démonstrations")
    
    choice = input("\nVotre choix (1-4): ").strip()
    
    if choice == "1":
        asyncio.run(demo_rrla_reasoning())
    elif choice == "2":
        demo_dag_visualization()
    elif choice == "3":
        asyncio.run(demo_memory_learning())
    elif choice == "4":
        demo_dag_visualization()
        asyncio.run(demo_memory_learning())
        asyncio.run(demo_rrla_reasoning())
    else:
        print("❌ Choix invalide")
        return
    
    print("\n🎉 Démonstration terminée!")
    print("\n💡 Le système RRLA apporte:")
    print("   ✅ Raisonnement structuré et explicable")
    print("   ✅ Apprentissage automatique des erreurs")
    print("   ✅ Métacognition et auto-évaluation")
    print("   ✅ Adaptation contextuelle")
    print("   ✅ Documentation automatique")
    print("   ✅ Visualisation des processus de pensée")


if __name__ == "__main__":
    main()
