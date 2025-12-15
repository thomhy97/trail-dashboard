"""
Client Supabase pour la gestion de la base de données
"""

import os
from supabase import create_client, Client
from typing import Optional, Dict, List
import json
from datetime import datetime, timedelta

class SupabaseDB:
    """Classe pour gérer toutes les interactions avec Supabase"""
    
    def __init__(self):
        """Initialise la connexion Supabase"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL et SUPABASE_KEY doivent être définis dans les variables d'environnement")
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    # ===== UTILISATEURS =====
    
    def create_or_update_user(self, strava_id: str, user_data: Dict) -> Dict:
        """
        Crée ou met à jour un utilisateur
        
        Args:
            strava_id: ID Strava unique
            user_data: Données utilisateur (nom, email, avatar, etc.)
        
        Returns:
            Données utilisateur créées/mises à jour
        """
        try:
            # Vérifier si l'utilisateur existe
            result = self.client.table('users').select('*').eq('strava_id', strava_id).execute()
            
            user_record = {
                'strava_id': strava_id,
                'name': user_data.get('firstname', '') + ' ' + user_data.get('lastname', ''),
                'email': user_data.get('email'),
                'avatar_url': user_data.get('profile'),
                'updated_at': datetime.now().isoformat()
            }
            
            if result.data:
                # Mise à jour
                response = self.client.table('users').update(user_record).eq('strava_id', strava_id).execute()
            else:
                # Création
                user_record['created_at'] = datetime.now().isoformat()
                response = self.client.table('users').insert(user_record).execute()
            
            return response.data[0] if response.data else None
        
        except Exception as e:
            print(f"Erreur create_or_update_user: {e}")
            return None
    
    def get_user(self, strava_id: str) -> Optional[Dict]:
        """Récupère un utilisateur par son ID Strava"""
        try:
            result = self.client.table('users').select('*').eq('strava_id', strava_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur get_user: {e}")
            return None
    
    # ===== TOKENS STRAVA =====
    
    def save_strava_token(self, strava_id: str, access_token: str, refresh_token: str, expires_at: int):
        """
        Sauvegarde les tokens Strava (chiffrés côté Supabase avec RLS)
        
        Args:
            strava_id: ID Strava
            access_token: Token d'accès
            refresh_token: Token de rafraîchissement
            expires_at: Timestamp d'expiration
        """
        try:
            token_data = {
                'strava_id': strava_id,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': expires_at,
                'updated_at': datetime.now().isoformat()
            }
            
            # Vérifier si existe
            result = self.client.table('strava_tokens').select('*').eq('strava_id', strava_id).execute()
            
            if result.data:
                # Mise à jour
                self.client.table('strava_tokens').update(token_data).eq('strava_id', strava_id).execute()
            else:
                # Création
                token_data['created_at'] = datetime.now().isoformat()
                self.client.table('strava_tokens').insert(token_data).execute()
            
            return True
        
        except Exception as e:
            print(f"Erreur save_strava_token: {e}")
            return False
    
    def get_strava_token(self, strava_id: str) -> Optional[Dict]:
        """Récupère les tokens Strava"""
        try:
            result = self.client.table('strava_tokens').select('*').eq('strava_id', strava_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur get_strava_token: {e}")
            return None
    
    # ===== CACHE DONNÉES STRAVA =====
    
    def save_strava_activities(self, strava_id: str, activities: List[Dict]):
        """
        Sauvegarde les activités Strava en cache
        
        Args:
            strava_id: ID Strava
            activities: Liste des activités
        """
        try:
            cache_data = {
                'strava_id': strava_id,
                'activities': json.dumps(activities),
                'cached_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
            # Vérifier si existe
            result = self.client.table('strava_cache').select('*').eq('strava_id', strava_id).execute()
            
            if result.data:
                # Mise à jour
                self.client.table('strava_cache').update(cache_data).eq('strava_id', strava_id).execute()
            else:
                # Création
                self.client.table('strava_cache').insert(cache_data).execute()
            
            return True
        
        except Exception as e:
            print(f"Erreur save_strava_activities: {e}")
            return False
    
    def get_strava_activities(self, strava_id: str) -> Optional[List[Dict]]:
        """
        Récupère les activités Strava du cache si valide
        
        Returns:
            Liste d'activités ou None si cache expiré
        """
        try:
            result = self.client.table('strava_cache').select('*').eq('strava_id', strava_id).execute()
            
            if not result.data:
                return None
            
            cache = result.data[0]
            
            # Vérifier expiration (gérer les timezones)
            expires_at_str = cache['expires_at']
            
            # Parser avec timezone
            if expires_at_str.endswith('Z'):
                expires_at_str = expires_at_str[:-1] + '+00:00'
            
            expires_at = datetime.fromisoformat(expires_at_str)
            
            # Comparer avec datetime.now() en UTC
            from datetime import timezone
            now = datetime.now(timezone.utc)
            
            # Si expires_at n'a pas de timezone, on considère qu'il est en UTC
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            if now > expires_at:
                return None
            
            return json.loads(cache['activities'])
        
        except Exception as e:
            print(f"Erreur get_strava_activities: {e}")
            return None
    
    # ===== PRÉFÉRENCES UTILISATEUR =====
    
    def save_user_preferences(self, strava_id: str, preferences: Dict):
        """
        Sauvegarde les préférences utilisateur
        
        Args:
            strava_id: ID Strava
            preferences: Dict avec fc_max, fc_repos, genre, etc.
        """
        try:
            pref_data = {
                'strava_id': strava_id,
                'fc_max': preferences.get('fc_max'),
                'fc_repos': preferences.get('fc_repos'),
                'gender': preferences.get('gender'),
                'runner_level': preferences.get('runner_level'),
                'updated_at': datetime.now().isoformat()
            }
            
            # Vérifier si existe
            result = self.client.table('user_preferences').select('*').eq('strava_id', strava_id).execute()
            
            if result.data:
                # Mise à jour
                self.client.table('user_preferences').update(pref_data).eq('strava_id', strava_id).execute()
            else:
                # Création
                pref_data['created_at'] = datetime.now().isoformat()
                self.client.table('user_preferences').insert(pref_data).execute()
            
            return True
        
        except Exception as e:
            print(f"Erreur save_user_preferences: {e}")
            return False
    
    def get_user_preferences(self, strava_id: str) -> Optional[Dict]:
        """Récupère les préférences utilisateur"""
        try:
            result = self.client.table('user_preferences').select('*').eq('strava_id', strava_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur get_user_preferences: {e}")
            return None
    
    # ===== OBJECTIFS DE SAISON =====
    
    def save_race_goal(self, strava_id: str, goal: Dict) -> bool:
        """
        Sauvegarde un objectif de course
        
        Args:
            strava_id: ID Strava
            goal: Dictionnaire avec les données de l'objectif
        """
        try:
            goal_data = {
                'strava_id': strava_id,
                'name': goal['name'],
                'date': goal['date'].isoformat() if hasattr(goal['date'], 'isoformat') else str(goal['date']),
                'distance_km': goal['distance_km'],
                'elevation_m': goal['elevation_m'],
                'race_type': goal['type'],
                'estimated_time_hours': goal['estimated_time_hours'],
                'pace_estimation': goal['pace_estimation'],
                'elevation_penalty': goal['elevation_penalty'],
                'created_at': datetime.now().isoformat()
            }
            
            self.client.table('race_goals').insert(goal_data).execute()
            return True
        
        except Exception as e:
            print(f"Erreur save_race_goal: {e}")
            return False
    
    def get_race_goals(self, strava_id: str) -> List[Dict]:
        """Récupère tous les objectifs de course d'un utilisateur"""
        try:
            result = self.client.table('race_goals').select('*').eq('strava_id', strava_id).order('date').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erreur get_race_goals: {e}")
            return []
    
    def delete_race_goal(self, goal_id: int) -> bool:
        """Supprime un objectif de course"""
        try:
            self.client.table('race_goals').delete().eq('id', goal_id).execute()
            return True
        except Exception as e:
            print(f"Erreur delete_race_goal: {e}")
            return False
    
    def update_race_goal(self, goal_id: int, goal: Dict) -> bool:
        """Met à jour un objectif de course"""
        try:
            goal_data = {
                'name': goal['name'],
                'date': goal['date'].isoformat() if hasattr(goal['date'], 'isoformat') else str(goal['date']),
                'distance_km': goal['distance_km'],
                'elevation_m': goal['elevation_m'],
                'race_type': goal['type'],
                'estimated_time_hours': goal['estimated_time_hours'],
                'updated_at': datetime.now().isoformat()
            }
            
            self.client.table('race_goals').update(goal_data).eq('id', goal_id).execute()
            return True
        
        except Exception as e:
            print(f"Erreur update_race_goal: {e}")
            return False
