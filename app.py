import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import os
from database import SupabaseDB

# Configuration de la page
st.set_page_config(
    page_title="Trail Training Dashboard",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser le client Supabase (optionnel)
@st.cache_resource
def init_database():
    """Initialise la connexion à Supabase (une seule fois)"""
    try:
        # Vérifier si les clés Supabase sont présentes
        if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
            return None
        
        # Configurer les variables d'environnement depuis secrets
        os.environ['SUPABASE_URL'] = st.secrets["SUPABASE_URL"]
        os.environ['SUPABASE_KEY'] = st.secrets["SUPABASE_KEY"]
        return SupabaseDB()
    except Exception as e:
        return None

# Initialiser la base de données
db = init_database()

# Afficher le status Supabase une seule fois
if 'supabase_status_shown' not in st.session_state:
    st.session_state.supabase_status_shown = True
    if db is None:
        st.info("ℹ️ Mode sans cache DB (Supabase non configuré). L'app fonctionne normalement.", icon="ℹ️")
    else:
        st.success("✅ Cache DB activé (Supabase connecté)", icon="✅")

# Fonction pour gérer l'authentification Strava
def get_strava_auth_url():
    client_id = st.secrets["STRAVA_CLIENT_ID"]
    redirect_uri = st.secrets.get("STRAVA_REDIRECT_URI", "http://localhost:8501")
    scope = "activity:read_all"
    return f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=force&scope={scope}"

def exchange_token(code):
    """Échange le code d'autorisation contre un token d'accès"""
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": st.secrets["STRAVA_CLIENT_ID"],
            "client_secret": st.secrets["STRAVA_CLIENT_SECRET"],
            "code": code,
            "grant_type": "authorization_code"
        }
    )
    token_data = response.json()
    
    # Sauvegarder l'utilisateur et les tokens en DB (si Supabase disponible)
    if db and 'athlete' in token_data and 'access_token' in token_data:
        athlete = token_data['athlete']
        strava_id = str(athlete['id'])
        
        # Créer/mettre à jour l'utilisateur
        db.create_or_update_user(strava_id, athlete)
        
        # Sauvegarder les tokens
        db.save_strava_token(
            strava_id,
            token_data['access_token'],
            token_data['refresh_token'],
            token_data['expires_at']
        )
        
        # Sauvegarder l'ID utilisateur en session
        st.session_state.strava_id = strava_id
    
    return token_data

def refresh_access_token(refresh_token, strava_id=None):
    """Rafraîchit le token d'accès et met à jour la DB"""
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": st.secrets["STRAVA_CLIENT_ID"],
            "client_secret": st.secrets["STRAVA_CLIENT_SECRET"],
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
    )
    token_data = response.json()
    
    # Mettre à jour les tokens en DB (si disponible)
    if db and strava_id and 'access_token' in token_data:
        db.save_strava_token(
            strava_id,
            token_data['access_token'],
            token_data['refresh_token'],
            token_data['expires_at']
        )
    
    return token_data

def get_activities(access_token, after_timestamp=None, per_page=200):
    """Récupère les activités depuis Strava"""
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": per_page}
    
    if after_timestamp:
        params["after"] = int(after_timestamp)
    
    all_activities = []
    page = 1
    
    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            st.error(f"Erreur API Strava: {response.status_code}")
            break
            
        activities = response.json()
        
        if not activities:
            break
            
        all_activities.extend(activities)
        page += 1
        
        # Limite de sécurité
        if page > 10:
            break
    
    return all_activities

def process_activities(activities):
    """Transforme les données Strava en DataFrame"""
    if not activities:
        return pd.DataFrame()
    
    df = pd.DataFrame(activities)
    
    # Sélection et renommage des colonnes importantes
    # ⚠️ IMPORTANT: Inclure 'id' pour l'analyse détaillée
    columns_to_keep = [
        'id', 'name', 'distance', 'moving_time', 'elapsed_time', 
        'total_elevation_gain', 'type', 'start_date', 
        'average_speed', 'max_speed', 'average_heartrate',
        'max_heartrate', 'suffer_score'
    ]
    
    df = df[[col for col in columns_to_keep if col in df.columns]]
    
    # Conversion des types
    df['start_date'] = pd.to_datetime(df['start_date']).dt.tz_localize(None)  # Retirer le timezone
    df['distance_km'] = df['distance'] / 1000
    df['distance_m'] = df['distance']  # Garder aussi en mètres pour les calculs
    df['elevation_gain_m'] = df['total_elevation_gain']
    df['duration_hours'] = df['moving_time'] / 3600
    df['speed_kmh'] = df['average_speed'] * 3.6
    
    # Calcul du pourcentage de D+ : (D+ en m) / (Distance en m) * 100
    df['deniv_percent'] = (df['elevation_gain_m'] / df['distance_m'] * 100).round(1)
    
    # Filtre sur les activités de course/trail
    run_types = ['Run', 'TrailRun', 'Trail']
    df = df[df['type'].isin(run_types)]
    
    return df

# Interface principale
st.title("🏔️ Trail Training Dashboard V2")
st.markdown("### Suivi d'entraînement avancé pour objectifs 2026")

# Gestion de l'authentification avec cache DB
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.strava_id = None

# Vérification du code d'autorisation dans l'URL
query_params = st.query_params
if 'code' in query_params and not st.session_state.access_token:
    with st.spinner("Connexion à Strava..."):
        token_data = exchange_token(query_params['code'])
        if 'access_token' in token_data:
            st.session_state.access_token = token_data.get('access_token')
            st.session_state.refresh_token = token_data.get('refresh_token')
            st.success("✅ Connecté avec succès !")
            st.rerun()
        else:
            st.error("❌ Erreur de connexion Strava")
            st.stop()

# Sidebar pour l'authentification et les filtres
with st.sidebar:
    st.header("⚙️ Configuration")
    
    if not st.session_state.access_token:
        st.warning("Connectez-vous à Strava pour commencer")
        auth_url = get_strava_auth_url()
        st.markdown(f"[🔗 Se connecter à Strava]({auth_url})")
        st.stop()
    else:
        # Afficher l'utilisateur connecté (si DB disponible)
        if db and st.session_state.strava_id:
            user = db.get_user(st.session_state.strava_id)
            if user:
                col_avatar, col_name = st.columns([1, 3])
                with col_avatar:
                    if user.get('avatar_url'):
                        st.image(user['avatar_url'], width=50)
                with col_name:
                    st.markdown(f"**{user['name']}**")
                    st.caption("Connecté")
            else:
                st.success("✅ Connecté à Strava")
        else:
            st.success("✅ Connecté à Strava")
        
        col_refresh, col_logout = st.columns(2)
        
        with col_refresh:
            if st.button("🔄 Rafraîchir", use_container_width=True):
                # Invalider le cache pour cet utilisateur
                st.cache_data.clear()
                st.rerun()
        
        with col_logout:
            if st.button("🚪 Déconnexion", use_container_width=True):
                st.session_state.access_token = None
                st.session_state.refresh_token = None
                st.session_state.strava_id = None
                st.rerun()
    
    st.divider()
    
    # Filtres temporels
    st.subheader("📅 Période")
    time_range = st.selectbox(
        "Afficher",
        ["30 derniers jours", "3 derniers mois", "6 derniers mois", 
         "Année en cours", "12 derniers mois", "Tout"]
    )
    
    # Calcul de la date de début selon le filtre
    now = datetime.now()
    if time_range == "30 derniers jours":
        after_date = now - timedelta(days=30)
    elif time_range == "3 derniers mois":
        after_date = now - timedelta(days=90)
    elif time_range == "6 derniers mois":
        after_date = now - timedelta(days=180)
    elif time_range == "Année en cours":
        after_date = datetime(now.year, 1, 1)
    elif time_range == "12 derniers mois":
        after_date = now - timedelta(days=365)
    else:
        after_date = None

# Fonction pour charger les données avec cache DB (si disponible)
def load_strava_data_with_cache(access_token, strava_id, after_timestamp):
    """Charge les activités depuis le cache DB ou Strava API"""
    
    # Si Supabase disponible, essayer le cache
    if db and strava_id:
        # 1. Essayer de charger depuis le cache DB
        cached_activities = db.get_strava_activities(strava_id)
        
        if cached_activities is not None:
            st.info("⚡ Données chargées depuis le cache (1h de validité)")
            df = process_activities(cached_activities)
            return df
    
    # 2. Cache expiré/inexistant ou pas de DB → appel API Strava
    if db and strava_id:
        st.info("🔄 Récupération des données depuis Strava...")
    
    activities = get_activities(access_token, after_timestamp)
    
    # 3. Sauvegarder en cache si DB disponible
    if db and strava_id and activities:
        db.save_strava_activities(strava_id, activities)
        st.success("✅ Données mises en cache")
    
    return process_activities(activities)

# Chargement des données
with st.spinner("Chargement des activités..."):
    after_timestamp = after_date.timestamp() if after_date else None
    
    # Vérifier si on a un strava_id
    if st.session_state.strava_id:
        df = load_strava_data_with_cache(
            st.session_state.access_token, 
            st.session_state.strava_id,
            after_timestamp
        )
    else:
        # Fallback sans cache si pas de strava_id
        activities = get_activities(st.session_state.access_token, after_timestamp)
        df = process_activities(activities)

if df.empty:
    st.warning("Aucune activité trouvée pour cette période")
    st.stop()

# Stockage des données dans session_state pour les autres pages
st.session_state.df = df
st.session_state.after_date = after_date

# Page d'accueil - Vue d'ensemble
# Les autres pages (Charge d'entraînement, Analyse détaillée) sont dans le dossier pages/
# et sont automatiquement détectées par Streamlit

# Métriques principales
st.header("📊 Vue d'ensemble")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_runs = len(df)
    st.metric("Sorties", f"{total_runs}")

with col2:
    total_distance = df['distance_km'].sum()
    st.metric("Distance totale", f"{total_distance:.0f} km")

with col3:
    total_elevation = df['elevation_gain_m'].sum()
    st.metric("D+ total", f"{total_elevation:.0f} m")

with col4:
    avg_distance = df['distance_km'].mean()
    st.metric("Distance moy.", f"{avg_distance:.1f} km")

with col5:
    total_time = df['duration_hours'].sum()
    st.metric("Temps total", f"{total_time:.0f}h")

st.divider()

# Graphiques
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Évolution hebdomadaire")
    
    # Regroupement par semaine
    df_weekly = df.copy()
    df_weekly['week'] = df_weekly['start_date'].dt.to_period('W').astype(str)
    
    weekly_stats = df_weekly.groupby('week').agg({
        'distance_km': 'sum',
        'elevation_gain_m': 'sum',
        'duration_hours': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weekly_stats['week'],
        y=weekly_stats['distance_km'],
        name='Distance (km)',
        marker_color='#FC4C02'
    ))
    
    fig.update_layout(
        height=400,
        xaxis_title="Semaine",
        yaxis_title="Distance (km)",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("⛰️ D+ hebdomadaire")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weekly_stats['week'],
        y=weekly_stats['elevation_gain_m'],
        name='D+ (m)',
        marker_color='#00A8E8'
    ))
    
    fig.update_layout(
        height=400,
        xaxis_title="Semaine",
        yaxis_title="Dénivelé (m)",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Analyses détaillées
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Distribution des distances")
    
    # Créer des catégories de distance
    bins = [0, 5, 10, 15, 20, 25, 30, 40, 50, 100]
    labels = ['0-5km', '5-10km', '10-15km', '15-20km', '20-25km', '25-30km', '30-40km', '40-50km', '50km+']
    
    df_temp = df.copy()
    df_temp['distance_category'] = pd.cut(df_temp['distance_km'], bins=bins, labels=labels, right=False)
    
    # Compter par catégorie
    distance_counts = df_temp['distance_category'].value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=distance_counts.index.astype(str),
        values=distance_counts.values,
        hole=0.3,  # Donut chart
        marker=dict(colors=px.colors.sequential.Oranges_r),
        textinfo='label+percent',
        textposition='auto'
    ))
    
    fig.update_layout(
        height=350,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📐 % de D+ par sortie")
    
    fig = px.scatter(
        df,
        x='distance_km',
        y='deniv_percent',
        size='elevation_gain_m',
        hover_data=['name', 'start_date'],
        labels={
            'distance_km': 'Distance (km)',
            'deniv_percent': '% D+ (m/m)',
            'elevation_gain_m': 'D+ (m)'
        },
        color_discrete_sequence=['#00A8E8']
    )
    
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Tableau des dernières activités
st.subheader("🏃 Dernières sorties")

display_df = df[['start_date', 'name', 'distance_km', 'elevation_gain_m', 
                 'duration_hours', 'speed_kmh', 'deniv_percent']].copy()

display_df.columns = ['Date', 'Nom', 'Distance (km)', 'D+ (m)', 
                      'Durée (h)', 'Vitesse (km/h)', '% D+']

display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
display_df = display_df.round(2)
display_df = display_df.sort_values('Date', ascending=False).head(15)

st.dataframe(display_df, use_container_width=True, hide_index=True)

# Footer
st.divider()
st.caption("🏔️ Dashboard V2 créé pour le suivi d'entraînement trail • Données synchronisées depuis Strava")
