import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

# Configuration de la page
st.set_page_config(
    page_title="Trail Training Dashboard",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour gérer l'authentification Strava
def get_strava_auth_url():
    client_id = st.secrets["strava"]["client_id"]
    redirect_uri = st.secrets["strava"]["redirect_uri"]
    scope = "activity:read_all"
    return f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=force&scope={scope}"

def exchange_token(code):
    """Échange le code d'autorisation contre un token d'accès"""
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": st.secrets["strava"]["client_id"],
            "client_secret": st.secrets["strava"]["client_secret"],
            "code": code,
            "grant_type": "authorization_code"
        }
    )
    return response.json()

def refresh_access_token(refresh_token):
    """Rafraîchit le token d'accès"""
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": st.secrets["strava"]["client_id"],
            "client_secret": st.secrets["strava"]["client_secret"],
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
    )
    return response.json()

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

# Gestion de l'authentification
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
    st.session_state.refresh_token = None

# Vérification du code d'autorisation dans l'URL
query_params = st.query_params
if 'code' in query_params and not st.session_state.access_token:
    with st.spinner("Connexion à Strava..."):
        token_data = exchange_token(query_params['code'])
        st.session_state.access_token = token_data.get('access_token')
        st.session_state.refresh_token = token_data.get('refresh_token')
        st.rerun()

# Sidebar pour l'authentification et les filtres
with st.sidebar:
    st.header("⚙️ Configuration")
    
    if not st.session_state.access_token:
        st.warning("Connectez-vous à Strava pour commencer")
        auth_url = get_strava_auth_url()
        st.markdown(f"[🔗 Se connecter à Strava]({auth_url})")
        st.stop()
    else:
        st.success("✅ Connecté à Strava")
        if st.button("🔄 Rafraîchir les données"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("🚪 Se déconnecter"):
            st.session_state.access_token = None
            st.session_state.refresh_token = None
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

# Cache des données pour éviter trop d'appels API
@st.cache_data(ttl=3600)
def load_strava_data(access_token, after_timestamp):
    activities = get_activities(access_token, after_timestamp)
    return process_activities(activities)

# Chargement des données
with st.spinner("Chargement des activités..."):
    after_timestamp = after_date.timestamp() if after_date else None
    df = load_strava_data(st.session_state.access_token, after_timestamp)

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
