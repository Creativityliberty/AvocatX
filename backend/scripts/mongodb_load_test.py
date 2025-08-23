#!/usr/bin/env python3
"""
Script de tests de charge MongoDB Atlas - DEFENSEUR-IA
Tests avec gros volumes pour valider performances et scalabilité
"""

import asyncio
import time
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import aiohttp
import statistics

# Configuration des tests
BASE_URL = "http://localhost:8001"
MONGODB_ENDPOINTS = {
    "health": "/api/v1/mongodb/health",
    "stats": "/api/v1/mongodb/stats", 
    "cases": "/api/v1/mongodb/cases",
    "documents": "/api/v1/mongodb/documents",
    "pipeline": "/api/v1/mongodb/pipeline/runs"
}

# Données de test réalistes
SAMPLE_CLIENTS = [
    "Marie Dubois", "Ahmed Benali", "Carlos Silva", "Fatima Al-Rashid", 
    "Ivan Petrov", "Priya Sharma", "Jean-Luc Martin", "Amina Kone",
    "Roberto Garcia", "Ling Wei", "Hassan Omar", "Elena Rossi"
]

SAMPLE_NATIONALITIES = [
    "Française", "Algérienne", "Marocaine", "Tunisienne", "Sénégalaise",
    "Malienne", "Ivoirienne", "Camerounaise", "Congolaise", "Guinéenne"
]

SAMPLE_CONTENTIEUX = [
    "OQTF", "Titre de séjour", "Regroupement familial", 
    "Naturalisation", "Asile", "Visa long séjour"
]

SAMPLE_DESCRIPTIONS = [
    "Demande de régularisation suite à OQTF reçue le {date}. Situation familiale complexe avec enfants scolarisés.",
    "Renouvellement de titre de séjour refusé. Besoin d'analyse juridique approfondie des motifs de refus.",
    "Procédure de regroupement familial en cours. Difficultés administratives multiples à résoudre.",
    "Dossier de naturalisation incomplet selon la préfecture. Assistance pour constituer le dossier.",
    "Demande d'asile en instance. Besoin d'accompagnement juridique pour l'audience OFPRA.",
    "Visa long séjour refusé. Analyse des voies de recours possibles et constitution du dossier d'appel."
]

class MongoDBLoadTester:
    def __init__(self):
        self.session = None
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "errors": [],
            "created_cases": [],
            "test_duration": 0
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def generate_case_data(self) -> Dict[str, Any]:
        """Génère des données de dossier réalistes"""
        client = random.choice(SAMPLE_CLIENTS)
        nationality = random.choice(SAMPLE_NATIONALITIES)
        contentieux = random.choice(SAMPLE_CONTENTIEUX)
        description = random.choice(SAMPLE_DESCRIPTIONS).format(
            date=(datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%d/%m/%Y")
        )
        
        return {
            "nom_client": client,
            "type_contentieux": contentieux,
            "nationalite": nationality,
            "description": description,
            "urgence": random.choice(["faible", "normale", "élevée", "critique"]),
            "status": "nouveau",
            "created_by": "load_test"
        }
    
    async def health_check(self) -> bool:
        """Vérification de santé MongoDB Atlas"""
        try:
            start_time = time.time()
            async with self.session.get(f"{BASE_URL}{MONGODB_ENDPOINTS['health']}") as response:
                response_time = time.time() - start_time
                self.results["response_times"].append(response_time)
                self.results["total_requests"] += 1
                
                if response.status == 200:
                    data = await response.json()
                    self.results["successful_requests"] += 1
                    return data.get("success", False) and data.get("status") == "connected"
                else:
                    self.results["failed_requests"] += 1
                    return False
        except Exception as e:
            self.results["failed_requests"] += 1
            self.results["errors"].append(f"Health check error: {str(e)}")
            return False
    
    async def create_case(self, case_data: Dict[str, Any]) -> bool:
        """Création d'un dossier MongoDB Atlas"""
        try:
            start_time = time.time()
            async with self.session.post(
                f"{BASE_URL}{MONGODB_ENDPOINTS['cases']}", 
                json=case_data
            ) as response:
                response_time = time.time() - start_time
                self.results["response_times"].append(response_time)
                self.results["total_requests"] += 1
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.results["successful_requests"] += 1
                        self.results["created_cases"].append(data.get("dossier_id"))
                        return True
                    else:
                        self.results["failed_requests"] += 1
                        return False
                else:
                    self.results["failed_requests"] += 1
                    return False
        except Exception as e:
            self.results["failed_requests"] += 1
            self.results["errors"].append(f"Create case error: {str(e)}")
            return False
    
    async def list_cases(self, skip: int = 0, limit: int = 10) -> bool:
        """Récupération de la liste des dossiers"""
        try:
            start_time = time.time()
            async with self.session.get(
                f"{BASE_URL}{MONGODB_ENDPOINTS['cases']}?skip={skip}&limit={limit}"
            ) as response:
                response_time = time.time() - start_time
                self.results["response_times"].append(response_time)
                self.results["total_requests"] += 1
                
                if response.status == 200:
                    data = await response.json()
                    self.results["successful_requests"] += 1
                    return data.get("success", False)
                else:
                    self.results["failed_requests"] += 1
                    return False
        except Exception as e:
            self.results["failed_requests"] += 1
            self.results["errors"].append(f"List cases error: {str(e)}")
            return False
    
    async def update_case(self, dossier_id: str, updates: Dict[str, Any]) -> bool:
        """Mise à jour d'un dossier"""
        try:
            start_time = time.time()
            async with self.session.put(
                f"{BASE_URL}{MONGODB_ENDPOINTS['cases']}/{dossier_id}",
                json=updates
            ) as response:
                response_time = time.time() - start_time
                self.results["response_times"].append(response_time)
                self.results["total_requests"] += 1
                
                if response.status == 200:
                    data = await response.json()
                    self.results["successful_requests"] += 1
                    return data.get("success", False)
                else:
                    self.results["failed_requests"] += 1
                    return False
        except Exception as e:
            self.results["failed_requests"] += 1
            self.results["errors"].append(f"Update case error: {str(e)}")
            return False
    
    async def get_stats(self) -> bool:
        """Récupération des statistiques MongoDB"""
        try:
            start_time = time.time()
            async with self.session.get(f"{BASE_URL}{MONGODB_ENDPOINTS['stats']}") as response:
                response_time = time.time() - start_time
                self.results["response_times"].append(response_time)
                self.results["total_requests"] += 1
                
                if response.status == 200:
                    data = await response.json()
                    self.results["successful_requests"] += 1
                    return data.get("success", False)
                else:
                    self.results["failed_requests"] += 1
                    return False
        except Exception as e:
            self.results["failed_requests"] += 1
            self.results["errors"].append(f"Get stats error: {str(e)}")
            return False
    
    async def concurrent_operations(self, num_operations: int = 50):
        """Opérations concurrentes pour tester la charge"""
        print(f"🚀 Lancement de {num_operations} opérations concurrentes...")
        
        tasks = []
        for i in range(num_operations):
            operation_type = random.choice(["create", "list", "stats", "health"])
            
            if operation_type == "create":
                case_data = self.generate_case_data()
                tasks.append(self.create_case(case_data))
            elif operation_type == "list":
                skip = random.randint(0, 20)
                limit = random.randint(5, 15)
                tasks.append(self.list_cases(skip, limit))
            elif operation_type == "stats":
                tasks.append(self.get_stats())
            elif operation_type == "health":
                tasks.append(self.health_check())
        
        # Exécution concurrente
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyse des résultats
        successful = sum(1 for r in results if r is True)
        failed = len(results) - successful
        
        print(f"✅ Opérations réussies: {successful}/{num_operations}")
        print(f"❌ Opérations échouées: {failed}/{num_operations}")
        print(f"⏱️  Durée totale: {end_time - start_time:.2f}s")
        print(f"📊 Débit: {num_operations / (end_time - start_time):.2f} ops/sec")
    
    async def sequential_load_test(self, num_cases: int = 100):
        """Test de charge séquentiel avec création de nombreux dossiers"""
        print(f"📈 Test de charge séquentiel: création de {num_cases} dossiers...")
        
        start_time = time.time()
        
        for i in range(num_cases):
            case_data = self.generate_case_data()
            success = await self.create_case(case_data)
            
            if (i + 1) % 10 == 0:
                print(f"   Créé {i + 1}/{num_cases} dossiers...")
            
            # Petite pause pour éviter de surcharger
            await asyncio.sleep(0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Test séquentiel terminé en {duration:.2f}s")
        print(f"📊 Débit: {num_cases / duration:.2f} dossiers/sec")
    
    async def stress_test(self, duration_seconds: int = 60):
        """Test de stress pendant une durée donnée"""
        print(f"💪 Test de stress pendant {duration_seconds} secondes...")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        operation_count = 0
        while time.time() < end_time:
            # Opération aléatoire
            operation_type = random.choice(["create", "list", "stats", "health", "update"])
            
            if operation_type == "create":
                case_data = self.generate_case_data()
                await self.create_case(case_data)
            elif operation_type == "list":
                await self.list_cases(random.randint(0, 50), random.randint(5, 20))
            elif operation_type == "stats":
                await self.get_stats()
            elif operation_type == "health":
                await self.health_check()
            elif operation_type == "update" and self.results["created_cases"]:
                dossier_id = random.choice(self.results["created_cases"])
                updates = {"description": f"Mis à jour par stress test - {datetime.now()}"}
                await self.update_case(dossier_id, updates)
            
            operation_count += 1
            
            # Pause aléatoire entre 0.1 et 0.5 secondes
            await asyncio.sleep(random.uniform(0.1, 0.5))
        
        actual_duration = time.time() - start_time
        print(f"✅ Test de stress terminé: {operation_count} opérations en {actual_duration:.2f}s")
        print(f"📊 Débit moyen: {operation_count / actual_duration:.2f} ops/sec")
    
    def print_final_report(self):
        """Rapport final des tests de charge"""
        if not self.results["response_times"]:
            print("❌ Aucune donnée de performance collectée")
            return
        
        avg_response_time = statistics.mean(self.results["response_times"])
        median_response_time = statistics.median(self.results["response_times"])
        max_response_time = max(self.results["response_times"])
        min_response_time = min(self.results["response_times"])
        
        success_rate = (self.results["successful_requests"] / self.results["total_requests"]) * 100
        
        print("\n" + "="*60)
        print("📊 RAPPORT FINAL - TESTS DE CHARGE MONGODB ATLAS")
        print("="*60)
        print(f"🔢 Total requêtes: {self.results['total_requests']}")
        print(f"✅ Requêtes réussies: {self.results['successful_requests']}")
        print(f"❌ Requêtes échouées: {self.results['failed_requests']}")
        print(f"📈 Taux de succès: {success_rate:.2f}%")
        print(f"📊 Dossiers créés: {len(self.results['created_cases'])}")
        print("\n📊 PERFORMANCES:")
        print(f"   ⏱️  Temps de réponse moyen: {avg_response_time:.3f}s")
        print(f"   📊 Temps de réponse médian: {median_response_time:.3f}s")
        print(f"   ⚡ Temps de réponse min: {min_response_time:.3f}s")
        print(f"   🐌 Temps de réponse max: {max_response_time:.3f}s")
        
        if self.results["errors"]:
            print(f"\n❌ ERREURS ({len(self.results['errors'])}):")
            for error in self.results["errors"][:5]:  # Afficher max 5 erreurs
                print(f"   • {error}")
            if len(self.results["errors"]) > 5:
                print(f"   ... et {len(self.results['errors']) - 5} autres erreurs")
        
        print("="*60)

async def main():
    """Fonction principale des tests de charge"""
    print("🛡️  TESTS DE CHARGE MONGODB ATLAS - DEFENSEUR-IA")
    print("="*60)
    
    async with MongoDBLoadTester() as tester:
        start_time = time.time()
        
        # 1. Vérification de santé initiale
        print("🔍 Vérification de la connexion MongoDB Atlas...")
        if not await tester.health_check():
            print("❌ Impossible de se connecter à MongoDB Atlas. Arrêt des tests.")
            return
        print("✅ Connexion MongoDB Atlas OK")
        
        # 2. Test de charge concurrentiel (léger)
        await tester.concurrent_operations(num_operations=25)
        
        # 3. Test de charge séquentiel (création en masse)
        await tester.sequential_load_test(num_cases=50)
        
        # 4. Test de stress (opérations continues)
        await tester.stress_test(duration_seconds=30)
        
        # 5. Test final de vérification
        print("\n🔍 Vérification finale des statistiques...")
        await tester.get_stats()
        
        tester.results["test_duration"] = time.time() - start_time
        
        # 6. Rapport final
        tester.print_final_report()
        
        # 7. Sauvegarde des résultats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"mongodb_load_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(tester.results, f, indent=2, default=str)
        
        print(f"\n💾 Résultats sauvegardés dans: {results_file}")

if __name__ == "__main__":
    asyncio.run(main())
