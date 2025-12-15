# 📊 Module Database - Supabase

## Vue d'ensemble

Ce module gère toutes les interactions avec la base de données Supabase pour le Trail Dashboard.

## Structure

```
database/
├── __init__.py              # Exports du module
├── supabase_client.py       # Client principal Supabase
├── init_supabase.sql        # Script d'initialisation DB
└── README.md                # Ce fichier
```

## Tables

### 1. `users`
Profils utilisateurs liés à Strava

**Colonnes** :
- `id` : ID auto-incrémenté
- `strava_id` : ID Strava unique (clé)
- `name` : Nom complet
- `email` : Email
- `avatar_url` : URL avatar Strava
- `created_at` / `updated_at` : Timestamps

### 2. `strava_tokens`
Tokens OAuth Strava (chiffrés avec RLS)

**Colonnes** :
- `id` : ID auto-incrémenté
- `strava_id` : Référence vers users
- `access_token` : Token d'accès actif
- `refresh_token` : Token pour rafraîchir
- `expires_at` : Timestamp d'expiration
- `created_at` / `updated_at` : Timestamps

### 3. `strava_cache`
Cache des activités Strava (1h de validité)

**Colonnes** :
- `id` : ID auto-incrémenté
- `strava_id` : Référence vers users
- `activities` : JSON des activités
- `cached_at` : Quand mis en cache
- `expires_at` : Quand expire
  
**Nettoyage** : Automatique via fonction `clean_expired_cache()`

### 4. `user_preferences`
Préférences utilisateur (FC, genre, niveau)

**Colonnes** :
- `id` : ID auto-incrémenté
- `strava_id` : Référence vers users
- `fc_max` : FC maximale
- `fc_repos` : FC de repos
- `gender` : 'M' ou 'F'
- `runner_level` : 'beginner', 'intermediate', 'advanced'
- `created_at` / `updated_at` : Timestamps

### 5. `race_goals`
Objectifs de courses saison

**Colonnes** :
- `id` : ID auto-incrémenté
- `strava_id` : Référence vers users
- `name` : Nom de la course
- `date` : Date de la course
- `distance_km` : Distance en km
- `elevation_m` : D+ en mètres
- `race_type` : Type de course
- `estimated_time_hours` : Temps estimé
- `pace_estimation` : Allure estimée
- `elevation_penalty` : Pénalité D+
- `created_at` / `updated_at` : Timestamps

## Vues

### `upcoming_races`
Vue des courses à venir avec compte à rebours

```sql
SELECT * FROM upcoming_races;
```

### `user_stats`
Statistiques agrégées par utilisateur

```sql
SELECT * FROM user_stats;
```

## Utilisation

### Initialisation

```python
from database import SupabaseDB

# Créer le client (utilise les variables d'environnement)
db = SupabaseDB()
```

### Gestion utilisateurs

```python
# Créer/mettre à jour un utilisateur
user = db.create_or_update_user(
    strava_id="12345",
    user_data={
        "firstname": "John",
        "lastname": "Doe",
        "email": "john@example.com",
        "profile": "https://..."
    }
)

# Récupérer un utilisateur
user = db.get_user("12345")
```

### Tokens Strava

```python
# Sauvegarder les tokens
db.save_strava_token(
    strava_id="12345",
    access_token="abc123...",
    refresh_token="xyz789...",
    expires_at=1234567890
)

# Récupérer les tokens
tokens = db.get_strava_token("12345")
```

### Cache activités

```python
# Sauvegarder en cache
db.save_strava_activities(
    strava_id="12345",
    activities=[{...}, {...}]
)

# Récupérer du cache (None si expiré)
activities = db.get_strava_activities("12345")

if activities is None:
    # Cache expiré, refaire l'appel API Strava
    pass
```

### Préférences

```python
# Sauvegarder
db.save_user_preferences(
    strava_id="12345",
    preferences={
        "fc_max": 190,
        "fc_repos": 50,
        "gender": "M",
        "runner_level": "intermediate"
    }
)

# Récupérer
prefs = db.get_user_preferences("12345")
```

### Objectifs de course

```python
# Créer un objectif
goal = {
    "name": "UTMB",
    "date": datetime(2025, 8, 25),
    "distance_km": 170,
    "elevation_m": 10000,
    "type": "Ultra-trail",
    "estimated_time_hours": 42,
    "pace_estimation": 6.5,
    "elevation_penalty": 4.5
}

db.save_race_goal("12345", goal)

# Récupérer tous les objectifs
goals = db.get_race_goals("12345")

# Supprimer un objectif
db.delete_race_goal(goal_id=123)

# Mettre à jour un objectif
db.update_race_goal(goal_id=123, goal=updated_goal)
```

## Sécurité

### Row Level Security (RLS)

Toutes les tables ont RLS activé. Pour le MVP, on utilise des policies permissives car l'isolation des données se fait côté application (via `strava_id`).

### Variables d'environnement

**Requises** :
- `SUPABASE_URL` : URL du projet Supabase
- `SUPABASE_KEY` : Clé API (anon/public key)

**Configuration locale** (`.streamlit/secrets.toml`) :
```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Configuration production** (Streamlit Cloud Secrets) :
Même format dans l'interface Streamlit Cloud

## Performance

### Cache

- **TTL** : 1 heure pour les activités Strava
- **Invalidation** : Automatique via `expires_at`
- **Nettoyage** : Fonction `clean_expired_cache()` (à configurer en CRON)

### Index

Tous les index nécessaires sont créés automatiquement :
- `strava_id` sur toutes les tables
- `expires_at` sur `strava_cache`
- `date` sur `race_goals`

### Requêtes optimisées

Toutes les requêtes utilisent les index appropriés pour des performances optimales même avec des milliers d'utilisateurs.

## Monitoring

### Requêtes utiles

**Nombre d'utilisateurs** :
```sql
SELECT COUNT(*) FROM users;
```

**Cache hit rate** :
```sql
SELECT 
    COUNT(*) FILTER (WHERE expires_at > NOW()) as valid_cache,
    COUNT(*) FILTER (WHERE expires_at <= NOW()) as expired_cache
FROM strava_cache;
```

**Objectifs par utilisateur** :
```sql
SELECT 
    u.name,
    COUNT(rg.id) as total_goals
FROM users u
LEFT JOIN race_goals rg ON u.strava_id = rg.strava_id
GROUP BY u.name
ORDER BY total_goals DESC;
```

## Migration

Si tu veux migrer vers PostgreSQL manuel plus tard, tu peux exporter les données :

```sql
-- Export users
COPY (SELECT * FROM users) TO '/tmp/users.csv' CSV HEADER;

-- Export race_goals
COPY (SELECT * FROM race_goals) TO '/tmp/race_goals.csv' CSV HEADER;
```

## Troubleshooting

### Erreur "SUPABASE_URL not found"

→ Vérifie que les variables d'environnement sont définies

### Tables n'existent pas

→ Execute `init_supabase.sql` dans SQL Editor

### Cache ne se vide pas

→ Exécute manuellement :
```sql
SELECT clean_expired_cache();
```

### Données dupliquées

→ Vérifie l'unicité de `strava_id` :
```sql
SELECT strava_id, COUNT(*) 
FROM users 
GROUP BY strava_id 
HAVING COUNT(*) > 1;
```

## Limites

**Supabase Free Tier** :
- 500 Mo de base de données
- 2 Go de transfert/mois
- Suffisant pour ~200 utilisateurs actifs

**Taille estimée par utilisateur** :
- User : ~500 bytes
- Tokens : ~300 bytes
- Cache : ~50 KB (temporaire)
- Preferences : ~100 bytes
- Goals : ~500 bytes par objectif

**Total estimé** : ~2 KB + cache par utilisateur

Avec 500 Mo, tu peux stocker ~250,000 utilisateurs (hors cache).
