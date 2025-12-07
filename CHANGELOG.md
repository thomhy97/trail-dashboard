# 📝 CHANGELOG - Trail Dashboard

## Version 2.0.0 - Décembre 2024

### 🎉 Nouvelles fonctionnalités majeures

#### ⚡ Analyse de charge d'entraînement
- **TSS (Training Stress Score)** : Quantification de l'intensité de chaque sortie (0-300+)
- **TRIMP (Training Impulse)** : Charge d'entraînement basée sur la fréquence cardiaque (méthode Banister)
- **ATL (Acute Training Load)** : Fatigue récente sur 7 jours (moyenne mobile exponentielle)
- **CTL (Chronic Training Load)** : Forme générale sur 42 jours (moyenne mobile exponentielle)
- **TSB (Training Stress Balance)** : Indicateur de fraîcheur (CTL - ATL)
  - TSB > +25 : Très frais, prêt pour course
  - TSB +5 à +25 : Frais, bon équilibre
  - TSB -10 à +5 : Zone optimale pour progresser
  - TSB -30 à -10 : Fatigué, attention
  - TSB < -30 : Surcharge, repos nécessaire
- **Détection automatique de surcharge** : Alertes quand TSB < -30 ou ATL anormalement élevée
- **Ramp Rate** : Taux de progression de la CTL (recommandé : +5 CTL/semaine max)
- **Graphiques interactifs** : Visualisation de l'évolution ATL/CTL/TSB dans le temps
- **TSS et TRIMP hebdomadaires** : Agrégation et visualisation par semaine
- **Configuration personnalisée** : FC max, FC repos, genre pour calculs précis

#### 🔍 Analyse détaillée des sorties
- **Carte interactive GPS** : Visualisation du parcours complet avec Plotly Mapbox
  - Points de départ (vert) et d'arrivée (rouge)
  - Coloration selon altitude ou vitesse
  - Zoom et navigation interactifs
- **Profil d'élévation** : Graphique altitude/distance avec zones de pente
  - Identification des montées fortes (> 8%)
  - Identification des descentes fortes (< -8%)
  - Statistiques : altitude min/max/moyenne, pente moyenne
- **Analyse allure & FC** : Graphique combiné par distance
  - Allure (min/km) sur axe gauche
  - Fréquence cardiaque (bpm) sur axe droite
  - Synchronisation pour voir corrélation effort/FC
- **Analyse par segments** : Découpage personnalisable de la sortie
  - Taille de segment configurable (0.5 à 5 km)
  - Métriques par segment : allure, FC, dénivelé, pente, vitesse
  - Tableaux et graphiques détaillés
  - Identification des segments les plus difficiles
- **Comparaison sorties similaires** : Recherche automatique
  - Tolérance configurable (±10% à ±50%)
  - Comparaison distance, D+, temps, vitesse, FC
  - Analyse de la progression

### 🏗️ Architecture améliorée

#### Structure modulaire
```
trail-dashboard-v2/
├── app.py                          # Application principale avec navigation
├── utils/
│   ├── training_load.py           # Logique TSS, TRIMP, ATL/CTL
│   └── activity_analysis.py       # Cartes, profils, segments
├── pages/
│   ├── 2_⚡_Charge_entrainement.py  # Page dédiée analyse charge
│   └── 3_🔍_Analyse_detaillee.py   # Page dédiée analyse sorties
└── ...
```

#### Modules réutilisables
- **TrainingLoadCalculator** : Classe complète pour tous les calculs de charge
  - Méthodes : calculate_trimp(), calculate_tss_hr(), calculate_atl_ctl_tsb()
  - Détection surcharge : detect_overreaching(), calculate_ramp_rate()
- **ActivityAnalyzer** : Classe pour analyse détaillée
  - Récupération streams Strava : get_activity_streams()
  - Génération graphiques : create_elevation_profile(), create_pace_hr_analysis(), create_interactive_map()
  - Analyse segments : analyze_segments()
  - Comparaison : compare_similar_activities()

#### Navigation multi-pages
- 🏠 Vue d'ensemble (page d'accueil)
- ⚡ Charge d'entraînement (nouvelle page)
- 🔍 Analyse détaillée (nouvelle page)
- Sidebar avec navigation intuitive

### 📚 Documentation enrichie

#### Nouveaux guides
- **GUIDE_UTILISATION.md** : Guide complet des nouvelles fonctionnalités
  - Explication détaillée de chaque métrique
  - Interprétation des valeurs (TSB, ramp rate, etc.)
  - Cas d'usage pratiques (préparation ultra, détection surcharge)
  - Exemples concrets avec valeurs
  - Formules mathématiques

- **PERSONNALISATION.md** : Extensions et customisation
  - Ajouter zones de fréquence cardiaque
  - Créer objectifs de course
  - Exporter rapports PDF
  - Intégrations tierces (TrainingPeaks, Garmin)
  - Extensions ML (prédiction performances)

#### README mis à jour
- Instructions d'installation clarifiées
- Description complète des nouvelles features
- Troubleshooting étendu
- Roadmap future

### 🐛 Corrections et améliorations

#### Données Strava
- **Ajout de l'ID activité** : Nécessaire pour récupérer les streams détaillés
  - Modification dans `process_activities()` pour inclure 'id'
  - Permet l'analyse détaillée des sorties

#### Performance
- **Cache amélioré** : TTL de 1h pour réduire les appels API Strava
- **Gestion des erreurs** : Try/catch sur toutes les requêtes API
- **Timeouts** : Ajout de timeouts (10-15s) sur les requêtes réseau

#### Expérience utilisateur
- **Messages d'erreur clairs** : Instructions précises en cas de problème
- **Spinners** : Indicateurs de chargement pendant récupération données
- **Tooltips** : Aide contextuelle sur les métriques
- **Formatage amélioré** : Arrondis cohérents, unités claires

### 🔧 Dépendances

#### Nouvelles dépendances
```
numpy==1.26.2  # Calculs scientifiques (EWM, gradients, etc.)
```

#### Dépendances existantes
```
streamlit==1.29.0
pandas==2.1.4
plotly==5.18.0
requests==2.31.0
```

### ⚠️ Breaking Changes

#### Changements dans app.py
- **Navigation par pages** : Structure différente de V1
  - V1 : Tout dans app.py
  - V2 : app.py + pages séparées
  
- **columns_to_keep** : Ajout obligatoire de 'id'
  ```python
  # V1
  columns_to_keep = ['name', 'distance', ...]
  
  # V2 (requis)
  columns_to_keep = ['id', 'name', 'distance', ...]  # 'id' nécessaire !
  ```

#### Migration depuis V1
1. Sauvegarde ton `.streamlit/secrets.toml`
2. Remplace tous les fichiers par la V2
3. Remets ton `secrets.toml`
4. Installe numpy : `pip install numpy==1.26.2`
5. Relance : `streamlit run app.py`

Tes données Strava seront automatiquement rechargées, aucune migration de données nécessaire.

### 🎯 Cas d'usage ajoutés

#### Préparation ultra-trail
- Suivi de la montée progressive de CTL
- Planification du taper (TSB > +20 le jour J)
- Détection de surcharge pendant le build-up

#### Optimisation hebdomadaire
- Distribution du TSS sur la semaine
- Équilibre ATL/CTL
- Placement des jours de repos

#### Analyse post-sortie
- Identification des sections difficiles sur carte
- Compréhension de l'évolution de la FC
- Comparaison avec sorties précédentes similaires

### 🚀 Déploiement

#### Compatible avec
- Streamlit Cloud (gratuit)
- Render.com (configuration fournie)
- Railway.app (configuration fournie)
- Hugging Face Spaces (configuration fournie)
- Docker (Dockerfile et docker-compose.yml fournis)

### 📊 Statistiques du projet

- **Lignes de code** : ~1500 (vs ~300 en V1)
- **Fichiers Python** : 5 (vs 1 en V1)
- **Pages** : 3 (vs 1 en V1)
- **Documentation** : 5 fichiers MD (vs 3 en V1)

---

## Version 1.0.0 - Novembre 2024

### Fonctionnalités initiales
- Connexion Strava OAuth
- Récupération activités via API Strava
- Métriques de base : distance, D+, temps, vitesse, FC
- Graphiques hebdomadaires (distance et D+)
- Distribution des distances
- Analyse % D+ par sortie
- Filtres temporels (30j, 3/6/12 mois, année, tout)
- Tableau des dernières sorties
- Cache des données (1h TTL)
- Déploiement Streamlit Cloud

---

## Roadmap future

### Version 2.1 (Q1 2025)
- [ ] Zones de fréquence cardiaque personnalisées
- [ ] Distribution temps par zone
- [ ] Analyse polarisée (80/20)

### Version 2.2 (Q2 2025)
- [ ] Objectifs de course avec suivi progression
- [ ] Plans d'entraînement
- [ ] Comparaison réalisé vs prévu

### Version 3.0 (Q3 2025)
- [ ] Base de données PostgreSQL
- [ ] API backend FastAPI
- [ ] Cache Redis
- [ ] Multi-utilisateurs
- [ ] Export PDF des rapports

### Version 3.1 (Q4 2025)
- [ ] Machine Learning : prédiction performances
- [ ] Recommandations d'entraînement
- [ ] Intégrations : Garmin, TrainingPeaks, Polar

---

**Bon entraînement avec la V2 ! 🏔️⚡**
