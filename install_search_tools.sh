#!/bin/bash

# 🔧 Installation des dépendances pour les outils de recherche

echo "📦 Installation des dépendances PydanticAI avec outils de recherche..."

cd /home/fredy/Téléchargements/pydantic_agants

# Activer l'environnement virtuel
source venv/bin/activate

echo "🦆 Installation DuckDuckGo Search..."
pip install "pydantic-ai-slim[duckduckgo]"

echo "🔍 Installation Tavily Search..."
pip install "pydantic-ai-slim[tavily]"

echo "🧠 Installation Exa Search..."
pip install "pydantic-ai-slim[exa]"

echo ""
echo "✅ Installation terminée!"
echo ""
echo "🔑 Configuration des clés API (optionnel):"
echo "Ajoutez à votre fichier .env:"
echo ""
echo "# Tavily API (gratuit pour tester)"
echo "TAVILY_API_KEY=votre_cle_tavily_ici"
echo ""
echo "# Exa API (gratuit pour tester)"
echo "EXA_API_KEY=votre_cle_exa_ici"
echo ""
echo "🌐 Liens pour obtenir les clés:"
echo "• Tavily: https://app.tavily.com/home"
echo "• Exa: https://dashboard.exa.ai"
echo ""
echo "🚀 Démarrez le serveur:"
echo "uvicorn model1:app --host 127.0.0.1 --port 7932"
echo ""
echo "🔧 Outils disponibles:"
echo "• DuckDuckGo Search (gratuit, pas de clé requise)"
echo "• Tavily Search (nécessite clé API)"
echo "• Exa Search (nécessite clé API)"
echo "• Code Execution (calculs et programmation)"
