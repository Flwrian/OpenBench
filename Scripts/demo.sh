#!/bin/bash
# Script pour lancer le serveur Django avec des données de test

cd "$(dirname "$0")/.."

echo "🧹 Nettoyage des anciennes données..."
python Scripts/quick_mock.py clear 2>/dev/null || echo "Aucune donnée à nettoyer"

echo ""
echo "🎲 Génération de 15 tests de démonstration..."
python Scripts/quick_mock.py 15

echo ""
echo "🚀 Démarrage du serveur Django..."
echo "📊 Ouvrez http://localhost:8000/ pour voir les résultats"
echo "   - Barre WDL colorée (Vert/Gris/Rouge) avec animations"
echo "   - Fond sombre bleu"
echo "   - Hover effects sur les barres"
echo ""
python manage.py runserver
