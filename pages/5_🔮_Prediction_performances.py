"""
Page de prédiction de performances
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from utils.performance_prediction import PerformancePredictor, format_time, format_pace

st.set_page_config(
    page_title="Prédiction de performances",
    page_icon="🔮",
    layout="wide"
)

# Vérifier que l'utilisateur est connecté
if 'access_token' not in st.session_state or not st.session_state.access_token:
    st.error("⚠️ Tu dois d'abord te connecter à Strava depuis la page d'accueil")
    st.stop()

if 'df' not in st.session_state or st.session_state.df.empty:
    st.error("⚠️ Aucune donnée disponible. Va d'abord sur la page d'accueil.")
    st.stop()

df = st.session_state.df

st.header("🔮 Prédiction de performances")

# Initialiser le prédicteur
predictor = PerformancePredictor()

# Tabs pour organiser les fonctionnalités
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 VDOT & Équivalences",
    "⛰️ Prédiction avec D+",
    "🎯 Progression nécessaire",
    "📁 Analyse GPX",
    "🏃 Mes performances"
])

# ===== TAB 1: VDOT & Équivalences =====
with tab1:
    st.subheader("📊 Modèle VDOT - Estimation de performances")
    
    st.markdown("""
    Le **VDOT** (VO2max estimé) est un indicateur de ta capacité aérobie développé par Jack Daniels.
    Il permet de prédire tes temps sur différentes distances à partir d'une performance de référence.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏃 Entre une performance récente")
        
        ref_distance_options = {
            '1 km': 1000,
            '5 km': 5000,
            '10 km': 10000,
            'Semi-marathon (21.1 km)': 21097.5,
            'Marathon (42.2 km)': 42195
        }
        
        ref_distance_name = st.selectbox("Distance", list(ref_distance_options.keys()))
        ref_distance_m = ref_distance_options[ref_distance_name]
        
        # Saisie du temps
        col_h, col_m, col_s = st.columns(3)
        with col_h:
            hours = st.number_input("Heures", min_value=0, max_value=24, value=0, step=1)
        with col_m:
            minutes = st.number_input("Minutes", min_value=0, max_value=59, value=30, step=1)
        with col_s:
            seconds = st.number_input("Secondes", min_value=0, max_value=59, value=0, step=1)
        
        ref_time_seconds = hours * 3600 + minutes * 60 + seconds
        
        if st.button("🔮 Calculer mon VDOT", type="primary"):
            if ref_time_seconds > 0:
                # Calculer le VDOT
                vdot = predictor.calculate_vdot_from_race(ref_distance_m, ref_time_seconds)
                st.session_state.calculated_vdot = vdot
                st.session_state.ref_performance = {
                    'distance': ref_distance_name,
                    'time': format_time(ref_time_seconds)
                }
    
    with col2:
        if 'calculated_vdot' in st.session_state:
            vdot = st.session_state.calculated_vdot
            
            st.markdown("#### ✨ Ton VDOT")
            st.markdown(f"### **{vdot:.1f}**")
            
            # Interprétation du VDOT
            if vdot < 35:
                level = "Débutant"
                color = "🔵"
            elif vdot < 45:
                level = "Intermédiaire"
                color = "🟢"
            elif vdot < 55:
                level = "Confirmé"
                color = "🟠"
            elif vdot < 65:
                level = "Avancé"
                color = "🟡"
            else:
                level = "Élite"
                color = "🔴"
            
            st.markdown(f"{color} **Niveau : {level}**")
            
            if 'ref_performance' in st.session_state:
                st.caption(f"Basé sur : {st.session_state.ref_performance['distance']} en {st.session_state.ref_performance['time']}")
    
    # Tableau des équivalences
    if 'calculated_vdot' in st.session_state:
        st.divider()
        st.markdown("### 🎯 Temps équivalents prédits")
        
        vdot = st.session_state.calculated_vdot
        predictions = predictor.predict_times_from_vdot(vdot)
        
        # Créer un DataFrame pour l'affichage
        df_pred = pd.DataFrame([
            {
                'Distance': dist,
                'Temps prédit': format_time(time_sec),
                'Allure': format_pace(time_sec / (dist_m / 1000)) if 'km' in dist else '-',
                'Temps (secondes)': time_sec
            }
            for dist, time_sec in predictions.items()
            for dist_name, dist_m in [
                ('1 km', 1000), ('5 km', 5000), ('10 km', 10000),
                ('Semi-marathon', 21097.5), ('Marathon', 42195),
                ('50 km', 50000), ('100 km', 100000)
            ]
            if dist == dist_name or (dist.startswith(dist_name.split()[0]) and len(dist_name.split()) == 2)
        ])
        
        # Afficher le tableau
        st.dataframe(
            df_pred[['Distance', 'Temps prédit', 'Allure']],
            use_container_width=True,
            hide_index=True
        )
        
        # Graphique de comparaison
        fig = go.Figure()
        
        distances_km = [1, 5, 10, 21.1, 42.2, 50, 100]
        times_hours = [predictions[d] / 3600 for d in predictions.keys()]
        
        fig.add_trace(go.Scatter(
            x=distances_km,
            y=times_hours,
            mode='lines+markers',
            name='Temps prédits',
            line=dict(color='#FC4C02', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Courbe des temps prédits selon la distance",
            xaxis_title="Distance (km)",
            yaxis_title="Temps (heures)",
            height=400,
            xaxis_type="log",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ===== TAB 2: Prédiction avec D+ =====
with tab2:
    st.subheader("⛰️ Prédiction de temps avec dénivelé")
    
    st.markdown("""
    Ajuste les prédictions de temps en fonction du dénivelé positif.
    L'algorithme prend en compte ton niveau pour estimer la pénalité due au D+.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📏 Caractéristiques de la course")
        
        target_distance_km = st.number_input("Distance (km)", min_value=1.0, max_value=300.0, value=42.2, step=5.0)
        target_elevation_m = st.number_input("Dénivelé positif (m)", min_value=0, max_value=15000, value=2000, step=100)
        
        runner_level = st.select_slider(
            "Ton niveau en trail",
            options=['beginner', 'intermediate', 'advanced'],
            value='intermediate',
            format_func=lambda x: {'beginner': '🔰 Débutant', 'intermediate': '🏃 Intermédiaire', 'advanced': '⚡ Avancé'}[x]
        )
        
        # Pénalité affichée
        penalties = {'beginner': 6.0, 'intermediate': 4.5, 'advanced': 3.0}
        st.info(f"Pénalité utilisée : **{penalties[runner_level]} min / 100m D+**")
    
    with col2:
        if 'calculated_vdot' in st.session_state:
            st.markdown("#### ⏱️ Temps prédit")
            
            vdot = st.session_state.calculated_vdot
            target_distance_m = target_distance_km * 1000
            
            # Temps sur plat
            flat_time = predictor._predict_time_for_distance(target_distance_m, vdot)
            
            # Temps avec D+
            adjusted_time = predictor.adjust_time_for_elevation(
                flat_time,
                target_elevation_m,
                target_distance_m,
                runner_level
            )
            
            # Affichage
            st.markdown("**Temps sur terrain plat :**")
            st.markdown(f"### {format_time(flat_time)}")
            
            st.markdown("**Temps avec D+ :**")
            st.markdown(f"### {format_time(adjusted_time)}")
            st.markdown(f"**+{format_time(adjusted_time - flat_time)}** de pénalité")
            
            # Allure moyenne
            avg_pace = adjusted_time / target_distance_km
            st.metric("Allure moyenne", format_pace(avg_pace))
            
            # % de D+
            deniv_percent = (target_elevation_m / target_distance_m) * 100
            st.metric("% D+", f"{deniv_percent:.1f}%")
        else:
            st.info("👆 Calcule d'abord ton VDOT dans l'onglet précédent")
    
    # Comparaison selon le niveau
    if 'calculated_vdot' in st.session_state:
        st.divider()
        st.markdown("### 📊 Comparaison selon le niveau")
        
        levels = ['beginner', 'intermediate', 'advanced']
        level_names = ['Débutant', 'Intermédiaire', 'Avancé']
        times_by_level = []
        
        for level in levels:
            adj_time = predictor.adjust_time_for_elevation(
                flat_time,
                target_elevation_m,
                target_distance_m,
                level
            )
            times_by_level.append(adj_time / 3600)  # en heures
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=level_names,
            y=times_by_level,
            text=[format_time(t * 3600) for t in times_by_level],
            textposition='outside',
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1']
        ))
        
        fig.update_layout(
            title=f"Temps prédit pour {target_distance_km:.0f} km avec {target_elevation_m}m D+",
            yaxis_title="Temps (heures)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ===== TAB 3: Progression nécessaire =====
with tab3:
    st.subheader("🎯 Progression nécessaire pour atteindre un objectif")
    
    st.markdown("""
    Analyse la faisabilité d'un objectif de temps et calcule la progression hebdomadaire nécessaire.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏁 Performance actuelle")
        
        current_distance_options = {
            '5 km': 5000,
            '10 km': 10000,
            'Semi-marathon': 21097.5,
            'Marathon': 42195,
            '50 km': 50000
        }
        
        current_distance_name = st.selectbox("Distance de référence", list(current_distance_options.keys()), key='prog_dist')
        current_distance_m = current_distance_options[current_distance_name]
        
        col_h2, col_m2, col_s2 = st.columns(3)
        with col_h2:
            current_hours = st.number_input("Heures", min_value=0, max_value=24, value=1, step=1, key='current_h')
        with col_m2:
            current_minutes = st.number_input("Minutes", min_value=0, max_value=59, value=30, step=1, key='current_m')
        with col_s2:
            current_seconds = st.number_input("Secondes", min_value=0, max_value=59, value=0, step=1, key='current_s')
        
        current_time = current_hours * 3600 + current_minutes * 60 + current_seconds
    
    with col2:
        st.markdown("#### 🎯 Objectif visé")
        
        col_h3, col_m3, col_s3 = st.columns(3)
        with col_h3:
            target_hours = st.number_input("Heures", min_value=0, max_value=24, value=1, step=1, key='target_h')
        with col_m3:
            target_minutes = st.number_input("Minutes", min_value=0, max_value=59, value=20, step=1, key='target_m')
        with col_s3:
            target_seconds = st.number_input("Secondes", min_value=0, max_value=59, value=0, step=1, key='target_s')
        
        target_time = target_hours * 3600 + target_minutes * 60 + target_seconds
        
        weeks_available = st.number_input("Nombre de semaines d'entraînement", min_value=1, max_value=52, value=12, step=1)
    
    if st.button("📈 Analyser la progression nécessaire", type="primary"):
        if current_time > 0 and target_time > 0:
            progression = predictor.calculate_progression_needed(current_time, target_time, weeks_available)
            
            st.divider()
            
            # Métriques principales
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                st.metric(
                    "Temps à gagner",
                    format_time(progression['time_diff_seconds']),
                    f"-{progression['time_diff_percent']:.1f}%"
                )
            
            with col_m2:
                st.metric(
                    "Par semaine",
                    format_time(progression['weekly_improvement_seconds']),
                    f"-{progression['weekly_improvement_percent']:.2f}%"
                )
            
            with col_m3:
                feasibility_color = {
                    'Réaliste': '🟢',
                    'Ambitieux': '🟠',
                    'Très ambitieux': '🔴'
                }
                st.metric(
                    "Faisabilité",
                    f"{feasibility_color.get(progression['feasibility'], '⚪')} {progression['feasibility']}"
                )
            
            with col_m4:
                st.metric(
                    "Difficulté",
                    progression['difficulty']
                )
            
            # Analyse détaillée
            st.markdown("### 📊 Analyse détaillée")
            
            # Explication
            if progression['feasibility'] == 'Réaliste':
                st.success("""
                ✅ **Objectif réaliste !**
                
                Ton objectif est atteignable avec un entraînement régulier et progressif.
                La progression demandée est dans les normes recommandées (max 2-3% par mois).
                """)
            elif progression['feasibility'] == 'Ambitieux':
                st.warning("""
                ⚠️ **Objectif ambitieux**
                
                Ton objectif est atteignable mais nécessite un entraînement soutenu et rigoureux.
                La progression est à la limite du raisonnable. Attention au risque de blessure.
                """)
            else:
                st.error("""
                🔴 **Objectif très ambitieux**
                
                Ton objectif nécessite une progression très rapide qui dépasse les recommandations.
                Risque élevé de blessure ou de surentraînement. Considère :
                - Augmenter le délai de préparation
                - Revoir l'objectif de temps à la baisse
                """)
            
            # Graphique de progression
            st.markdown("### 📈 Évolution projetée")
            
            weeks = list(range(weeks_available + 1))
            projected_times = [
                current_time - (progression['weekly_improvement_seconds'] * week)
                for week in weeks
            ]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=weeks,
                y=[t / 60 for t in projected_times],  # en minutes
                mode='lines+markers',
                name='Progression projetée',
                line=dict(color='#FC4C02', width=3),
                marker=dict(size=8)
            ))
            
            fig.add_hline(
                y=target_time / 60,
                line_dash="dash",
                line_color="green",
                annotation_text=f"Objectif: {format_time(target_time)}",
                annotation_position="right"
            )
            
            fig.update_layout(
                xaxis_title="Semaines d'entraînement",
                yaxis_title="Temps (minutes)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommandations
            st.markdown("### 💡 Recommandations")
            
            col_r1, col_r2 = st.columns(2)
            
            with col_r1:
                st.markdown("**📅 Plan d'entraînement suggéré :**")
                st.markdown(f"""
                - Semaines 1-{weeks_available//3} : Base aérobie (volume)
                - Semaines {weeks_available//3+1}-{2*weeks_available//3} : Travail au seuil
                - Semaines {2*weeks_available//3+1}-{weeks_available-2} : Spécifique objectif
                - Dernières 2 semaines : Affûtage
                """)
            
            with col_r2:
                st.markdown("**🎯 Points clés :**")
                weekly_pct = progression['weekly_improvement_percent']
                if weekly_pct < 0.5:
                    st.markdown("- Maintien du volume actuel suffisant")
                    st.markdown("- Ajouter 1 séance qualité / semaine")
                elif weekly_pct < 1:
                    st.markdown("- Augmenter volume progressivement")
                    st.markdown("- 2 séances qualité / semaine")
                else:
                    st.markdown("- Augmentation significative du volume")
                    st.markdown("- 2-3 séances qualité / semaine")
                    st.markdown("- ⚠️ Surveillance fatigue nécessaire")

# ===== TAB 4: Analyse GPX =====
with tab4:
    st.subheader("📁 Analyse de GPX - Profil du parcours")
    
    st.markdown("""
    Analyse en détail le profil d'élévation de ton objectif :
    distribution des pentes, portions roulantes, montées/descentes techniques.
    """)
    
    st.info("💡 **Comment faire :** Ouvre ton fichier GPX dans un éditeur de texte (Notepad, TextEdit, etc.), copie tout le contenu (Ctrl+A puis Ctrl+C) et colle-le ci-dessous")
    
    gpx_content = st.text_area(
        "📋 Colle le contenu de ton fichier GPX ici :",
        height=250,
        placeholder='<?xml version="1.0"?>\n<gpx version="1.1" creator="Strava">\n  <trk>\n    <trkseg>\n      <trkpt lat="45.123" lon="6.456">\n        <ele>1234</ele>\n      </trkpt>\n      ...\n    </trkseg>\n  </trk>\n</gpx>',
        help="Copie-colle le contenu entier de ton fichier .gpx"
    )
    
    if gpx_content and len(gpx_content) > 100:
        if st.button("🔮 Analyser le parcours", type="primary"):
            with st.spinner("Analyse du parcours en cours..."):
                try:
                    # Parser le GPX
                    gpx_data = predictor.parse_gpx_file(gpx_content)
                    
                    if 'error' in gpx_data:
                        st.error(f"❌ Erreur lors de la lecture du fichier : {gpx_data['error']}")
                        st.info("💡 Assure-toi d'avoir copié l'intégralité du fichier GPX, depuis la première ligne jusqu'à la dernière")
                    else:
                        # Analyser le profil
                        profile = predictor.analyze_gpx_elevation_profile(gpx_data)
                        
                        st.success("✅ Fichier GPX analysé avec succès !")
                        
                        # Métriques principales
                        st.markdown("### 📊 Caractéristiques du parcours")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Distance", f"{profile['total_distance_m']/1000:.2f} km")
                        
                        with col2:
                            st.metric("D+", f"{profile['positive_elevation_m']:.0f} m")
                        
                        with col3:
                            st.metric("D-", f"{profile['negative_elevation_m']:.0f} m")
                        
                        with col4:
                            deniv_pct = (profile['positive_elevation_m'] / profile['total_distance_m']) * 100
                            st.metric("% D+", f"{deniv_pct:.1f}%")
                        
                        col5, col6, col7 = st.columns(3)
                        
                        with col5:
                            st.metric("Altitude min", f"{profile['altitude_min']:.0f} m")
                        
                        with col6:
                            st.metric("Altitude max", f"{profile['altitude_max']:.0f} m")
                        
                        with col7:
                            st.metric("Altitude moy", f"{profile['altitude_avg']:.0f} m")
                        
                        st.divider()
                        
                        # Distribution des pentes
                        st.markdown("### 📈 Distribution des pentes")
                
                        slope_dist = profile['slope_distribution']
                
                        # Préparer les données pour le graphique
                        categories = []
                        percentages = []
                        colors = []
                        distances = []
                
                        # D- très raide
                        if slope_dist['very_steep_downhill']['percent'] > 0:
                            categories.append('D- très raide\n(< -15%)')
                            percentages.append(slope_dist['very_steep_downhill']['percent'])
                            distances.append(slope_dist['very_steep_downhill']['distance_m'] / 1000)
                            colors.append('#8B0000')
                
                        # D- raide
                        if slope_dist['steep_downhill']['percent'] > 0:
                            categories.append('D- raide\n(-15% à -10%)')
                            percentages.append(slope_dist['steep_downhill']['percent'])
                            distances.append(slope_dist['steep_downhill']['distance_m'] / 1000)
                            colors.append('#CD5C5C')
                
                        # D- modérée
                        if slope_dist['moderate_downhill']['percent'] > 0:
                            categories.append('D- modérée\n(-10% à -6%)')
                            percentages.append(slope_dist['moderate_downhill']['percent'])
                            distances.append(slope_dist['moderate_downhill']['distance_m'] / 1000)
                            colors.append('#FFA07A')
                
                        # D- légère
                        if slope_dist['gentle_downhill']['percent'] > 0:
                            categories.append('D- légère\n(-6% à -3%)')
                            percentages.append(slope_dist['gentle_downhill']['percent'])
                            distances.append(slope_dist['gentle_downhill']['distance_m'] / 1000)
                            colors.append('#FFB6C1')
                
                        # Plat
                        if slope_dist['flat']['percent'] > 0:
                            categories.append('Plat\n(-3% à 3%)')
                            percentages.append(slope_dist['flat']['percent'])
                            distances.append(slope_dist['flat']['distance_m'] / 1000)
                            colors.append('#90EE90')
                
                        # D+ légère
                        if slope_dist['gentle_uphill']['percent'] > 0:
                            categories.append('D+ légère\n(3% à 6%)')
                            percentages.append(slope_dist['gentle_uphill']['percent'])
                            distances.append(slope_dist['gentle_uphill']['distance_m'] / 1000)
                            colors.append('#98FB98')
                
                        # D+ modérée
                        if slope_dist['moderate_uphill']['percent'] > 0:
                            categories.append('D+ modérée\n(6% à 10%)')
                            percentages.append(slope_dist['moderate_uphill']['percent'])
                            distances.append(slope_dist['moderate_uphill']['distance_m'] / 1000)
                            colors.append('#32CD32')
                
                        # D+ raide
                        if slope_dist['steep_uphill']['percent'] > 0:
                            categories.append('D+ raide\n(10% à 15%)')
                            percentages.append(slope_dist['steep_uphill']['percent'])
                            distances.append(slope_dist['steep_uphill']['distance_m'] / 1000)
                            colors.append('#228B22')
                
                        # D+ très raide
                        if slope_dist['very_steep_uphill']['percent'] > 0:
                            categories.append('D+ très raide\n(> 15%)')
                            percentages.append(slope_dist['very_steep_uphill']['percent'])
                            distances.append(slope_dist['very_steep_uphill']['distance_m'] / 1000)
                            colors.append('#006400')
                
                        # Graphiques
                        col_g1, col_g2 = st.columns(2)
                
                        with col_g1:
                            # Graphique en barres (pourcentages)
                            fig1 = go.Figure()
                    
                            fig1.add_trace(go.Bar(
                                x=categories,
                                y=percentages,
                                marker_color=colors,
                                text=[f"{p:.1f}%" for p in percentages],
                                textposition='outside'
                            ))
                    
                            fig1.update_layout(
                                title="Répartition par type de pente (%)",
                                xaxis_title="Type de pente",
                                yaxis_title="Pourcentage du parcours",
                                height=400,
                                showlegend=False
                            )
                    
                            st.plotly_chart(fig1, use_container_width=True)
                
                        with col_g2:
                            # Pie chart
                            fig2 = go.Figure()
                    
                            fig2.add_trace(go.Pie(
                                labels=categories,
                                values=distances,
                                marker_colors=colors,
                                textinfo='label+percent',
                                hovertemplate='<b>%{label}</b><br>%{value:.1f} km<br>%{percent}<extra></extra>'
                            ))
                    
                            fig2.update_layout(
                                title="Répartition par distance (km)",
                                height=400
                            )
                    
                            st.plotly_chart(fig2, use_container_width=True)
                
                        # Profil d'élévation
                        st.markdown("### ⛰️ Profil d'élévation")
                
                        fig3 = go.Figure()
                
                        fig3.add_trace(go.Scatter(
                            x=[d/1000 for d in gpx_data['distance']],
                            y=gpx_data['altitude'],
                            fill='tozeroy',
                            line=dict(color='#FC4C02', width=2),
                            name='Altitude'
                        ))
                
                        fig3.update_layout(
                            xaxis_title="Distance (km)",
                            yaxis_title="Altitude (m)",
                            height=400,
                            hovermode='x unified'
                        )
                
                        st.plotly_chart(fig3, use_container_width=True)
                
                        # Analyse tactique
                        st.markdown("### 💡 Analyse tactique")
                
                        col_t1, col_t2 = st.columns(2)
                
                        with col_t1:
                            st.markdown("**🟢 Points forts du parcours :**")
                    
                            flat_pct = slope_dist['flat']['percent']
                            gentle_down = slope_dist['gentle_downhill']['percent']
                            gentle_up = slope_dist['gentle_uphill']['percent']
                    
                            if flat_pct > 30:
                                st.markdown(f"- {flat_pct:.0f}% de portions roulantes (récupération possible)")
                            if gentle_down > 20:
                                st.markdown(f"- {gentle_down:.0f}% de descentes légères (pour refaire du temps)")
                            if gentle_up < 15:
                                st.markdown("- Peu de montées techniques")
                
                        with col_t2:
                            st.markdown("**🔴 Difficultés du parcours :**")
                    
                            steep_up = slope_dist['steep_uphill']['percent'] + slope_dist['very_steep_uphill']['percent']
                            steep_down = slope_dist['steep_downhill']['percent'] + slope_dist['very_steep_downhill']['percent']
                    
                            if steep_up > 15:
                                st.markdown(f"- {steep_up:.0f}% de montées raides/très raides")
                            if steep_down > 15:
                                st.markdown(f"- {steep_down:.0f}% de descentes techniques")
                            if deniv_pct > 5:
                                st.markdown(f"- D+ important : {deniv_pct:.1f}%")
                
                        # Estimation du temps avec ce profil
                        if 'calculated_vdot' in st.session_state:
                            st.divider()
                            st.markdown("### ⏱️ Estimation de temps pour ce parcours")
                    
                            vdot = st.session_state.calculated_vdot
                            distance_m = profile['total_distance_m']
                            elevation_m = profile['positive_elevation_m']
                    
                            # Temps plat
                            flat_time = predictor._predict_time_for_distance(distance_m, vdot)
                    
                            # Pour chaque niveau
                            levels = ['beginner', 'intermediate', 'advanced']
                            level_names = ['🔰 Débutant', '🏃 Intermédiaire', '⚡ Avancé']
                    
                            cols = st.columns(3)
                    
                            for idx, (level, level_name) in enumerate(zip(levels, level_names)):
                                adjusted = predictor.adjust_time_for_elevation(
                                    flat_time, elevation_m, distance_m, level
                                )
        
                                with cols[idx]:
                                    st.metric(
                                        level_name,
                                        format_time(adjusted),
                                        f"+{format_time(adjusted - flat_time)}"
                                    )
                        st.divider()
                        
                        # NOUVELLE SECTION : Analyse de compatibilité
                        st.markdown("### 🎯 Compatibilité avec ton entraînement actuel")
                        
                        # Définir les variables du parcours
                        distance_m = profile['total_distance_m']
                        elevation_m = profile['positive_elevation_m']
                        
                        # Récupérer les données d'entraînement
                        if 'df' in st.session_state and not st.session_state.df.empty:
                            df_training = st.session_state.df
                            
                            # Stats des 8 dernières semaines
                            cutoff_date = pd.Timestamp.now() - pd.Timedelta(weeks=8)
                            df_recent = df_training[df_training['start_date'] >= cutoff_date]
                            
                            if not df_recent.empty:
                                # Calculer les stats
                                avg_distance_weekly = df_recent['distance_km'].sum() / 8
                                avg_elevation_weekly = df_recent['elevation_gain_m'].sum() / 8
                                max_distance = df_recent['distance_km'].max()
                                max_elevation = df_recent['elevation_gain_m'].max()
                                avg_deniv_percent = df_recent['deniv_percent'].mean()
                                
                                # Distance de la course
                                race_distance_km = distance_m / 1000
                                race_elevation_m = elevation_m
                                race_deniv_percent = (race_elevation_m / distance_m) * 100
                                
                                st.markdown("#### 📊 Comparaison entraînement vs course")
                                
                                # Tableau comparatif
                                col_comp1, col_comp2, col_comp3 = st.columns(3)
                                
                                with col_comp1:
                                    st.markdown("**📏 Distance**")
                                    st.metric(
                                        "Course",
                                        f"{race_distance_km:.1f} km"
                                    )
                                    st.metric(
                                        "Sortie max (8 sem)",
                                        f"{max_distance:.1f} km",
                                        delta=f"{((max_distance / race_distance_km) * 100 - 100):.0f}%"
                                    )
                                
                                with col_comp2:
                                    st.markdown("**⛰️ Dénivelé**")
                                    st.metric(
                                        "Course",
                                        f"{race_elevation_m:.0f} m"
                                    )
                                    st.metric(
                                        "Sortie max (8 sem)",
                                        f"{max_elevation:.0f} m",
                                        delta=f"{((max_elevation / race_elevation_m) * 100 - 100):.0f}%"
                                    )
                                
                                with col_comp3:
                                    st.markdown("**📈 % D+**")
                                    st.metric(
                                        "Course",
                                        f"{race_deniv_percent:.1f}%"
                                    )
                                    st.metric(
                                        "Tes sorties moy",
                                        f"{avg_deniv_percent:.1f}%",
                                        delta=f"{(avg_deniv_percent - race_deniv_percent):.1f}%",
                                        delta_color="inverse"
                                    )
                                
                                st.divider()
                                
                                # Scores de préparation
                                distance_readiness = min(100, (max_distance / race_distance_km) * 100)
                                elevation_readiness = min(100, (max_elevation / race_elevation_m) * 100)
                                
                                # Score global
                                overall_readiness = (distance_readiness * 0.5 + elevation_readiness * 0.5)
                                
                                # Affichage du score global
                                st.markdown("#### 💡 Niveau de préparation")
                                col_score1, col_score2, col_score3 = st.columns([2, 1, 2])
                                
                                with col_score2:
                                    if overall_readiness >= 75:
                                        score_color = "🟢"
                                        readiness_text = "Prêt"
                                    elif overall_readiness >= 50:
                                        score_color = "🟠"
                                        readiness_text = "En progression"
                                    else:
                                        score_color = "🔴"
                                        readiness_text = "À renforcer"
                                    
                                    st.markdown(f"### {score_color} {overall_readiness:.0f}%")
                                    st.markdown(f"**{readiness_text}**")
                                
                                # Barres de progression
                                st.progress(distance_readiness / 100, text=f"Distance max : {distance_readiness:.0f}%")
                                st.progress(elevation_readiness / 100, text=f"D+ max : {elevation_readiness:.0f}%")
                                
                                st.divider()
                                
                                # Recommandations
                                st.markdown("#### 🎯 Recommandations")
                                
                                if distance_readiness < 60:
                                    st.warning(f"📏 **Distance** : Ta sortie longue ({max_distance:.1f} km) est insuffisante. Vise au moins {race_distance_km * 0.6:.1f} km.")
                                elif distance_readiness < 80:
                                    st.info(f"📏 **Distance** : Continue à allonger ta sortie longue vers {race_distance_km * 0.8:.1f} km.")
                                else:
                                    st.success(f"✅ **Distance** : Ta sortie longue est suffisante !")
                                
                                if elevation_readiness < 50:
                                    st.warning(f"⛰️ **D+** : Ton D+ max ({max_elevation:.0f}m) est trop faible. Priorité absolue sur les sorties dénivelées !")
                                elif elevation_readiness < 75:
                                    st.info(f"⛰️ **D+** : Continue le travail sur le dénivelé. Vise {race_elevation_m * 0.7:.0f}m sur une sortie.")
                                else:
                                    st.success(f"✅ **D+** : Tu es habitué au dénivelé !")
                                
                                # Temps de préparation
                                if overall_readiness >= 75:
                                    weeks_needed = 4
                                elif overall_readiness >= 50:
                                    weeks_needed = 8
                                else:
                                    weeks_needed = 12
                                
                                st.metric(
                                    "⏰ Préparation minimale suggérée",
                                    f"{weeks_needed} semaines"
                                )
                                
                            else:
                                st.info("📊 Pas assez de données récentes (8 dernières semaines)")
                        else:
                            st.info("📊 Charge tes activités Strava pour une analyse personnalisée !")
                
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
                    st.info("💡 Vérifie que le contenu GPX est complet et valide")

# ===== TAB 5: Mes performances =====
with tab5:
    st.subheader("🏃 Historique de mes performances")
    
    st.markdown("Analyse automatique de tes meilleures performances Strava")
    
    # Filtrer les courses "importantes" (> 5km)
    df_races = df[df['distance_km'] >= 5].copy()
    df_races = df_races.sort_values('start_date', ascending=False)
    
    if not df_races.empty:
        # Catégories de distances
        categories = {
            '5 km': (4, 6),
            '10 km': (9, 11),
            'Semi-marathon': (20, 22),
            'Marathon': (40, 44),
            '50 km': (45, 55),
            'Ultra (>55km)': (55, 1000)
        }
        
        st.markdown("### 🏆 Records personnels")
        
        # Pour chaque catégorie, trouver le meilleur temps
        records = []
        
        for cat_name, (min_km, max_km) in categories.items():
            cat_races = df_races[
                (df_races['distance_km'] >= min_km) &
                (df_races['distance_km'] < max_km)
            ]
            
            if not cat_races.empty:
                best_race = cat_races.loc[cat_races['duration_hours'].idxmin()]
                
                records.append({
                    'Catégorie': cat_name,
                    'Distance': f"{best_race['distance_km']:.2f} km",
                    'Temps': format_time(best_race['duration_hours'] * 3600),
                    'Allure': format_pace((best_race['duration_hours'] * 3600) / best_race['distance_km']),
                    'Date': best_race['start_date'].strftime('%d/%m/%Y'),
                    'Nom': best_race['name']
                })
        
        if records:
            df_records = pd.DataFrame(records)
            st.dataframe(df_records, use_container_width=True, hide_index=True)
            
            # Calculer VDOT moyen de ces performances
            st.markdown("### 📊 Analyse VDOT")
            
            vdots = []
            for record in records:
                # Extraire distance et temps
                dist_km = float(record['Distance'].split()[0])
                time_str = record['Temps']
                
                # Parser le temps
                if 'h' in time_str:
                    parts = time_str.replace('h', ':').replace("'", ':').replace('"', '').split(':')
                    time_sec = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                else:
                    parts = time_str.replace("'", ':').replace('"', '').split(':')
                    time_sec = int(parts[0]) * 60 + int(parts[1])
                
                vdot = predictor.calculate_vdot_from_race(dist_km * 1000, time_sec)
                vdots.append({
                    'distance': record['Catégorie'],
                    'vdot': vdot,
                    'date': record['Date']
                })
            
            df_vdots = pd.DataFrame(vdots)
            avg_vdot = df_vdots['vdot'].mean()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("VDOT moyen", f"{avg_vdot:.1f}")
                st.caption("Basé sur tes records personnels")
            
            with col2:
                # Graphique VDOT par distance
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=df_vdots['distance'],
                    y=df_vdots['vdot'],
                    marker_color='#FC4C02',
                    text=[f"{v:.1f}" for v in df_vdots['vdot']],
                    textposition='outside'
                ))
                
                fig.add_hline(
                    y=avg_vdot,
                    line_dash="dash",
                    line_color="green",
                    annotation_text=f"Moyenne: {avg_vdot:.1f}"
                )
                
                fig.update_layout(
                    title="VDOT par catégorie de distance",
                    height=300,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune course significative trouvée dans ton historique")
    else:
        st.info("Aucune activité de plus de 5 km trouvée")

# Footer
st.divider()
st.caption("""
💡 **À propos du VDOT :** Développé par Jack Daniels, le VDOT est une estimation de ta VO2max 
et permet de prédire tes performances sur différentes distances. Plus le VDOT est élevé, 
meilleure est ta capacité aérobie.
""")
