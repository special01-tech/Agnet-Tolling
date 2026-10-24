#!/usr/bin/env python3
"""
🤖 KWAME AI - Agent PydanticAI avec Outils Intégrés
Version corrigée avec outils décorés directement sur l'agent
"""

import os
import requests
import trafilatura
from dotenv import load_dotenv
from pydantic_ai import Agent, ModelMessage
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from pydantic_ai.models.google import GoogleModel

load_dotenv()

# Configuration des modèles
llama_model = GroqModel(
    'llama-3.3-70b-versatile',
    provider=GroqProvider(api_key=os.getenv('GROQ_API_KEY'))
)

gpt_model = GroqModel(
    'gpt-oss-120b',
    provider=GroqProvider(api_key=os.getenv('GROQ_API_KEY'))
)

gemini_model = GoogleModel('gemini-1.5-flash')

async def keep_recent_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
    """Keep only the last 10 messages to manage token usage."""
    return messages[-10:] if len(messages) > 10 else messages

# Création de l'agent
agent = Agent(
    llama_model,
    history_processors=[keep_recent_messages]
)

# ===== IMPORT DES OUTILS =====
from tools.tavily_search import tavily_search
from tools.weather_tool import get_weather, get_weather_forecast
from tools.link_retriever import online_article_retriever, get_article_metadata
from tools.send_mail import send_email
from tools.notes_tool import (
    save_note, list_notes, search_notes, get_note_by_id,
    update_note, delete_note, list_categories, get_notes_stats
)
from tools.calendar_manager import (
    get_todays_events, create_event, check_availability,
    get_events_by_date, get_upcoming_events, delete_event
)

# ===== OUTILS NOTES =====
@agent.tool_plain
def save_note_tool(title: str, content: str, category: str = "general") -> str:
    """Sauvegarde une note avec titre et contenu"""
    return save_note(title, content, category)

@agent.tool_plain
def list_notes_tool(category: str = None) -> str:
    """Liste toutes les notes ou par catégorie"""
    return list_notes(category)

@agent.tool_plain
def search_notes_tool(keyword: str) -> str:
    """Recherche des notes par mot-clé"""
    return search_notes(keyword)

@agent.tool_plain
def get_note_tool(note_id: int) -> str:
    """Affiche une note spécifique par ID"""
    return get_note_by_id(note_id)

@agent.tool_plain
def update_note_tool(note_id: int, title: str = None, content: str = None, category: str = None) -> str:
    """Met à jour une note existante"""
    return update_note(note_id, title, content, category)

@agent.tool_plain
def delete_note_tool(note_id: int) -> str:
    """Supprime une note par ID"""
    return delete_note(note_id)

@agent.tool_plain
def list_categories_tool() -> str:
    """Liste toutes les catégories disponibles"""
    return list_categories()

@agent.tool_plain
def get_notes_stats_tool() -> str:
    """Affiche les statistiques des notes"""
    return get_notes_stats()

# ===== OUTILS CALENDRIER =====
@agent.tool_plain
def get_todays_events_tool() -> str:
    """Affiche les événements du jour"""
    return get_todays_events()

@agent.tool_plain
def create_event_tool(title: str, date: str, start_time: str, end_time: str, description: str = "") -> str:
    """Crée un nouvel événement"""
    return create_event(title, date, start_time, end_time, description)

@agent.tool_plain
def check_availability_tool(date: str, start_time: str, end_time: str) -> str:
    """Vérifie la disponibilité pour un créneau horaire"""
    return check_availability(date, start_time, end_time)

@agent.tool_plain
def get_events_by_date_tool(date: str) -> str:
    """Affiche les événements pour une date spécifique"""
    return get_events_by_date(date)

@agent.tool_plain
def get_upcoming_events_tool(days: int = 7) -> str:
    """Affiche les événements à venir"""
    return get_upcoming_events(days)

@agent.tool_plain
def delete_event_tool(event_id: int) -> str:
    """Supprime un événement"""
    return delete_event(event_id)

# ===== OUTIL EMAIL =====
@agent.tool_plain
def send_email_tool(receiver_email: str = "fredyhoundayi@gmail.com", subject: str = "Subject", message: str = "") -> str:
    """Envoie un email avec disclaimer automatique"""
    try:
        send_email(receiver_email, subject, message)
        return f"✅ Email envoyé avec succès à {receiver_email}"
    except Exception as e:
        return f"❌ Erreur lors de l'envoi de l'email: {str(e)}"
        # ===== INSTRUCTIONS DE L'AGENT =====
instructions = """
Je suis KWAME AI, votre assistant intelligent avec outils intégrés.

🎯 CAPACITÉS PRINCIPALES:
• Recherche web en temps réel avec Tavily
• Informations météo actuelles et prévisions
• Extraction et analyse de contenu web
• Gestion des notes avec catégories
• Gestion du calendrier et événements
• Envoi d'emails automatiques

💡 UTILISATION DES OUTILS:
- **Recherche web:** "cherche [sujet]" ou "trouve des informations sur [topic]"
- **Météo:** "météo à [ville]" ou "quelle température à [ville]"
- **Prévisions:** "prévisions météo pour [ville]"
- **Articles:** "analyse l'article [URL]" ou "extrais le contenu de [URL]"
- **Métadonnées:** "informations sur l'article [URL]"
- **Sauvegarder note:** "sauvegarde une note: [titre] - [contenu]"
- **Lister notes:** "montre mes notes" ou "liste les notes"
- **Rechercher note:** "cherche mes notes sur [mot-clé]"
- **Note spécifique:** "montre la note ID [numéro]"
- **Mettre à jour note:** "modifie la note ID [numéro] avec [nouveau contenu]"
- **Supprimer note:** "supprime la note ID [numéro]"
- **Catégories:** "montre les catégories de notes"
- **Statistiques:** "statistiques des notes"
- **Calendrier aujourd'hui:** "montre mes événements aujourd'hui"
- **Créer événement:** "crée un événement: [titre] le [date] de [heure] à [heure]"
- **Vérifier disponibilité:** "disponible le [date] de [heure] à [heure]"
- **Événements par date:** "montre les événements le [date]"
- **Événements à venir:** "montre mes événements pour les [nombre] prochains jours"
- **Envoyer email:** "envoie un email à [adresse] avec sujet [sujet] et message [message]"

🌐 MODÈLES DISPONIBLES:
• 🦆 **Llama 3.3 70b** - Rapide et efficace pour tâches quotidiennes
• 🧠 **GPT 5.2** - Équilibré et puissant pour analyses complexes
• ⚡ **Gemini Flash** - Ultra-rapide pour réponses instantanées

🔧 CONFIGURATION DES OUTILS:
• Tavily Search: {'✅' if os.getenv('TAVILY_API_KEY') else '❌ Clé API manquante'}
• WeatherAPI: {'✅' if os.getenv('GETWEATHER_API_KEY') else '❌ Clé API manquante'}
• Article Retriever: {'✅ Toujours disponible'}
• Notes Tool: {'✅ Toujours disponible (SQLite)'}
• Calendar Tool: {'✅ Toujours disponible (JSON)'}
• Email Tool: {'✅ Toujours disponible (Gmail SMTP)'}

Je suis prêt à vous aider avec tous vos projets! 🚀
"""
    """
    return send_email_draft(draft_id, approval)

@agent.tool_plain
def get_email_stats_tool() -> str:
    """
    Affiche des statistiques détaillées sur les emails.
    
    Returns:
        Statistiques complètes sur les emails
    """
    return get_email_stats()
from tools.notes_tool import (
    save_note, list_notes, search_notes, get_note, 
    update_note, delete_note, list_categories, get_notes_stats
)

@agent.tool_plain
def save_note_tool(title: str, content: str, tags: str = "", category: str = "general") -> str:
    """
    Sauvegarde une nouvelle note dans la base de données persistante.
    
    Args:
        title: Titre de la note
        content: Contenu détaillé de la note
        tags: Tags séparés par des virgules (optionnel)
        category: Catégorie de la note (défaut: general)
        
    Returns:
        Message de confirmation avec l'ID de la note créée
    """
    return save_note(title, content, tags, category)

@agent.tool_plain
def list_notes_tool(limit: int = 20, category: str = None) -> str:
    """
    Liste toutes les notes avec filtre optionnel par catégorie.
    
    Args:
        limit: Nombre maximum de notes à afficher (défaut: 20)
        category: Filtrer par catégorie spécifique (optionnel)
        
    Returns:
        Liste formatée des notes avec ID, titre, catégorie et date
    """
    return list_notes(limit, category)

@agent.tool_plain
def search_notes_tool(keyword: str, category: str = None) -> str:
    """
    Recherche des notes par mot-clé avec filtre optionnel par catégorie.
    
    Args:
        keyword: Mot-clé à rechercher dans les titres et contenus
        category: Limiter la recherche à une catégorie (optionnel)
        
    Returns:
        Liste des notes contenant le mot-clé
    """
    return search_notes(keyword, category)

@agent.tool_plain
def get_note_tool(note_id: int) -> str:
    """
    Récupère une note spécifique par son ID.
    
    Args:
        note_id: ID numérique de la note à récupérer
        
    Returns:
        Contenu complet de la note avec métadonnées
    """
    return get_note(note_id)

@agent.tool_plain
def update_note_tool(note_id: int, title: str = None, content: str = None, tags: str = None, category: str = None) -> str:
    """
    Met à jour une note existante.
    
    Args:
        note_id: ID de la note à mettre à jour
        title: Nouveau titre (optionnel)
        content: Nouveau contenu (optionnel)
        tags: Nouveaux tags (optionnel)
        category: Nouvelle catégorie (optionnel)
        
    Returns:
        Message de confirmation de la mise à jour
    """
    return update_note(note_id, title, content, tags, category)

@agent.tool_plain
def delete_note_tool(note_id: int) -> str:
    """
    Supprime une note par son ID.
    
    Args:
        note_id: ID de la note à supprimer
        
    Returns:
        Message de confirmation de la suppression
    """
    return delete_note(note_id)

@agent.tool_plain
def list_categories_tool() -> str:
    """
    Liste toutes les catégories de notes disponibles.
    
    Returns:
        Liste des catégories avec descriptions
    """
    return list_categories()

@agent.tool_plain
def get_notes_stats_tool() -> str:
    """
    Affiche des statistiques détaillées sur les notes.
    
    Returns:
        Statistiques complètes sur les notes stockées
    """
    return get_notes_stats()

# Instructions de l'agent
instructions = f"""
🤖 KWAME AI - Votre Assistant IA Complet avec Outils Personnalisés

Je suis KWAME, votre assistant IA intelligent avec accès à plusieurs outils puissants:

🛠️ **Outils disponibles:**
• 🔍 **tavily_search** - Recherche web en temps réel avec Tavily
• 🌤️ **get_weather** - Météo actuelle pour n'importe quelle ville
• 🌤️ **get_weather_forecast** - Prévisions météo sur plusieurs jours
• 📄 **online_article_retriever** - Extraction de contenu d'articles web
• 📋 **get_article_metadata** - Métadonnées d'articles (titre, auteur, date)
• 📝 **save_note_tool** - Sauvegarde des notes persistantes
• 📋 **list_notes_tool** - Liste toutes les notes avec filtres
• 🔍 **search_notes_tool** - Recherche des notes par mot-clé
• 📄 **get_note_tool** - Récupère une note spécifique
• ✏️ **update_note_tool** - Met à jour une note existante
• 🗑️ **delete_note_tool** - Supprime une note
• 📂 **list_categories_tool** - Liste les catégories de notes
• 📊 **get_notes_stats_tool** - Statistiques des notes
• 📅 **get_todays_events_tool** - Événements d'aujourd'hui
• 📝 **create_event_tool** - Créer un événement dans le calendrier
• 🔍 **check_availability_tool** - Vérifier la disponibilité horaire
• 📋 **get_events_by_date_tool** - Événements pour une date spécifique
• 📅 **get_upcoming_events_tool** - Événements à venir
• 📧 **get_recent_emails_tool** - Emails récents avec filtres
• 📧 **read_email_tool** - Lire le contenu d'un email spécifique
• 🔍 **search_emails_tool** - Rechercher des emails par mot-clé
• 📝 **draft_reply_tool** - Créer un brouillon de réponse
• 📤 **send_email_draft_tool** - Envoyer un brouillon (avec approbation)
• 📊 **get_email_stats_tool** - Statistiques des emails

🎯 CAPACITÉS PRINCIPALES:
• Analyse de texte et de code
• Calculs mathématiques complexes
• Recherche d'informations en temps réel
• Extraction et analyse de contenu web
• Prévisions météo détaillées

💡 UTILISATION DES OUTILS:
- **Recherche web:** "cherche [sujet]" ou "trouve des informations sur [topic]"
- **Météo:** "météo à [ville]" ou "quelle température à [ville],current dates "
- **Prévisions:** "prévisions météo pour [ville]"
- **Articles:** "analyse l'article [URL]" ou "extrais le contenu de [URL]"
- **Métadonnées:** "informations sur l'article [URL]"
- **Sauvegarder note:** "sauvegarde une note: [titre] - [contenu]"
- **Lister notes:** "montre mes notes" ou "liste les notes"
- **Rechercher note:** "cherche mes notes sur [mot-clé]"
- **Note spécifique:** "montre la note ID [numéro]"
- **Mettre à jour note:** "modifie la note ID [numéro] avec [nouveau contenu]"
- **Supprimer note:** "supprime la note ID [numéro]"
- **Catégories:** "montre les catégories de notes"
- **Statistiques:** "statistiques des notes"
- **Calendrier aujourd'hui:** "montre mes événements aujourd'hui"
- **Créer événement:** "crée un événement: [titre] le [date] de [heure] à [heure]"
- **Vérifier disponibilité:** "disponible le [date] de [heure] à [heure]"
- **Événements par date:** "montre les événements le [date]"
- **Événements à venir:** "montre mes événements pour les [nombre] prochains jours"
- **Emails récents:** "montre mes emails récents"
- **Lire email:** "lis l'email ID [numéro]"
- **Rechercher emails:** "cherche mes emails sur [sujet]"
- **Répondre email:** "réponds à l'email ID [numéro] avec [texte]"
- **Envoyer brouillon:** "envoie le brouillon ID [numéro] (nécessite approbation)"
- **Stats emails:** "statistiques des emails"

🌐 MODÈLES DISPONIBLES:
• 🦆 **Llama 3.3 70b** - Rapide et efficace pour tâches quotidiennes
• 🧠 **GPT 5.2** - Équilibré et puissant pour analyses complexes
• ⚡ **Gemini Flash** - Ultra-rapide pour réponses instantanées

🔧 CONFIGURATION DES OUTILS:
• Tavily Search: {'✅' if os.getenv('TAVILY_API_KEY') else '❌ Clé API manquante'}
• WeatherAPI: {'✅' if os.getenv('GETWEATHER_API_KEY') else '❌ Clé API manquante'}
• Article Retriever: {'✅ Toujours disponible'}
• Notes Tool: {'✅ Toujours disponible (SQLite)'}
• Calendar Tool: {'✅ Toujours disponible (JSON)'}
• Email Tool: {'✅ Toujours disponible (JSON)'}

Je suis prêt à vous aider avec tous vos projets! 🚀
"""

# Mettre à jour les instructions de l'agent
agent.instructions = instructions

# Configuration de l'interface web
app = agent.to_web(
    models={
        '🦆 Llama 3.3 70b': llama_model,
        '🧠 GPT 5.2': gpt_model,
        '⚡ Gemini Flash': gemini_model,
    },
    instructions="KWAME AI - Agent complet avec outils de recherche, météo et extraction d'articles",
)

if __name__ == "__main__":
    print("🤖 KWAME AI - Agent Complet avec Outils Intégrés")
    print("=" * 60)
    print("✅ Configuration:")
    print("  • Agent: KWAME AI avec outils décorés")
    print("  • Outils: Recherche web, Météo, Extraction d'articles")
    print("  • Modèles: Llama, GPT, Gemini")
    print("  • Interface: PydanticAI par défaut")
    print("\n🔑 Status des clés API:")
    print(f"  • Tavily: {'✅' if os.getenv('TAVILY_API_KEY') else '❌'}")
    print(f"  • WeatherAPI: {'✅' if os.getenv('GETWEATHER_API_KEY') else '❌'}")
    print(f"  • Groq: {'✅' if os.getenv('GROQ_API_KEY') else '❌'}")
    print(f"  • Gemini: {'✅' if os.getenv('GEMINI_API_KEY') else '❌'}")
    print("\n🚀 Lancement:")
    print("uvicorn pydantic_agent_fixed:app --host 127.0.0.1 --port 7932")
    print("\n📱 Interface: http://127.0.0.1:7932")
    print("\n🛠️ Outils disponibles:")
    print("  • tavily_search")
    print("  • get_weather")
    print("  • get_weather_forecast")
    print("  • online_article_retriever")
    print("  • get_article_metadata")
    print("\n💡 L'agent est prêt à vous aider!")
