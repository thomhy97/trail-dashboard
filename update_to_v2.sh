#!/bin/bash

# Script de mise à jour vers V2
# Usage: ./update_to_v2.sh

echo "🏔️ Trail Dashboard - Migration vers V2"
echo "========================================"
echo ""

# Vérification qu'on est dans un repo git
if [ ! -d .git ]; then
    echo "❌ Erreur: Ce n'est pas un repo Git"
    echo "   Lance ce script depuis la racine de ton repo trail-dashboard"
    exit 1
fi

# Sauvegarde des secrets si ils existent
echo "📦 Sauvegarde de secrets.toml..."
if [ -f .streamlit/secrets.toml ]; then
    cp .streamlit/secrets.toml /tmp/secrets_backup.toml
    echo "✅ Secrets sauvegardés dans /tmp/secrets_backup.toml"
else
    echo "⚠️  Pas de secrets.toml trouvé (normal si première installation)"
fi

echo ""
echo "🔄 Vérification du statut Git..."
git status

echo ""
read -p "📝 Veux-tu continuer avec la mise à jour V2 ? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Migration annulée"
    exit 1
fi

# Commit des changements locaux si nécessaire
if [[ `git status --porcelain` ]]; then
    echo ""
    echo "💾 Sauvegarde de tes changements locaux..."
    git add .
    git commit -m "Sauvegarde avant migration V2"
    echo "✅ Changements locaux sauvegardés"
fi

# Restauration des secrets
if [ -f /tmp/secrets_backup.toml ]; then
    echo ""
    echo "🔑 Restauration de secrets.toml..."
    mkdir -p .streamlit
    cp /tmp/secrets_backup.toml .streamlit/secrets.toml
    echo "✅ Secrets restaurés"
fi

# Installation des dépendances
echo ""
echo "📦 Installation de numpy..."
if command -v python3 &> /dev/null; then
    python3 -m pip install numpy==1.26.2
elif command -v python &> /dev/null; then
    python -m pip install numpy==1.26.2
else
    echo "⚠️  Python non trouvé, installe numpy manuellement:"
    echo "   pip install numpy==1.26.2"
fi

echo ""
echo "✨ Migration vers V2 complète !"
echo ""
echo "📋 Prochaines étapes:"
echo "   1. Teste localement: streamlit run app.py"
echo "   2. Si OK, commit et push:"
echo "      git add ."
echo "      git commit -m 'Migration vers V2 avec analyse de charge'"
echo "      git push origin main"
echo ""
echo "📖 Consulte MIGRATION.md pour plus de détails"
echo "📖 Lis GUIDE_UTILISATION.md pour comprendre les nouvelles features"
echo ""
echo "🏃 Bon entraînement !"
