#!/usr/bin/env python3
"""
🔍 Tavily Search Tool pour PydanticAI
Recherche web en temps réel avec Tavily API
"""

import os
from dotenv import load_dotenv
import requests
from typing import Dict, Any

load_dotenv()

class TavilySearchTool:
    """Outil de recherche web Tavily pour PydanticAI"""
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com/search"
    
    def search(self, query: str, max_results: int = 5) -> str:
        """
        Effectue une recherche web en temps réel avec Tavily
        
        Args:
            query: Question ou mots-clés de recherche
            max_results: Nombre maximum de résultats (défaut: 5)
            
        Returns:
            Résultats de recherche formatés avec titres, contenus et URLs
        """
        if not self.api_key:
            return "❌ TAVILY_API_KEY non configurée. Veuillez configurer votre clé API Tavily."
        
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
                "include_answer": True,
                "include_raw_content": False
            }
            
            response = requests.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Formater les résultats
            output = f"🔍 **Résultats de recherche pour '{query}':**\n\n"
            
            # Ajouter la réponse directe si disponible
            if data.get("answer"):
                output += f"💡 **Réponse directe:** {data['answer']}\n\n"
            
            # Ajouter les résultats détaillés
            for i, result in enumerate(data.get("results", []), 1):
                output += f"**{i}. {result.get('title', 'Sans titre')}**\n"
                output += f"📍 **URL:** {result.get('url', '')}\n"
                output += f"📝 **Contenu:** {result.get('content', 'Pas de contenu')[:300]}...\n"
                output += f"🔗 **Score:** {result.get('score', 'N/A')}\n\n"
            
            return output
            
        except requests.exceptions.RequestException as e:
            return f"❌ Erreur réseau lors de la recherche: {str(e)}"
        except Exception as e:
            return f"❌ Erreur lors de la recherche Tavily: {str(e)}"

# Fonction pour PydanticAI
def tavily_search(query: str, max_results: int = 5) -> str:
    """
    Effectue une recherche web en temps réel en utilisant Tavily.
    
    Utilisez cet outil quand vous avez besoin:
    - d'informations à jour ou en direct
    - de questions sur des événements récents, actualités ou tendances
    - de vérification factuelle
    - de connaissances externes au-delà des données d'entraînement du modèle
    
    Args:
        query: Question ou mots-clés de recherche
        max_results: Nombre maximum de résultats (optionnel, défaut: 5)
    
    Returns:
        Liste résumée des résultats pertinents avec titres, contenus extraits et URLs sources.
    """
    tool = TavilySearchTool()
    return tool.search(query, max_results)

if __name__ == "__main__":
    # Test de l'outil
    print("🔍 Test Tavily Search Tool")
    print("=" * 40)
    print(tavily_search("dernières nouvelles sur l'IA"))
