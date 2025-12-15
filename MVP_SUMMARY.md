# 🚀 MVP Multi-utilisateurs - Résumé exécutif

## ✅ Ce qui a été créé

### 📁 Nouveaux fichiers

```
trail-dashboard-update/
├── database/
│   ├── __init__.py                 # Module database
│   ├── supabase_client.py          # Client Supabase (toutes les fonctions DB)
│   ├── init_supabase.sql           # Script SQL d'initialisation
│   └── README.md                   # Documentation database
├── DEPLOYMENT_GUIDE.md             # Guide de déploiement complet
├── MVP_SUMMARY.md                  # Ce fichier
└── requirements.txt                # Mis à jour avec supabase + dotenv
```

### 🔧 Fichiers modifiés

- `requirements.txt` : Ajout de `supabase==2.3.4` et `python-dotenv==1.0.0`

---

## 🎯 Fonctionnalités MVP

### 1. ✅ Multi-utilisateurs
- Chaque utilisateur se connecte avec son compte Strava
- Données complètement isolées par utilisateur
- Pas de confusion entre utilisateurs

### 2. ✅ Sauvegarde objectifs
- Les objectifs de saison sont sauvegardés en base Supabase
- Persistance entre sessions
- Synchronisation entre devices

### 3. ✅ Cache données Strava
- Les activités sont mises en cache 1 heure
- Évite les appels API répétés (économise quota Strava)
- Chargement instantané au retour

### 4. ✅ Sauvegarde préférences
- FC max, FC repos
- Genre (M/F)
- Niveau runner (débutant/intermédiaire/avancé)
- Restaurées automatiquement

---

## 📋 Prochaines étapes (dans l'ordre)

### Étape 1 : Créer compte Supabase (5 min)

1. Va sur [supabase.com](https://supabase.com)
2. Clique "Start your project" (gratuit)
3. Crée un projet :
   - Name: `trail-dashboard`
   - Password: (génère fort)
   - Region: Europe West

### Étape 2 : Initialiser la base de données (2 min)

1. Dans Supabase → **SQL Editor**
2. Copie le contenu de `database/init_supabase.sql`
3. Colle et clique **Run**
4. Vérifie le message de succès

### Étape 3 : Récupérer les clés (1 min)

Dans Supabase → **Settings** → **API** :
- Note `Project URL`
- Note `anon public key`

### Étape 4 : Tester en local (10 min)

Crée `.streamlit/secrets.toml` :

```toml
STRAVA_CLIENT_ID = "ton_client_id"
STRAVA_CLIENT_SECRET = "ton_client_secret"
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR..."
```

Lance :
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Étape 5 : Intégrer dans app.py (30 min)

**Je vais t'aider avec ça maintenant !** 

Il faut modifier `app.py` pour :
1. Initialiser le client Supabase
2. Charger les données depuis le cache
3. Sauvegarder les préférences
4. Gérer les sessions utilisateur

### Étape 6 : Pousser sur GitHub (5 min)

```bash
git add .
git commit -m "MVP multi-utilisateurs avec Supabase"
git push origin main
```

### Étape 7 : Déployer sur Streamlit Cloud (10 min)

Suis `DEPLOYMENT_GUIDE.md` étape 4

---

## 🔑 Variables d'environnement nécessaires

### Local (`.streamlit/secrets.toml`)
```toml
STRAVA_CLIENT_ID = "..."
STRAVA_CLIENT_SECRET = "..."
STRAVA_REDIRECT_URI = "http://localhost:8501"
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJ..."
```

### Production (Streamlit Cloud Secrets)
```toml
STRAVA_CLIENT_ID = "..."
STRAVA_CLIENT_SECRET = "..."
STRAVA_REDIRECT_URI = "https://ton-app.streamlit.app"
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJ..."
```

---

## 📊 Schema de la base de données

```
┌─────────────┐
│   users     │ ← Profil utilisateur (nom, email, avatar)
└──────┬──────┘
       │
       ├─── strava_tokens    ← Tokens OAuth (access, refresh)
       │
       ├─── strava_cache     ← Cache activités (1h TTL)
       │
       ├─── user_preferences ← FC max/repos, genre, niveau
       │
       └─── race_goals       ← Objectifs de courses
```

---

## 🔄 Flow utilisateur

### Première connexion

1. User clique "Se connecter avec Strava"
2. OAuth Strava → obtient tokens
3. **NOUVEAU** : Enregistre user dans Supabase
4. **NOUVEAU** : Sauvegarde tokens dans Supabase
5. Récupère activités Strava
6. **NOUVEAU** : Met en cache dans Supabase
7. Affiche dashboard

### Connexions suivantes

1. User clique "Se connecter"
2. OAuth Strava
3. Vérifie token en base → rafraîchit si expiré
4. **CACHE HIT** : Charge activités depuis Supabase (instantané !)
5. **NOUVEAU** : Charge préférences sauvegardées
6. **NOUVEAU** : Charge objectifs sauvegardés
7. Affiche dashboard avec tout pré-rempli

### Ajout objectif

1. User remplit formulaire objectif
2. Clique "Ajouter"
3. **NOUVEAU** : Sauvegarde dans Supabase
4. Objectif persisté → visible même après déconnexion

---

## 🎨 Changements UI (à faire)

### Page d'accueil (app.py)

**Avant** :
```python
if st.button("Se connecter"):
    # OAuth simple
```

**Après** :
```python
# Initialiser DB
db = SupabaseDB()

# Vérifier si déjà connecté
if 'strava_id' in st.session_state:
    # Charger depuis cache
    cached_activities = db.get_strava_activities(st.session_state.strava_id)
    
    if cached_activities:
        df = pd.DataFrame(cached_activities)
        st.success("✅ Données chargées depuis le cache !")
    else:
        # Appel API Strava
        # ... puis sauver en cache
        db.save_strava_activities(st.session_state.strava_id, activities)
```

### Page objectifs (pages/4_🎯_Objectifs_saison.py)

**Avant** :
```python
if 'race_goals' not in st.session_state:
    st.session_state.race_goals = []
```

**Après** :
```python
# Charger depuis DB
db = SupabaseDB()
goals = db.get_race_goals(st.session_state.strava_id)

# Sauvegarder nouveau goal
if st.button("Ajouter"):
    db.save_race_goal(st.session_state.strava_id, new_goal)
```

---

## 📈 Métriques de succès MVP

### Semaine 1
- [ ] 5 utilisateurs testent
- [ ] Cache fonctionne (vérifier dans Supabase)
- [ ] Objectifs sauvegardés correctement
- [ ] Aucune confusion de données entre users

### Semaine 2-3
- [ ] 20+ utilisateurs
- [ ] Temps de chargement < 2s (grâce au cache)
- [ ] Taux de sauvegarde objectifs > 50%
- [ ] 0 bug critique

---

## 💰 Coûts

### Gratuit ! (jusqu'à ~100 users actifs)

**Supabase Free Tier** :
- ✅ 500 Mo database
- ✅ 2 Go transfert/mois
- ✅ Illimité requêtes

**Streamlit Cloud Free** :
- ✅ 1 app publique
- ✅ 1 Go RAM
- ✅ Redéploiement auto

**Total : 0€/mois** pour le MVP !

---

## 🐛 Troubleshooting

### "Cannot connect to Supabase"
→ Vérifie `SUPABASE_URL` et `SUPABASE_KEY`

### "Table users does not exist"
→ Exécute `init_supabase.sql` dans Supabase

### Cache ne fonctionne pas
→ Regarde dans Supabase → Table Editor → `strava_cache`

### Données d'un autre user visibles
→ **BUG CRITIQUE** - Vérifie l'isolation par `strava_id`

---

## 🚀 Timeline réaliste

- **Maintenant** : J'intègre Supabase dans app.py (1h)
- **Aujourd'hui** : Tu testes en local (30 min)
- **Demain** : Tu déploies sur Streamlit Cloud (1h)
- **J+2** : Tu invites 5 beta testeurs
- **Semaine 1** : Retours et ajustements
- **Semaine 2-3** : Ouverture progressive

**MVP production : dans 2-3 jours ! 🎉**

---

## ✅ Checklist avant production

- [ ] Supabase project créé
- [ ] `init_supabase.sql` exécuté avec succès
- [ ] Tables visibles dans Supabase Table Editor
- [ ] Clés API récupérées
- [ ] Test local fonctionne
- [ ] Cache fonctionne (2ème chargement instant)
- [ ] Objectifs se sauvegardent
- [ ] Préférences se sauvegardent
- [ ] Code pushé sur GitHub
- [ ] Streamlit Cloud déployé
- [ ] Secrets configurés
- [ ] Premier test production OK
- [ ] Test multi-users (2 comptes) OK

---

**Prêt à passer à l'intégration dans app.py ? 🚀**

Dis-moi et je modifie `app.py` pour intégrer tout ça !
