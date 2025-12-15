# 🚀 Guide de déploiement - Trail Dashboard MVP Multi-utilisateurs

## 📋 Prérequis

- Compte GitHub
- Compte Supabase (gratuit)
- Compte Streamlit Cloud (gratuit)
- Application Strava OAuth (déjà configurée)

---

## Étape 1 : Configuration Supabase

### 1.1 Créer un projet Supabase

1. Va sur [supabase.com](https://supabase.com)
2. Clique sur "Start your project"
3. Crée un nouveau projet :
   - **Name** : trail-dashboard
   - **Database Password** : (génère un mot de passe fort)
   - **Region** : Europe West (Irlande) ou le plus proche

⏱️ Attends 2-3 minutes que le projet soit créé

### 1.2 Initialiser la base de données

1. Dans ton projet Supabase, va dans **SQL Editor**
2. Clique sur "+ New query"
3. Copie-colle le contenu de `database/init_supabase.sql`
4. Clique sur **Run** (en bas à droite)

✅ Tu devrais voir : "Base de données initialisée avec succès !"

### 1.3 Récupérer les clés API

1. Va dans **Settings** → **API**
2. Note ces 2 valeurs (tu en auras besoin) :
   - **Project URL** : `https://xxxxx.supabase.co`
   - **anon/public key** : `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

---

## Étape 2 : Préparer le code pour GitHub

### 2.1 Mettre à jour requirements.txt

Ajoute ces lignes à `requirements.txt` :

```txt
supabase==2.3.4
python-dotenv==1.0.0
```

### 2.2 Créer .streamlit/secrets.toml (local uniquement)

Pour tester en local, crée `.streamlit/secrets.toml` :

```toml
# Strava OAuth
STRAVA_CLIENT_ID = "your_strava_client_id"
STRAVA_CLIENT_SECRET = "your_strava_client_secret"

# Supabase
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

⚠️ **IMPORTANT** : Vérifie que `.streamlit/secrets.toml` est dans `.gitignore`

### 2.3 Mettre à jour .gitignore

Assure-toi que `.gitignore` contient :

```
.streamlit/secrets.toml
.env
__pycache__/
*.pyc
.DS_Store
```

---

## Étape 3 : Pousser sur GitHub

```bash
# Initialiser git si pas déjà fait
git init

# Ajouter tous les fichiers
git add .

# Commit
git commit -m "MVP multi-utilisateurs avec Supabase"

# Créer un repo sur GitHub (via l'interface web)
# Puis lier et pousser :
git remote add origin https://github.com/ton-username/trail-dashboard.git
git branch -M main
git push -u origin main
```

---

## Étape 4 : Déployer sur Streamlit Cloud

### 4.1 Créer l'app Streamlit

1. Va sur [share.streamlit.io](https://share.streamlit.io)
2. Connecte-toi avec GitHub
3. Clique sur **New app**
4. Configure :
   - **Repository** : ton-username/trail-dashboard
   - **Branch** : main
   - **Main file path** : app.py
   - **App URL** : trail-dashboard-ton-nom (ou autre)

### 4.2 Configurer les secrets

1. Dans Streamlit Cloud, clique sur **Advanced settings**
2. Dans la section **Secrets**, colle :

```toml
# Strava OAuth
STRAVA_CLIENT_ID = "your_strava_client_id"
STRAVA_CLIENT_SECRET = "your_strava_client_secret"
STRAVA_REDIRECT_URI = "https://trail-dashboard-ton-nom.streamlit.app"

# Supabase
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

⚠️ **IMPORTANT** : Remplace `STRAVA_REDIRECT_URI` par l'URL exacte de ton app Streamlit

### 4.3 Mettre à jour Strava OAuth

1. Va sur [strava.com/settings/api](https://www.strava.com/settings/api)
2. Dans **Authorization Callback Domain**, ajoute :
   ```
   trail-dashboard-ton-nom.streamlit.app
   ```

### 4.4 Déployer

Clique sur **Deploy** !

⏱️ Attends 2-3 minutes que l'app démarre

---

## Étape 5 : Tester

### 5.1 Premier test

1. Va sur ton URL : `https://trail-dashboard-ton-nom.streamlit.app`
2. Clique sur "Se connecter avec Strava"
3. Autorise l'application
4. Tu devrais voir tes données !

### 5.2 Vérifier Supabase

1. Va dans Supabase → **Table Editor**
2. Regarde la table `users`
3. Tu devrais voir ton profil !

### 5.3 Tester multi-utilisateurs

1. Demande à un ami de se connecter
2. Chaque utilisateur devrait voir UNIQUEMENT ses propres données
3. Les objectifs sauvegardés devraient persister entre sessions

---

## 🔧 Fonctionnalités activées

✅ **Authentification multi-utilisateurs**
- Chaque utilisateur a ses propres données
- Tokens Strava sauvegardés et rafraîchis automatiquement

✅ **Cache des données Strava**
- Les activités sont mises en cache 1h
- Évite les appels API répétés
- Charge instantanée au retour

✅ **Sauvegarde des objectifs**
- Les objectifs de saison sont persistés en base
- Synchronisés entre devices
- Suppression/modification possible

✅ **Préférences utilisateur**
- FC max/repos sauvegardées
- Genre et niveau sauvegardés
- Restaurées automatiquement

---

## 📊 Monitoring

### Voir les utilisateurs actifs

Dans Supabase → **SQL Editor** :

```sql
SELECT 
    name,
    email,
    created_at,
    updated_at
FROM users
ORDER BY created_at DESC;
```

### Voir les objectifs

```sql
SELECT * FROM upcoming_races;
```

### Statistiques

```sql
SELECT * FROM user_stats;
```

---

## 🐛 Troubleshooting

### Erreur "SUPABASE_URL not found"

→ Vérifie que les secrets sont bien configurés dans Streamlit Cloud

### Erreur "Failed to fetch activities"

→ Vérifie que le token Strava est valide dans Supabase

### Les objectifs ne se sauvegardent pas

→ Regarde les logs Streamlit Cloud pour voir l'erreur exacte

### Cache ne fonctionne pas

→ Vérifie que la table `strava_cache` existe dans Supabase

---

## 🔐 Sécurité

### Row Level Security (RLS)

Supabase RLS est activé sur toutes les tables. Pour le MVP, on utilise des policies permissives car l'isolation se fait côté application.

### Pour plus de sécurité (optionnel)

Si tu veux durcir la sécurité, tu peux ajouter des policies strictes :

```sql
-- Exemple : limiter l'accès aux données de l'utilisateur
CREATE POLICY "Users see only their data" ON race_goals
    FOR SELECT USING (strava_id = current_setting('app.current_user_id'));
```

---

## 📈 Limites gratuites

**Supabase Free Tier** :
- 500 Mo de base de données
- 1 Go de stockage fichiers
- 2 Go de transfert/mois
- ✅ Largement suffisant pour 100-200 utilisateurs actifs

**Streamlit Cloud Free** :
- 1 app publique
- 1 Go RAM
- Partage CPU
- ✅ Suffisant pour ~50 utilisateurs simultanés

---

## 🚀 Mise à jour

Pour mettre à jour l'app après modifications :

```bash
git add .
git commit -m "Description des changements"
git push origin main
```

Streamlit Cloud redéploie automatiquement en 1-2 minutes !

---

## ✅ Checklist de déploiement

- [ ] Projet Supabase créé
- [ ] Base de données initialisée (`init_supabase.sql` exécuté)
- [ ] Clés Supabase récupérées
- [ ] Requirements.txt mis à jour
- [ ] Code poussé sur GitHub
- [ ] App créée sur Streamlit Cloud
- [ ] Secrets configurés dans Streamlit
- [ ] Strava OAuth mis à jour avec nouvelle URL
- [ ] Premier test de connexion réussi
- [ ] Vérification multi-utilisateurs OK

---

**Ton dashboard est maintenant en production et accessible à plusieurs utilisateurs ! 🎉**

**URL de ton app** : `https://trail-dashboard-ton-nom.streamlit.app`

---

## 💡 Prochaines étapes (V3.1)

Une fois le MVP en production :
- Export PDF des rapports
- Alertes email automatiques
- API backend FastAPI (pour mobile app)
- Cache Redis pour performances
- Analytics utilisateurs
