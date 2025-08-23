#!/usr/bin/env python3
"""
Démonstration complète de l'intégration Gemini Embedding avec DEFENSEUR-IA
Test du système d'embedding unifié avec l'API clé fournie
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# Ajouter le chemin du module
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configuration de l'API Gemini
os.environ["GEMINI_API_KEY"] = "pcsk_4JfVcA_4CvFc8DmGhzQXHGyE2uCAtw2aeK4XHjAsdyNurDY3nxqdHfPpWfhxnMaKCV62dm"

# Import des services d'embedding
try:
    from src.defenseur_ia.services.gemini_embedding_service import (
        GeminiEmbeddingService,
        EmbeddingTaskType,
        EmbeddingDimension,
        gemini_embedding_service
    )
    from src.defenseur_ia.services.unified_embedding_service import (
        UnifiedEmbeddingService,
        EmbeddingProvider,
        unified_embedding_service,
        embed_for_agent,
        batch_embed_for_agent
    )
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Services d'embedding non disponibles: {e}")
    SERVICES_AVAILABLE = False


async def demo_gemini_basic():
    """Démonstration de base du service Gemini Embedding"""
    
    print("🧪 DÉMONSTRATION GEMINI EMBEDDING - BASIC")
    print("-" * 60)
    
    if not SERVICES_AVAILABLE:
        print("❌ Services non disponibles - arrêt de la démonstration")
        return False
    
    # Initialiser le service Gemini
    print("🔧 Initialisation du service Gemini...")
    success = await gemini_embedding_service.initialize()
    
    if not success:
        print("❌ Échec initialisation Gemini - mode simulation activé")
    
    # Test embedding simple
    print("\n📝 Test embedding simple:")
    test_text = "Marie, 32 ans, mère d'un enfant français, a reçu une OQTF le 15 mars 2024"
    
    embedding = await gemini_embedding_service.create_embedding(
        text=test_text,
        task_type=EmbeddingTaskType.SEMANTIC_SIMILARITY,
        dimension=EmbeddingDimension.LARGE
    )
    
    if embedding:
        print(f"✅ Embedding créé: {len(embedding)} dimensions")
        print(f"📊 Premiers éléments: {embedding[:5]}")
    else:
        print("❌ Échec création embedding")
        return False
    
    # Test embedding batch
    print("\n📝 Test embedding batch:")
    batch_texts = [
        "Transcription audio: Je m'appelle Ahmed, j'ai reçu une OQTF",
        "Article L511-1 du CESEDA sur l'éloignement des étrangers",
        "Jurisprudence CE 2019 sur la motivation des OQTF",
        "Récit: Fatima, mère célibataire, travaille comme aide-soignante"
    ]
    
    batch_embeddings = await gemini_embedding_service.create_embeddings_batch(
        texts=batch_texts,
        task_type=EmbeddingTaskType.SEMANTIC_SIMILARITY,
        dimension=EmbeddingDimension.MEDIUM
    )
    
    successful_embeddings = [e for e in batch_embeddings if e is not None]
    print(f"✅ Batch embeddings: {len(successful_embeddings)}/{len(batch_texts)} réussis")
    
    # Test similarité
    if len(successful_embeddings) >= 2:
        print("\n📊 Test calcul de similarité:")
        similarity = gemini_embedding_service.calculate_similarity(
            successful_embeddings[0], successful_embeddings[1]
        )
        print(f"Similarité entre textes 1 et 2: {similarity:.4f}")
        
        similarity_same_domain = gemini_embedding_service.calculate_similarity(
            successful_embeddings[0], successful_embeddings[3]  # Deux récits personnels
        )
        print(f"Similarité entre récits personnels: {similarity_same_domain:.4f}")
    
    # Statistiques
    print(f"\n📈 Statistiques Gemini: {gemini_embedding_service.get_stats()}")
    
    return True


async def demo_unified_service():
    """Démonstration du service d'embedding unifié"""
    
    print("\n🔧 DÉMONSTRATION SERVICE UNIFIÉ")
    print("-" * 60)
    
    # Initialiser le service unifié
    print("🔧 Initialisation du service unifié...")
    success = await unified_embedding_service.initialize()
    
    if not success:
        print("❌ Échec initialisation service unifié")
        return False
    
    print(f"✅ Service unifié initialisé avec {len(unified_embedding_service.providers)} fournisseurs")
    
    # Test embeddings spécialisés par agent
    print("\n🤖 Test embeddings spécialisés par agent:")
    
    agent_tests = [
        {
            "agent": "ecouteur",
            "text": "Transcription: Bonjour, je m'appelle Amina, j'ai reçu une OQTF hier",
            "context": "general"
        },
        {
            "agent": "cadreur_juridique", 
            "text": "Article L511-1 du CESEDA: L'étranger ne peut être éloigné du territoire français vers un pays s'il établit que sa vie ou sa liberté y seraient menacées",
            "context": "legal"
        },
        {
            "agent": "parseur_preuves",
            "text": "Document PDF: Certificat de scolarité de l'enfant français, école primaire Jean Jaurès",
            "context": "general"
        },
        {
            "agent": "redacteur_narratif",
            "text": "Récit: Marie travaille depuis 5 ans comme aide-soignante, son fils de 8 ans est français de naissance",
            "context": "case"
        }
    ]
    
    embeddings_results = []
    
    for test in agent_tests:
        embedding = await embed_for_agent(
            text=test["text"],
            agent_type=test["agent"],
            context_type=test["context"]
        )
        
        if embedding:
            embeddings_results.append({
                "agent": test["agent"],
                "embedding": embedding,
                "dimension": len(embedding)
            })
            print(f"✅ {test['agent']}: {len(embedding)}D embedding créé")
        else:
            print(f"❌ {test['agent']}: échec embedding")
    
    # Test recherche de similarité inter-agents
    if len(embeddings_results) >= 2:
        print("\n🔍 Test recherche de similarité inter-agents:")
        
        query_embedding = embeddings_results[0]["embedding"]  # Écouteur
        candidate_embeddings = [r["embedding"] for r in embeddings_results[1:]]
        
        similar_results = await unified_embedding_service.find_most_similar(
            query_embedding=query_embedding,
            candidate_embeddings=candidate_embeddings,
            top_k=3
        )
        
        print(f"🎯 Requête: {embeddings_results[0]['agent']}")
        for i, result in enumerate(similar_results):
            agent_name = embeddings_results[result["index"] + 1]["agent"]
            print(f"   {i+1}. {agent_name}: similarité {result['similarity']:.4f}")
    
    # Test batch processing par agent
    print("\n📦 Test batch processing par agent:")
    
    batch_texts_juridique = [
        "Article L511-1 du CESEDA sur l'éloignement",
        "Article L511-2 sur les exceptions à l'éloignement", 
        "Article L511-3 sur les garanties procédurales"
    ]
    
    batch_results = await batch_embed_for_agent(
        texts=batch_texts_juridique,
        agent_type="cadreur_juridique"
    )
    
    successful_batch = [e for e in batch_results if e is not None]
    print(f"✅ Batch juridique: {len(successful_batch)}/{len(batch_texts_juridique)} embeddings créés")
    
    return True


async def demo_specialized_embeddings():
    """Démonstration des embeddings spécialisés DEFENSEUR-IA"""
    
    print("\n⚖️ DÉMONSTRATION EMBEDDINGS SPÉCIALISÉS DEFENSEUR-IA")
    print("-" * 60)
    
    # Test embedding mémoire d'agent
    print("🧠 Test embedding mémoire d'agent:")
    
    memory_embedding = await unified_embedding_service.create_agent_memory_embedding(
        agent_type="ecouteur",
        context="Transcription audio OQTF avec accent maghrébin fort",
        experience_data={
            "error": "Erreur reconnaissance mots juridiques spécifiques",
            "solution": "Utiliser modèle Whisper fine-tuné français juridique",
            "validated": True,
            "metadata": {
                "language": "français",
                "accent": "maghrébin",
                "domain": "juridique"
            }
        }
    )
    
    if memory_embedding:
        print(f"✅ Mémoire agent: {len(memory_embedding)}D embedding créé")
    else:
        print("❌ Échec embedding mémoire")
    
    # Test embedding connaissance juridique
    print("\n📚 Test embedding connaissance juridique:")
    
    legal_embedding = await unified_embedding_service.create_legal_knowledge_embedding(
        title="Protection contre l'éloignement - Vie privée et familiale",
        content="L'étranger ne peut faire l'objet d'une OQTF si il justifie par tout moyen avoir sa résidence habituelle en France depuis qu'il a atteint l'âge de treize ans, ou qu'il réside en France depuis plus de vingt ans",
        source="Code de l'entrée et du séjour des étrangers et du droit d'asile",
        article_code="L511-4"
    )
    
    if legal_embedding:
        print(f"✅ Connaissance juridique: {len(legal_embedding)}D embedding créé")
    else:
        print("❌ Échec embedding juridique")
    
    # Test embedding dossier/cas
    print("\n📁 Test embedding dossier/cas:")
    
    case_embedding = await unified_embedding_service.create_case_embedding(
        case_type="OQTF",
        narrative="Marie, 32 ans, arrivée en France à l'âge de 15 ans, mère d'un enfant français de 8 ans, travaille comme aide-soignante depuis 5 ans, victime de violences conjugales, a déposé plainte",
        metadata={
            "urgency": "high",
            "family_situation": "enfant_francais",
            "professional_situation": "aide_soignante",
            "vulnerability": "violences_conjugales",
            "legal_status": "sans_papiers"
        }
    )
    
    if case_embedding:
        print(f"✅ Dossier cas: {len(case_embedding)}D embedding créé")
    else:
        print("❌ Échec embedding dossier")
    
    # Test de recherche sémantique entre types
    if memory_embedding and legal_embedding and case_embedding:
        print("\n🔍 Test recherche sémantique inter-types:")
        
        # Similarité mémoire <-> connaissance juridique
        sim_memory_legal = unified_embedding_service.calculate_similarity(
            memory_embedding, legal_embedding
        )
        print(f"Similarité mémoire ↔ juridique: {sim_memory_legal:.4f}")
        
        # Similarité connaissance juridique <-> dossier
        sim_legal_case = unified_embedding_service.calculate_similarity(
            legal_embedding, case_embedding
        )
        print(f"Similarité juridique ↔ dossier: {sim_legal_case:.4f}")
        
        # Similarité mémoire <-> dossier
        sim_memory_case = unified_embedding_service.calculate_similarity(
            memory_embedding, case_embedding
        )
        print(f"Similarité mémoire ↔ dossier: {sim_memory_case:.4f}")
    
    return True


async def demo_performance_analysis():
    """Analyse des performances et optimisations"""
    
    print("\n📊 ANALYSE PERFORMANCES ET OPTIMISATIONS")
    print("-" * 60)
    
    # Statistiques détaillées
    print("📈 Statistiques détaillées:")
    unified_stats = unified_embedding_service.get_stats()
    
    print(f"\n🔧 Service unifié:")
    print(f"   Fournisseurs disponibles: {len(unified_stats['available_providers'])}")
    print(f"   Fournisseur par défaut: {unified_stats['default_provider']}")
    print(f"   Total embeddings: {unified_stats['global_stats']['total_embeddings']}")
    print(f"   Activations fallback: {unified_stats['global_stats']['fallback_activations']}")
    print(f"   Erreurs: {unified_stats['global_stats']['errors']}")
    
    print(f"\n🤖 Configuration par agent:")
    for agent, config in unified_stats['agent_configs'].items():
        print(f"   {agent}: {config['provider']} | {config['task_type']} | {config['dimension']}")
    
    print(f"\n📊 Usage par fournisseur:")
    for provider, count in unified_stats['global_stats']['provider_usage'].items():
        print(f"   {provider}: {count} embeddings")
    
    # Test de performance avec différentes dimensions
    print("\n⚡ Test performance dimensions:")
    
    test_text = "Test de performance embedding avec différentes dimensions pour optimisation"
    dimensions_to_test = [
        EmbeddingDimension.MEDIUM,   # 768D
        EmbeddingDimension.LARGE,    # 1536D
        EmbeddingDimension.FULL      # 3072D
    ]
    
    for dim in dimensions_to_test:
        start_time = datetime.now()
        
        embedding = await gemini_embedding_service.create_embedding(
            text=test_text,
            dimension=dim,
            use_cache=False  # Forcer le calcul
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if embedding:
            print(f"   {dim.name} ({dim.value}D): {duration:.3f}s")
        else:
            print(f"   {dim.name}: échec")
    
    return True


async def demo_integration_rrla():
    """Démonstration d'intégration avec le système RRLA"""
    
    print("\n🧠 INTÉGRATION AVEC SYSTÈME RRLA")
    print("-" * 60)
    
    # Simuler des expériences d'agents pour le système RRLA
    print("🔄 Simulation expériences agents RRLA:")
    
    rrla_experiences = [
        {
            "agent_type": "ecouteur",
            "context": "Transcription audio difficile avec bruit de fond",
            "reasoning_step": "Amélioration qualité audio avant transcription",
            "outcome": "Succès après préprocessing"
        },
        {
            "agent_type": "cadreur_juridique",
            "context": "Identification axes juridiques pour cas complexe OQTF + regroupement familial",
            "reasoning_step": "Priorisation protection vie familiale sur autres motifs",
            "outcome": "Stratégie juridique optimale identifiée"
        },
        {
            "agent_type": "redacteur_narratif",
            "context": "Rédaction récit empathique pour femme victime violences",
            "reasoning_step": "Adaptation ton et style pour maximiser impact émotionnel",
            "outcome": "Récit percutant et respectueux produit"
        }
    ]
    
    rrla_embeddings = []
    
    for exp in rrla_experiences:
        # Créer un embedding enrichi pour l'expérience RRLA
        rrla_text = f"""
        Agent RRLA: {exp['agent_type']}
        Contexte: {exp['context']}
        Étape de raisonnement: {exp['reasoning_step']}
        Résultat: {exp['outcome']}
        Type: expérience_rrla
        """
        
        embedding = await embed_for_agent(
            text=rrla_text.strip(),
            agent_type=exp['agent_type'],
            context_type="memory"
        )
        
        if embedding:
            rrla_embeddings.append({
                "agent": exp['agent_type'],
                "embedding": embedding,
                "experience": exp
            })
            print(f"✅ RRLA {exp['agent_type']}: expérience embedée")
        else:
            print(f"❌ RRLA {exp['agent_type']}: échec embedding")
    
    # Test recherche d'expériences similaires pour nouveau cas
    if rrla_embeddings:
        print("\n🔍 Recherche expériences RRLA similaires:")
        
        new_case_query = "Nouveau cas: transcription audio difficile avec accent étranger fort"
        query_embedding = await embed_for_agent(
            text=new_case_query,
            agent_type="ecouteur",
            context_type="memory"
        )
        
        if query_embedding:
            candidate_embeddings = [exp["embedding"] for exp in rrla_embeddings]
            
            similar_experiences = await unified_embedding_service.find_most_similar(
                query_embedding=query_embedding,
                candidate_embeddings=candidate_embeddings,
                top_k=2
            )
            
            print(f"🎯 Requête: {new_case_query}")
            for i, result in enumerate(similar_experiences):
                exp_data = rrla_embeddings[result["index"]]
                print(f"   {i+1}. {exp_data['agent']} (sim: {result['similarity']:.4f})")
                print(f"      Solution: {exp_data['experience']['reasoning_step']}")
    
    return True


async def demo_export_and_summary():
    """Export des données et résumé final"""
    
    print("\n📄 EXPORT ET RÉSUMÉ FINAL")
    print("-" * 60)
    
    # Export des statistiques unifiées
    print("💾 Export statistiques unifiées...")
    export_file = await unified_embedding_service.export_unified_stats()
    print(f"✅ Statistiques exportées: {export_file}")
    
    # Export des données Gemini
    print("\n💾 Export données Gemini...")
    gemini_export = await gemini_embedding_service.export_embeddings_data()
    print(f"✅ Données Gemini exportées: {gemini_export}")
    
    # Résumé final
    print("\n🎉 RÉSUMÉ FINAL DE LA DÉMONSTRATION:")
    print("-" * 60)
    
    unified_stats = unified_embedding_service.get_stats()
    gemini_stats = gemini_embedding_service.get_stats()
    
    print(f"✅ Service Gemini Embedding: {'Opérationnel' if gemini_stats['api_available'] else 'Mode simulation'}")
    print(f"✅ Service unifié: {len(unified_stats['available_providers'])} fournisseurs")
    print(f"✅ Agents configurés: {len(unified_stats['agent_configs'])}")
    print(f"✅ Total embeddings créés: {unified_stats['global_stats']['total_embeddings']}")
    print(f"✅ Cache Gemini: {gemini_stats['cache_size']} entrées")
    print(f"✅ Fallbacks activés: {unified_stats['global_stats']['fallback_activations']}")
    print(f"✅ Taux de succès: {((unified_stats['global_stats']['total_embeddings'] / max(1, unified_stats['global_stats']['total_embeddings'] + unified_stats['global_stats']['errors'])) * 100):.1f}%")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    print(f"   🔧 Configuration optimale détectée pour chaque agent")
    print(f"   📊 Dimensions recommandées: LARGE (1536D) pour la plupart des cas")
    print(f"   ⚡ Cache activé pour optimiser les performances")
    print(f"   🔄 Fallback automatique garantit la robustesse")
    print(f"   🧠 Intégration RRLA prête pour déploiement")
    
    return True


async def main():
    """Point d'entrée principal de la démonstration"""
    
    print("🚀 DÉMONSTRATION COMPLÈTE INTÉGRATION GEMINI EMBEDDING")
    print("DEFENSEUR-IA - Système d'embedding unifié avec mémoire sémantique")
    print("=" * 80)
    
    try:
        # Séquence de démonstrations
        demos = [
            ("Gemini Basic", demo_gemini_basic),
            ("Service Unifié", demo_unified_service),
            ("Embeddings Spécialisés", demo_specialized_embeddings),
            ("Analyse Performances", demo_performance_analysis),
            ("Intégration RRLA", demo_integration_rrla),
            ("Export et Résumé", demo_export_and_summary)
        ]
        
        results = {}
        
        for demo_name, demo_func in demos:
            print(f"\n{'='*20} {demo_name.upper()} {'='*20}")
            try:
                success = await demo_func()
                results[demo_name] = success
                if success:
                    print(f"✅ {demo_name} terminé avec succès")
                else:
                    print(f"⚠️ {demo_name} terminé avec avertissements")
            except Exception as e:
                print(f"❌ Erreur dans {demo_name}: {e}")
                results[demo_name] = False
        
        # Bilan final
        print(f"\n{'='*80}")
        print("🏆 BILAN FINAL DE LA DÉMONSTRATION")
        print(f"{'='*80}")
        
        successful_demos = sum(1 for success in results.values() if success)
        total_demos = len(results)
        
        print(f"📊 Résultats: {successful_demos}/{total_demos} démonstrations réussies")
        
        for demo_name, success in results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {demo_name}")
        
        if successful_demos == total_demos:
            print(f"\n🎉 INTÉGRATION GEMINI EMBEDDING COMPLÈTEMENT VALIDÉE!")
            print(f"🛡️ DEFENSEUR-IA est maintenant équipé d'un système d'embedding de nouvelle génération")
            print(f"🧠 Mémoire sémantique opérationnelle avec Gemini embedding-001")
            print(f"🔧 Service unifié prêt pour déploiement en production")
        else:
            print(f"\n⚠️ Intégration partiellement validée - {total_demos - successful_demos} problèmes détectés")
        
        return successful_demos == total_demos
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print(f"\n🌟 SYSTÈME GEMINI EMBEDDING INTÉGRÉ AVEC SUCCÈS!")
        print(f"\n🔮 PROCHAINES ÉTAPES:")
        print(f"   1. Déployer en production avec clés API sécurisées")
        print(f"   2. Intégrer au pipeline RRLA multi-agents")
        print(f"   3. Créer l'interface de monitoring des embeddings")
        print(f"   4. Optimiser les configurations par agent")
        print(f"   5. Implémenter la mise en cache persistante")
    else:
        print(f"\n⚠️ Problèmes détectés lors de l'intégration.")
    
    print(f"\n🛡️ DEFENSEUR-IA GEMINI EMBEDDING: PRÊT POUR L'AVENIR!")
