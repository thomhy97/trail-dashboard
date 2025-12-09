"""
Page de gestion des objectifs de saison
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

st.set_page_config(
    page_title="Objectifs de saison",
    page_icon="🎯",
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

st.header("🎯 Objectifs de saison")

# Initialiser les objectifs dans session_state s'ils n'existent pas
if 'race_goals' not in st.session_state:
    st.session_state.race_goals = []

# Fonction pour sauvegarder les objectifs (optionnel - pour persistance future)
def save_goals():
    # Pour l'instant, juste dans session_state
    # Plus tard : sauvegarder dans un fichier JSON ou BDD
    pass

# Fonction pour calculer les statistiques depuis une date
def get_stats_since_date(df, start_date):
    """Calcule les stats depuis une date donnée"""
    df_filtered = df[df['start_date'] >= start_date].copy()
    
    if df_filtered.empty:
        return {
            'total_km': 0,
            'total_elevation': 0,
            'total_time': 0,
            'num_activities': 0
        }
    
    return {
        'total_km': df_filtered['distance_km'].sum(),
        'total_elevation': df_filtered['elevation_gain_m'].sum(),
        'total_time': df_filtered['duration_hours'].sum(),
        'num_activities': len(df_filtered)
    }

# Fonction pour calculer le temps estimé nécessaire
def estimate_time_needed(distance_km, elevation_m, pace_min_km=6.5, elevation_penalty_min_per_100m=5):
    """
    Estime le temps nécessaire pour une course
    
    Args:
        distance_km: Distance en km
        elevation_m: Dénivelé positif en mètres
        pace_min_km: Allure de base en min/km (défaut: 6.5 min/km)
        elevation_penalty_min_per_100m: Temps supplémentaire par 100m D+ (défaut: 5 min)
    
    Returns:
        Temps estimé en heures
    """
    # Temps de base sur la distance
    base_time_min = distance_km * pace_min_km
    
    # Temps supplémentaire pour le dénivelé
    elevation_time_min = (elevation_m / 100) * elevation_penalty_min_per_100m
    
    # Temps total
    total_time_min = base_time_min + elevation_time_min
    total_time_hours = total_time_min / 60
    
    return total_time_hours

# Section : Ajouter un objectif
st.subheader("➕ Ajouter un objectif de course")

with st.expander("Définir un nouvel objectif", expanded=len(st.session_state.race_goals) == 0):
    col1, col2 = st.columns(2)
    
    with col1:
        goal_name = st.text_input("Nom de la course", placeholder="Ex: Ultra Trail du Mont Blanc")
        goal_date = st.date_input("Date de la course", min_value=datetime.now().date())
        goal_distance = st.number_input("Distance (km)", min_value=1.0, max_value=500.0, value=50.0, step=5.0)
        goal_elevation = st.number_input("D+ (m)", min_value=0, max_value=20000, value=3000, step=100)
    
    with col2:
        goal_type = st.selectbox(
            "Type de course",
            ["Trail", "Ultra-trail", "Marathon", "Semi-marathon", "Course montagne", "Autre"]
        )
        
        # Paramètres d'estimation
        st.markdown("**Paramètres d'estimation du temps :**")
        pace_estimation = st.slider("Allure de base (min/km)", 4.0, 10.0, 6.5, 0.5)
        elevation_penalty = st.slider("Pénalité D+ (min/100m)", 2.0, 10.0, 5.0, 0.5)
        
        # Calcul automatique du temps estimé
        estimated_time = estimate_time_needed(goal_distance, goal_elevation, pace_estimation, elevation_penalty)
        st.info(f"⏱️ Temps estimé : **{estimated_time:.1f}h** ({estimated_time*60:.0f} min)")
    
    # Bouton pour ajouter
    if st.button("➕ Ajouter cet objectif", type="primary"):
        if goal_name:
            new_goal = {
                'id': len(st.session_state.race_goals),
                'name': goal_name,
                'date': goal_date,
                'distance_km': goal_distance,
                'elevation_m': goal_elevation,
                'type': goal_type,
                'estimated_time_hours': estimated_time,
                'created_at': datetime.now(),
                'pace_estimation': pace_estimation,
                'elevation_penalty': elevation_penalty
            }
            st.session_state.race_goals.append(new_goal)
            save_goals()
            st.success(f"✅ Objectif '{goal_name}' ajouté !")
            st.rerun()
        else:
            st.error("⚠️ Le nom de la course est obligatoire")

st.divider()

# Affichage des objectifs
if len(st.session_state.race_goals) == 0:
    st.info("📝 Aucun objectif défini pour le moment. Ajoute ta première course cible ci-dessus !")
else:
    st.subheader(f"🏁 Mes objectifs ({len(st.session_state.race_goals)} course(s))")
    
    # Trier par date
    goals_sorted = sorted(st.session_state.race_goals, key=lambda x: x['date'])
    
    # Calculer la date de début de saison (plus ancien objectif - 6 mois)
    oldest_goal_date = goals_sorted[0]['date']
    season_start = oldest_goal_date - timedelta(days=180)  # 6 mois avant
    
    # Stats globales de la saison
    season_stats = get_stats_since_date(df, pd.Timestamp(season_start))
    
    # Métriques globales
    st.markdown("### 📊 Progression globale de la saison")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total entraînement",
            f"{season_stats['num_activities']} sorties",
            help="Depuis le début de saison"
        )
    
    with col2:
        st.metric(
            "Distance totale",
            f"{season_stats['total_km']:.0f} km",
            help="Cumul depuis le début de saison"
        )
    
    with col3:
        st.metric(
            "D+ total",
            f"{season_stats['total_elevation']:.0f} m",
            help="Cumul depuis le début de saison"
        )
    
    with col4:
        st.metric(
            "Temps total",
            f"{season_stats['total_time']:.0f}h",
            help="Cumul depuis le début de saison"
        )
    
    st.divider()
    
    # Affichage de chaque objectif
    for idx, goal in enumerate(goals_sorted):
        goal_date = pd.Timestamp(goal['date'])
        today = pd.Timestamp(datetime.now().date())
        days_remaining = (goal_date - today).days
        
        # Calculer les stats depuis la création de l'objectif
        stats_since_goal = get_stats_since_date(df, pd.Timestamp(goal['created_at']))
        
        # Carte de l'objectif
        with st.container():
            # Header avec compte à rebours
            if days_remaining > 0:
                col_header1, col_header2 = st.columns([3, 1])
                
                with col_header1:
                    st.markdown(f"### 🏆 {goal['name']}")
                    st.caption(f"{goal['type']} • {goal_date.strftime('%d/%m/%Y')}")
                
                with col_header2:
                    # Compte à rebours stylisé
                    if days_remaining <= 7:
                        countdown_color = "🔴"
                    elif days_remaining <= 30:
                        countdown_color = "🟠"
                    else:
                        countdown_color = "🟢"
                    
                    st.markdown(f"### {countdown_color} J-{days_remaining}")
                    
                    # Semaines restantes
                    weeks_remaining = days_remaining / 7
                    st.caption(f"({weeks_remaining:.1f} semaines)")
            
            else:
                st.markdown(f"### 🏁 {goal['name']}")
                st.caption(f"{goal['type']} • {goal_date.strftime('%d/%m/%Y')} • **Terminée !**")
            
            # Informations de la course
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Distance", f"{goal['distance_km']:.0f} km")
            
            with col2:
                st.metric("D+", f"{goal['elevation_m']:.0f} m")
            
            with col3:
                st.metric("Temps estimé", f"{goal['estimated_time_hours']:.1f}h")
            
            with col4:
                # Calcul du % D+
                deniv_pct = (goal['elevation_m'] / (goal['distance_km'] * 1000)) * 100
                st.metric("% D+", f"{deniv_pct:.1f}%")
            
            # Progression vers l'objectif (si la course n'est pas passée)
            if days_remaining > 0:
                st.markdown("#### 📈 Progression vers l'objectif")
                
                # Barres de progression
                col_prog1, col_prog2, col_prog3 = st.columns(3)
                
                with col_prog1:
                    # Objectif : distance totale = 3x la distance de course
                    target_distance = goal['distance_km'] * 3
                    progress_distance = min(100, (stats_since_goal['total_km'] / target_distance) * 100)
                    
                    st.markdown(f"**Distance** : {stats_since_goal['total_km']:.0f} / {target_distance:.0f} km")
                    st.progress(progress_distance / 100)
                    st.caption(f"{progress_distance:.0f}% de l'objectif")
                
                with col_prog2:
                    # Objectif : D+ total = 5x le D+ de la course
                    target_elevation = goal['elevation_m'] * 5
                    progress_elevation = min(100, (stats_since_goal['total_elevation'] / target_elevation) * 100)
                    
                    st.markdown(f"**D+** : {stats_since_goal['total_elevation']:.0f} / {target_elevation:.0f} m")
                    st.progress(progress_elevation / 100)
                    st.caption(f"{progress_elevation:.0f}% de l'objectif")
                
                with col_prog3:
                    # Objectif : temps total = 10x le temps estimé
                    target_time = goal['estimated_time_hours'] * 10
                    progress_time = min(100, (stats_since_goal['total_time'] / target_time) * 100)
                    
                    st.markdown(f"**Temps** : {stats_since_goal['total_time']:.0f} / {target_time:.0f}h")
                    st.progress(progress_time / 100)
                    st.caption(f"{progress_time:.0f}% de l'objectif")
                
                # Graphique d'évolution
                st.markdown("#### 📊 Évolution de la préparation")
                
                # Filtrer les données depuis la création de l'objectif
                df_goal = df[df['start_date'] >= pd.Timestamp(goal['created_at'])].copy()
                df_goal = df_goal.sort_values('start_date')
                
                if not df_goal.empty:
                    # Calculer les cumuls
                    df_goal['cumul_km'] = df_goal['distance_km'].cumsum()
                    df_goal['cumul_elevation'] = df_goal['elevation_gain_m'].cumsum()
                    
                    fig = go.Figure()
                    
                    # Distance cumulée
                    fig.add_trace(go.Scatter(
                        x=df_goal['start_date'],
                        y=df_goal['cumul_km'],
                        name='Distance (km)',
                        line=dict(color='#FC4C02', width=2),
                        fill='tozeroy'
                    ))
                    
                    # Ligne objectif distance
                    fig.add_hline(
                        y=target_distance,
                        line_dash="dash",
                        line_color="#FC4C02",
                        annotation_text=f"Objectif: {target_distance:.0f} km",
                        annotation_position="right"
                    )
                    
                    fig.update_layout(
                        height=300,
                        xaxis_title="Date",
                        yaxis_title="Distance cumulée (km)",
                        hovermode='x unified',
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Recommandations
                st.markdown("#### 💡 Recommandations")
                
                # Calculer ce qui reste à faire
                remaining_distance = max(0, target_distance - stats_since_goal['total_km'])
                remaining_elevation = max(0, target_elevation - stats_since_goal['total_elevation'])
                
                if days_remaining > 7:
                    weekly_distance_needed = (remaining_distance / days_remaining) * 7
                    weekly_elevation_needed = (remaining_elevation / days_remaining) * 7
                    
                    col_reco1, col_reco2 = st.columns(2)
                    
                    with col_reco1:
                        if weekly_distance_needed > 0:
                            st.info(f"📏 **{weekly_distance_needed:.0f} km/semaine** nécessaires pour atteindre l'objectif distance")
                        else:
                            st.success("✅ Objectif distance atteint !")
                    
                    with col_reco2:
                        if weekly_elevation_needed > 0:
                            st.info(f"⛰️ **{weekly_elevation_needed:.0f} m D+/semaine** nécessaires pour atteindre l'objectif D+")
                        else:
                            st.success("✅ Objectif D+ atteint !")
                else:
                    st.warning("⏰ Moins d'une semaine avant la course - Phase de taper ! Repose-toi bien.")
            
            # Actions
            col_action1, col_action2 = st.columns([1, 5])
            
            with col_action1:
                if st.button(f"🗑️ Supprimer", key=f"delete_{goal['id']}"):
                    st.session_state.race_goals = [g for g in st.session_state.race_goals if g['id'] != goal['id']]
                    save_goals()
                    st.rerun()
            
            st.divider()
    
    # Vue timeline de tous les objectifs
    st.subheader("📅 Timeline des objectifs")
    
    fig_timeline = go.Figure()
    
    today = datetime.now()
    
    for goal in goals_sorted:
        goal_date = pd.Timestamp(goal['date'])
        days_to_goal = (goal_date - pd.Timestamp(today.date())).days
        
        # Couleur selon proximité
        if days_to_goal < 0:
            color = 'gray'
            status = '✓ Terminé'
        elif days_to_goal <= 7:
            color = 'red'
            status = f'J-{days_to_goal}'
        elif days_to_goal <= 30:
            color = 'orange'
            status = f'J-{days_to_goal}'
        else:
            color = 'green'
            status = f'J-{days_to_goal}'
        
        fig_timeline.add_trace(go.Scatter(
            x=[goal_date],
            y=[goal['distance_km']],
            mode='markers+text',
            name=goal['name'],
            marker=dict(
                size=20,
                color=color,
                line=dict(width=2, color='white')
            ),
            text=f"{goal['name']}<br>{status}",
            textposition="top center",
            hovertemplate=f"<b>{goal['name']}</b><br>" +
                         f"Date: {goal_date.strftime('%d/%m/%Y')}<br>" +
                         f"Distance: {goal['distance_km']:.0f} km<br>" +
                         f"D+: {goal['elevation_m']:.0f} m<br>" +
                         "<extra></extra>"
        ))
    
    # Ligne verticale pour aujourd'hui
    fig_timeline.add_vline(
        x=today,
        line_dash="dash",
        line_color="blue",
        annotation_text="Aujourd'hui",
        annotation_position="top"
    )
    
    fig_timeline.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Distance (km)",
        showlegend=False,
        hovermode='closest'
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)

# Footer
st.divider()
st.caption("💡 Les objectifs de préparation sont calculés automatiquement : Distance totale = 3x la course, D+ total = 5x la course, Temps = 10x le temps estimé")
