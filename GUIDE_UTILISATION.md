# 📖 Guide d'utilisation - Features avancées

## ⚡ Analyse de charge d'entraînement

### Qu'est-ce que c'est ?

La charge d'entraînement permet de quantifier l'intensité de tes sorties et de suivre ta fatigue/forme sur le long terme.

### Métriques principales

#### 1. TSS (Training Stress Score)
**Ce que c'est :**
- Score d'intensité d'une sortie (0-300+)
- 100 TSS = 1h à ton seuil lactique

**Valeurs typiques :**
- 🟢 Sortie facile (endurance) : 20-50 TSS
- 🟡 Sortie modérée : 50-100 TSS
- 🟠 Sortie dure (tempo/fractionné) : 100-200 TSS
- 🔴 Sortie très dure (course) : 200-400 TSS

**Comment c'est calculé :**
```python
TSS = (durée_h × (FC_moy / FC_seuil)²) × 100
```

Si tu n'as pas de cardio, estimation selon :
- Durée + intensité perçue (easy/moderate/hard)
- Distance + dénivelé

#### 2. TRIMP (Training Impulse)
**Ce que c'est :**
- Alternative au TSS, basé sur FC
- Méthode Banister : prend en compte la réponse cardiaque non-linéaire

**Valeurs typiques :**
- Sortie 1h facile : ~40-60 TRIMP
- Sortie 1h modérée : ~80-120 TRIMP  
- Sortie 1h dure : ~150-250 TRIMP

#### 3. ATL (Acute Training Load)
**Ce que c'est :**
- Moyenne mobile exponentielle du TSS sur 7 jours
- Représente ta **fatigue récente**

**Interprétation :**
- ATL faible (<50) : Peu de fatigue, sous-entraînement possible
- ATL modérée (50-100) : Bon équilibre
- ATL élevée (>100) : Fatigue importante

#### 4. CTL (Chronic Training Load)
**Ce que c'est :**
- Moyenne mobile exponentielle du TSS sur 42 jours
- Représente ta **forme générale** / capacité d'entraînement

**Interprétation :**
- CTL faible (<40) : Débutant ou reprise
- CTL modérée (40-80) : Coureur régulier
- CTL élevée (80-120) : Coureur entraîné
- CTL très élevée (>120) : Athlète de haut niveau

**Exemple concret :**
Si ton CTL = 70, tu es capable de supporter ~70 TSS/jour en moyenne sans te surcharger.

#### 5. TSB (Training Stress Balance)
**Ce que c'est :**
- **TSB = CTL - ATL**
- Indique ton niveau de **fraîcheur / récupération**

**Interprétation détaillée :**

| TSB | État | Recommandation |
|-----|------|----------------|
| > +25 | 🟢 Très frais | Parfait pour une course importante |
| +10 à +25 | 🟢 Frais | Prêt pour un gros effort |
| +5 à +10 | 🟡 Bien récupéré | Continue comme ça |
| -5 à +5 | 🟠 Équilibré | **Zone optimale pour progresser** |
| -10 à -5 | 🟠 Légèrement fatigué | Normal en période d'entraînement |
| -20 à -10 | 🔴 Fatigué | Attention, semaine plus légère conseillée |
| -30 à -20 | 🔴 Très fatigué | Réduire la charge, repos nécessaire |
| < -30 | 🔴 Surcharge | ⚠️ STOP ! Risque de blessure/surentraînement |

**Exemple pratique :**
```
Situation : CTL = 70, ATL = 85, donc TSB = -15

Interprétation :
- Ta forme (CTL) est bonne à 70
- Mais tu as beaucoup chargé cette semaine (ATL = 85)
- Tu es fatigué (TSB = -15)
- → Semaine prochaine, allège !
```

### Comment utiliser ces métriques ?

#### 📅 Planification d'une course

**6 semaines avant :**
- Augmente progressivement ta CTL
- TSB peut être négatif (-5 à -15)
- C'est le moment de charger !

**3 semaines avant :**
- Maintiens ta CTL haute
- Commence à surveiller ton TSB

**2 semaines avant (tapering) :**
- Réduis le volume (ATL baisse)
- CTL reste haute
- TSB commence à remonter

**1 semaine avant :**
- Volume très réduit
- TSB doit être > +10 pour être frais

**Jour J :**
- TSB idéal : +15 à +25
- Tu es frais mais garde ta forme !

#### ⚠️ Détection de surcharge

Le dashboard t'alerte si :

1. **TSB < -30 pendant plusieurs jours**
   - Risque : Surentraînement
   - Action : Repos immédiat, semaine de récupération

2. **ATL > 90e percentile + TSB < -10**
   - Risque : Charge trop élevée
   - Action : Réduire intensité/volume

3. **Ramp Rate > 8 CTL/semaine**
   - Risque : Progression trop rapide
   - Action : Ralentir l'augmentation

### Taux de progression (Ramp Rate)

**Ce que c'est :**
- Variation de ta CTL par semaine
- Indique si tu progresses trop vite

**Règles d'or :**
- ✅ **+5 CTL/semaine** : Progression optimale
- ⚠️ **+8 CTL/semaine** : Limite haute
- ❌ **> +10 CTL/semaine** : Trop rapide ! Risque blessure

**Exemple :**
```
Semaine 1 : CTL = 60
Semaine 2 : CTL = 67
Ramp rate = +7 points/semaine → OK mais à la limite
```

---

## 🔍 Analyse détaillée des sorties

### Carte interactive

**Ce que tu vois :**
- Ton parcours GPS complet
- Points de départ (vert) et d'arrivée (rouge)
- Couleur selon altitude ou vitesse

**Utilisation :**
- Zoom pour voir les détails
- Survole pour voir lat/lon exactes
- Vérifie que ton GPS a bien tracké

### Profil d'élévation

**Ce que tu vois :**
- Altitude en fonction de la distance
- Points rouges : montées > 8%
- Points bleus : descentes > 8%

**Analyse :**
- Identifie les sections difficiles
- Comprends où tu as perdu/gagné du temps
- Compare la répartition du D+

**Métriques calculées :**
- Altitude min/max/moyenne
- Pente moyenne des montées
- Distribution des pentes

### Allure & FC par segment

**Ce que tu vois :**
- Courbe d'allure (min/km)
- Courbe de FC (bpm)
- Corrélation entre les deux

**Analyse :**
- 📊 **Allure stable + FC stable** : Endurance pure
- 📈 **FC monte mais allure baisse** : Fatigue ou terrain difficile
- 📉 **Allure monte + FC baisse** : Descente récup
- ⚡ **Pics de FC + allure rapide** : Fractionnés ou montées dures

**Exemple d'interprétation :**
```
Km 0-5 : Allure 6:00/km, FC 140 → Échauffement OK
Km 5-10 : Allure 6:30/km, FC 165 → Montée, effort cohérent
Km 10-15 : Allure 5:00/km, FC 130 → Descente, récup active
Km 15-20 : Allure 7:00/km, FC 160 → Fatigue (FC haute pour allure lente)
```

### Analyse par segments

**Ce que c'est :**
- Découpage de ta sortie en tronçons (ex: 1 km)
- Calcul des métriques par segment

**Métriques par segment :**
- Allure moyenne
- FC moyenne/max
- Dénivelé
- Pente moyenne
- Vitesse

**Utilisation :**
1. Règle la taille des segments (0.5 à 5 km)
2. Identifie tes segments :
   - Les plus rapides
   - Les plus durs (FC haute)
   - Les plus techniques (pente forte)
3. Compare avec sorties similaires

**Exemple :**
```
Segment 5-6 km :
- Allure : 8:30/km
- FC : 175 bpm
- Pente : +12%
→ Montée technique dure, cohérent
```

### Comparaison avec sorties similaires

**Comment ça marche :**
1. Sélectionne une tolérance (ex: ±20%)
2. Le dashboard trouve des sorties avec :
   - Distance similaire (±20%)
   - D+ similaire (±20%)

**Ce que tu compares :**
- ⏱️ Temps : As-tu progressé ?
- 💓 FC moyenne : Même effort pour moins de fatigue ?
- 🏃 Vitesse : Plus rapide à FC égale ?

**Exemple d'analyse :**
```
Sortie A (aujourd'hui) : 15 km, 800m D+, 2h15, FC 155
Sortie B (il y a 2 mois) : 15 km, 820m D+, 2h30, FC 162

Analyse :
✅ Temps : -15 min → Progression !
✅ FC : -7 bpm → Meilleure économie de course
→ Tu as progressé sur ce parcours type 🎉
```

---

## 💡 Cas d'usage pratiques

### 1. Préparer un ultra-trail

**Objectif : UTMB (170 km, 10000m D+) dans 4 mois**

**Semaine 1-8 : Build-up**
- Augmente CTL progressivement : +5/semaine
- TSB entre -5 et +5
- Surveille le ramp rate

**Semaine 9-12 : Pic de volume**
- CTL autour de 80-100
- Sorties longues 30-50 km
- TSB peut descendre à -10/-15

**Semaine 13-14 : Taper**
- Volume -30% puis -50%
- CTL reste haute
- TSB remonte à +15/+20

**Semaine 15 : Course**
- TSB > +20
- Une sortie courte 2 jours avant
- Prêt à tout donner ! 🏔️

### 2. Détecter une baisse de forme

**Signes d'alerte :**
```
Sortie habituelle 10 km, 500m D+
Avant : 1h15, FC 150, TSS 60
Maintenant : 1h25, FC 165, TSS 80

→ FC plus haute pour performance moindre
→ Possible :
  - Fatigue accumulée (regarde TSB)
  - Début de surentraînement
  - Maladie qui couve
  
Action :
1. Check TSB (< -20 ? Repos !)
2. Semaine récup
3. Si persiste : consulte médecin
```

### 3. Optimiser un entraînement hebdo

**Exemple semaine équilibrée (CTL cible : 60)**

| Jour | Type | TSS | Cumul ATL |
|------|------|-----|-----------|
| Lun | Repos | 0 | - |
| Mar | Endurance 1h | 45 | - |
| Mer | Fractionné court | 65 | - |
| Jeu | Repos | 0 | - |
| Ven | Endurance 45min | 35 | - |
| Sam | Sortie longue 2h30 | 120 | - |
| Dim | Récup 30min | 20 | ~60 |

**TSS total semaine :** ~285
**ATL fin de semaine :** ~60
**TSB :** Neutre si CTL = 60

---

## 🎓 Pour aller plus loin

### Lectures recommandées

- "Training and Racing with a Power Meter" (Coggan & Allen)
- "The Science of Running" (Steve Magness)
- Concepts TrainingPeaks : https://www.trainingpeaks.com/learn/

### Formules mathématiques

**TSS :**
```
TSS = (t × NP × IF) / (FTP × 3600) × 100

Où :
- t = durée en secondes
- NP = Normalized Power (ou équivalent FC)
- IF = Intensity Factor = NP / FTP
- FTP = Functional Threshold Power (ou FC seuil)
```

**ATL/CTL (EWM) :**
```
ATL(n) = ATL(n-1) + α_ATL × (TSS(n) - ATL(n-1))
CTL(n) = CTL(n-1) + α_CTL × (TSS(n) - CTL(n-1))

Où :
- α_ATL = 2 / (7 + 1) = 0.25
- α_CTL = 2 / (42 + 1) ≈ 0.047
```

---

**Bon entraînement intelligent ! 🧠🏃‍♂️**
