# 🔧 CORRECTIF APPLIQUÉ

## Problème résolu

**Erreur** : `ImportError: cannot import name 'show_training_load_page' from 'pages'`

## Cause

Dans Streamlit, les pages dans le dossier `pages/` sont automatiquement détectées et ne doivent **PAS** être importées manuellement dans `app.py`.

## Solution appliquée

### 1. Suppression des imports incorrects dans `app.py`

**Avant (incorrect) :**
```python
from pages import show_training_load_page, show_activity_detail_page
```

**Après (correct) :**
```python
# Pas d'import - Streamlit détecte automatiquement les pages/
```

### 2. Suppression du routing manuel

**Avant (incorrect) :**
```python
if page == "⚡ Charge d'entraînement":
    from pages.charge_entrainement import show_training_load_page
    show_training_load_page(df)
```

**Après (correct) :**
Les pages sont accessibles via la sidebar de Streamlit automatiquement.

### 3. Passage des données via `st.session_state`

Pour que les autres pages aient accès aux données, on les stocke dans `st.session_state` :

**Dans `app.py` :**
```python
# Stockage des données
st.session_state.df = df
st.session_state.access_token = access_token
```

**Dans chaque page (`pages/2_*.py`, `pages/3_*.py`) :**
```python
# Récupération des données
if 'df' not in st.session_state:
    st.error("Va d'abord sur la page d'accueil")
    st.stop()

df = st.session_state.df
access_token = st.session_state.access_token
```

## Comment ça marche maintenant

### Navigation

Streamlit détecte automatiquement les fichiers dans `pages/` avec le pattern `N_emoji_nom.py` :

```
pages/
├── 2_⚡_Charge_entrainement.py  → Page "⚡ Charge entrainement"
└── 3_🔍_Analyse_detaillee.py   → Page "🔍 Analyse detaillee"
```

La navigation apparaît automatiquement dans la sidebar :
- 🏠 app.py (page d'accueil)
- ⚡ Charge entrainement
- 🔍 Analyse detaillee

### Flux de données

1. **Page d'accueil (`app.py`)** :
   - Connexion Strava
   - Chargement des données
   - Stockage dans `st.session_state.df`
   - Affichage de la vue d'ensemble

2. **Autres pages** :
   - Vérifient que `st.session_state.df` existe
   - Récupèrent les données
   - Affichent leurs analyses

## Vérification

L'erreur est maintenant corrigée. Pour tester :

```bash
streamlit run app.py
```

Tu devrais voir :
1. La page d'accueil avec connexion Strava
2. La sidebar avec les 3 pages
3. Navigation fluide entre les pages

---

**Version corrigée : ✅ Prête à l'emploi**
