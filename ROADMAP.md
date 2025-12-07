# 🗺️ ROADMAP - Trail Dashboard

## 📅 Version 2.0 - Décembre 2024 ✅ TERMINÉ

### 🎯 Objectifs initiaux
Créer un dashboard complet d'analyse d'entraînement trail avec :
- Analyse de charge d'entraînement (TSS, TRIMP, ATL/CTL/TSB)
- Analyse détaillée des sorties (cartes, profils, segments)
- Interface multi-pages intuitive

---

## ✅ Fonctionnalités implémentées

### 🏠 Page 1 : Vue d'ensemble

#### Métriques principales
- ✅ Nombre total de sorties
- ✅ Distance totale cumulée
- ✅ Dénivelé positif total
- ✅ Distance moyenne par sortie
- ✅ Temps total d'entraînement

#### Graphiques hebdomadaires
- ✅ Évolution de la distance par semaine (bar chart)
- ✅ Évolution du D+ par semaine (bar chart)
- ✅ Regroupement automatique par semaine

#### Analyses détaillées
- ✅ **Distribution des distances** (Pie Chart / Donut)
  - Catégories : 0-5km, 5-10km, 10-15km, 15-20km, 20-25km, 25-30km, 30-40km, 40-50km, 50km+
  - Affichage : Labels + pourcentages
  - Palette : Dégradé orange (cohérent thème Strava)
  
- ✅ **% de D+ par sortie** (Scatter plot)
  - Axe X : Distance (km)
  - Axe Y : % D+ (calculé correctement : D+ en m / Distance en m * 100)
  - Taille des bulles : Dénivelé total
  - Correction mathématique appliquée (était incorrect en V1)

#### Tableau des sorties
- ✅ 15 dernières activités
- ✅ Colonnes : Date, Nom, Distance, D+, Durée, Vitesse, % D+
- ✅ Tri par date décroissante

#### Filtres temporels
- ✅ 30 derniers jours
- ✅ 3 derniers mois
- ✅ 6 derniers mois
- ✅ 12 derniers mois
- ✅ Année en cours
- ✅ Toutes les données

---

### ⚡ Page 2 : Charge d'entraînement

#### Configuration personnalisée
- ✅ FC Max configurable (par défaut : 190 bpm)
- ✅ FC Repos configurable (par défaut : 50 bpm)
- ✅ Genre (M/F) pour calcul TRIMP
- ✅ Période d'analyse (3/6/12 mois, tout)

#### Métriques de charge actuelles
- ✅ **ATL (Acute Training Load)** - Fatigue sur 7 jours
  - Moyenne mobile exponentielle (α = 0.25)
  - Représente la fatigue récente
  
- ✅ **CTL (Chronic Training Load)** - Forme sur 42 jours
  - Moyenne mobile exponentielle (α = 0.047)
  - Représente la capacité d'entraînement
  
- ✅ **TSB (Training Stress Balance)** - Fraîcheur
  - Formule : TSB = CTL - ATL
  - Interprétation automatique avec recommandations :
    - TSB > +25 : Très frais, prêt pour course
    - TSB +5 à +25 : Frais, bon équilibre
    - TSB -10 à +5 : Zone optimale pour progresser
    - TSB -30 à -10 : Fatigué, attention
    - TSB < -30 : Surcharge, repos nécessaire
  
- ✅ **TSS hebdomadaire** - Total des 7 derniers jours

#### Graphiques d'évolution
- ✅ **Graphique ATL/CTL/TSB combiné**
  - ATL en rouge (zone remplie)
  - CTL en bleu (zone remplie)
  - TSB en barres (vert/orange/rouge selon valeur)
  - Ligne de référence TSB = 0
  - Hover unifié sur l'axe X

- ✅ **TSS par semaine** (Bar chart)
  - Agrégation hebdomadaire automatique
  - Échelle de couleur rouge selon intensité

- ✅ **TRIMP par semaine** (Bar chart)
  - Agrégation hebdomadaire automatique
  - Échelle de couleur bleue selon intensité

#### Analyse de progression
- ✅ **Ramp Rate** (Taux de progression CTL)
  - Calcul sur fenêtre glissante de 7 jours
  - Zones de sécurité visuelles :
    - Vert : -5 à +5 CTL/semaine (sécurisé)
    - Orange : +5 à +8 CTL/semaine (progression rapide)
    - Rouge : > +8 CTL/semaine (danger blessure)
  - Annotations automatiques

#### Détection de surcharge
- ✅ **Alertes automatiques** quand :
  - TSB < -30 (fatigue excessive)
  - ATL anormalement élevée par rapport à CTL
- ✅ Affichage de la date et du message d'alerte
- ✅ Limite aux 5 dernières alertes

#### Tableau des dernières sorties avec charge
- ✅ 10 dernières activités
- ✅ Colonnes : Date, Nom, Distance, D+, Durée, TSS, TRIMP
- ✅ Valeurs arrondies pour lisibilité

#### Formules implémentées

**TSS (Training Stress Score) :**
```
IF = FC_avg / FC_threshold
TSS = duration_hours × IF² × 100

Avec fallback si pas de FC :
TSS_estimé = duration_hours × intensity_factor × 100
```

**TRIMP (Training Impulse - Méthode Banister) :**
```
HR_ratio = (FC_avg - FC_repos) / (FC_max - FC_repos)
y = 1.92 (homme) ou 1.67 (femme)
TRIMP = duration_min × HR_ratio × 0.64 × e^(y × HR_ratio)
```

**ATL (Acute Training Load) :**
```
α = 2 / (7 + 1) = 0.25
ATL(n) = ATL(n-1) + α × (TSS(n) - ATL(n-1))
```

**CTL (Chronic Training Load) :**
```
α = 2 / (42 + 1) ≈ 0.047
CTL(n) = CTL(n-1) + α × (TSS(n) - CTL(n-1))
```

**TSB (Training Stress Balance) :**
```
TSB = CTL - ATL
```

**Ramp Rate :**
```
RampRate(semaine) = (CTL_fin_semaine - CTL_début_semaine) / 7 jours
```

---

### 🔍 Page 3 : Analyse détaillée des sorties

#### Sélection d'activité
- ✅ Liste déroulante avec format : "YYYY-MM-DD - Nom (X.X km, XXXm D+)"
- ✅ Métriques de base affichées : Distance, D+, Durée, Vitesse moy., FC moy.

#### Onglet 1 : Carte GPS 🗺️
- ✅ **Carte interactive Plotly Mapbox**
  - Points colorés selon altitude (gradient Viridis)
  - Mode markers avec échelle de couleur
  - Point de départ (vert) et d'arrivée (rouge)
  - Zoom automatique sur le parcours
  - Hover : Latitude, Longitude, Altitude
  - Fond de carte : OpenStreetMap

#### Onglet 2 : Profil d'élévation ⛰️
- ✅ **Graphique altitude vs distance**
  - Zone remplie sous la courbe
  - Identification automatique des zones :
    - Montées fortes (> 8%) en rouge
    - Descentes fortes (< -8%) en bleu
  - Hover : Distance, Altitude, Pente
  
- ✅ **Statistiques d'élévation**
  - Altitude min/max/moyenne
  - Pente moyenne en montée
  - Calcul de gradient avec numpy

#### Onglet 3 : Allure & FC 📊
- ✅ **Graphique double axe**
  - Axe gauche : Allure (min/km)
  - Axe droit : Fréquence cardiaque (bpm)
  - Synchronisation des deux courbes par distance
  - Détection de patterns de fatigue
  
- ✅ **Statistiques**
  - Colonne 1 : Allure min/max/médiane
  - Colonne 2 : FC min/max/médiane
  - Filtrage des valeurs aberrantes

#### Onglet 4 : Analyse par segments 🔬
- ✅ **Découpage personnalisable**
  - Slider : 0.5 à 5 km par segment
  - Calculs par segment :
    - Distance exacte
    - Allure moyenne (min/km)
    - FC moyenne (bpm)
    - Dénivelé positif
    - Pente moyenne (%)
    - Vitesse moyenne (km/h)

- ✅ **Graphiques par segment**
  - Subplot 1 : Allure par segment (bar chart orange)
  - Subplot 2 : FC par segment (bar chart rouge)
  - Identification des segments difficiles

- ✅ **Tableau détaillé**
  - Toutes les métriques par segment
  - Valeurs arrondies
  - Export possible

#### Comparaison avec sorties similaires
- ✅ **Recherche automatique**
  - Tolérance configurable (10% à 50%)
  - Critères : Distance ± tolérance ET D+ ± tolérance
  - Exclusion de l'activité sélectionnée

- ✅ **Tableau des sorties similaires**
  - Top 5 sorties les plus proches
  - Date, Nom, Distance, D+, Durée, Vitesse

- ✅ **Comparaison détaillée**
  - Sélection d'une sortie à comparer
  - Métriques côte à côte avec deltas :
    - Distance (km) avec différence
    - D+ (m) avec différence
    - Durée (h) avec différence (inversé : moins = mieux)
  - Analyse de progression

---

## 🔧 Corrections techniques appliquées

### Bug fixes (6 correctifs majeurs)

1. ✅ **ImportError : show_training_load_page**
   - Problème : Import manuel des pages Streamlit
   - Solution : Suppression - Streamlit détecte automatiquement les pages/
   - Fichier : app.py

2. ✅ **IndentationError ligne 206**
   - Problème : Indentation incorrecte après suppression du routing manuel
   - Solution : Correction de toutes les indentations
   - Fichier : app.py

3. ✅ **IndentationError dans pages/**
   - Problème : Indentation inconsistante après refactoring
   - Solution : Réécriture complète des pages
   - Fichiers : pages/2_*.py, pages/3_*.py

4. ✅ **TypeError : timezone datetime**
   - Problème : Comparaison entre datetime UTC (Strava) et datetime naïve (Python)
   - Solution : `.dt.tz_localize(None)` pour retirer le timezone
   - Fichier : app.py ligne 102

5. ✅ **TypeError : format Series**
   - Problème : f-string sur Series pandas (pas supporté)
   - Solution : Utilisation de `.apply(lambda x: f"{x:.1f}")`
   - Fichier : pages/3_*.py ligne 45

6. ✅ **ValueError : Plotly Scattermapbox**
   - Problème : `line.color` avec liste + colorscale (non supporté)
   - Solution : Utilisation de `mode='markers'` avec `marker.color`
   - Fichier : utils/activity_analysis.py ligne 234

### Améliorations mathématiques

7. ✅ **Correction calcul % D+**
   - Problème : Comparaison D+ (mètres) / Distance (kilomètres) = valeurs x1000 trop élevées
   - Solution : Calcul correct (D+ en m) / (Distance en m) * 100
   - Impact : Valeurs réalistes (5% au lieu de 5000%)
   - Fichier : app.py ligne 103-109

### Améliorations UX

8. ✅ **Distribution distances en Donut Chart**
   - Changement : Histogramme → Pie Chart (donut)
   - Avantages : Plus visuel, pourcentages clairs, palette orange cohérente
   - Fichier : app.py

---

## 🏗️ Architecture technique

### Structure modulaire
```
trail-dashboard-v2/
├── app.py                          # Page d'accueil + navigation
├── utils/                          # Modules métier
│   ├── training_load.py           # Calculs TSS/TRIMP/ATL/CTL
│   └── activity_analysis.py       # Cartes/profils/segments
├── pages/                          # Pages Streamlit
│   ├── 2_⚡_Charge_entrainement.py
│   └── 3_🔍_Analyse_detaillee.py
└── .streamlit/
    ├── config.toml                # Thème Strava orange
    └── secrets.toml.template      # Template secrets
```

### Classes principales

**TrainingLoadCalculator** (`utils/training_load.py`)
- Méthodes : `calculate_trimp()`, `calculate_tss_hr()`, `calculate_tss_simplified()`
- Analyse : `calculate_atl_ctl_tsb()`, `detect_overreaching()`, `calculate_ramp_rate()`
- Interprétation : `interpret_tsb()`

**ActivityAnalyzer** (`utils/activity_analysis.py`)
- Récupération : `get_activity_streams()`
- Visualisations : `create_elevation_profile()`, `create_pace_hr_analysis()`, `create_interactive_map()`
- Analyse : `analyze_segments()`, `compare_similar_activities()`

### Gestion des données

**Flux de données :**
1. Connexion Strava OAuth
2. Récupération activités via API
3. Stockage dans `st.session_state.df`
4. Accès depuis toutes les pages
5. Cache avec TTL de 1h

**Colonnes DataFrame :**
- Base : id, name, distance, moving_time, total_elevation_gain, start_date
- Calculées : distance_km, distance_m, elevation_gain_m, duration_hours, speed_kmh, deniv_percent
- Charge : tss, trimp, atl, ctl, tsb

---

## 📊 Statistiques du projet

### Code
- **Lignes totales** : ~2500
- **Fichiers Python** : 5
- **Pages Streamlit** : 3
- **Modules** : 2

### Fonctionnalités
- **Métriques calculées** : 15+
- **Graphiques** : 12+
- **Visualisations interactives** : 10+

### Documentation
- **Fichiers MD** : 8
- **Pages totales** : ~40
- **Guides** : 5

---

## 🚀 Déploiement

### Plateformes supportées
- ✅ **Streamlit Cloud** (recommandé, gratuit)
- ✅ **Render.com** (config fournie)
- ✅ **Railway.app** (config fournie)
- ✅ **Hugging Face Spaces** (config fournie)
- ✅ **Docker** (Dockerfile + docker-compose)

### Dépendances
```
streamlit==1.29.0
pandas==2.1.4
plotly==5.18.0
requests==2.31.0
numpy==1.26.2
```

---

## 📚 Documentation fournie

1. **README.md** - Documentation technique complète
2. **CHANGELOG.md** - Liste détaillée des changements
3. **MIGRATION.md** - Guide de migration V1 → V2
4. **GIT_COMMANDS.md** - Commandes Git pour la migration
5. **GUIDE_UTILISATION.md** - Guide utilisateur complet (TSS/ATL/CTL)
6. **STATUT_CORRECTIFS.md** - Liste des bugs corrigés
7. **VERSION_FINALE.md** - Résumé version finale
8. **ROADMAP.md** - Ce fichier

---

## 🎯 Objectifs atteints

### Fonctionnalités principales
- ✅ Dashboard multi-pages fonctionnel
- ✅ Analyse de charge complète (TSS/TRIMP/ATL/CTL/TSB)
- ✅ Analyse détaillée des sorties (cartes, profils, segments)
- ✅ Détection automatique de surcharge
- ✅ Comparaison entre sorties
- ✅ Visualisations interactives de qualité

### Qualité du code
- ✅ Architecture modulaire
- ✅ Code bien structuré et commenté
- ✅ Gestion d'erreurs robuste
- ✅ Cache optimisé
- ✅ Formules mathématiques correctes

### Documentation
- ✅ Guide utilisateur complet
- ✅ Guide de migration détaillé
- ✅ Documentation technique
- ✅ Troubleshooting complet

### Déploiement
- ✅ Prêt pour production
- ✅ Multi-plateformes
- ✅ Docker ready
- ✅ Configurations fournies

---

## 🔮 Futures améliorations (V2.1+)

### Court terme (V2.1 - Q1 2025)
- [ ] Zones de fréquence cardiaque personnalisées (Z1-Z5)
- [ ] Distribution du temps par zone FC
- [ ] Analyse polarisée 80/20
- [ ] Export des graphiques en PNG/PDF
- [ ] Mode sombre / clair

### Moyen terme (V2.2 - Q2 2025)
- [ ] Objectifs de course avec suivi de progression
- [ ] Plans d'entraînement personnalisés
- [ ] Comparaison réalisé vs prévu
- [ ] Notifications d'alertes
- [ ] Tableau de bord personnalisable

### Long terme (V3.0 - Q3 2025)
- [ ] Base de données PostgreSQL
- [ ] API backend FastAPI
- [ ] Cache Redis
- [ ] Multi-utilisateurs avec authentification
- [ ] Export PDF complet des rapports
- [ ] Intégration email (alertes automatiques)

### Très long terme (V3.1 - Q4 2025)
- [ ] Machine Learning : prédiction de performances
- [ ] Recommandations d'entraînement IA
- [ ] Intégrations : Garmin Connect, TrainingPeaks, Polar Flow
- [ ] Analyse de récupération (HRV, sommeil)
- [ ] Progressive Web App (PWA) mobile
- [ ] Partage social et challenges

---

## 🏆 Conclusion

**Version 2.0 : SUCCÈS COMPLET** ✅

- Tous les objectifs atteints
- Dashboard fonctionnel et stable
- Code de qualité professionnelle
- Documentation exhaustive
- Prêt pour production

**Projet livré clé en main pour objectifs trail 2025 ! 🏔️⚡**

---

*Dernière mise à jour : 7 décembre 2024*
*Version : 2.0 FINALE*
*Status : ✅ Production Ready*
