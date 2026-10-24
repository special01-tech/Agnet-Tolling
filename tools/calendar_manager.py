import os
import datetime
from typing import Optional
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]

def get_calendar_service():
    """
    Construit le service Google Calendar soit depuis les variables d'environnement
    (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN), soit depuis token.json.
    """
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    # Mode 1 : Variables d'environnement directes (Recommandé pour Render et Cloud)
    if refresh_token and client_id and client_secret:
        try:
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES
            )
            creds.refresh(Request())
            return build("calendar", "v3", credentials=creds)
        except Exception as e:
            print(f"⚠️ Erreur initialisation Google Calendar via refresh_token: {e}")

    # Mode 2 : Fallback fichier local token.json
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            return build("calendar", "v3", credentials=creds)
        except Exception as e:
            print(f"⚠️ Erreur token.json: {e}")

    return None

def get_todays_events() -> str:
    """Affiche les événements du jour"""
    service = get_calendar_service()
    if service is None:
        return "❌ Service Google Calendar non connecté. Veuillez renseigner GOOGLE_REFRESH_TOKEN dans votre .env."

    try:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        end_of_day = datetime.datetime.now(datetime.timezone.utc).replace(hour=23, minute=59, second=59).isoformat()

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
        if not events:
            return "📅 Aucun événement prévu pour aujourd'hui."

        output = f"📅 **Événements d'aujourd'hui ({len(events)}) :**\n\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "Sans titre")
            event_id = event.get("id", "N/A")
            output += f"• **{summary}** (ID: `{event_id}`) à {start}\n"

        return output.strip()
    except Exception as e:
        return f"❌ Erreur récupération événements : {str(e)}"

def get_upcoming_events(days: int = 7) -> str:
    """Affiche les événements à venir pour les prochains jours"""
    service = get_calendar_service()
    if service is None:
        return "❌ Service Google Calendar non connecté. Veuillez renseigner GOOGLE_REFRESH_TOKEN dans votre .env."

    try:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        future = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)).isoformat()

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=future,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
        if not events:
            return f"📅 Aucun événement trouvé pour les {days} prochains jours."

        output = f"📆 **Événements des {days} prochains jours ({len(events)}) :**\n\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "Sans titre")
            event_id = event.get("id", "N/A")
            output += f"• **{summary}** (ID: `{event_id}`) — {start}\n"

        return output.strip()
    except Exception as e:
        return f"❌ Erreur récupération événements à venir : {str(e)}"

def create_event(title: str, date: str, start_time: str, end_time: str, description: str = "") -> str:
    """Crée un nouvel événement dans Google Calendar"""
    service = get_calendar_service()
    if service is None:
        return "❌ Service Google Calendar non connecté. Veuillez renseigner GOOGLE_REFRESH_TOKEN dans votre .env."

    try:
        start_datetime = f"{date}T{start_time}:00"
        end_datetime = f"{date}T{end_time}:00"

        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_datetime, "timeZone": "UTC"},
            "end": {"dateTime": end_datetime, "timeZone": "UTC"},
        }

        created = service.events().insert(calendarId="primary", body=event).execute()
        event_id = created.get("id", "N/A")
        return f"✅ Événement créé avec succès !\n• Titre : **{title}**\n• Date : {date} de {start_time} à {end_time}\n• ID : `{event_id}`"
    except Exception as e:
        return f"❌ Erreur lors de la création de l'événement : {str(e)}"

def update_event(event_id: str, title: Optional[str] = None, date: Optional[str] = None, 
                 start_time: Optional[str] = None, end_time: Optional[str] = None, 
                 description: Optional[str] = None, confirmation: str = "") -> str:
    """
    Modifie un événement existant dans Google Calendar.
    CONFIRMATION OBLIGATOIRE : confirmation doit valoir 'oui', 'yes' ou 'confirmer'.
    """
    service = get_calendar_service()
    if service is None:
        return "❌ Service Google Calendar non connecté. Veuillez renseigner GOOGLE_REFRESH_TOKEN dans votre .env."

    # 1. Vérification de la confirmation
    valid_confirmations = {"oui", "yes", "confirmer", "valider", "confirm"}
    if not confirmation or confirmation.strip().lower() not in valid_confirmations:
        return (
            f"⚠️ **Confirmation obligatoire pour modification d'événement :**\n"
            f"Vous souhaitez modifier l'événement `{event_id}` avec les paramètres suivants :\n"
            f"• Titre : {title or '(inchangé)'}\n"
            f"• Date/Heure : {date or '(inchangé)'} {start_time or ''} - {end_time or ''}\n"
            f"• Description : {description or '(inchangée)'}\n\n"
            f"Veuillez répondre explicitement **« OUI »** dans le chat pour exécuter cette modification."
        )

    try:
        event = service.events().get(calendarId="primary", eventId=event_id).execute()
        if title:
            event["summary"] = title
        if description is not None:
            event["description"] = description
        if date and start_time and end_time:
            event["start"] = {"dateTime": f"{date}T{start_time}:00", "timeZone": "UTC"}
            event["end"] = {"dateTime": f"{date}T{end_time}:00", "timeZone": "UTC"}

        updated = service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
        return f"✅ Événement `{event_id}` mis à jour avec succès : **{updated.get('summary')}**"
    except Exception as e:
        return f"❌ Erreur lors de la mise à jour de l'événement : {str(e)}"

def delete_event(event_id: str, confirmation: str = "") -> str:
    """
    Supprime un événement dans Google Calendar.
    CONFIRMATION OBLIGATOIRE : confirmation doit valoir 'oui', 'yes' ou 'confirmer'.
    """
    service = get_calendar_service()
    if service is None:
        return "❌ Service Google Calendar non connecté. Veuillez renseigner GOOGLE_REFRESH_TOKEN dans votre .env."

    # 1. Vérification de la confirmation
    valid_confirmations = {"oui", "yes", "confirmer", "valider", "confirm"}
    if not confirmation or confirmation.strip().lower() not in valid_confirmations:
        try:
            ev = service.events().get(calendarId="primary", eventId=event_id).execute()
            summary = ev.get("summary", "Sans titre")
        except Exception:
            summary = "Inconnu"
        return (
            f"⚠️ **Confirmation obligatoire pour suppression d'événement :**\n"
            f"Êtes-vous certain de vouloir supprimer définitivement l'événement **« {summary} »** (ID: `{event_id}`) ?\n"
            f"Veuillez répondre explicitement **« OUI »** dans le chat pour confirmer la suppression."
        )

    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return f"🗑️ Événement `{event_id}` supprimé avec succès de Google Calendar !"
    except Exception as e:
        return f"❌ Erreur lors de la suppression de l'événement : {str(e)}"

if __name__ == "__main__":
    print(get_todays_events())
