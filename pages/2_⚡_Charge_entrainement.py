"""
Page d'analyse de charge d'entraînement (TSS, TRIMP, ATL/CTL/TSB)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
sys.path.append('..')

from utils.training_load import (
    TrainingLoadCalculator, 
    add_training_load_metrics
)


def show_training_load_page(df):
    """
    Page principale d'analyse de charge d'entraînement
    
    Args:
        df: DataFrame des activités avec métriques de base
    """
    st.header("⚡ Charge d'entraînement")
    
    # Configuration personnalisée
    with st.sidebar:
        st.subheader("⚙️ Configuration")
        
        fc_max = st.number_input(
            "FC Max (bpm)",
            min_value=150,
            max_value=220,
            value=190,
            help="Ta fréquence cardiaque maximale"
        )
        
        fc_repos = st.number_input(
            "FC Repos (bpm)",
            min_value=30,
            max_value=80,
            value=50,
            help="Ta fréquence cardiaque au repos"
        )
        
        gender = st.selectbox(
            "Genre",
            options=['M', 'F'],
            help="Pour le calcul du TRIMP"
        )
        
        st.divider()
        
        # Période d'analyse
        analysis_period = st.selectbox(
            "Période d'analyse",
            ["3 derniers mois", "6 derniers mois", "12 derniers mois", "Tout"]
        )
    
    # Filtrage de la période
    now = datetime.now()
    if analysis_period == "3 derniers mois":
        cutoff_date = now - timedelta(days=90)
    elif analysis_period == "6 derniers mois":
        cutoff_date = now - timedelta(days=180)
    elif analysis_period == "12 derniers mois":
        cutoff_date = now - timedelta(days=365)
    else:
        cutoff_date = df['start_date'].min()
    
    df_filtered = df[df['start_date'] >= cutoff_date].copy()
    
    if df_filtered.empty:
        st.warning("Aucune donnée pour cette période")
        return
    
    # Calcul des métriques de charge
    with st.spinner("Calcul des métriques de charge..."):
        df_with_load = add_training_load_metrics(df_filtered, fc_max, fc_repos, gender)
        
        calculator = TrainingLoadCalculator(fc_max, fc_repos)
        load_df = calculator.calculate_atl_ctl_tsb(df_with_load, 'tss')
    
    # Métriques clés actuelles
    st.subheader("📊 État actuel")
    
    latest = load_df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "ATL (Fatigue)",
            f"{latest['ATL']:.1f}",
            help="Acute Training Load - Charge des 7 derniers jours"
        )
    
    with col2:
        st.metric(
            "CTL (Forme)",
            f"{latest['CTL']:.1f}",
            help="Chronic Training Load - Charge des 42 derniers jours"
        )
    
    with col3:
        tsb_interpretation = calculator.interpret_tsb(latest['TSB'])
        delta_color = "normal"
        if latest['TSB'] > 5:
            delta_color = "normal"
        elif latest['TSB'] < -10:
            delta_color = "inverse"
        
        st.metric(
            "TSB (Fraîcheur)",
            f"{latest['TSB']:.1f}",
            delta=tsb_interpretation['status'],
            delta_color=delta_color,
            help="Training Stress Balance - CTL - ATL"
        )
    
    with col4:
        total_tss_week = df_with_load[
            df_with_load['start_date'] >= (now - timedelta(days=7))
        ]['tss'].sum()
        
        st.metric(
            "TSS cette semaine",
            f"{total_tss_week:.0f}",
            help="Training Stress Score cumulé sur 7 jours"
        )
    
    # Message de statut
    st.info(f"**{tsb_interpretation['status']}** : {tsb_interpretation['recommendation']}")
    
    st.divider()
    
    # Graphique ATL/CTL/TSB
    st.subheader("📈 Évolution ATL / CTL / TSB")
    
    fig = go.Figure()
    
    # ATL (Fatigue) - 7 jours
    fig.add_trace(go.Scatter(
        x=load_df['date'],
        y=load_df['ATL'],
        name='ATL (Fatigue)',
        line=dict(color='#FF6B6B', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 107, 0.1)'
    ))
    
    # CTL (Forme) - 42 jours
    fig.add_trace(go.Scatter(
        x=load_df['date'],
        y=load_df['CTL'],
        name='CTL (Forme)',
        line=dict(color='#4ECDC4', width=2),
        fill='tozeroy',
        fillcolor='rgba(78, 205, 196, 0.1)'
    ))
    
    # TSB (Fraîcheur)
    colors = ['green' if tsb > 5 else 'orange' if tsb > -10 else 'red' 
              for tsb in load_df['TSB']]
    
    fig.add_trace(go.Bar(
        x=load_df['date'],
        y=load_df['TSB'],
        name='TSB (Fraîcheur)',
        marker_color=colors,
        opacity=0.6
    ))
    
    # Ligne de référence TSB = 0
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="Charge / Score",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Explications
    with st.expander("ℹ️ Comprendre ATL / CTL / TSB"):
        st.markdown("""
        ### ATL (Acute Training Load) - Fatigue
        - Moyenne exponentielle mobile sur **7 jours**
        - Représente la **fatigue récente**
        - Plus c'est élevé, plus tu es fatigué
        
        ### CTL (Chronic Training Load) - Forme
        - Moyenne exponentielle mobile sur **42 jours**
        - Représente ta **forme générale** / capacité d'entraînement
        - Plus c'est élevé, plus tu es entraîné
        
        ### TSB (Training Stress Balance) - Fraîcheur
        - **TSB = CTL - ATL**
        - Indique ton niveau de **fraîcheur / récupération**
        
        **Interprétation du TSB :**
        - 🟢 **TSB > +25** : Très frais, prêt pour une course
        - 🟢 **TSB +5 à +25** : Frais, bon équilibre
        - 🟠 **TSB -10 à +5** : Zone optimale pour progresser
        - 🔴 **TSB -30 à -10** : Fatigué, attention
        - 🔴 **TSB < -30** : Très fatigué, risque de surcharge !
        """)
    
    st.divider()
    
    # TSS hebdomadaire
    st.subheader("📊 TSS hebdomadaire")
    
    # Agrégation par semaine
    df_weekly = df_with_load.copy()
    df_weekly['week'] = df_weekly['start_date'].dt.to_period('W').astype(str)
    
    weekly_tss = df_weekly.groupby('week').agg({
        'tss': 'sum',
        'trimp': 'sum',
        'distance_km': 'sum',
        'elevation_gain_m': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_tss = px.bar(
            weekly_tss,
            x='week',
            y='tss',
            title='TSS par semaine',
            labels={'week': 'Semaine', 'tss': 'TSS'},
            color='tss',
            color_continuous_scale='Reds'
        )
        fig_tss.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_tss, use_container_width=True)
    
    with col2:
        fig_trimp = px.bar(
            weekly_tss,
            x='week',
            y='trimp',
            title='TRIMP par semaine',
            labels={'week': 'Semaine', 'trimp': 'TRIMP'},
            color='trimp',
            color_continuous_scale='Blues'
        )
        fig_trimp.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_trimp, use_container_width=True)
    
    st.divider()
    
    # Détection de surcharge
    st.subheader("⚠️ Alertes de surcharge")
    
    warnings = calculator.detect_overreaching(load_df, threshold_days=7, tsb_threshold=-30)
    
    if warnings:
        st.warning(f"{len(warnings)} période(s) à risque détectée(s)")
        
        warnings_df = pd.DataFrame(warnings)
        warnings_df['date'] = pd.to_datetime(warnings_df['date'])
        warnings_df = warnings_df.sort_values('date', ascending=False)
        
        for _, warning in warnings_df.head(5).iterrows():
            date_str = warning['date'].strftime('%Y-%m-%d')
            st.error(f"**{date_str}** : {warning['message']}")
    else:
        st.success("✅ Aucune période de surcharge détectée récemment")
    
    st.divider()
    
    # Taux de progression CTL (ramp rate)
    st.subheader("📊 Taux de progression (CTL Ramp Rate)")
    
    load_df_ramp = calculator.calculate_ramp_rate(load_df, window=7)
    
    fig_ramp = go.Figure()
    
    fig_ramp.add_trace(go.Scatter(
        x=load_df_ramp['date'],
        y=load_df_ramp['ramp_rate'],
        mode='lines',
        name='Ramp Rate',
        line=dict(color='purple', width=2)
    ))
    
    # Zones de sécurité
    fig_ramp.add_hrect(
        y0=-5, y1=5,
        fillcolor="green", opacity=0.1,
        line_width=0,
        annotation_text="Zone sécurisée",
        annotation_position="top left"
    )
    
    fig_ramp.add_hrect(
        y0=5, y1=8,
        fillcolor="orange", opacity=0.1,
        line_width=0,
        annotation_text="Progression rapide",
        annotation_position="top left"
    )
    
    fig_ramp.add_hrect(
        y0=8, y1=20,
        fillcolor="red", opacity=0.1,
        line_width=0,
        annotation_text="⚠️ Trop rapide !",
        annotation_position="top left"
    )
    
    fig_ramp.update_layout(
        title="Variation de CTL par semaine",
        xaxis_title="Date",
        yaxis_title="Changement CTL (points/semaine)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_ramp, use_container_width=True)
    
    st.info("""
    **Recommandations :**
    - 🟢 **-5 à +5 points/semaine** : Progression safe
    - 🟠 **+5 à +8 points/semaine** : Progression rapide mais gérable
    - 🔴 **> +8 points/semaine** : Risque de blessure, ralentis !
    """)
    
    st.divider()
    
    # Tableau des dernières sorties avec métriques
    st.subheader("🏃 Dernières sorties avec métriques de charge")
    
    display_df = df_with_load[
        ['start_date', 'name', 'distance_km', 'elevation_gain_m', 
         'duration_hours', 'tss', 'trimp']
    ].copy()
    
    display_df.columns = ['Date', 'Nom', 'Distance (km)', 'D+ (m)', 
                          'Durée (h)', 'TSS', 'TRIMP']
    
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    display_df = display_df.round(1)
    display_df = display_df.sort_values('Date', ascending=False).head(10)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    st.set_page_config(page_title="Charge d'entraînement", page_icon="⚡", layout="wide")
    
    # Pour tester localement
    st.title("⚡ Analyse de charge d'entraînement")
    st.info("Cette page nécessite des données d'activités pour fonctionner")
