# 🚀 Quick Start Guide

## En 5 minutes chrono !

### 1️⃣ Récupère le code
```bash
git clone https://github.com/TON_USERNAME/trail-dashboard.git
cd trail-dashboard
```

### 2️⃣ Installe Python et dépendances
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ Configure Strava

**A. Crée ton app Strava** (2 min)
1. Va sur https://www.strava.com/settings/api
2. Clique "Create an App"
3. Remplis :
   - **Application Name** : "Mon Dashboard Trail"
   - **Category** : "Other"
   - **Website** : http://localhost
   - **Authorization Callback Domain** : `localhost`
4. Note ton **Client ID** et **Client Secret**

**B. Configure les secrets** (1 min)
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
nano .streamlit/secrets.toml  # ou ton éditeur préféré
```

Mets tes vraies valeurs :
```toml
[strava]
client_id = "123456"           # ← Colle ton Client ID
client_secret = "abcdef123..."  # ← Colle ton Client Secret
redirect_uri = "http://localhost:8501"
```

### 4️⃣ Lance l'app
```bash
streamlit run app.py
```

### 5️⃣ Connecte-toi
1. Clique sur "Se connecter à Strava"
2. Autorise l'application
3. C'est parti ! 🎉

---

## 🌐 Déploiement en ligne (Gratuit)

### Option 1 : Streamlit Cloud (le plus simple)

1. **Push sur GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Déploie sur Streamlit Cloud**
   - Va sur https://streamlit.io/cloud
   - "New app" → Sélectionne ton repo
   - Dans "Advanced settings" → "Secrets" → Colle :
     ```toml
     [strava]
     client_id = "123456"
     client_secret = "abcdef..."
     redirect_uri = "https://TON-APP.streamlit.app"
     ```

3. **Mets à jour Strava**
   - Retourne sur https://www.strava.com/settings/api
   - Change "Authorization Callback Domain" : `ton-app.streamlit.app`

✅ **C'est en ligne !**

---

## 🐳 Avec Docker (optionnel)

```bash
# Build
docker build -t trail-dashboard .

# Run
docker run -p 8501:8501 \
  -e STRAVA_CLIENT_ID="123456" \
  -e STRAVA_CLIENT_SECRET="abc..." \
  trail-dashboard
```

Ou avec docker-compose :
```bash
cp .env.example .env
nano .env  # Complète tes infos
docker-compose up
```

---

## 🆘 Problèmes courants

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Could not connect to Strava"
- Vérifie que tes credentials sont corrects dans `secrets.toml`
- Vérifie que le `redirect_uri` correspond (localhost vs domaine)

### "Authorization callback domain mismatch"
Dans Strava API settings, le domaine doit matcher exactement :
- Local : `localhost`
- Cloud : `ton-app.streamlit.app` (sans http://)

---

## 📊 Ce que tu vas voir

- **Vue d'ensemble** : Sorties, km, D+, temps
- **Graphiques hebdo** : Distance et dénivelé
- **Analyses** : Distribution distances, % D+
- **Historique** : Tes 15 dernières sorties

---

## 🎯 Prochaines étapes

Après avoir pris en main le dashboard :

1. **Personnalise** les métriques qui t'intéressent
2. **Ajoute** des objectifs de volume hebdo
3. **Implémente** le calcul de charge (TSS)
4. **Crée** des zones de fréquence cardiaque

Bon courage pour tes objectifs 2026 ! 🏔️
