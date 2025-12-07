# 🏔️ Trail Training Dashboard V2

Dashboard Streamlit avancé pour suivre ton entraînement trail avec analyse de charge (TSS, TRIMP, ATL/CTL) et analyse détaillée des sorties.

## 🆕 Nouvelles fonctionnalités V2

### ⚡ Analyse de charge d'entraînement
- **TSS (Training Stress Score)** : Score d'intensité par sortie
- **TRIMP** : Charge d'entraînement basée sur la FC
- **ATL/CTL/TSB** : Modèle de fatigue/forme/fraîcheur
  - ATL (Acute Training Load) : Fatigue sur 7 jours
  - CTL (Chronic Training Load) : Forme sur 42 jours
  - TSB (Training Stress Balance) : Équilibre forme/fatigue
- **Détection de surcharge** : Alertes automatiques
- **Taux de progression (Ramp Rate)** : Évolution de la CTL

### 🔍 Analyse détaillée des sorties
- **Carte interactive** : Visualisation du parcours GPS
- **Profil d'élévation** : Avec zones de pente
- **Allure & FC par segment** : Analyse détaillée
- **Comparaison entre sorties** : Trouve des sorties similaires

## 📊 Fonctionnalités V1 (conservées)

- Connexion Strava OAuth
- Métriques clés : Distance, D+, temps, vitesse, FC
- Graphiques hebdomadaires
- Distribution des distances
- Filtres temporels
- Historique des sorties

## 🚀 Installation

### Prérequis

- Python 3.11+
- Compte Strava avec API configurée
- Git

### Configuration rapide

1. **Clone le repo**
```bash
git clone https://github.com/TON_USERNAME/trail-dashboard-v2.git
cd trail-dashboard-v2
```

2. **Installe les dépendances**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Strava API**

- Va sur https://www.strava.com/settings/api
- Crée une app (si pas déjà fait)
- Note Client ID et Client Secret

4. **Configure les secrets**

Copie et complète `.streamlit/secrets.toml.template` :

```toml
[strava]
client_id = "123456"
client_secret = "abc123..."
redirect_uri = "http://localhost:8501"
```

5. **Lance l'app**
```bash
streamlit run app.py
```

## 📱 Structure du projet

```
trail-dashboard-v2/
├── app.py                          # App principale avec navigation
├── requirements.txt                # Dépendances
├── utils/
│   ├── training_load.py           # Calculs TSS, TRIMP, ATL/CTL
│   └── activity_analysis.py       # Analyse détaillée sorties
├── pages/
│   ├── 2_⚡_Charge_entrainement.py  # Page charge
│   └── 3_🔍_Analyse_detaillee.py   # Page analyse détaillée
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.template
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🎯 Utilisation

### Page d'accueil
- Vue d'ensemble de tes entraînements
- Graphiques hebdomadaires
- Distribution des distances
- Dernières sorties

### ⚡ Charge d'entraînement
1. Configure ta FC max et FC repos
2. Visualise ton ATL/CTL/TSB
3. Surveille les alertes de surcharge
4. Analyse ton taux de progression

**Interprétation du TSB :**
- 🟢 TSB > +5 : Frais, récupéré
- 🟠 TSB -10 à +5 : Zone optimale
- 🔴 TSB < -30 : Surcharge, repos nécessaire !

### 🔍 Analyse détaillée
1. Sélectionne une sortie
2. Visualise :
   - Carte interactive du parcours
   - Profil d'élévation avec zones de pente
   - Allure et FC par segment
3. Compare avec des sorties similaires

## 🔧 Configuration avancée

### Personnalisation des zones FC

Modifie dans `utils/training_load.py` :

```python
calculator = TrainingLoadCalculator(
    fc_max=190,      # Ta FC max
    fc_repos=50,     # Ta FC repos
    seuil_fc=165     # Ton seuil lactique (optionnel)
)
```

### Calcul du TSS

Le TSS est calculé selon :
- **Avec FC** : Basé sur l'Intensity Factor (IF = FC_moy / FC_seuil)
- **Sans FC** : Estimation selon durée et intensité perçue

### Modèle ATL/CTL

- **ATL** : EWM (Exponential Weighted Mean) sur 7 jours
- **CTL** : EWM sur 42 jours
- **TSB** : CTL - ATL

## 📈 Prochaines évolutions

- [ ] Zones de fréquence cardiaque personnalisées
- [ ] Plans d'entraînement avec comparaison
- [ ] Prédiction de performances
- [ ] Export PDF des rapports
- [ ] Base de données PostgreSQL
- [ ] API backend FastAPI
- [ ] Multi-utilisateurs

## 🐛 Troubleshooting

### "Module not found: utils.training_load"

Vérifie que tu es dans le bon dossier :
```bash
cd trail-dashboard-v2
python -c "import sys; print(sys.path)"
```

### "ID Strava manquant"

Assure-toi que `'id'` est dans la liste `columns_to_keep` dans `app.py` ligne ~70

### Données de streams non disponibles

Certaines vieilles activités n'ont pas de streams détaillés. Essaie avec une sortie récente.

## 📄 Licence

MIT

## 🏃 Auteur

Data scientist passionné de trail, en préparation pour les objectifs 2026 !

---

**Bon entraînement et bonne analyse ! 🏔️⚡**
