#!/usr/bin/env python3
"""
Démonstration automatique du système RRLA DEFENSEUR-IA
Sans interaction utilisateur - pour tests et présentation
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


async def main():
    """Démonstration automatique complète du système RRLA"""
    
    print("🧠 DÉMONSTRATION AUTOMATIQUE SYSTÈME RRLA - DEFENSEUR-IA")
    print("=" * 70)
    print("Raisonnement, Réflexion, Apprentissage, Adaptation")
    print("=" * 70)
    
    # 1. Créer un agent Écouteur amélioré
    print("\n1️⃣ CRÉATION AGENT ÉCOUTEUR AVEC RAISONNEMENT RRLA")
    print("-" * 50)
    agent = create_enhanced_ecouteur()
    print(f"✅ Agent créé: {agent.agent_id}")
    print(f"🎯 Objectif: {agent.reasoning.wm.g}")
    print(f"🔧 Compétences: {', '.join(agent.reasoning.exp)}")
    
    # 2. Afficher le DAG initial
    print("\n2️⃣ STRUCTURE DAG DE RAISONNEMENT INITIAL")
    print("-" * 50)
    print(agent.get_dag_visualization())
    
    # 3. Préparer le contexte de test
    print("\n3️⃣ PRÉPARATION DU CONTEXTE DE TEST")
    print("-" * 50)
    shared_store = SharedStore()
    await shared_store.initialize()
    
    # Simuler des données d'entrée réalistes
    test_data = {
        "meta_info": {
            "dossier_id": "OQTF_2024_001",
            "type_contentieux": "OQTF",
            "date_creation": datetime.now().isoformat(),
            "urgence": "haute"
        },
        "audio_input": {
            "file_path": "/tmp/marie_dubois_temoignage.wav",
            "duration": 125,
            "format": "wav",
            "quality": "moyenne"
        }
    }
    
    for key, value in test_data.items():
        await shared_store.set(key, value)
    
    print(f"📁 Dossier: {test_data['meta_info']['dossier_id']}")
    print(f"⚖️ Type: {test_data['meta_info']['type_contentieux']}")
    print(f"🎤 Audio: {test_data['audio_input']['duration']}s")
    
    # 4. Exécuter le raisonnement complet
    print("\n4️⃣ EXÉCUTION DU PIPELINE DE RAISONNEMENT RRLA")
    print("-" * 50)
    
    try:
        result = await agent.process(
            shared_store, 
            immediate_goal="Analyser témoignage OQTF Marie Dubois",
            context="Dossier urgent avec enjeux familiaux"
        )
        
        print("✅ PIPELINE TERMINÉ AVEC SUCCÈS!")
        
        # 5. Afficher les résultats détaillés
        print("\n5️⃣ RÉSULTATS DU RAISONNEMENT RRLA")
        print("-" * 50)
        
        status = agent.get_reasoning_status()
        print(f"🎯 Objectif principal: {status['goal']}")
        print(f"📋 Sous-objectif: {status['subgoal']}")
        print(f"✅ Progression: {status['completed_steps']}/{status['total_steps']} étapes")
        print(f"⚡ Étape courante: {status['current_step']}")
        print(f"💡 Explication: {status['explainability']}")
        
        if status['errors']:
            print(f"❌ Erreurs: {', '.join(status['errors'])}")
        else:
            print("✅ Aucune erreur détectée")
        
        if status['warnings']:
            print(f"⚠️ Avertissements: {', '.join(status['warnings'])}")
        
        # 6. DAG final avec état d'exécution
        print("\n6️⃣ VISUALISATION DAG FINALE")
        print("-" * 50)
        print(agent.get_dag_visualization())
        
        # 7. Analyse des connaissances acquises
        print("\n7️⃣ CONNAISSANCES ET APPRENTISSAGES")
        print("-" * 50)
        
        reasoning_export = agent.export_reasoning()
        reasoning_data = reasoning_export['reasoning']
        
        # Triplets de connaissance
        kg_triplets = reasoning_data.get('kg', {}).get('tri', [])
        print(f"🧠 Triplets de connaissance acquis: {len(kg_triplets)}")
        for i, triplet in enumerate(kg_triplets):
            print(f"   {i+1}. {triplet['sub']} → {triplet['pred']} → {triplet['obj']}")
        
        # Expériences mémorisées
        experiences = reasoning_data.get('rrla_ext', {}).get('memory_experiential', [])
        print(f"\n💭 Expériences mémorisées: {len(experiences)}")
        for i, exp in enumerate(experiences):
            print(f"   {i+1}. Contexte: {exp['context']}")
            print(f"      Erreur: {exp['error']}")
            print(f"      Solution: {exp['solution']}")
            print(f"      Validée: {'✅' if exp['validated'] else '❌'}")
        
        # Propositions logiques
        logic_data = reasoning_data.get('logic', {})
        propos = logic_data.get('propos', [])
        proofs = logic_data.get('proofs', [])
        doubts = logic_data.get('doubts', [])
        
        print(f"\n🔬 Raisonnement logique:")
        print(f"   📋 Propositions: {len(propos)}")
        for prop in propos:
            print(f"      • {prop['nl']}")
        
        print(f"   ✅ Preuves: {len(proofs)}")
        for proof in proofs:
            print(f"      • {proof['nl']}")
        
        if doubts:
            print(f"   ❓ Incertitudes: {len(doubts)}")
            for doubt in doubts:
                print(f"      • {doubt['nl']}")
        
        # 8. Résultats métier extraits
        print("\n8️⃣ RÉSULTATS MÉTIER EXTRAITS")
        print("-" * 50)
        
        # Qualité audio
        audio_quality = await shared_store.get("audio_quality_analysis", {})
        if audio_quality:
            print(f"🔊 Qualité audio:")
            print(f"   Grade: {audio_quality.get('quality_grade', 'N/A')}")
            print(f"   Score: {audio_quality.get('clarity_score', 0):.2f}")
            print(f"   Langue: {audio_quality.get('language_detected', 'N/A')}")
        
        # Transcription
        transcription = await shared_store.get("transcription_result", {})
        if transcription:
            print(f"\n🎤 Transcription:")
            print(f"   Modèle: {transcription.get('model_used', 'N/A')}")
            print(f"   Mots: {transcription.get('word_count', 0)}")
            print(f"   Confiance: {transcription.get('confidence', 0):.2f}")
            print(f"   Texte: {transcription.get('text', '')[:100]}...")
        
        # Émotions
        emotions = await shared_store.get("emotion_analysis", {})
        if emotions:
            print(f"\n😟 Analyse émotionnelle:")
            print(f"   Émotion dominante: {emotions.get('primary_emotion', 'N/A')}")
            print(f"   Intensité: {emotions.get('emotion_intensity', 0):.2f}")
            print(f"   Urgence: {emotions.get('urgency_level', 'N/A')}")
            print(f"   Score empathie: {emotions.get('empathy_score', 0):.2f}")
        
        # Segmentation
        narration = await shared_store.get("narration", {})
        if narration:
            print(f"\n📝 Segmentation narrative:")
            print(f"   Segments: {narration.get('total_segments', 0)}")
            print(f"   Cohérence: {narration.get('coherence_score', 0):.2f}")
            print(f"   Thèmes: {', '.join(narration.get('key_themes', []))}")
            
            segments = narration.get('segments', [])
            for i, segment in enumerate(segments[:3]):  # Afficher 3 premiers segments
                print(f"   Segment {i+1}: {segment.get('type', 'N/A')} - {segment.get('contenu', '')[:50]}...")
        
        # 9. Diagramme Mermaid pour documentation
        print("\n9️⃣ DIAGRAMME MERMAID (POUR DOCUMENTATION)")
        print("-" * 50)
        print(agent.get_mermaid_diagram())
        
        # 10. Comparaison des capacités
        print("\n🔟 COMPARAISON DES CAPACITÉS")
        print("-" * 50)
        print("📊 AGENT CLASSIQUE (AVANT):")
        print("   ❌ Exécution linéaire rigide")
        print("   ❌ Pas de mémoire des erreurs")
        print("   ❌ Pas d'explication du processus")
        print("   ❌ Pas d'adaptation contextuelle")
        print("   ❌ Pas de métacognition")
        
        print("\n🧠 AGENT RRLA (APRÈS):")
        print("   ✅ Raisonnement structuré avec DAG")
        print("   ✅ Mémoire expérientielle et apprentissage")
        print("   ✅ Métacognition et auto-évaluation")
        print("   ✅ Adaptation basée sur le contexte")
        print("   ✅ Anticipation des erreurs")
        print("   ✅ Documentation automatique")
        print("   ✅ Explication des décisions")
        print("   ✅ Raisonnement logique formel")
        
        # 11. Export pour analyse
        print("\n1️⃣1️⃣ EXPORT POUR ANALYSE")
        print("-" * 50)
        
        export_filename = f"./rrla_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_filename, 'w', encoding='utf-8') as f:
            json.dump(reasoning_export, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Export complet sauvegardé: {export_filename}")
        
        # 12. Métriques de performance
        print("\n1️⃣2️⃣ MÉTRIQUES DE PERFORMANCE RRLA")
        print("-" * 50)
        
        temporal_actions = reasoning_data.get('rrla_ext', {}).get('temporal_memory', [])
        if len(temporal_actions) >= 2:
            start_time = datetime.fromisoformat(temporal_actions[0]['timestamp'])
            end_time = datetime.fromisoformat(temporal_actions[-1]['timestamp'])
            duration = (end_time - start_time).total_seconds()
            print(f"⏱️ Durée totale: {duration:.2f} secondes")
        
        print(f"🎯 Taux de réussite: {(status['completed_steps']/status['total_steps'])*100:.1f}%")
        print(f"🧠 Connaissances acquises: {len(kg_triplets)} triplets")
        print(f"💭 Expériences mémorisées: {len(experiences)}")
        print(f"🔬 Propositions logiques: {len(propos)}")
        
        print("\n🎉 DÉMONSTRATION RRLA TERMINÉE AVEC SUCCÈS!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE L'EXÉCUTION: {e}")
        
        # Afficher l'état de l'agent même en cas d'erreur
        status = agent.get_reasoning_status()
        print(f"\n📊 ÉTAT DE L'AGENT AU MOMENT DE L'ERREUR:")
        print(f"   - Étape courante: {status['current_step']}")
        print(f"   - Étapes complétées: {status['completed_steps']}")
        print(f"   - Erreurs: {status['errors']}")
        
        return False


if __name__ == "__main__":
    print("🚀 Lancement de la démonstration RRLA automatique...")
    success = asyncio.run(main())
    
    if success:
        print("\n💡 AVANTAGES DU SYSTÈME RRLA:")
        print("   🧠 Raisonnement explicable et traçable")
        print("   📈 Apprentissage automatique des erreurs")
        print("   🔄 Adaptation contextuelle intelligente")
        print("   📊 Visualisation des processus de pensée")
        print("   🛡️ Robustesse et fiabilité accrues")
        print("   📝 Documentation automatique complète")
    else:
        print("\n⚠️ La démonstration a rencontré des erreurs.")
    
    print("\n🎯 Le système RRLA est prêt pour l'intégration dans tous les agents DEFENSEUR-IA!")
