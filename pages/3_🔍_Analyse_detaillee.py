"""
Page d'analyse détaillée des sorties
"""

import streamlit as st
import pandas as pd
import sys
sys.path.append('..')

from utils.activity_analysis import ActivityAnalyzer, get_similar_activities

st.set_page_config(
    page_title="Analyse détaillée",
    page_icon="🔍",
    layout="wide"
)

# Vérifier que l'utilisateur est connecté et a des données
if 'access_token' not in st.session_state or not st.session_state.access_token:
    st.error("⚠️ Tu dois d'abord te connecter à Strava depuis la page d'accueil")
    st.stop()

if 'df' not in st.session_state or st.session_state.df.empty:
    st.error("⚠️ Aucune donnée disponible. Va d'abord sur la page d'accueil.")
    st.stop()

df = st.session_state.df
access_token = st.session_state.access_token

st.header("🔍 Analyse détaillée des sorties")

if df.empty:
    st.warning("Aucune activité disponible")
    st.stop()

# Sélection de l'activité
st.subheader("Sélectionne une sortie à analyser")

# Préparer la liste des activités
df_display = df.copy()
df_display['display_name'] = (
    df_display['start_date'].dt.strftime('%Y-%m-%d') + 
    " - " + 
    df_display['name'] + 
    " (" + 
    df_display['distance_km'].apply(lambda x: f"{x:.1f}") + " km, " +
    df_display['elevation_gain_m'].apply(lambda x: f"{x:.0f}") + "m D+)"
)

# Sélecteur
selected_activity_name = st.selectbox(
    "Activité",
    options=df_display['display_name'].tolist(),
    index=0
)

# Récupération de l'activité sélectionnée
selected_idx = df_display[df_display['display_name'] == selected_activity_name].index[0]
selected_activity = df.loc[selected_idx]

# Affichage des infos de base
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Distance", f"{selected_activity['distance_km']:.2f} km")

with col2:
    st.metric("D+", f"{selected_activity['elevation_gain_m']:.0f} m")

with col3:
    st.metric("Durée", f"{selected_activity['duration_hours']:.2f} h")

with col4:
    st.metric("Vitesse moy.", f"{selected_activity['speed_kmh']:.2f} km/h")

with col5:
    if 'average_heartrate' in selected_activity and pd.notna(selected_activity['average_heartrate']):
        st.metric("FC moy.", f"{selected_activity['average_heartrate']:.0f} bpm")
    else:
        st.metric("FC moy.", "N/A")

st.divider()

# Récupération de l'ID Strava
if 'id' not in selected_activity or pd.isna(selected_activity['id']):
    st.error("""
    ⚠️ ID Strava manquant pour cette activité.
    
    Pour activer l'analyse détaillée, modifie `app.py` ligne ~70 :
    ```python
    columns_to_keep = [
        'id',  # ← Ajoute cette ligne
        'name', 'distance', 'moving_time', ...
    ]
    ```
    """)
    st.stop()

activity_id = int(selected_activity['id'])

# Récupération des streams
analyzer = ActivityAnalyzer(access_token)

with st.spinner("Chargement des données détaillées..."):
    streams = analyzer.get_activity_streams(
        activity_id,
        stream_types=['time', 'latlng', 'distance', 'altitude', 
                     'velocity_smooth', 'heartrate', 'cadence']
    )

if not streams:
    st.error("Impossible de récupérer les données détaillées de cette activité")
    st.stop()

# Tabs pour les différentes analyses
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Carte", 
    "⛰️ Profil d'élévation", 
    "📊 Allure & FC",
    "🔬 Analyse par segments"
])

# TAB 1: Carte interactive
with tab1:
    st.subheader("Carte du parcours")
    
    if 'latlng' in streams:
        activity_info = {
            'name': selected_activity['name'],
            'distance': selected_activity['distance_km'] * 1000,
            'elevation_gain': selected_activity['elevation_gain_m']
        }
        
        map_fig = analyzer.create_interactive_map(streams, activity_info)
        
        if map_fig:
            st.plotly_chart(map_fig, use_container_width=True)
        else:
            st.warning("Impossible de créer la carte")
    else:
        st.warning("Données GPS non disponibles pour cette activité")

# TAB 2: Profil d'élévation
with tab2:
    st.subheader("Profil d'élévation")
    
    if 'altitude' in streams and 'distance' in streams:
        activity_info = {
            'name': selected_activity['name']
        }
        
        elev_fig = analyzer.create_elevation_profile(streams, activity_info)
        
        if elev_fig:
            st.plotly_chart(elev_fig, use_container_width=True)
            
            # Stats d'élévation
            import numpy as np
            altitude = np.array(streams['altitude']['data'])
            distance_m = np.array(streams['distance']['data'])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Altitude min", f"{altitude.min():.0f} m")
            
            with col2:
                st.metric("Altitude max", f"{altitude.max():.0f} m")
            
            with col3:
                st.metric("Altitude moy.", f"{altitude.mean():.0f} m")
            
            with col4:
                # Calcul pente moyenne
                gradient = np.gradient(altitude, distance_m) * 100
                avg_gradient = np.mean(gradient[gradient > 0])  # Seulement montées
                st.metric("Pente moy. montée", f"{avg_gradient:.1f} %")
        else:
            st.warning("Impossible de créer le profil")
    else:
        st.warning("Données d'altitude non disponibles")

# TAB 3: Allure & FC
with tab3:
    st.subheader("Allure et fréquence cardiaque")
    
    activity_info = {
        'name': selected_activity['name']
    }
    
    pace_hr_fig = analyzer.create_pace_hr_analysis(streams, activity_info)
    
    if pace_hr_fig:
        st.plotly_chart(pace_hr_fig, use_container_width=True)
        
        # Stats
        col1, col2 = st.columns(2)
        
        with col1:
            if 'velocity_smooth' in streams:
                import numpy as np
                velocity = np.array(streams['velocity_smooth']['data'])
                velocity = velocity[velocity > 0]  # Enlever les 0
                
                pace = 1000 / (velocity * 60)  # min/km
                pace = pace[pace < 20]  # Enlever les valeurs aberrantes
                
                st.metric("Allure min", f"{pace.min():.2f} min/km")
                st.metric("Allure max", f"{pace.max():.2f} min/km")
                st.metric("Allure médiane", f"{np.median(pace):.2f} min/km")
        
        with col2:
            if 'heartrate' in streams:
                import numpy as np
                hr = np.array(streams['heartrate']['data'])
                hr = hr[hr > 0]
                
                st.metric("FC min", f"{hr.min():.0f} bpm")
                st.metric("FC max", f"{hr.max():.0f} bpm")
                st.metric("FC médiane", f"{np.median(hr):.0f} bpm")
    else:
        st.warning("Données de vitesse/FC non disponibles")

# TAB 4: Analyse par segments
with tab4:
    st.subheader("Analyse par segments")
    
    segment_size = st.slider(
        "Taille des segments (km)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5
    )
    
    segments_df = analyzer.analyze_segments(streams, segment_distance_km=segment_size)
    
    if segments_df is not None and not segments_df.empty:
        st.write(f"**{len(segments_df)} segments analysés**")
        
        # Graphique par segment
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Allure par segment", "FC par segment"),
            vertical_spacing=0.15
        )
        
        # Allure
        if 'pace_min_km' in segments_df.columns:
            fig.add_trace(
                go.Bar(
                    x=segments_df['segment_start_km'],
                    y=segments_df['pace_min_km'],
                    name='Allure',
                    marker_color='orange'
                ),
                row=1, col=1
            )
        
        # FC
        if 'avg_hr' in segments_df.columns:
            fig.add_trace(
                go.Bar(
                    x=segments_df['segment_start_km'],
                    y=segments_df['avg_hr'],
                    name='FC moyenne',
                    marker_color='red'
                ),
                row=2, col=1
            )
        
        fig.update_xaxes(title_text="Distance (km)", row=2, col=1)
        fig.update_yaxes(title_text="Allure (min/km)", row=1, col=1)
        fig.update_yaxes(title_text="FC (bpm)", row=2, col=1)
        
        fig.update_layout(height=600, showlegend=False)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau des segments
        st.write("**Détail des segments**")
        
        display_segments = segments_df[[
            'segment_start_km', 'distance_km', 'pace_min_km', 
            'elevation_gain_m', 'gradient_pct', 'avg_hr'
        ]].copy() if all(col in segments_df.columns for col in ['pace_min_km', 'elevation_gain_m', 'gradient_pct', 'avg_hr']) else segments_df
        
        display_segments = display_segments.round(2)
        st.dataframe(display_segments, use_container_width=True, hide_index=True)
    else:
        st.warning("Impossible d'analyser par segments")

st.divider()

# Comparaison avec sorties similaires
st.subheader("🔄 Sorties similaires")

tolerance = st.slider(
    "Tolérance (%)",
    min_value=10,
    max_value=50,
    value=20,
    help="Variation acceptée en % pour distance et D+"
)

similar_activities = get_similar_activities(df, selected_activity, tolerance_pct=tolerance)

# Exclure l'activité sélectionnée
similar_activities = similar_activities[similar_activities.index != selected_idx]

if len(similar_activities) > 0:
    st.write(f"**{len(similar_activities)} sortie(s) similaire(s) trouvée(s)**")
    
    # Comparaison visuelle
    comparison_df = similar_activities[
        ['start_date', 'name', 'distance_km', 'elevation_gain_m', 
         'duration_hours', 'speed_kmh']
    ].head(5).copy()
    
    comparison_df.columns = ['Date', 'Nom', 'Distance (km)', 'D+ (m)', 
                             'Durée (h)', 'Vitesse (km/h)']
    
    comparison_df['Date'] = comparison_df['Date'].dt.strftime('%Y-%m-%d')
    comparison_df = comparison_df.round(2)
    
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Sélection pour comparaison détaillée
    if len(similar_activities) > 0:
        st.write("**Comparaison détaillée**")
        
        compare_activity_name = st.selectbox(
            "Choisir une sortie à comparer",
            options=similar_activities['name'].tolist()
        )
        
        compare_activity = similar_activities[
            similar_activities['name'] == compare_activity_name
        ].iloc[0]
        
        # Métriques de comparaison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dist_diff = compare_activity['distance_km'] - selected_activity['distance_km']
            st.metric(
                "Distance",
                f"{compare_activity['distance_km']:.2f} km",
                delta=f"{dist_diff:+.2f} km"
            )
        
        with col2:
            elev_diff = compare_activity['elevation_gain_m'] - selected_activity['elevation_gain_m']
            st.metric(
                "D+",
                f"{compare_activity['elevation_gain_m']:.0f} m",
                delta=f"{elev_diff:+.0f} m"
            )
        
        with col3:
            time_diff = compare_activity['duration_hours'] - selected_activity['duration_hours']
            st.metric(
                "Durée",
                f"{compare_activity['duration_hours']:.2f} h",
                delta=f"{time_diff:+.2f} h",
                delta_color="inverse"
            )
else:
    st.info("Aucune sortie similaire trouvée avec ces critères")
