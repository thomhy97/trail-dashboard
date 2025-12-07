# 🔧 Commandes Git pour mettre à jour ton repo

## Option 1 : Mise à jour directe (RECOMMANDÉE)

### Préparation

```bash
# 1. Va dans ton repo local
cd chemin/vers/ton/trail-dashboard

# 2. Sauvegarde tes secrets Strava
cp .streamlit/secrets.toml ~/secrets_backup.toml

# 3. Vérifie le statut
git status
```

### Si tu as des modifications locales

```bash
# Commit tes changements
git add .
git commit -m "Sauvegarde avant migration V2"
```

### Téléchargement des fichiers V2

Tu as 2 options :

#### Option A : Remplacer tous les fichiers (le plus simple)

1. **Télécharge** le ZIP depuis les outputs
2. **Dézippe** dans un dossier temporaire
3. **Copie** tous les fichiers (SAUF .git/) dans ton repo
4. **Restaure** ton secrets.toml :
   ```bash
   cp ~/secrets_backup.toml .streamlit/secrets.toml
   ```

#### Option B : Utiliser Git directement

Si tu as accès à mon repo complet :

```bash
# Ajoute le repo source comme remote
git remote add source https://github.com/TON_REPO_SOURCE/trail-dashboard-v2.git

# Pull les changements
git pull source main --allow-unrelated-histories

# Ou si conflit, force:
git fetch source main
git reset --hard source/main

# Restaure tes secrets
cp ~/secrets_backup.toml .streamlit/secrets.toml
```

### Après le téléchargement

```bash
# 1. Installe numpy
pip install numpy==1.26.2

# 2. Teste localement
streamlit run app.py

# 3. Si tout OK, commit
git add .
git commit -m "Migration vers V2 - Ajout analyse de charge et détails sorties"

# 4. Push vers GitHub
git push origin main
```

---

## Option 2 : Création d'une branche V2

Si tu veux garder V1 accessible :

```bash
# 1. Crée une branche pour V1
git checkout -b v1-archive
git push origin v1-archive

# 2. Retourne sur main
git checkout main

# 3. Remplace par les fichiers V2 (voir Option 1)

# 4. Commit et push
git add .
git commit -m "Migration vers V2"
git push origin main
```

Maintenant tu as :
- `main` : Version 2 (actuelle)
- `v1-archive` : Version 1 (sauvegardée)

---

## Option 3 : Nouveau repo pour V2

Si tu veux garder les 2 versions séparées :

```bash
# 1. Crée un nouveau repo sur GitHub
# Nom : trail-dashboard-v2

# 2. Clone le nouveau repo
git clone https://github.com/TON_USERNAME/trail-dashboard-v2.git
cd trail-dashboard-v2

# 3. Copie tous les fichiers V2 dedans

# 4. Copie tes secrets
cp ~/secrets_backup.toml .streamlit/secrets.toml

# 5. Commit et push
git add .
git commit -m "Initial commit - Trail Dashboard V2"
git push origin main
```

---

## Fichiers à ajouter/modifier

### ✅ Nouveaux fichiers à ajouter

```bash
git add utils/
git add pages/
git add CHANGELOG.md
git add MIGRATION.md
git add GUIDE_UTILISATION.md
git add update_to_v2.sh
```

### ✏️ Fichiers modifiés

```bash
git add app.py              # Restructuré avec navigation
git add requirements.txt    # + numpy
git add README.md          # Documentation enrichie
```

### 🔒 Fichiers à NE PAS committer

```bash
# Déjà dans .gitignore, mais double-check:
.streamlit/secrets.toml   # ❌ NE JAMAIS COMMITTER !
__pycache__/              # ❌
*.pyc                     # ❌
venv/                     # ❌
.env                      # ❌
```

---

## Vérification avant le push

```bash
# Check ce qui va être committé
git status

# Vérifie que secrets.toml n'est PAS là
git status | grep secrets.toml
# Devrait être vide !

# Regarde le diff si tu veux
git diff

# Liste des fichiers qui seront pushés
git diff --name-only origin/main
```

---

## Si Streamlit Cloud

### Après le push sur GitHub

Streamlit Cloud va automatiquement :
1. Détecter les changements
2. Réinstaller les dépendances (avec numpy)
3. Redémarrer l'app

**⚠️ Important** : Vérifie que tes secrets sont bien configurés dans Streamlit Cloud :

1. Va dans Settings → Secrets
2. Vérifie que le contenu est toujours :
   ```toml
   [strava]
   client_id = "..."
   client_secret = "..."
   redirect_uri = "https://ton-app.streamlit.app"
   ```

### Si l'app plante

```bash
# Dans Streamlit Cloud:
# 1. Clique sur "Reboot app"
# 2. Regarde les logs
# 3. Vérifie que numpy s'est bien installé
```

---

## Rollback si problème

### Retour rapide à V1

```bash
# Trouve le dernier commit V1
git log --oneline

# Reviens à ce commit
git reset --hard <hash_du_commit_v1>

# Force push (⚠️ attention, écrase la V2)
git push origin main --force
```

### Avec la branche v1-archive

```bash
# Si tu as créé une branche V1
git checkout v1-archive
git checkout -b main-v1-restored
git push origin main-v1-restored --force
```

---

## Commandes complètes (copier/coller)

```bash
# ÉTAPE 1 : Préparation
cd ~/ton-repo-trail-dashboard
cp .streamlit/secrets.toml ~/secrets_backup.toml
git status

# ÉTAPE 2 : Commit actuel si modifs
git add .
git commit -m "Sauvegarde avant V2"

# ÉTAPE 3 : Remplace par fichiers V2
# (Manuellement : copie tous les fichiers V2 dans le repo)

# ÉTAPE 4 : Restaure secrets
cp ~/secrets_backup.toml .streamlit/secrets.toml

# ÉTAPE 5 : Installe dépendances
pip install numpy==1.26.2

# ÉTAPE 6 : Teste
streamlit run app.py

# ÉTAPE 7 : Commit et push
git add .
git commit -m "Migration V2 : Analyse charge (TSS/ATL/CTL) + Analyse détaillée sorties"
git push origin main

# ÉTAPE 8 : Vérifie Streamlit Cloud
# Va sur streamlit.io/cloud et vérifie que l'app redémarre bien
```

---

## Tags Git (optionnel mais recommandé)

Pour marquer clairement les versions :

```bash
# Crée un tag pour V2.0.0
git tag -a v2.0.0 -m "Version 2.0 - Analyse de charge et sorties détaillées"
git push origin v2.0.0

# Liste des tags
git tag

# Voir les infos d'un tag
git show v2.0.0
```

---

## En cas de problème

### "Merge conflict"

```bash
# Si conflit lors du pull
git status  # Voir les fichiers en conflit

# Option simple : garde la V2
git checkout --theirs .
git add .
git commit -m "Migration V2"
```

### "Secrets perdus"

```bash
# Si tu as oublié de sauvegarder secrets.toml
# Pas de panique, recrée-le :
nano .streamlit/secrets.toml

# Et remets :
[strava]
client_id = "ton_client_id"
client_secret = "ton_secret"
redirect_uri = "http://localhost:8501"
```

### "L'app ne démarre pas"

```bash
# Check les dépendances
pip list | grep numpy
# Doit afficher : numpy 1.26.2

# Réinstalle si besoin
pip install -r requirements.txt

# Regarde les erreurs
streamlit run app.py
# Lis les messages d'erreur
```

---

**Bon courage pour la migration ! 🚀**
