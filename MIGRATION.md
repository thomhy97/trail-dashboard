# 🔄 Guide de migration V1 → V2

## Migration rapide (5 minutes)

### Étape 1 : Sauvegarde tes secrets Strava

```bash
# Dans ton repo actuel (V1)
cp .streamlit/secrets.toml ~/secrets_backup.toml
```

### Étape 2 : Pull les changements V2

```bash
# Dans ton repo local
git pull origin main

# Ou si tu as des conflits, récupère tout depuis GitHub
git fetch origin
git reset --hard origin/main
```

### Étape 3 : Restaure tes secrets

```bash
# Remets ton fichier de secrets
cp ~/secrets_backup.toml .streamlit/secrets.toml
```

### Étape 4 : Installe numpy (nouvelle dépendance)

```bash
# Active ton venv si pas déjà fait
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installe numpy
pip install numpy==1.26.2

# Ou réinstalle tout
pip install -r requirements.txt
```

### Étape 5 : Teste localement

```bash
streamlit run app.py
```

### Étape 6 : Push sur Streamlit Cloud (si déployé)

```bash
# Commit tes éventuels changements locaux
git add .
git commit -m "Migration vers V2 avec analyse de charge"
git push origin main
```

Streamlit Cloud va automatiquement redéployer avec la nouvelle version !

---

## Changements importants

### ✅ Ce qui reste identique

- **Authentification Strava** : Fonctionne exactement pareil
- **Fichier secrets.toml** : Même format, même contenu
- **Données Strava** : Rechargées automatiquement, rien à migrer
- **Configuration** : `.streamlit/config.toml` compatible

### 🆕 Ce qui change

#### 1. Structure des fichiers

**Avant (V1) :**
```
trail-dashboard/
├── app.py
├── requirements.txt
├── .streamlit/
└── ...
```

**Après (V2) :**
```
trail-dashboard/
├── app.py                      # Modifié : navigation multi-pages
├── requirements.txt            # Modifié : + numpy
├── utils/                      # NOUVEAU : modules
│   ├── training_load.py
│   └── activity_analysis.py
├── pages/                      # NOUVEAU : pages supplémentaires
│   ├── 2_⚡_Charge_entrainement.py
│   └── 3_🔍_Analyse_detaillee.py
├── CHANGELOG.md                # NOUVEAU
├── GUIDE_UTILISATION.md        # NOUVEAU
└── .streamlit/
```

#### 2. Navigation

**V1 :** Une seule page avec tout

**V2 :** 3 pages accessibles via sidebar
- 🏠 Vue d'ensemble (même contenu que V1)
- ⚡ Charge d'entraînement (NOUVEAU)
- 🔍 Analyse détaillée (NOUVEAU)

#### 3. Code modifié dans app.py

**Important** : Le fichier `app.py` a été complètement restructuré.

Changement principal - ajout de `'id'` dans les colonnes :

```python
# V1
columns_to_keep = [
    'name', 'distance', 'moving_time', ...
]

# V2 (ligne ~73)
columns_to_keep = [
    'id',  # ← AJOUTÉ : nécessaire pour analyse détaillée
    'name', 'distance', 'moving_time', ...
]
```

Si tu as modifié `app.py` en V1, **tes changements seront écrasés**. Note-les avant de migrer !

---

## Vérification post-migration

### ✅ Checklist

- [ ] `streamlit run app.py` démarre sans erreur
- [ ] La connexion Strava fonctionne
- [ ] La page "Vue d'ensemble" affiche tes données
- [ ] La page "Charge d'entraînement" affiche ATL/CTL/TSB
- [ ] La page "Analyse détaillée" te permet de sélectionner une sortie
- [ ] Les cartes GPS s'affichent (si ta sortie a des données GPS)

### 🐛 Résolution des problèmes courants

#### "Module 'numpy' not found"

```bash
pip install numpy==1.26.2
```

#### "Module 'utils' not found"

Vérifie que les dossiers `utils/` et `pages/` sont bien présents :

```bash
ls -la
# Tu dois voir :
# - utils/
# - pages/
```

Si manquants, re-pull depuis GitHub.

#### "ID Strava manquant"

C'est normal si tu visualises une vieille sortie. Essaie avec une sortie plus récente.

Si le problème persiste, vérifie dans `app.py` ligne ~73 que `'id'` est bien dans `columns_to_keep`.

#### "Could not connect to Strava"

Vérifie que ton fichier `secrets.toml` est bien remis :

```bash
cat .streamlit/secrets.toml
# Tu dois voir ton client_id et client_secret
```

#### Problème sur Streamlit Cloud

Si déployé sur Streamlit Cloud et que ça plante :

1. Va dans les settings de ton app
2. Section "Secrets"
3. Vérifie que le contenu est bien là
4. Clique "Reboot app"

---

## Nouvelles fonctionnalités à explorer

### ⚡ Page Charge d'entraînement

1. **Configure ta FC** dans la sidebar (FC max, FC repos)
2. **Observe tes métriques actuelles** : ATL, CTL, TSB
3. **Analyse les graphiques** :
   - Évolution ATL/CTL/TSB dans le temps
   - TSS et TRIMP hebdomadaires
4. **Vérifie les alertes** de surcharge
5. **Surveille ton ramp rate** (progression CTL)

**Conseil** : Lis le `GUIDE_UTILISATION.md` pour comprendre comment interpréter ces métriques !

### 🔍 Page Analyse détaillée

1. **Sélectionne une sortie** dans la liste
2. **Explore les 4 onglets** :
   - 🗺️ Carte : Visualise ton parcours GPS
   - ⛰️ Profil : Analyse ton profil d'élévation
   - 📊 Allure & FC : Corrélation effort/cardio
   - 🔬 Segments : Découpage par km
3. **Compare** avec des sorties similaires

**Astuce** : Fonctionne mieux avec des sorties récentes qui ont toutes les données (GPS, FC, etc.)

---

## Personnalisations à refaire

Si tu avais personnalisé la V1, voici où refaire les changements :

### Thème / Couleurs

Fichier : `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#FC4C02"  # Ta couleur principale
backgroundColor = "#FFFFFF"
# ...
```

### FC Max / FC Repos par défaut

Fichier : `pages/2_⚡_Charge_entrainement.py` (lignes ~35-45)

```python
fc_max = st.number_input(
    "FC Max (bpm)",
    value=190,  # ← Change ici
)

fc_repos = st.number_input(
    "FC Repos (bpm)",
    value=50,  # ← Change ici
)
```

### Filtres temporels par défaut

Fichier : `app.py` (lignes ~110-120)

```python
time_range = st.selectbox(
    "Afficher",
    ["30 derniers jours", "3 derniers mois", ...],
    index=0  # ← Change l'index pour changer le défaut
)
```

---

## Rollback (retour à V1)

Si tu veux revenir en arrière :

### Option 1 : Via Git

```bash
# Retourne au dernier commit V1
git log  # Trouve le hash du commit V1
git reset --hard <hash_commit_v1>
git push origin main --force  # ⚠️ Force push !
```

### Option 2 : Télécharge la V1

Récupère `trail-dashboard.zip` (V1) depuis les fichiers fournis et remplace tout.

---

## Support migration

### Tu bloques ?

1. **Vérifie les logs** :
   ```bash
   streamlit run app.py
   # Lis les messages d'erreur
   ```

2. **Compare avec le repo de référence** :
   - Vérifie que ta structure de dossiers est identique
   - Compare les fichiers modifiés

3. **Teste étape par étape** :
   ```bash
   # Test import des modules
   python -c "from utils.training_load import TrainingLoadCalculator; print('OK')"
   python -c "from utils.activity_analysis import ActivityAnalyzer; print('OK')"
   ```

4. **Consulte** :
   - `CHANGELOG.md` : Liste complète des changements
   - `GUIDE_UTILISATION.md` : Aide sur les nouvelles features
   - `README.md` : Documentation générale

---

## Prochaines étapes après migration

1. ✅ **Teste toutes les pages** pour vérifier que tout fonctionne
2. 📖 **Lis le GUIDE_UTILISATION.md** pour comprendre TSS/ATL/CTL
3. 🎯 **Configure** ta FC max et FC repos correctement
4. 📊 **Explore** les analyses de charge sur tes derniers mois
5. 🔍 **Analyse** quelques sorties en détail
6. 🎨 **Personnalise** selon tes besoins

---

**Bonne migration ! 🚀**

*En cas de problème, n'hésite pas à ouvrir une issue sur GitHub !*
