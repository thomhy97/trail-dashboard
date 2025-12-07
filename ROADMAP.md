# 💡 Roadmap & Idées d'amélioration

## Phase 1 : MVP (Actuel) ✅
- [x] Connexion Strava OAuth
- [x] Récupération des activités
- [x] Métriques de base (distance, D+, temps)
- [x] Graphiques hebdomadaires
- [x] Filtres temporels
- [x] Déploiement Streamlit Cloud

---

## Phase 2 : Analyse avancée 📊

### Charge d'entraînement
- [ ] **TSS (Training Stress Score)** : Basé sur FC ou puissance
- [ ] **TRIMP** : Charge d'entraînement selon FC
- [ ] **ATL/CTL/TSB** : Modèle de fatigue/forme/équilibre
  - ATL (Acute Training Load) : Fatigue - 7 jours
  - CTL (Chronic Training Load) : Forme - 42 jours
  - TSB (Training Stress Balance) : CTL - ATL
- [ ] Graphique de charge cumulée
- [ ] Alertes de surcharge/sous-charge

### Zones d'intensité
- [ ] **Configuration zones FC** : 5 zones personnalisées
- [ ] Distribution temps par zone
- [ ] Analyse polarisée (80/20)
- [ ] Zones de vitesse/allure
- [ ] Graphiques par zone sur période

### Vitesse ascensionnelle
- [ ] **Calcul VAM** (Vitesse Ascensionnelle Moyenne)
- [ ] Évolution VAM dans le temps
- [ ] Comparaison par type de sortie
- [ ] Détection des meilleures performances

### Analyse détaillée des sorties
- [ ] Carte interactive (Folium ou Plotly)
- [ ] Profil d'élévation
- [ ] Allure/FC par segment
- [ ] Comparaison entre sorties similaires

---

## Phase 3 : Planification & Objectifs 🎯

### Objectifs de saison
- [ ] **Définition objectifs** : Courses cibles avec dates
- [ ] Calcul temps nécessaire pour chaque objectif
- [ ] Progression vers objectifs (km, D+, temps)
- [ ] Compte à rebours

### Plan d'entraînement
- [ ] **Import/création plans** : Par semaine
- [ ] Comparaison réalisé vs prévu
- [ ] Alertes écarts au plan
- [ ] Templates de plans (type Garmin, TrainingPeaks)

### Prédiction de performances
- [ ] **Modèle VDOT** : Estimation temps sur distances
- [ ] Calculateur d'équivalence courses
- [ ] Prédiction temps selon le D+
- [ ] Progression nécessaire pour objectif

---

## Phase 4 : Architecture robuste 🏗️

### Backend
- [ ] **API FastAPI** : Séparation front/back
- [ ] Endpoints REST pour toutes les données
- [ ] Cache Redis pour requêtes fréquentes
- [ ] Jobs périodiques (sync Strava auto)

### Base de données
- [ ] **PostgreSQL** : Persistance des données
- [ ] Schema :
  ```sql
  - users (id, strava_id, tokens, preferences)
  - activities (id, user_id, strava_data, processed_metrics)
  - training_plans (id, user_id, weeks, workouts)
  - goals (id, user_id, race_date, target_time, distance)
  - zones (id, user_id, hr_zones, pace_zones)
  ```
- [ ] Migrations Alembic
- [ ] Backup automatique

### Authentification
- [ ] JWT tokens
- [ ] Refresh token rotation
- [ ] Multi-utilisateurs
- [ ] Gestion des droits

### Performance
- [ ] Mise en cache intelligente
- [ ] Pagination des activités
- [ ] Lazy loading des graphiques
- [ ] Optimisation des requêtes SQL

---

## Phase 5 : Fonctionnalités avancées 🚀

### Export & Partage
- [ ] **Export PDF** : Rapports mensuels/annuels
- [ ] Export Excel des données
- [ ] Partage de stats (image/lien)
- [ ] Templates de rapports personnalisables

### Comparaisons
- [ ] **Multi-athlètes** : Comparaison anonyme
- [ ] Benchmark par âge/sexe/niveau
- [ ] Classements communautaires
- [ ] Évolution vs groupe

### Intégrations
- [ ] **Garmin Connect** : Import données
- [ ] TrainingPeaks : Export/sync
- [ ] Polar Flow
- [ ] Suunto
- [ ] Wahoo

### Machine Learning
- [ ] **Détection anomalies** : Blessures potentielles
- [ ] Prédiction performances ML
- [ ] Recommandations d'entraînement
- [ ] Clustering types de sorties
- [ ] Analyse de récupération

### Météo & Conditions
- [ ] Intégration API météo
- [ ] Corrélation performances/météo
- [ ] Historique conditions
- [ ] Alertes conditions favorables

---

## Phase 6 : Expérience utilisateur 🎨

### Interface
- [ ] **Mode sombre**
- [ ] Thème personnalisable
- [ ] Layout responsive mobile
- [ ] PWA (Progressive Web App)
- [ ] Raccourcis clavier

### Notifications
- [ ] Rappels d'entraînement
- [ ] Alertes objectifs
- [ ] Résumés hebdo par email
- [ ] Push notifications mobile

### Gamification
- [ ] **Badges** : Réalisations
- [ ] Streaks : Jours consécutifs
- [ ] Challenges mensuels
- [ ] Progression niveau

---

## Stack technique évolutive

### Phase 1 (Actuel)
```
Streamlit + Plotly + Pandas
└── Streamlit Cloud
```

### Phase 2-3
```
Streamlit (Frontend)
└── FastAPI (Backend)
    └── PostgreSQL
    └── Redis (Cache)
└── Déploiement : Railway / Render
```

### Phase 4-6
```
React/Next.js (Frontend) ou Streamlit amélioré
└── FastAPI (Backend)
    ├── PostgreSQL (Primary)
    ├── Redis (Cache)
    ├── Celery (Background jobs)
    └── ML Models (scikit-learn, TensorFlow)
└── Déploiement : 
    ├── Frontend: Vercel
    ├── Backend: Google Cloud Run
    ├── DB: Supabase / Cloud SQL
    └── Queue: Cloud Tasks
```

---

## Métriques à ajouter

### Basiques
- [ ] Allure moyenne (min/km)
- [ ] Calories
- [ ] Cadence
- [ ] Temps d'arrêt vs temps en mouvement

### Avancées
- [ ] Ratio efficacité (E/A)
- [ ] Variabilité fréquence cardiaque
- [ ] Temps de récupération
- [ ] Charge de travail par muscle

### Trail spécifique
- [ ] **Coefficient de traîlitude** : (D+/km)
- [ ] Équivalence km plat
- [ ] Efficacité montée/descente
- [ ] Technicité du terrain

---

## Priorités suggérées

### Court terme (1-2 mois)
1. Zones de fréquence cardiaque
2. Calcul charge TSS/TRIMP
3. Graphique ATL/CTL
4. Définition objectifs

### Moyen terme (3-6 mois)
1. Base de données PostgreSQL
2. API FastAPI
3. Plans d'entraînement
4. Export PDF

### Long terme (6-12 mois)
1. Machine Learning prédictions
2. Multi-utilisateurs
3. Application mobile
4. Intégrations tierces

---

## Notes techniques

### APIs à explorer
- **Strava** : Actuel ✅
- **OpenWeather** : Météo
- **Google Maps Elevation** : Profils
- **TrainingPeaks** : Plans
- **Mapbox** : Cartes avancées

### Librairies Python utiles
```python
# Actuelles
streamlit, pandas, plotly, requests

# À ajouter
fastapi          # API backend
sqlalchemy       # ORM database
alembic          # Migrations
redis            # Cache
celery           # Background tasks
stravalib        # Wrapper Strava plus complet
gpxpy            # Parse fichiers GPX
fitparse         # Parse fichiers FIT
scikit-learn     # ML basique
tensorflow       # ML avancé
reportlab        # Export PDF
folium           # Cartes interactives
```

---

## Ressources

### Documentation
- [Strava API](https://developers.strava.com/)
- [TrainingPeaks API](https://developers.trainingpeaks.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### Concepts d'entraînement
- [Training Stress Score](https://www.trainingpeaks.com/blog/what-is-tss/)
- [TRIMP](https://www.movescount.com/fr/page/trimp)
- [80/20 Training](https://www.8020endurance.com/)

### Inspiration
- [Strava Labs](https://labs.strava.com/)
- [TrainingPeaks Dashboard](https://www.trainingpeaks.com/)
- [Golden Cheetah](https://www.goldencheetah.org/)

---

Bon courage pour faire évoluer ton dashboard ! 💪🏔️
