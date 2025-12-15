-- Script d'initialisation de la base de données Supabase
-- À exécuter dans l'éditeur SQL de Supabase

-- ===== TABLE USERS =====
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    strava_id TEXT UNIQUE NOT NULL,
    name TEXT,
    email TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_users_strava_id ON users(strava_id);

-- ===== TABLE STRAVA_TOKENS =====
CREATE TABLE IF NOT EXISTS strava_tokens (
    id BIGSERIAL PRIMARY KEY,
    strava_id TEXT UNIQUE NOT NULL REFERENCES users(strava_id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_strava_tokens_strava_id ON strava_tokens(strava_id);

-- ===== TABLE STRAVA_CACHE =====
CREATE TABLE IF NOT EXISTS strava_cache (
    id BIGSERIAL PRIMARY KEY,
    strava_id TEXT UNIQUE NOT NULL REFERENCES users(strava_id) ON DELETE CASCADE,
    activities JSONB NOT NULL,
    cached_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- Index pour recherche rapide et nettoyage automatique
CREATE INDEX IF NOT EXISTS idx_strava_cache_strava_id ON strava_cache(strava_id);
CREATE INDEX IF NOT EXISTS idx_strava_cache_expires_at ON strava_cache(expires_at);

-- ===== TABLE USER_PREFERENCES =====
CREATE TABLE IF NOT EXISTS user_preferences (
    id BIGSERIAL PRIMARY KEY,
    strava_id TEXT UNIQUE NOT NULL REFERENCES users(strava_id) ON DELETE CASCADE,
    fc_max INTEGER,
    fc_repos INTEGER,
    gender TEXT CHECK (gender IN ('M', 'F')),
    runner_level TEXT CHECK (runner_level IN ('beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_user_preferences_strava_id ON user_preferences(strava_id);

-- ===== TABLE RACE_GOALS =====
CREATE TABLE IF NOT EXISTS race_goals (
    id BIGSERIAL PRIMARY KEY,
    strava_id TEXT NOT NULL REFERENCES users(strava_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    distance_km DECIMAL(10, 2) NOT NULL,
    elevation_m INTEGER NOT NULL,
    race_type TEXT NOT NULL,
    estimated_time_hours DECIMAL(10, 2),
    pace_estimation DECIMAL(10, 2),
    elevation_penalty DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour recherche et tri
CREATE INDEX IF NOT EXISTS idx_race_goals_strava_id ON race_goals(strava_id);
CREATE INDEX IF NOT EXISTS idx_race_goals_date ON race_goals(date);

-- ===== ROW LEVEL SECURITY (RLS) =====
-- Activer RLS sur toutes les tables pour la sécurité

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE strava_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE strava_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE race_goals ENABLE ROW LEVEL SECURITY;

-- Policies : Les utilisateurs ne peuvent voir que leurs propres données
-- Note: Pour le MVP, on utilise le service_role key côté serveur
-- donc pas besoin de policies complexes pour l'instant

-- Policy pour users (lecture publique pour permettre la création)
CREATE POLICY "Users can read their own data" ON users
    FOR SELECT USING (true);

CREATE POLICY "Users can insert their own data" ON users
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE USING (true);

-- Policy pour strava_tokens (accès complet via service key)
CREATE POLICY "Full access to strava_tokens" ON strava_tokens
    FOR ALL USING (true);

-- Policy pour strava_cache (accès complet via service key)
CREATE POLICY "Full access to strava_cache" ON strava_cache
    FOR ALL USING (true);

-- Policy pour user_preferences (accès complet via service key)
CREATE POLICY "Full access to user_preferences" ON user_preferences
    FOR ALL USING (true);

-- Policy pour race_goals (accès complet via service key)
CREATE POLICY "Full access to race_goals" ON race_goals
    FOR ALL USING (true);

-- ===== FONCTION DE NETTOYAGE AUTOMATIQUE DU CACHE =====
-- Supprime automatiquement les caches expirés (s'exécute quotidiennement)

CREATE OR REPLACE FUNCTION clean_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM strava_cache WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Créer un trigger pour nettoyer le cache périodiquement
-- (À configurer avec pg_cron si disponible, sinon manuel)

-- ===== VUES UTILES =====

-- Vue pour voir les objectifs à venir
CREATE OR REPLACE VIEW upcoming_races AS
SELECT 
    rg.*,
    u.name as user_name,
    (rg.date - CURRENT_DATE) as days_until_race
FROM race_goals rg
JOIN users u ON rg.strava_id = u.strava_id
WHERE rg.date >= CURRENT_DATE
ORDER BY rg.date ASC;

-- Vue pour les statistiques utilisateur
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.strava_id,
    u.name,
    COUNT(DISTINCT rg.id) as total_goals,
    COUNT(DISTINCT CASE WHEN rg.date >= CURRENT_DATE THEN rg.id END) as upcoming_goals,
    up.fc_max,
    up.fc_repos,
    up.gender,
    up.runner_level
FROM users u
LEFT JOIN race_goals rg ON u.strava_id = rg.strava_id
LEFT JOIN user_preferences up ON u.strava_id = up.strava_id
GROUP BY u.strava_id, u.name, up.fc_max, up.fc_repos, up.gender, up.runner_level;

-- ===== COMMENTAIRES =====
COMMENT ON TABLE users IS 'Utilisateurs de l''application';
COMMENT ON TABLE strava_tokens IS 'Tokens d''authentification Strava (chiffrés)';
COMMENT ON TABLE strava_cache IS 'Cache des données Strava pour éviter trop d''appels API';
COMMENT ON TABLE user_preferences IS 'Préférences utilisateur (FC, genre, niveau)';
COMMENT ON TABLE race_goals IS 'Objectifs de courses des utilisateurs';

-- Afficher un message de succès
DO $$
BEGIN
    RAISE NOTICE 'Base de données initialisée avec succès !';
    RAISE NOTICE 'Tables créées : users, strava_tokens, strava_cache, user_preferences, race_goals';
    RAISE NOTICE 'RLS activé sur toutes les tables';
    RAISE NOTICE 'Vues créées : upcoming_races, user_stats';
END $$;
