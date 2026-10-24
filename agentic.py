#!/usr/bin/env python3
"""
🤖 Agent IA Personnel avec Tool Calling
Propulsé par OpenRouter (GPT-4o) - Service unique Front + Back pour déploiement Render
"""

import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv

# Encodage UTF-8 pour Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kwame_ai.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("agentic")

from pydantic_ai import Agent, ModelMessage
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# =====================================================================
# CONFIGURATION DU MODÈLE IA : OpenRouter (GPT-4o)
# =====================================================================
openrouter_api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip()
openrouter_base_url = (os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip()
openrouter_model_name = (os.getenv("OPENROUTER_MODEL_NAME") or "openai/gpt-4o").strip()

if not openrouter_api_key:
    logger.warning("⚠️ OPENROUTER_API_KEY absente du fichier .env. Veuillez la configurer.")

openrouter_provider = OpenAIProvider(
    base_url=openrouter_base_url,
    api_key=openrouter_api_key or "missing_key"
)

main_model = OpenAIChatModel(
    openrouter_model_name,
    provider=openrouter_provider
)

logger.info(f"✅ Modèle configuré : {openrouter_model_name} via {openrouter_base_url}")

# =====================================================================
# INITIALISATION DE L'AGENT PYDANTIC-AI
# =====================================================================
agent = Agent(main_model)

# =====================================================================
# IMPORT DES OUTILS (dossier tools/)
# =====================================================================
from tools.tavily_search import tavily_search
from tools.weather_tool import get_weather, get_weather_forecast, compare_weather_tool
from tools.send_mail import send_email, create_email_draft
from tools.calendar_manager import (
    get_todays_events, get_upcoming_events, create_event, 
    update_event, delete_event
)
from tools.notion_tool import (
    search_notion_tool as _search_notion,
    read_notion_page_tool as _read_notion,
    create_notion_page_tool as _create_notion,
    append_to_notion_page_tool as _append_notion
)
from tools.drive_tool import (
    search_drive_tool as _search_drive,
    read_drive_file_tool as _read_drive
)

# =====================================================================
# ENREGISTREMENT DES OUTILS SUR L'AGENT (@agent.tool_plain)
# =====================================================================

# 1. Recherche Web (Tavily)
@agent.tool_plain
async def search_web_tool(query: str, max_results: int = 5) -> str:
    """Recherche web en temps réel avec Tavily. Fournit les sources et liens vérifiés."""
    logger.info(f"🔍 Recherche web: {query}")
    return tavily_search(query, max_results)

# 2. Météo (OpenWeather)
@agent.tool_plain
async def get_current_weather_tool(city: str) -> str:
    """Obtient la météo actuelle pour une ville donnée."""
    logger.info(f"🌤️ Météo actuelle: {city}")
    return get_weather(city)

@agent.tool_plain
async def get_weather_forecast_tool(city: str, days: int = 3) -> str:
    """Obtient les prévisions météo pour les prochains jours (y compris demain)."""
    logger.info(f"📅 Prévisions météo: {city} ({days} jours)")
    return get_weather_forecast(city, days)

@agent.tool_plain
async def compare_cities_weather_tool(cities: str) -> str:
    """Compare la météo entre plusieurs villes (ex: 'Lagos, Nairobi')."""
    logger.info(f"⚖️ Comparaison météo: {cities}")
    return compare_weather_tool(cities)

# 3. Email avec Confirmation Obligatoire et Liste Blanche
@agent.tool_plain
async def prepare_email_draft_tool(subject: str, message: str, receiver_email: Optional[str] = None) -> str:
    """
    Prépare et affiche un brouillon d'email sans l'envoyer.
    L'agent DOIT TOUJOURS appeler cet outil en premier et attendre la confirmation 'OUI' de l'utilisateur.
    """
    logger.info(f"📝 Préparation brouillon email: {subject}")
    return create_email_draft(subject=subject, message=message, receiver_email=receiver_email)

@agent.tool_plain
async def send_email_tool(confirmation: str, subject: str, message: str, receiver_email: Optional[str] = None) -> str:
    """
    Envoie l'email après accord explicite. Le paramètre 'confirmation' doit valoir 'oui', 'yes' ou 'confirmer'.
    L'agent ne doit appeler cet outil QUE si l'utilisateur a confirmé après avoir lu le brouillon.
    """
    logger.info(f"📧 Envoi email: confirmation='{confirmation}', sujet='{subject}'")
    return send_email(receiver_email=receiver_email, subject=subject, message=message, confirmation=confirmation)

# 4. Calendrier avec Confirmation Obligatoire (Google Calendar)
@agent.tool_plain
async def get_todays_calendar_tool() -> str:
    """Affiche les événements prévus aujourd'hui dans l'agenda."""
    return get_todays_events()

@agent.tool_plain
async def get_upcoming_calendar_tool(days: int = 7) -> str:
    """Affiche les événements des prochains jours dans l'agenda."""
    return get_upcoming_events(days)

@agent.tool_plain
async def create_calendar_event_tool(title: str, date: str, start_time: str, end_time: str, description: str = "") -> str:
    """Crée un nouvel événement dans l'agenda (date au format YYYY-MM-DD, heures HH:MM)."""
    logger.info(f"📅 Création événement: {title} le {date}")
    return create_event(title, date, start_time, end_time, description)

@agent.tool_plain
async def update_calendar_event_tool(event_id: str, title: Optional[str] = None, date: Optional[str] = None,
                                   start_time: Optional[str] = None, end_time: Optional[str] = None,
                                   description: Optional[str] = None, confirmation: str = "") -> str:
    """
    Modifie un événement d'agenda existant.
    CONFIRMATION OBLIGATOIRE : L'agent doit d'abord demander l'accord de l'utilisateur.
    Si confirmation != 'oui', l'action est suspendue et le récapitulatif est présenté.
    """
    logger.info(f"✏️ Modification événement {event_id} (confirmation={confirmation})")
    return update_event(event_id, title, date, start_time, end_time, description, confirmation)

@agent.tool_plain
async def delete_calendar_event_tool(event_id: str, confirmation: str = "") -> str:
    """
    Supprime définitivement un événement d'agenda.
    CONFIRMATION OBLIGATOIRE : L'agent doit d'abord demander confirmation à l'utilisateur.
    Si confirmation != 'oui', l'action est suspendue.
    """
    logger.info(f"🗑️ Suppression événement {event_id} (confirmation={confirmation})")
    return delete_event(event_id, confirmation)

# 5. Notion
@agent.tool_plain
async def search_notion_pages_tool(query: str = "") -> str:
    """Recherche des pages et bases de données Notion par mot-clé."""
    logger.info(f"📚 Recherche Notion: {query}")
    return _search_notion(query)

@agent.tool_plain
async def read_notion_page_tool(page_id: str) -> str:
    """Lit le texte d'une page Notion à partir de son ID."""
    logger.info(f"📖 Lecture Notion ID: {page_id}")
    return _read_notion(page_id)

@agent.tool_plain
async def create_notion_page_tool(title: str, content: str = "", parent_page_id: str = "") -> str:
    """Crée une nouvelle page dans Notion."""
    logger.info(f"📝 Création page Notion: {title}")
    return _create_notion(title, content, parent_page_id)

@agent.tool_plain
async def append_to_notion_page_tool(page_id: str, content: str) -> str:
    """Ajoute du contenu à une page Notion existante."""
    logger.info(f"➕ Ajout contenu Notion: {page_id}")
    return _append_notion(page_id, content)

# 6. Google Drive
@agent.tool_plain
async def search_google_drive_tool(query: str, max_results: int = 5) -> str:
    """Recherche des documents Google Docs et fichiers texte sur Google Drive."""
    logger.info(f"📁 Recherche Google Drive: {query}")
    return _search_drive(query, max_results)

@agent.tool_plain
async def read_google_drive_file_tool(file_id: str) -> str:
    """Lit le texte intégral d'un Google Doc ou fichier texte à partir de son ID."""
    logger.info(f"📄 Lecture Google Drive ID: {file_id}")
    return _read_drive(file_id)

# =====================================================================
# INSTRUCTIONS SYSTÈME DE L'AGENT
# =====================================================================
allowed_email = os.getenv("ALLOWED_EMAIL_RECIPIENT", "Non configuré")

agent.instructions = f"""
Tu es l'Agent IA Personnel de l'utilisateur, propulsé par GPT-4o via OpenRouter.
Tu as accès à une palette d'outils (Tool Calling) pour la recherche web, la météo, la messagerie, le calendrier, Notion et Google Drive.

🚨 RÈGLES CRITIQUES DE SÉCURITÉ ET DE CONFIRMATION (NON NÉGOCIABLES) :

1. ENVOI D'EMAILS :
   - Destinataire exclusif (Liste blanche) : Tu n'as le droit d'envoyer des emails QU'À `{allowed_email}`. Refuse tout autre destinataire.
   - Procédure en 2 temps obligatoire :
     a) Quand l'utilisateur demande d'envoyer un email, utilise TOUJOURS `prepare_email_draft_tool`.
        Affiche clairement le destinataire, l'objet et le texte complet, puis invite explicitement : « Répondez OUI pour confirmer l'envoi ».
     b) N'appelle JAMAIS `send_email_tool` dans le même tour ! Tu dois impérativement attendre un nouveau message de confirmation (« oui », « confirme ») avant de déclencher l'envoi réel avec confirmation="oui".

2. MODIFICATION ET SUPPRESSION D'ÉVÉNEMENTS D'AGENDA :
   - Avant de supprimer (`delete_calendar_event_tool`) ou de modifier (`update_calendar_event_tool`) un événement, présente l'action envisagée et demande confirmation à l'utilisateur.
   - N'exécute la suppression ou la modification qu'après un « OUI » explicite dans la conversation.

3. UTILISATION DES AUTRES OUTILS :
   - Recherche Web : Utilise `search_web_tool` pour actualités et faits récents. Fournis toujours les sources et liens.
   - Météo : Utilise `get_current_weather_tool`, `get_weather_forecast_tool` (pour demain et prochains jours), ou `compare_cities_weather_tool`.
   - Notion : Recherche (`search_notion_pages_tool`), lecture (`read_notion_page_tool`), création (`create_notion_page_tool`), ajout (`append_to_notion_page_tool`).
   - Drive : Recherche (`search_google_drive_tool`) et lecture (`read_google_drive_file_tool`).

Sois synthétique, réactif et rigoureux.
"""

# =====================================================================
# APPLICATION WEB ASGI / FASTAPI (agent.to_web)
# =====================================================================
render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")

allowed_hosts = [
    "localhost",
    "127.0.0.1",
    "agnet-tolling.onrender.com",
    "*.onrender.com",
    "*"
]
if render_hostname and render_hostname not in allowed_hosts:
    allowed_hosts.append(render_hostname)

app = agent.to_web(
    models={
        f"🧠 GPT-4o ({openrouter_model_name})": main_model,
    },
    instructions="Agent IA personnel avec Tool Calling - Service unifié Front + Back",
    allowed_hosts=allowed_hosts,
)

def main():
    print(f"🚀 KWAME AI démarré avec succès.")
    print(f"Modèle actif : {openrouter_model_name}")
    print(f"Destinataire autorisé : {allowed_email}")

if __name__ == "__main__":
    main()
