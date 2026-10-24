#!/usr/bin/env python3
"""
📄 Online Article Retriever Tool pour PydanticAI
Extraction de contenu d'articles en ligne avec Trafilatura
"""

import os
from dotenv import load_dotenv
import requests
import trafilatura
from typing import Dict, Any

load_dotenv()

class OnlineArticleRetriever:
    """Outil d'extraction d'articles en ligne pour PydanticAI"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_content(self, url: str) -> str:
        """
        Extrait et analyse le contenu d'un article en ligne
        
        Args:
            url: URL de l'article à extraire
            
        Returns:
            Contenu de l'article formaté et nettoyé
        """
        try:
            # Vérifier que l'URL est valide
            if not url.startswith(('http://', 'https://')):
                return "❌ URL invalide. L'URL doit commencer par http:// ou https://"
            
            # Faire la requête avec timeout
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Vérifier le type de contenu
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return f"❌ Le contenu n'est pas du HTML. Type détecté: {content_type}"
            
            # Extraire le contenu avec trafilatura
            content = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=True,
                include_formatting=True,
                include_links=True
            )
            
            if not content:
                # Essayer une méthode alternative
                content = trafilatura.extract(
                    response.text,
                    fallback=True,
                    include_comments=False,
                    include_tables=False,
                    include_formatting=False
                )
            
            if content:
                # Limiter la longueur pour éviter les réponses trop longues
                max_length = 8000
                if len(content) > max_length:
                    content = content[:max_length] + "\n\n... (contenu tronqué pour la lisibilité)"
                
                # Formater la réponse
                output = f"📄 **Contenu extrait de:** {url}\n\n"
                output += f"📊 **Longueur:** {len(content)} caractères\n\n"
                output += f"📝 **Contenu:**\n\n{content}"
                
                return output
            else:
                return f"❌ Impossible d'extraire le contenu de l'URL: {url}\n\n💡 Suggestions:\n- Vérifiez que l'URL pointe vers une page web avec du contenu textuel\n- Certains sites peuvent bloquer l'extraction automatique\n- Essayez une URL différente"
                
        except requests.exceptions.Timeout:
            return f"❌ Timeout lors de la récupération de l'URL: {url}"
        except requests.exceptions.ConnectionError:
            return f"❌ Erreur de connexion lors de la récupération de l'URL: {url}"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                return f"❌ Accès interdit (403) pour l'URL: {url}\nLe site bloque probablement l'accès automatique."
            elif e.response.status_code == 404:
                return f"❌ Page non trouvée (404) pour l'URL: {url}"
            else:
                return f"❌ Erreur HTTP {e.response.status_code} pour l'URL: {url}"
        except Exception as e:
            return f"❌ Erreur lors de l'extraction de l'article: {str(e)}\n\nURL: {url}"
    
    def extract_metadata(self, url: str) -> Dict[str, Any]:
        """
        Extrait les métadonnées d'un article
        
        Args:
            url: URL de l'article
            
        Returns:
            Dictionnaire avec les métadonnées extraites
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            metadata = trafilatura.extract_metadata(response.text, default_url=url)
            
            if metadata:
                return {
                    "title": metadata.title or "Titre non trouvé",
                    "author": metadata.author or "Auteur non trouvé",
                    "date": metadata.date or "Date non trouvée",
                    "description": metadata.description or "Description non trouvée",
                    "url": metadata.url or url,
                    "language": metadata.language or "Langue non détectée"
                }
            else:
                return {"error": "Impossible d'extraire les métadonnées"}
                
        except Exception as e:
            return {"error": f"Erreur lors de l'extraction des métadonnées: {str(e)}"}

# Fonction pour PydanticAI
def online_article_retriever(url: str) -> str:
    """
    Récupère et analyse le contenu d'un article en ligne donné son URL.
    
    Utilisez cet outil quand:
    - vous avez besoin d'informations spécifiques d'un article en ligne connu
    - l'URL nécessite un contenu détaillé d'une source spécifique
    - vous voulez analyser ou résumer le contenu d'une page web
    
    Args:
        url: URL de l'article en ligne
        
    Returns:
        Le contenu analysé de l'article en ligne sous forme de chaîne de caractères.
    """
    tool = OnlineArticleRetriever()
    return tool.extract_content(url)

def get_article_metadata(url: str) -> str:
    """
    Extrait les métadonnées d'un article en ligne.
    
    Args:
        url: URL de l'article
        
    Returns:
        Métadonnées formatées (titre, auteur, date, description, etc.)
    """
    tool = OnlineArticleRetriever()
    metadata = tool.extract_metadata(url)
    
    if "error" in metadata:
        return f"❌ {metadata['error']}"
    
    output = f"📋 **Métadonnées de l'article:**\n\n"
    output += f"📰 **Titre:** {metadata['title']}\n"
    output += f"✍️ **Auteur:** {metadata['author']}\n"
    output += f"📅 **Date:** {metadata['date']}\n"
    output += f"📝 **Description:** {metadata['description']}\n"
    output += f"🌐 **URL:** {metadata['url']}\n"
    output += f"🌍 **Langue:** {metadata['language']}\n"
    
    return output

if __name__ == "__main__":
    # Test de l'outil
    print("📄 Test Online Article Retriever")
    print("=" * 50)
    
    # Test URL (remplacez par une URL réelle pour tester)
    test_url = "https://www.example.com/article"
    print(f"Test avec URL: {test_url}")
    print(online_article_retriever(test_url))
