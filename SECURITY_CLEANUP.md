# 🚨 Nettoyage de Sécurité - Instructions Urgentes

## Problème Identifié

Une clé API Pinecone (`pcsk_53kgE6...`) a été trouvée dans l'historique Git du projet (commit: `bf40873`).

## ⚠️ Actions Urgentes Requises

### 1. RÉVOQUER LA CLÉ API PINECONE IMMÉDIATEMENT

**Cette clé doit être révoquée même si le repo est privé.**

**Étapes :**
1. Connexion à Pinecone: https://app.pinecone.io/
2. Aller dans "API Keys"
3. Révoquer la clé commençant par `pcsk_53kgE6...`
4. Générer une nouvelle clé
5. Ajouter la nouvelle clé dans votre fichier `.env` (PAS dans Git)

### 2. Vérifier si le Repo est Public

```bash
# Vérifier l'URL du remote
git remote -v

# Si le repo est sur GitHub/GitLab public, c'est CRITIQUE
# La clé est exposée publiquement et doit être révoquée IMMÉDIATEMENT
```

**Si le repo EST public ou l'a été dans le passé :**
- ❗ La clé est compromise
- ❗ Possibilité d'utilisation frauduleuse
- ❗ Coûts potentiels non autorisés
- ❗ Révocation IMMÉDIATE obligatoire

### 3. Nettoyer l'Historique Git (Optionnel mais Recommandé)

**ATTENTION : Cette opération réécrit l'historique Git. À faire avec précaution.**

#### Option A : Utiliser BFG Repo-Cleaner (Recommandé)

```bash
# 1. Installer BFG (si pas déjà fait)
# macOS: brew install bfg
# Linux: télécharger depuis https://rtyley.github.io/bfg-repo-cleaner/

# 2. Créer une sauvegarde
git clone --mirror . ../AvocatX-backup.git

# 3. Nettoyer les secrets
bfg --replace-text secrets.txt .git

# 4. Expirer et nettoyer
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push (ATTENTION : coordonner avec l'équipe)
git push --force --all
git push --force --tags
```

**Fichier `secrets.txt` :**
```
pcsk_53kgE6_BRouDzLZuN5PPKvjykzNu2dYbBueVmTgnrBkP5gkpmrtFCgREoz8goGUF9c2UsA
defenseur123
defenseur-secret-key-change-in-production
```

#### Option B : Utiliser git filter-repo (Alternative)

```bash
# 1. Installer git-filter-repo
pip install git-filter-repo

# 2. Créer une sauvegarde
git clone . ../AvocatX-backup

# 3. Filtrer le fichier contenant la clé
git filter-repo --path backend/src/defenseur_ia/services/pinecone_service.py --invert-paths

# 4. Ou remplacer les secrets directement
git filter-repo --replace-text secrets.txt

# 5. Force push
git push --force --all
```

### 4. Prévenir les Futures Fuites

✅ **Déjà fait dans ce commit :**
- Clé API retirée du code
- Mots de passe par défaut supprimés
- Validation en production ajoutée
- `.env.example` mis à jour avec instructions

✅ **À faire maintenant :**
- [ ] Révoquer la clé Pinecone compromise
- [ ] Générer de nouveaux secrets forts
- [ ] Créer un fichier `.env` avec les nouveaux secrets
- [ ] Configurer un gestionnaire de secrets pour production

✅ **Bonnes pratiques pour l'avenir :**
- [ ] Utiliser git-secrets ou pre-commit hooks
- [ ] Scanner régulièrement avec truffleHog ou gitleaks
- [ ] Rotation des secrets tous les 90 jours
- [ ] Utiliser AWS Secrets Manager / Azure Key Vault en production

## 5. Générer de Nouveaux Secrets

```bash
# Générer un mot de passe Postgres fort
python -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(32))"

# Générer une clé secrète JWT forte
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Ajouter ces valeurs dans backend/.env (PAS dans Git)
```

## 6. Configuration Docker-Compose Sécurisée

Au lieu de hardcoder les mots de passe dans `docker-compose.yml`, utiliser des variables d'environnement :

```yaml
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  SECRET_KEY: ${SECRET_KEY}
```

Ou utiliser Docker secrets (recommandé pour production).

## 7. Vérification Post-Nettoyage

```bash
# Vérifier qu'aucun secret n'est présent
git log --all -S "pcsk_" --source --all
git log --all -S "defenseur123" --source --all

# Les commandes ci-dessus ne doivent retourner AUCUN résultat
```

## 📞 Besoin d'Aide ?

Si vous avez des questions sur cette procédure :
1. Consulter la documentation Git : https://git-scm.com/docs
2. Documentation BFG : https://rtyley.github.io/bfg-repo-cleaner/
3. Contacter l'équipe de sécurité

## ⏱️ Timeline Recommandée

- **Maintenant** : Révoquer la clé Pinecone
- **Dans l'heure** : Générer de nouveaux secrets
- **Aujourd'hui** : Nettoyer l'historique Git (si repo public/partagé)
- **Cette semaine** : Configurer les hooks de sécurité

---

**Date de découverte :** 2025-10-20
**Sévérité :** CRITIQUE
**Statut :** Corrections appliquées dans le code, révocation de clé requise
