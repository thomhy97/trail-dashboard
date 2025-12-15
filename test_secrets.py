import streamlit as st

st.title("🔍 Test des secrets")

st.write("Vérification des secrets configurés :")

secrets_to_check = [
    "STRAVA_CLIENT_ID",
    "STRAVA_CLIENT_SECRET", 
    "STRAVA_REDIRECT_URI",
    "SUPABASE_URL",
    "SUPABASE_KEY"
]

for secret in secrets_to_check:
    if secret in st.secrets:
        value = st.secrets[secret]
        # Masquer les valeurs sensibles
        if len(value) > 20:
            display = value[:10] + "..." + value[-10:]
        else:
            display = value[:5] + "..."
        st.success(f"✅ {secret} : {display}")
    else:
        st.error(f"❌ {secret} : MANQUANT")

st.divider()

# Test connexion Supabase
if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
    st.write("Test de connexion Supabase...")
    try:
        import os
        from database import SupabaseDB
        
        os.environ['SUPABASE_URL'] = st.secrets["SUPABASE_URL"]
        os.environ['SUPABASE_KEY'] = st.secrets["SUPABASE_KEY"]
        
        db = SupabaseDB()
        st.success("✅ Connexion Supabase réussie !")
        
        # Test de lecture
        st.write("Test de lecture des tables...")
        try:
            # Essayer de lire la table users
            from supabase import create_client
            client = create_client(
                st.secrets["SUPABASE_URL"],
                st.secrets["SUPABASE_KEY"]
            )
            result = client.table('users').select('*').limit(1).execute()
            st.success("✅ Lecture table 'users' : OK")
        except Exception as e:
            st.error(f"❌ Erreur lecture table : {e}")
            
    except Exception as e:
        st.error(f"❌ Erreur connexion Supabase : {e}")
else:
    st.warning("⚠️ SUPABASE_URL ou SUPABASE_KEY manquant")
