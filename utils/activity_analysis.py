"""
Module d'analyse détaillée des sorties
- Cartes interactives
- Profils d'élévation
- Analyse allure/FC par segment
- Comparaisons entre sorties
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import requests


class ActivityAnalyzer:
    """Analyse détaillée d'une activité"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://www.strava.com/api/v3"
    
    def get_activity_streams(self, activity_id, stream_types=None):
        """
        Récupère les streams (données détaillées) d'une activité
        
        Args:
            activity_id: ID de l'activité Strava
            stream_types: Liste des types de streams à récupérer
                         ['time', 'latlng', 'distance', 'altitude', 
                          'velocity_smooth', 'heartrate', 'cadence', 'watts']
        
        Returns:
            dict avec les streams
        """
        if stream_types is None:
            stream_types = ['time', 'latlng', 'distance', 'altitude', 
                           'velocity_smooth', 'heartrate']
        
        url = f"{self.base_url}/activities/{activity_id}/streams"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            'keys': ','.join(stream_types),
            'key_by_type': True
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erreur récupération streams: {e}")
            return None
    
    def create_elevation_profile(self, streams, activity_info=None):
        """
        Crée un profil d'élévation interactif
        
        Args:
            streams: Données streams de l'activité
            activity_info: Infos générales de l'activité (optionnel)
        
        Returns:
            Figure Plotly
        """
        if not streams or 'distance' not in streams or 'altitude' not in streams:
            return None
        
        distance_km = np.array(streams['distance']['data']) / 1000
        altitude = np.array(streams['altitude']['data'])
        
        # Calcul de la pente par segment
        gradient = np.gradient(altitude, distance_km * 1000) * 100
        gradient = np.clip(gradient, -30, 30)  # Limite à ±30%
        
        fig = go.Figure()
        
        # Profil d'élévation avec gradient de couleur selon la pente
        fig.add_trace(go.Scatter(
            x=distance_km,
            y=altitude,
            mode='lines',
            name='Altitude',
            line=dict(color='#00A8E8', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 168, 232, 0.3)',
            hovertemplate='<b>Distance</b>: %{x:.2f} km<br>' +
                          '<b>Altitude</b>: %{y:.0f} m<br>' +
                          '<extra></extra>'
        ))
        
        # Zones de pente
        # Descente forte (< -8%)
        fig.add_trace(go.Scatter(
            x=distance_km[gradient < -8],
            y=altitude[gradient < -8],
            mode='markers',
            name='Descente forte (< -8%)',
            marker=dict(color='blue', size=3),
            hovertemplate='<b>Pente</b>: %{text:.1f}%<extra></extra>',
            text=gradient[gradient < -8]
        ))
        
        # Montée forte (> 8%)
        fig.add_trace(go.Scatter(
            x=distance_km[gradient > 8],
            y=altitude[gradient > 8],
            mode='markers',
            name='Montée forte (> 8%)',
            marker=dict(color='red', size=3),
            hovertemplate='<b>Pente</b>: %{text:.1f}%<extra></extra>',
            text=gradient[gradient > 8]
        ))
        
        title = "Profil d'élévation"
        if activity_info:
            title += f" - {activity_info.get('name', '')}"
        
        fig.update_layout(
            title=title,
            xaxis_title="Distance (km)",
            yaxis_title="Altitude (m)",
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_pace_hr_analysis(self, streams, activity_info=None):
        """
        Crée un graphique combinant allure et FC par segment
        
        Args:
            streams: Données streams
            activity_info: Infos activité
        
        Returns:
            Figure Plotly
        """
        if not streams or 'distance' not in streams:
            return None
        
        distance_km = np.array(streams['distance']['data']) / 1000
        
        fig = go.Figure()
        
        # Vitesse (convertie en allure min/km)
        if 'velocity_smooth' in streams:
            velocity = np.array(streams['velocity_smooth']['data'])  # m/s
            # Conversion en allure (min/km)
            pace = np.where(velocity > 0, 1000 / (velocity * 60), 0)
            pace = np.clip(pace, 0, 20)  # Limite à 20 min/km max
            
            fig.add_trace(go.Scatter(
                x=distance_km,
                y=pace,
                mode='lines',
                name='Allure',
                line=dict(color='#FC4C02', width=2),
                yaxis='y',
                hovertemplate='<b>Allure</b>: %{y:.2f} min/km<extra></extra>'
            ))
        
        # Fréquence cardiaque
        if 'heartrate' in streams:
            hr = np.array(streams['heartrate']['data'])
            
            fig.add_trace(go.Scatter(
                x=distance_km,
                y=hr,
                mode='lines',
                name='FC',
                line=dict(color='red', width=2),
                yaxis='y2',
                hovertemplate='<b>FC</b>: %{y:.0f} bpm<extra></extra>'
            ))
        
        title = "Allure et fréquence cardiaque"
        if activity_info:
            title += f" - {activity_info.get('name', '')}"
        
        fig.update_layout(
            title=title,
            xaxis_title="Distance (km)",
            yaxis=dict(
                title="Allure (min/km)",
                side='left'
            ),
            yaxis2=dict(
                title="FC (bpm)",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    def create_interactive_map(self, streams, activity_info=None):
        """
        Crée une carte interactive du parcours
        
        Args:
            streams: Données streams avec latlng
            activity_info: Infos activité
        
        Returns:
            Figure Plotly (carte)
        """
        if not streams or 'latlng' not in streams:
            return None
        
        coords = np.array(streams['latlng']['data'])
        lats = coords[:, 0]
        lons = coords[:, 1]
        
        # Couleur selon l'altitude si disponible
        color_data = None
        color_label = None
        
        if 'altitude' in streams:
            color_data = streams['altitude']['data']
            color_label = 'Altitude (m)'
        elif 'velocity_smooth' in streams:
            velocity = np.array(streams['velocity_smooth']['data'])
            color_data = velocity * 3.6  # Conversion en km/h
            color_label = 'Vitesse (km/h)'
        
        fig = go.Figure()
        
        if color_data is not None:
            fig.add_trace(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='lines',
                line=dict(width=3, color=color_data, colorscale='Viridis'),
                marker=dict(size=5, colorbar=dict(title=color_label)),
                hovertemplate='<b>Lat</b>: %{lat:.5f}<br>' +
                              '<b>Lon</b>: %{lon:.5f}<br>' +
                              f'<b>{color_label}</b>: %{{marker.color:.1f}}<br>' +
                              '<extra></extra>'
            ))
        else:
            fig.add_trace(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='lines',
                line=dict(width=3, color='#FC4C02'),
                hovertemplate='<b>Lat</b>: %{lat:.5f}<br>' +
                              '<b>Lon</b>: %{lon:.5f}<br>' +
                              '<extra></extra>'
            ))
        
        # Points de départ et d'arrivée
        fig.add_trace(go.Scattermapbox(
            lat=[lats[0]],
            lon=[lons[0]],
            mode='markers',
            marker=dict(size=15, color='green'),
            name='Départ',
            hovertemplate='<b>Départ</b><extra></extra>'
        ))
        
        fig.add_trace(go.Scattermapbox(
            lat=[lats[-1]],
            lon=[lons[-1]],
            mode='markers',
            marker=dict(size=15, color='red'),
            name='Arrivée',
            hovertemplate='<b>Arrivée</b><extra></extra>'
        ))
        
        # Centre de la carte
        center_lat = (lats.min() + lats.max()) / 2
        center_lon = (lons.min() + lons.max()) / 2
        
        # Calcul du zoom optimal
        lat_range = lats.max() - lats.min()
        lon_range = lons.max() - lons.min()
        max_range = max(lat_range, lon_range)
        
        if max_range < 0.01:
            zoom = 14
        elif max_range < 0.05:
            zoom = 12
        elif max_range < 0.1:
            zoom = 11
        elif max_range < 0.5:
            zoom = 9
        else:
            zoom = 8
        
        title = "Parcours"
        if activity_info:
            title += f" - {activity_info.get('name', '')}"
        
        fig.update_layout(
            title=title,
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=zoom
            ),
            height=500,
            showlegend=True
        )
        
        return fig
    
    def analyze_segments(self, streams, segment_distance_km=1.0):
        """
        Analyse l'activité par segments (ex: tous les 1 km)
        
        Args:
            streams: Données streams
            segment_distance_km: Taille des segments en km
        
        Returns:
            DataFrame avec analyse par segment
        """
        if not streams or 'distance' not in streams:
            return None
        
        distance = np.array(streams['distance']['data']) / 1000  # en km
        time_data = np.array(streams['time']['data']) if 'time' in streams else None
        altitude = np.array(streams['altitude']['data']) if 'altitude' in streams else None
        hr = np.array(streams['heartrate']['data']) if 'heartrate' in streams else None
        velocity = np.array(streams['velocity_smooth']['data']) if 'velocity_smooth' in streams else None
        
        # Création des segments
        max_distance = distance[-1]
        segments = []
        
        current_dist = 0
        while current_dist < max_distance:
            next_dist = current_dist + segment_distance_km
            
            # Indices pour ce segment
            mask = (distance >= current_dist) & (distance < next_dist)
            
            if not mask.any():
                current_dist = next_dist
                continue
            
            segment_data = {
                'segment_start_km': current_dist,
                'segment_end_km': min(next_dist, max_distance),
                'distance_km': min(segment_distance_km, max_distance - current_dist)
            }
            
            # Temps
            if time_data is not None:
                segment_time = time_data[mask][-1] - time_data[mask][0]
                segment_data['time_min'] = segment_time / 60
                segment_data['pace_min_km'] = (segment_time / 60) / segment_data['distance_km']
            
            # Dénivelé
            if altitude is not None:
                segment_alt = altitude[mask]
                segment_data['elevation_gain_m'] = max(0, segment_alt[-1] - segment_alt[0])
                segment_data['avg_altitude_m'] = segment_alt.mean()
                segment_data['gradient_pct'] = (segment_data['elevation_gain_m'] / 
                                               (segment_data['distance_km'] * 1000)) * 100
            
            # FC
            if hr is not None:
                segment_hr = hr[mask]
                segment_data['avg_hr'] = segment_hr.mean()
                segment_data['max_hr'] = segment_hr.max()
            
            # Vitesse
            if velocity is not None:
                segment_vel = velocity[mask]
                segment_data['avg_speed_kmh'] = segment_vel.mean() * 3.6
                segment_data['max_speed_kmh'] = segment_vel.max() * 3.6
            
            segments.append(segment_data)
            current_dist = next_dist
        
        return pd.DataFrame(segments)
    
    def compare_similar_activities(self, activity1_streams, activity2_streams, 
                                   activity1_info, activity2_info):
        """
        Compare deux sorties similaires
        
        Args:
            activity1_streams: Streams activité 1
            activity2_streams: Streams activité 2
            activity1_info: Infos activité 1
            activity2_info: Infos activité 2
        
        Returns:
            dict avec métriques de comparaison
        """
        comparison = {
            'activity1': activity1_info.get('name', 'Activité 1'),
            'activity2': activity2_info.get('name', 'Activité 2'),
            'metrics': {}
        }
        
        # Distance
        dist1 = activity1_info.get('distance', 0) / 1000
        dist2 = activity2_info.get('distance', 0) / 1000
        comparison['metrics']['distance_km'] = {
            'activity1': dist1,
            'activity2': dist2,
            'diff': dist2 - dist1,
            'diff_pct': ((dist2 - dist1) / dist1 * 100) if dist1 > 0 else 0
        }
        
        # Dénivelé
        elev1 = activity1_info.get('total_elevation_gain', 0)
        elev2 = activity2_info.get('total_elevation_gain', 0)
        comparison['metrics']['elevation_m'] = {
            'activity1': elev1,
            'activity2': elev2,
            'diff': elev2 - elev1,
            'diff_pct': ((elev2 - elev1) / elev1 * 100) if elev1 > 0 else 0
        }
        
        # Temps
        time1 = activity1_info.get('moving_time', 0) / 60
        time2 = activity2_info.get('moving_time', 0) / 60
        comparison['metrics']['time_min'] = {
            'activity1': time1,
            'activity2': time2,
            'diff': time2 - time1,
            'diff_pct': ((time2 - time1) / time1 * 100) if time1 > 0 else 0
        }
        
        # Vitesse moyenne
        speed1 = activity1_info.get('average_speed', 0) * 3.6
        speed2 = activity2_info.get('average_speed', 0) * 3.6
        comparison['metrics']['avg_speed_kmh'] = {
            'activity1': speed1,
            'activity2': speed2,
            'diff': speed2 - speed1,
            'diff_pct': ((speed2 - speed1) / speed1 * 100) if speed1 > 0 else 0
        }
        
        # FC moyenne
        hr1 = activity1_info.get('average_heartrate', 0)
        hr2 = activity2_info.get('average_heartrate', 0)
        if hr1 > 0 and hr2 > 0:
            comparison['metrics']['avg_hr'] = {
                'activity1': hr1,
                'activity2': hr2,
                'diff': hr2 - hr1,
                'diff_pct': ((hr2 - hr1) / hr1 * 100)
            }
        
        return comparison


def get_similar_activities(df, reference_activity, tolerance_pct=20):
    """
    Trouve des activités similaires à une activité de référence
    
    Args:
        df: DataFrame de toutes les activités
        reference_activity: Ligne du DataFrame (activité de référence)
        tolerance_pct: Tolérance en % pour distance et D+
    
    Returns:
        DataFrame des activités similaires
    """
    ref_distance = reference_activity['distance_km']
    ref_elevation = reference_activity['elevation_gain_m']
    
    # Calcul des limites
    dist_min = ref_distance * (1 - tolerance_pct / 100)
    dist_max = ref_distance * (1 + tolerance_pct / 100)
    elev_min = ref_elevation * (1 - tolerance_pct / 100)
    elev_max = ref_elevation * (1 + tolerance_pct / 100)
    
    # Filtrage
    similar = df[
        (df['distance_km'] >= dist_min) &
        (df['distance_km'] <= dist_max) &
        (df['elevation_gain_m'] >= elev_min) &
        (df['elevation_gain_m'] <= elev_max)
    ].copy()
    
    # Tri par date (plus récent d'abord)
    similar = similar.sort_values('start_date', ascending=False)
    
    return similar
