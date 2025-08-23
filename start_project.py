#!/usr/bin/env python3
"""
Script de démarrage global pour DEFENSEUR-IA
Organise et lance le projet complet (frontend + backend)
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Configuration des chemins
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BLUE}={'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BLUE}={'='*60}{Colors.RESET}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    print_header("Vérification des dépendances")
    
    # Vérifier Python
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print_success(f"Python: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print_error("Python non trouvé")
        return False
    
    # Vérifier Node.js
    try:
        result = subprocess.run(["node", "--version"], 
                              capture_output=True, text=True, check=True)
        print_success(f"Node.js: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print_error("Node.js non trouvé")
        return False
    
    # Vérifier Poetry
    try:
        result = subprocess.run(["poetry", "--version"], 
                              capture_output=True, text=True, check=True)
        print_success(f"Poetry: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Poetry non trouvé. Veuillez l'installer avec 'pip3 install poetry'")
        return False
    
    # Vérifier Docker (optionnel)
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, check=True)
        print_success(f"Docker: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print_info("Docker non trouvé (optionnel)")
    
    return True

def setup_backend():
    """Configure et prépare le backend"""
    print_header("Configuration du Backend")
    
    os.chdir(BACKEND_DIR)
    
    # Installer les dépendances Python
    print_info("Installation des dépendances Python...")
    try:
        subprocess.run(["poetry", "install"], check=True)
        print_success("Dépendances Python installées")
    except subprocess.CalledProcessError as e:
        print_error(f"Erreur installation Python: {e}")
        return False
    
    # Retourner au répertoire racine
    os.chdir(PROJECT_ROOT)
    return True

def setup_frontend():
    """Configure et prépare le frontend"""
    print_header("Configuration du Frontend")
    
    os.chdir(FRONTEND_DIR)
    
    # Installer les dépendances Node.js
    print_info("Installation des dépendances Node.js...")
    try:
        subprocess.run(["npm", "install"], check=True)
        print_success("Dépendances Node.js installées")
    except subprocess.CalledProcessError as e:
        print_error(f"Erreur installation Node.js: {e}")
        return False
    
    # Retourner au répertoire racine
    os.chdir(PROJECT_ROOT)
    return True

def start_backend():
    """Lance le backend"""
    print_header("Démarrage du Backend")
    
    os.chdir(BACKEND_DIR)
    
    print_info("Lancement du backend FastAPI...")
    try:
        # Lancer le backend en arrière-plan
        backend_process = subprocess.Popen([
            "poetry", "run", "python", "-m", "uvicorn", 
            "src.defenseur_ia.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print_success("Backend lancé sur http://localhost:8000")
        print_info("Documentation API: http://localhost:8000/docs")
        
        return backend_process
    except Exception as e:
        print_error(f"Erreur démarrage backend: {e}")
        return None

def start_frontend():
    """Lance le frontend"""
    print_header("Démarrage du Frontend")
    
    os.chdir(FRONTEND_DIR)
    
    print_info("Lancement du frontend React...")
    try:
        # Lancer le frontend en arrière-plan
        frontend_process = subprocess.Popen([
            "npm", "start"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print_success("Frontend lancé sur http://localhost:3000")
        
        return frontend_process
    except Exception as e:
        print_error(f"Erreur démarrage frontend: {e}")
        return None

def display_menu():
    """Affiche le menu principal"""
    print_header("DEFENSEUR-IA - Menu Principal")
    
    print("1. 🚀 Démarrer le projet complet (backend + frontend)")
    print("2. 🔧 Démarrer uniquement le backend")
    print("3. 🎨 Démarrer uniquement le frontend")
    print("4. 📊 Vérifier l'état des services")
    print("5. 🧪 Lancer les tests")
    print("6. ❌ Quitter")
    print()

def check_services():
    """Vérifie l'état des services"""
    print_header("État des Services")
    
    # Vérifier PostgreSQL
    try:
        subprocess.run(["pg_isready", "-h", "localhost", "-p", "5432"], 
                      check=True, capture_output=True)
        print_success("PostgreSQL: En ligne")
    except:
        print_error("PostgreSQL: Hors ligne")
    
    # Vérifier Redis
    try:
        subprocess.run(["redis-cli", "ping"], check=True, capture_output=True)
        print_success("Redis: En ligne")
    except:
        print_error("Redis: Hors ligne")
    
    # Vérifier backend
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print_success("Backend: En ligne")
        else:
            print_error("Backend: Hors ligne")
    except:
        print_error("Backend: Hors ligne")

def main():
    """Fonction principale"""
    print_header("DEFENSEUR-IA - Système d'IA Juridique")
    
    # Vérifier les dépendances
    if not check_dependencies():
        print_error("Dépendances manquantes. Veuillez installer les outils nécessaires.")
        return
    
    # Configurer le projet
    if not setup_backend() or not setup_frontend():
        print_error("Erreur lors de la configuration du projet")
        return
    
    while True:
        display_menu()
        choice = input("Choisissez une option (1-6): ").strip()
        
        if choice == "1":
            print_info("Démarrage du projet complet...")
            backend = start_backend()
            time.sleep(3)  # Attendre que le backend démarre
            frontend = start_frontend()
            
            print_success("🎉 Projet lancé avec succès!")
            print_info("Backend: http://localhost:8000")
            print_info("Frontend: http://localhost:3000")
            print_info("Documentation API: http://localhost:8000/docs")
            
            input("\nAppuyez sur Entrée pour arrêter les services...")
            if backend:
                backend.terminate()
            if frontend:
                frontend.terminate()
            break
            
        elif choice == "2":
            start_backend()
            input("Appuyez sur Entrée pour arrêter le backend...")
            break
            
        elif choice == "3":
            start_frontend()
            input("Appuyez sur Entrée pour arrêter le frontend...")
            break
            
        elif choice == "4":
            check_services()
            input("\nAppuyez sur Entrée pour continuer...")
            
        elif choice == "5":
            print_info("Tests en cours de développement...")
            input("Appuyez sur Entrée pour continuer...")
            
        elif choice == "6":
            print_success("Au revoir! 👋")
            break
            
        else:
            print_error("Option invalide. Veuillez réessayer.")

if __name__ == "__main__":
    main()
