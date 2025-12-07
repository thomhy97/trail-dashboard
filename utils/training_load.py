"""
Module de calcul de charge d'entraînement
- TRIMP (Training Impulse)
- TSS (Training Stress Score)
- ATL/CTL/TSB (Acute/Chronic Training Load, Training Stress Balance)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TrainingLoadCalculator:
    """Calcule les métriques de charge d'entraînement"""
    
    def __init__(self, fc_max=190, fc_repos=50, seuil_fc=None):
        """
        Args:
            fc_max: Fréquence cardiaque maximale
            fc_repos: Fréquence cardiaque au repos
            seuil_fc: FC au seuil lactique (si None, estimée à 85% FCmax)
        """
        self.fc_max = fc_max
        self.fc_repos = fc_repos
        self.seuil_fc = seuil_fc or int(fc_max * 0.85)
        self.fc_reserve = fc_max - fc_repos
    
    def calculate_trimp(self, duration_minutes, avg_hr, gender='M'):
        """
        Calcule le TRIMP (Training Impulse) - Méthode Banister
        
        Args:
            duration_minutes: Durée de l'entraînement en minutes
            avg_hr: Fréquence cardiaque moyenne
            gender: 'M' ou 'F' (facteur de pondération différent)
        
        Returns:
            TRIMP score
        """
        if pd.isna(avg_hr) or avg_hr == 0:
            return 0
        
        # Calcul de l'intensité relative (HR Reserve)
        hr_ratio = (avg_hr - self.fc_repos) / self.fc_reserve
        hr_ratio = max(0, min(1, hr_ratio))  # Clamp entre 0 et 1
        
        # Facteur exponentiel selon le genre
        y_factor = 1.92 if gender == 'M' else 1.67
        
        # TRIMP = durée × HR ratio × 0.64 × e^(y × HR ratio)
        trimp = duration_minutes * hr_ratio * 0.64 * np.exp(y_factor * hr_ratio)
        
        return round(trimp, 1)
    
    def calculate_tss_hr(self, duration_minutes, avg_hr, normalized_power=None):
        """
        Calcule le TSS basé sur la fréquence cardiaque
        
        TSS = (durée_sec × FC_norm × IF) / (FC_seuil × 3600) × 100
        où IF (Intensity Factor) = FC_norm / FC_seuil
        
        Args:
            duration_minutes: Durée en minutes
            avg_hr: FC moyenne
            normalized_power: Non utilisé ici (pour compatibilité)
        
        Returns:
            TSS score
        """
        if pd.isna(avg_hr) or avg_hr == 0:
            return 0
        
        duration_hours = duration_minutes / 60
        
        # Intensity Factor
        intensity_factor = avg_hr / self.seuil_fc
        intensity_factor = max(0, min(2, intensity_factor))  # Clamp
        
        # TSS = durée_h × IF^2 × 100
        tss = duration_hours * (intensity_factor ** 2) * 100
        
        return round(tss, 1)
    
    def calculate_tss_simplified(self, duration_minutes, avg_hr=None, intensity='moderate'):
        """
        TSS simplifié basé sur la durée et l'intensité perçue
        Utile quand on n'a pas de données FC
        
        Args:
            duration_minutes: Durée
            avg_hr: FC moyenne (optionnel)
            intensity: 'easy', 'moderate', 'hard', 'very_hard'
        
        Returns:
            TSS estimé
        """
        # Facteurs d'intensité standards
        intensity_factors = {
            'easy': 0.65,       # IF ~ 0.65 → 42 TSS/h
            'moderate': 0.75,   # IF ~ 0.75 → 56 TSS/h
            'hard': 0.85,       # IF ~ 0.85 → 72 TSS/h
            'very_hard': 0.95,  # IF ~ 0.95 → 90 TSS/h
            'max': 1.05         # IF ~ 1.05 → 110 TSS/h
        }
        
        # Si on a la FC, on calcule l'IF réel
        if avg_hr and avg_hr > 0:
            if_value = avg_hr / self.seuil_fc
        else:
            if_value = intensity_factors.get(intensity, 0.75)
        
        duration_hours = duration_minutes / 60
        tss = duration_hours * (if_value ** 2) * 100
        
        return round(tss, 1)
    
    def calculate_atl_ctl_tsb(self, df, tss_column='tss'):
        """
        Calcule ATL (Acute Training Load), CTL (Chronic Training Load) et TSB
        
        ATL = Moyenne mobile exponentielle sur 7 jours (fatigue)
        CTL = Moyenne mobile exponentielle sur 42 jours (forme)
        TSB = CTL - ATL (fraîcheur/équilibre)
        
        TSB positif = frais, bien récupéré
        TSB négatif = fatigué, peut être en surcharge
        
        Args:
            df: DataFrame avec colonnes 'start_date' et tss_column
            tss_column: Nom de la colonne TSS
        
        Returns:
            DataFrame avec colonnes ATL, CTL, TSB ajoutées
        """
        df = df.copy()
        df = df.sort_values('start_date')
        
        # Création d'un index journalier complet (pour gérer les jours sans activité)
        date_range = pd.date_range(
            start=df['start_date'].min().date(),
            end=df['start_date'].max().date(),
            freq='D'
        )
        
        # Agrégation du TSS par jour
        df['date'] = df['start_date'].dt.date
        daily_tss = df.groupby('date')[tss_column].sum().reindex(
            date_range.date, 
            fill_value=0
        )
        
        # Calcul des EWM (Exponentially Weighted Moving Average)
        # ATL (7 jours) → α = 2/(7+1) ≈ 0.25
        # CTL (42 jours) → α = 2/(42+1) ≈ 0.047
        
        atl = daily_tss.ewm(span=7, adjust=False).mean()
        ctl = daily_tss.ewm(span=42, adjust=False).mean()
        tsb = ctl - atl
        
        # Création du DataFrame de résultats
        load_df = pd.DataFrame({
            'date': date_range,
            'daily_tss': daily_tss.values,
            'ATL': atl.round(1),
            'CTL': ctl.round(1),
            'TSB': tsb.round(1)
        })
        
        return load_df
    
    def interpret_tsb(self, tsb_value):
        """
        Interprète la valeur TSB
        
        Args:
            tsb_value: Valeur TSB
        
        Returns:
            dict avec statut et recommandation
        """
        if tsb_value > 25:
            return {
                'status': 'Très frais',
                'color': 'green',
                'recommendation': 'Prêt pour une grosse séance ou une course importante'
            }
        elif tsb_value > 5:
            return {
                'status': 'Frais',
                'color': 'lightgreen',
                'recommendation': 'Bon équilibre, continue comme ça'
            }
        elif tsb_value > -10:
            return {
                'status': 'Équilibré',
                'color': 'orange',
                'recommendation': 'Zone optimale pour progresser'
            }
        elif tsb_value > -30:
            return {
                'status': 'Fatigué',
                'color': 'red',
                'recommendation': 'Attention à la fatigue, envisage une semaine plus légère'
            }
        else:
            return {
                'status': 'Très fatigué',
                'color': 'darkred',
                'recommendation': '⚠️ Risque de surcharge, repos nécessaire !'
            }
    
    def detect_overreaching(self, load_df, threshold_days=7, tsb_threshold=-30):
        """
        Détecte les périodes de surcharge potentielle
        
        Args:
            load_df: DataFrame avec ATL/CTL/TSB
            threshold_days: Nombre de jours consécutifs de TSB négatif
            tsb_threshold: Seuil de TSB considéré comme critique
        
        Returns:
            Liste des périodes à risque
        """
        warnings = []
        
        # Détection de TSB très négatif
        critical_periods = load_df[load_df['TSB'] < tsb_threshold]
        
        if len(critical_periods) > 0:
            for _, row in critical_periods.iterrows():
                warnings.append({
                    'date': row['date'],
                    'tsb': row['TSB'],
                    'type': 'critical',
                    'message': f"TSB critique ({row['TSB']:.1f}) - Risque de surcharge"
                })
        
        # Détection de pics d'ATL (fatigue aiguë)
        atl_90th = load_df['ATL'].quantile(0.9)
        high_atl = load_df[load_df['ATL'] > atl_90th]
        
        for _, row in high_atl.iterrows():
            if row['TSB'] < -10:
                warnings.append({
                    'date': row['date'],
                    'atl': row['ATL'],
                    'tsb': row['TSB'],
                    'type': 'high_load',
                    'message': f"Charge élevée (ATL: {row['ATL']:.1f})"
                })
        
        return warnings
    
    def calculate_ramp_rate(self, load_df, window=7):
        """
        Calcule le taux d'augmentation de la CTL (rampe)
        
        Une augmentation > 5-8 CTL/semaine peut être risquée
        
        Args:
            load_df: DataFrame avec CTL
            window: Fenêtre en jours pour calculer la variation
        
        Returns:
            DataFrame avec ramp_rate
        """
        load_df = load_df.copy()
        load_df['ctl_change'] = load_df['CTL'].diff(window)
        load_df['ramp_rate'] = (load_df['ctl_change'] / window * 7).round(2)
        
        return load_df


def estimate_intensity_from_data(row, calculator):
    """
    Estime l'intensité d'une sortie basée sur les données disponibles
    
    Args:
        row: Ligne du DataFrame avec les données de la sortie
        calculator: Instance de TrainingLoadCalculator
    
    Returns:
        Intensité estimée ('easy', 'moderate', 'hard', 'very_hard')
    """
    # Si on a la FC
    if 'average_heartrate' in row and pd.notna(row['average_heartrate']) and row['average_heartrate'] > 0:
        hr_percent = row['average_heartrate'] / calculator.fc_max
        
        if hr_percent < 0.70:
            return 'easy'
        elif hr_percent < 0.80:
            return 'moderate'
        elif hr_percent < 0.90:
            return 'hard'
        else:
            return 'very_hard'
    
    # Sinon, basé sur la vitesse et le D+
    if 'speed_kmh' in row and 'deniv_percent' in row:
        # Sortie longue et lente
        if row['distance_km'] > 20 and row['speed_kmh'] < 8:
            return 'easy'
        # Beaucoup de D+ = plus dur
        elif row['deniv_percent'] > 10:
            return 'hard'
        # Sortie courte et rapide
        elif row['distance_km'] < 10 and row['speed_kmh'] > 11:
            return 'hard'
        else:
            return 'moderate'
    
    # Par défaut
    return 'moderate'


# Fonctions utilitaires pour Streamlit
def add_training_load_metrics(df, fc_max=190, fc_repos=50, gender='M'):
    """
    Ajoute toutes les métriques de charge d'entraînement au DataFrame
    
    Args:
        df: DataFrame des activités
        fc_max: FC max
        fc_repos: FC repos
        gender: Genre pour le TRIMP
    
    Returns:
        DataFrame enrichi
    """
    calculator = TrainingLoadCalculator(fc_max, fc_repos)
    
    df = df.copy()
    
    # Calcul TRIMP
    df['trimp'] = df.apply(
        lambda row: calculator.calculate_trimp(
            row['duration_hours'] * 60,
            row.get('average_heartrate', 0),
            gender
        ) if pd.notna(row.get('average_heartrate', 0)) else 0,
        axis=1
    )
    
    # Calcul TSS
    df['tss'] = df.apply(
        lambda row: calculator.calculate_tss_hr(
            row['duration_hours'] * 60,
            row.get('average_heartrate', 0)
        ) if pd.notna(row.get('average_heartrate', 0)) else calculator.calculate_tss_simplified(
            row['duration_hours'] * 60,
            intensity=estimate_intensity_from_data(row, calculator)
        ),
        axis=1
    )
    
    return df
