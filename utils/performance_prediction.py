"""
Module de calculs pour la prédiction de performances
Inclut VDOT, équivalences, prédictions selon D+
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import gpxpy
import gpxpy.gpx
from datetime import datetime

class PerformancePredictor:
    """Classe pour les calculs de prédiction de performances"""
    
    # Tables de référence VDOT (Daniels)
    # Format: {VDOT: {distance_m: temps_secondes}}
    VDOT_REFERENCE = {
        30: {5000: 1560, 10000: 3300, 21097: 7380, 42195: 16200},
        35: {5000: 1320, 10000: 2760, 21097: 6120, 42195: 13380},
        40: {5000: 1140, 10000: 2400, 21097: 5280, 42195: 11400},
        45: {5000: 1020, 10000: 2100, 21097: 4620, 42195: 9900},
        50: {5000: 900, 10000: 1860, 21097: 4080, 42195: 8700},
        55: {5000: 810, 10000: 1680, 21097: 3660, 42195: 7800},
        60: {5000: 735, 10000: 1530, 21097: 3300, 42195: 7020},
        65: {5000: 675, 10000: 1395, 21097: 3000, 42195: 6360},
        70: {5000: 615, 10000: 1275, 21097: 2730, 42195: 5820},
        75: {5000: 570, 10000: 1170, 21097: 2505, 42195: 5310},
        80: {5000: 525, 10000: 1080, 21097: 2310, 42195: 4860}
    }
    
    def __init__(self):
        self.vdot_values = sorted(self.VDOT_REFERENCE.keys())
    
    def calculate_vdot_from_race(self, distance_m: float, time_seconds: float) -> float:
        """
        Calcule le VDOT à partir d'une performance de course
        
        Args:
            distance_m: Distance en mètres
            time_seconds: Temps en secondes
            
        Returns:
            VDOT estimé
        """
        # Interpolation pour trouver le VDOT correspondant
        best_vdot = 30
        min_diff = float('inf')
        
        for vdot in self.vdot_values:
            predicted_time = self._predict_time_for_distance(distance_m, vdot)
            diff = abs(predicted_time - time_seconds)
            
            if diff < min_diff:
                min_diff = diff
                best_vdot = vdot
        
        # Interpolation linéaire entre deux VDOT
        if best_vdot < max(self.vdot_values):
            vdot_low = best_vdot
            vdot_high = vdot_low + 5
            
            time_low = self._predict_time_for_distance(distance_m, vdot_low)
            time_high = self._predict_time_for_distance(distance_m, vdot_high)
            
            if time_low != time_high:
                ratio = (time_seconds - time_high) / (time_low - time_high)
                return vdot_low + ratio * 5
        
        return float(best_vdot)
    
    def _predict_time_for_distance(self, distance_m: float, vdot: float) -> float:
        """Prédit le temps pour une distance donnée avec un VDOT donné"""
        
        # Trouver les deux distances de référence encadrantes
        ref_distances = sorted([5000, 10000, 21097, 42195])
        
        # Si distance exacte dans la table
        if distance_m in ref_distances and vdot in self.VDOT_REFERENCE:
            return self.VDOT_REFERENCE[vdot][distance_m]
        
        # Interpolation
        if distance_m <= 5000:
            # Extrapolation en dessous de 5km
            ref_time = self.VDOT_REFERENCE.get(vdot, {}).get(5000, 1000)
            return ref_time * (distance_m / 5000) ** 1.06
        
        elif distance_m >= 42195:
            # Extrapolation au-dessus du marathon
            ref_time = self.VDOT_REFERENCE.get(vdot, {}).get(42195, 10000)
            return ref_time * (distance_m / 42195) ** 1.06
        
        else:
            # Interpolation entre deux distances
            for i in range(len(ref_distances) - 1):
                if ref_distances[i] <= distance_m <= ref_distances[i+1]:
                    d1, d2 = ref_distances[i], ref_distances[i+1]
                    t1 = self.VDOT_REFERENCE.get(vdot, {}).get(d1, 0)
                    t2 = self.VDOT_REFERENCE.get(vdot, {}).get(d2, 0)
                    
                    # Interpolation logarithmique (plus précise pour les temps)
                    ratio = np.log(distance_m / d1) / np.log(d2 / d1)
                    return t1 + ratio * (t2 - t1)
        
        return 1000  # Valeur par défaut
    
    def predict_times_from_vdot(self, vdot: float) -> Dict[str, float]:
        """
        Prédit les temps pour différentes distances à partir d'un VDOT
        
        Args:
            vdot: Valeur VDOT
            
        Returns:
            Dictionnaire {distance_name: temps_en_secondes}
        """
        distances = {
            '1 km': 1000,
            '5 km': 5000,
            '10 km': 10000,
            'Semi-marathon': 21097.5,
            'Marathon': 42195,
            '50 km': 50000,
            '100 km': 100000
        }
        
        predictions = {}
        for name, distance_m in distances.items():
            predictions[name] = self._predict_time_for_distance(distance_m, vdot)
        
        return predictions
    
    def calculate_race_equivalences(self, distance_m: float, time_seconds: float) -> Dict[str, float]:
        """
        Calcule les temps équivalents pour d'autres distances
        
        Args:
            distance_m: Distance de référence en mètres
            time_seconds: Temps de référence en secondes
            
        Returns:
            Dictionnaire des équivalences
        """
        # Calculer le VDOT
        vdot = self.calculate_vdot_from_race(distance_m, time_seconds)
        
        # Prédire les temps équivalents
        return self.predict_times_from_vdot(vdot)
    
    def adjust_time_for_elevation(
        self,
        flat_time_seconds: float,
        elevation_gain_m: float,
        distance_m: float,
        runner_level: str = 'intermediate'
    ) -> float:
        """
        Ajuste le temps prédit en fonction du dénivelé
        
        Args:
            flat_time_seconds: Temps sur terrain plat
            elevation_gain_m: Dénivelé positif en mètres
            distance_m: Distance totale en mètres
            runner_level: Niveau du coureur ('beginner', 'intermediate', 'advanced')
            
        Returns:
            Temps ajusté en secondes
        """
        # Pénalités par niveau (minutes par 100m D+)
        penalties = {
            'beginner': 6.0,      # 6 min/100m
            'intermediate': 4.5,  # 4.5 min/100m
            'advanced': 3.0       # 3 min/100m
        }
        
        penalty_per_100m = penalties.get(runner_level, 4.5)
        
        # Calcul de la pénalité
        elevation_penalty_seconds = (elevation_gain_m / 100) * penalty_per_100m * 60
        
        # Facteur de réduction pour longues distances (fatigue)
        distance_km = distance_m / 1000
        fatigue_factor = 1.0 + (distance_km / 100) * 0.1  # +10% par 100km
        
        adjusted_time = flat_time_seconds + (elevation_penalty_seconds * fatigue_factor)
        
        return adjusted_time
    
    def calculate_progression_needed(
        self,
        current_time_seconds: float,
        target_time_seconds: float,
        weeks_available: int
    ) -> Dict[str, any]:
        """
        Calcule la progression nécessaire pour atteindre un objectif
        
        Args:
            current_time_seconds: Temps actuel
            target_time_seconds: Temps objectif
            weeks_available: Nombre de semaines disponibles
            
        Returns:
            Dictionnaire avec analyse de progression
        """
        time_diff_seconds = current_time_seconds - target_time_seconds
        time_diff_percent = (time_diff_seconds / current_time_seconds) * 100
        
        # Progression hebdomadaire nécessaire
        weekly_improvement_seconds = time_diff_seconds / weeks_available
        weekly_improvement_percent = time_diff_percent / weeks_available
        
        # Évaluation de la faisabilité
        # Règle générale : max 2-3% d'amélioration par mois
        max_monthly_improvement = 2.5
        monthly_improvement_needed = (weeks_available / 4.33) * weekly_improvement_percent
        
        if monthly_improvement_needed <= max_monthly_improvement:
            feasibility = "Réaliste"
            difficulty = "Facile" if monthly_improvement_needed < 1.5 else "Modéré"
        elif monthly_improvement_needed <= max_monthly_improvement * 1.5:
            feasibility = "Ambitieux"
            difficulty = "Difficile"
        else:
            feasibility = "Très ambitieux"
            difficulty = "Très difficile"
        
        return {
            'time_diff_seconds': time_diff_seconds,
            'time_diff_percent': time_diff_percent,
            'weekly_improvement_seconds': weekly_improvement_seconds,
            'weekly_improvement_percent': weekly_improvement_percent,
            'monthly_improvement_needed': monthly_improvement_needed,
            'feasibility': feasibility,
            'difficulty': difficulty
        }
    
    def analyze_gpx_elevation_profile(self, gpx_data: Dict) -> Dict[str, any]:
        """
        Analyse le profil d'élévation d'un parcours GPX
        
        Args:
            gpx_data: Données GPX avec latitudes, longitudes, altitudes
            
        Returns:
            Analyse détaillée du profil
        """
        if 'altitude' not in gpx_data or len(gpx_data['altitude']) < 2:
            return {}
        
        altitudes = np.array(gpx_data['altitude'])
        distances = np.array(gpx_data.get('distance', range(len(altitudes))))
        
        # Calculer les pentes
        slopes = []
        for i in range(1, len(altitudes)):
            delta_alt = altitudes[i] - altitudes[i-1]
            delta_dist = distances[i] - distances[i-1]
            
            if delta_dist > 0:
                slope = (delta_alt / delta_dist) * 100  # en pourcentage
                slopes.append(slope)
        
        slopes = np.array(slopes)
        
        # Catégorisation des pentes
        flat = np.sum((slopes >= -3) & (slopes <= 3))
        gentle_uphill = np.sum((slopes > 3) & (slopes <= 6))
        moderate_uphill = np.sum((slopes > 6) & (slopes <= 10))
        steep_uphill = np.sum((slopes > 10) & (slopes <= 15))
        very_steep_uphill = np.sum(slopes > 15)
        
        gentle_downhill = np.sum((slopes < -3) & (slopes >= -6))
        moderate_downhill = np.sum((slopes < -6) & (slopes >= -10))
        steep_downhill = np.sum((slopes < -10) & (slopes >= -15))
        very_steep_downhill = np.sum(slopes < -15)
        
        total_segments = len(slopes)
        
        # Calcul des distances par catégorie
        segment_distance = (distances[-1] - distances[0]) / total_segments
        
        # Dénivelé positif et négatif
        positive_elevation = np.sum(np.maximum(0, altitudes[1:] - altitudes[:-1]))
        negative_elevation = np.sum(np.maximum(0, altitudes[:-1] - altitudes[1:]))
        
        return {
            'total_distance_m': distances[-1] - distances[0],
            'positive_elevation_m': positive_elevation,
            'negative_elevation_m': negative_elevation,
            'altitude_min': np.min(altitudes),
            'altitude_max': np.max(altitudes),
            'altitude_avg': np.mean(altitudes),
            'slope_distribution': {
                'flat': {
                    'count': flat,
                    'percent': (flat / total_segments) * 100,
                    'distance_m': flat * segment_distance
                },
                'gentle_uphill': {
                    'count': gentle_uphill,
                    'percent': (gentle_uphill / total_segments) * 100,
                    'distance_m': gentle_uphill * segment_distance
                },
                'moderate_uphill': {
                    'count': moderate_uphill,
                    'percent': (moderate_uphill / total_segments) * 100,
                    'distance_m': moderate_uphill * segment_distance
                },
                'steep_uphill': {
                    'count': steep_uphill,
                    'percent': (steep_uphill / total_segments) * 100,
                    'distance_m': steep_uphill * segment_distance
                },
                'very_steep_uphill': {
                    'count': very_steep_uphill,
                    'percent': (very_steep_uphill / total_segments) * 100,
                    'distance_m': very_steep_uphill * segment_distance
                },
                'gentle_downhill': {
                    'count': gentle_downhill,
                    'percent': (gentle_downhill / total_segments) * 100,
                    'distance_m': gentle_downhill * segment_distance
                },
                'moderate_downhill': {
                    'count': moderate_downhill,
                    'percent': (moderate_downhill / total_segments) * 100,
                    'distance_m': moderate_downhill * segment_distance
                },
                'steep_downhill': {
                    'count': steep_downhill,
                    'percent': (steep_downhill / total_segments) * 100,
                    'distance_m': steep_downhill * segment_distance
                },
                'very_steep_downhill': {
                    'count': very_steep_downhill,
                    'percent': (very_steep_downhill / total_segments) * 100,
                    'distance_m': very_steep_downhill * segment_distance
                }
            },
            'average_slope': np.mean(slopes),
            'max_slope': np.max(slopes),
            'min_slope': np.min(slopes)
        }
    
    def parse_gpx_file(self, gpx_content: str) -> Dict:
        """
        Parse un fichier GPX et extrait les données d'élévation
        
        Args:
            gpx_content: Contenu du fichier GPX en string
            
        Returns:
            Dictionnaire avec les données extraites
        """
        try:
            # Parser avec gpxpy (beaucoup plus robuste)
            gpx = gpxpy.parse(gpx_content)
            
            latitudes = []
            longitudes = []
            altitudes = []
            distances = [0]
            
            prev_lat, prev_lon = None, None
            cumulative_distance = 0
            
            # Parcourir tous les tracks et segments
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        if point.elevation is not None:
                            latitudes.append(point.latitude)
                            longitudes.append(point.longitude)
                            altitudes.append(point.elevation)
                            
                            # Calcul distance
                            if prev_lat is not None and prev_lon is not None:
                                dist = self._haversine_distance(
                                    prev_lat, prev_lon, 
                                    point.latitude, point.longitude
                                )
                                cumulative_distance += dist
                            
                            distances.append(cumulative_distance)
                            prev_lat, prev_lon = point.latitude, point.longitude
            
            if len(altitudes) < 2:
                return {'error': 'Pas assez de points avec altitude trouvés (minimum 2 requis)'}
            
            return {
                'latitude': latitudes,
                'longitude': longitudes,
                'altitude': altitudes,
                'distance': distances[1:]  # Remove initial 0
            }
        
        except gpxpy.gpx.GPXException as e:
            return {'error': f'Fichier GPX invalide: {str(e)}'}
        except Exception as e:
            return {'error': f'Erreur lors de la lecture: {str(e)}'}
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance entre deux points GPS (en mètres)"""
        R = 6371000  # Rayon de la Terre en mètres
        
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)
        
        a = np.sin(delta_phi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c

def format_time(seconds: float) -> str:
    """Formate un temps en secondes vers HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h{minutes:02d}'{secs:02d}\""
    else:
        return f"{minutes}'{secs:02d}\""

def format_pace(seconds_per_km: float) -> str:
    """Formate une allure en min/km"""
    minutes = int(seconds_per_km // 60)
    secs = int(seconds_per_km % 60)
    return f"{minutes}'{secs:02d}\"/km"
