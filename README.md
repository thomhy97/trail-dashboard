# 🏔️ Trail Training Dashboard

Dashboard Streamlit pour suivre ton entraînement trail en vue des objectifs 2026. Synchronisation automatique avec Strava.

![Python](https://img.shields.io/badge/python-3.11-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.29-red)

## 📊 Fonctionnalités

- **Connexion Strava OAuth** : Synchronisation automatique de tes activités
- **Métriques clés** : Distance, D+, temps, vitesse, fréquence cardiaque
- **Visualisations** :
  - Évolution hebdomadaire (distance et D+)
  - Distribution des distances
  - Analyse du % de D+ par sortie
- **Historique détaillé** : Tableau des dernières sorties
- **Filtres temporels** : 30 jours, 3/6/12 mois, année en cours

## 🚀 Installation locale

### Prérequis

- Python 3.11+
- Un compte Strava
- Git

### Étapes

1. **Clone le repo**
```bash
git clone https://github.com/TON_USERNAME/trail-dashboard.git
cd trail-dashboard
```

2. **Crée un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installe les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configure Strava API**

- Va sur [Strava API Settings](https://www.strava.com/settings/api)
- Crée une nouvelle application
- Note ton `Client ID` et `Client Secret`
- Dans "Authorization Callback Domain", mets `localhost`

5. **Configure les secrets**

Copie le template et complète avec tes infos :
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Édite `.streamlit/secrets.toml` :
```toml
[strava]
client_id = "123456"  # Ton Client ID Strava
client_secret = "abc123..."  # Ton Client Secret
redirect_uri = "http://localhost:8501"
```

6. **Lance l'application**
```bash
streamlit run app.py
```

L'app s'ouvrira dans ton navigateur à `http://localhost:8501`

## 🌐 Déploiement sur Streamlit Cloud

### Préparation

1. **Push ton code sur GitHub** (sans le fichier secrets.toml !)

2. **Va sur [Streamlit Cloud](https://streamlit.io/cloud)**
   - Connecte-toi avec GitHub
   - Clique sur "New app"
   - Sélectionne ton repo `trail-dashboard`
   - Branche : `main`
   - Fichier : `app.py`

3. **Configure les secrets dans Streamlit Cloud**
   - Dans les paramètres de l'app, section "Secrets"
   - Copie le contenu de ton fichier `secrets.toml` local
   - **Important** : Change le `redirect_uri` :
   ```toml
   [strava]
   client_id = "123456"
   client_secret = "abc123..."
   redirect_uri = "https://TON-APP.streamlit.app"
   ```

4. **Mets à jour Strava API**
   - Retourne dans [Strava API Settings](https://www.strava.com/settings/api)
   - Dans "Authorization Callback Domain", ajoute : `ton-app.streamlit.app`

5. **Déploie !**
   - Clique sur "Deploy"
   - Attends quelques minutes
   - Ton app sera disponible sur `https://ton-app.streamlit.app`

## 🐳 Déploiement avec Docker

### Build l'image
```bash
docker build -t trail-dashboard .
```

### Run le container
```bash
docker run -p 8501:8501 \
  -e STRAVA_CLIENT_ID="ton_client_id" \
  -e STRAVA_CLIENT_SECRET="ton_secret" \
  -e STRAVA_REDIRECT_URI="http://localhost:8501" \
  trail-dashboard
```

Ou avec docker-compose (à créer) :
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STRAVA_CLIENT_ID=${STRAVA_CLIENT_ID}
      - STRAVA_CLIENT_SECRET=${STRAVA_CLIENT_SECRET}
      - STRAVA_REDIRECT_URI=${STRAVA_REDIRECT_URI}
```

## 📈 Évolutions prévues (Phase 2)

- [ ] Base de données PostgreSQL pour persistance
- [ ] API backend FastAPI séparée
- [ ] Calcul de charge d'entraînement (TSS/TRIMP)
- [ ] Modèle ATL/CTL pour fatigue/forme
- [ ] Zones de fréquence cardiaque
- [ ] Comparaison avec plans d'entraînement
- [ ] Export de rapports PDF
- [ ] Prédiction de performances
- [ ] Multi-utilisateurs

## 🛠️ Stack technique

- **Frontend** : Streamlit
- **Visualisation** : Plotly
- **Data** : Pandas
- **API** : Strava OAuth2
- **Déploiement** : Streamlit Cloud / Docker

## 📝 Structure du projet

```
trail-dashboard/
├── app.py                    # Application principale
├── requirements.txt          # Dépendances Python
├── Dockerfile               # Configuration Docker
├── .streamlit/
│   ├── config.toml          # Config Streamlit
│   └── secrets.toml.template # Template secrets
├── .gitignore
└── README.md
```

## 🤝 Contribution

Ce projet est personnel mais ouvert aux suggestions ! N'hésite pas à ouvrir une issue pour proposer des améliorations.

## 📄 Licence

MIT

## 🏃 Auteur

Data scientist passionné de trail, en préparation pour les objectifs 2026 !

---

**Bon entraînement ! 🏔️**
